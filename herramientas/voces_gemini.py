"""Voces de El Jambo con Gemini TTS (plan gratuito): una petición por personaje y episodio.

El plan gratuito da 10 peticiones por día y por modelo, así que no se puede pedir réplica a réplica. Se hace en dos pasos:
  generar <pedido.json> <salida>   (necesita GEMINI_API_KEY; solo biblioteca estándar)
      Por cada personaje manda TODAS sus réplicas de TODOS los episodios del pedido en una sola petición, cada frase con su intención
      (emoción de la escena + carácter del personaje). Guarda lote_<personaje>.wav y plan.json.
  empaquetar <pedido.json> <salida>  voces.tar con los mp3 y los <n>_voces.json, subido a una URL pública temporal (listo.json).
  cortar <pedido.json> <salida>    (necesita faster-whisper, numpy y ffmpeg)
      Localiza cada palabra con Whisper, corta el audio por réplica, ajusta ritmo y volumen y escribe <n>_<i>.mp3 y
      <n>_voces.json (duración y tiempos de cada palabra, lo que necesita gen_episodios.py para los subtítulos).
Voces y estilos: equipo/voz_gemini.json. Creado el 23/11/2026 (orden del dueño: voces naturales, distintas, expresivas y gratis).
27/11/2026 (orden del dueño): Jambo habla con CECEO (s = z) y se le entiende; ver ceceo() más abajo.
"""
import base64, difflib, json, os, re, struct, subprocess, sys, time, unicodedata, urllib.error, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(RAIZ, "equipo", "voz_gemini.json"), encoding="utf-8"))
API = "https://generativelanguage.googleapis.com/v1beta"
# carácter fijo de cada personaje al decir cualquier frase (se suma a la emoción de la escena)
# 27/11/2026 (orden del dueño: «la voz del jambo no se entiende apenas»): Jambo sigue siendo el más relajado, pero articulando:
# la pachorra va en las pausas y la entonación, no en arrastrar las sílabas hasta hacerlas ininteligibles.
CARACTER = {"rosa": "bossy, theatrical", "felipe": "smug know-it-all, laid-back", "sindy": "cheeky, streetwise, fast",
            "neo": "calm, polite, composed", "conchaqueton": "whiny, wheedling",
            "jambo": "real unacted street talk, raw documentary feel, thin nasal cracked worn-out voice, lazy tired drawl trailing off at the end of phrases, half-voiced, weary pestering tone of someone asking a favour, southern Andalusian working-class accent, never theatrical, never sing-song, never cartoonish, still intelligible",
            "cliente": "impatient"}
RITMO = "fast, lively sitcom pace"
# Orden del dueño 23/11 22:27: «el Jambo tiene que arrastrar más las eses y hablar más lento, tipo yonqui, y un poco de
# velocidad en el resto de voces». Jambo nunca se acelera; el resto se lleva a unas 3 palabras por segundo.
# 27/11/2026 (noche, «más estiradas las vocales»): el corte aceleraba a Jambo hasta 1,78x para llegar a 2,2 palabras/s y le aplastaba las vocales;
# ahora su objetivo es 1,7 palabras/s y nunca se acelera más de 1,2x. Historial: 1,6 (23/11) -> 2,2 (27/11 tarde) -> 1,7 (27/11 noche).
# 27/11/2026: Jambo sube de 1,6 a 2,2 palabras por segundo para que se entienda (sigue siendo el más lento del reparto).
LENTOS_QUIEN = {"jambo"}
PAL_S = {None: 3.0, "jambo": 1.7, "neo": 2.8}       # palabras por segundo a las que se lleva cada réplica si sale más lenta
TEMPO_MAX = {None: 1.3, "jambo": 1.2}                 # tope de aceleración sin cambiar el tono (atempo)
PAUSA_MAX = {None: 0.35, "jambo": 0.55}               # ninguna pausa interna más larga que esto (segundos)


def ceceo(texto):
    """CECEO de Jambo (27/11/2026): s -> z en el texto que va al TTS (solo réplicas de Jambo). El texto del guion («v») no se toca:
    subtítulos y control de audio siguen usando el original. «eso es una señora cosa» -> «ezo ez una zeñora coza»."""
    partes = re.split(r"(<[^>]*>)", texto)   # las marcas del TTS (<long pause>...) no se tocan
    return "".join(p if p.startswith("<") else p.replace("s", "z").replace("S", "Z") for p in partes)


EMO_JAMBO = {"normal": "casual, offhand, half-voiced", "seco": "deadpan, low, final", "cansado": "tired, low, long sigh",
             "ironia": "dry street sarcasm, slow", "chulea": "cocky, streetwise, taking his time", "susurra": "low conspiratorial murmur"}


ALARGUE, ALARGUE_COMA = 2, 0   # letras de la última vocal de cada frase de Jambo y de la vocal anterior a una coma (0 = no)


def alargar(texto):
    """Jambo estira la última vocal de CADA frase (y, si ALARGUE_COMA, la de la palabra anterior a cada coma). Solo en el texto del TTS."""
    def una(f):
        if ALARGUE_COMA:
            f = re.sub(r"([aeiouáéíóú])([^aeiouáéíóú\s,]*),", lambda m: m.group(1) * ALARGUE_COMA + m.group(2) + ",", f, flags=re.I)
        m = re.search(r"([aeiouáéíóú])([^aeiouáéíóú\s]*)([.!?…]*)\s*$", f, re.I)
        return f if not m else f[:m.start()] + m.group(1) * ALARGUE + m.group(2) + m.group(3)
    return " ".join(una(f) for f in frases(texto))


def frases(texto):
    return [f.strip() for f in re.findall(r"[^.!?…]+(?:[.!?…]+|$)", texto) if f.strip()]


def estilo(quien, emo, frase):
    base = CFG["estilo_por_emo"].get(emo or "normal", CFG["estilo_por_emo"]["normal"])
    if frase.endswith("?") and emo not in ("pregunta", "sorpresa"):
        base = "questioning, " + base
    elif frase.count("!") and emo in ("normal", "seco", "cansado", "susurra") and quien != "neo":
        base = "sudden loud burst, " + base
    if quien in LENTOS_QUIEN:   # nunca «fast» para Jambo: se altera, pero sigue arrastrando
        base = base.replace(", fast", ", agitated but still drawling").replace("hurried", "agitated")
    if quien == "jambo":   # Jambo nunca suena plano: cada emoción con su cante (27/11/2026)
        base = EMO_JAMBO.get(emo or "normal", base)
    partes = [CARACTER.get(quien, ""), base]
    if quien not in LENTOS_QUIEN:
        partes.append(RITMO)
    return ", ".join(p for p in partes if p)


def fusionar(pedido):
    """Todos los episodios del pedido como uno solo: así cada personaje gasta UNA petición por pedido (no por episodio)."""
    escenas = []
    for ep in pedido["episodios"]:
        for i, e in enumerate(ep["escenas"]):
            escenas.append({**e, "_n": ep["slug"][:3], "_i": i})
    return {"slug": "lote", "escenas": escenas}


def lineas_de(ep, quien):
    return [(i, e) for i, e in enumerate(ep["escenas"]) if e.get("h") == quien and e.get("v")]


def generar(pedido, out):
    clave = os.environ["GEMINI_API_KEY"]; modelos = pedido.get("modelos") or CFG["modelos"]; todo_bien = True
    # "muestras": [{clave, genero, descripcion}] = solo diseñar voces candidatas y guardar la muestra que devuelve el
    # diseño (no gasta la cuota diaria de voz). Con "sin_generar": true no se pide ninguna réplica.
    if pedido.get("muestras"):
        hechas = {}
        for m in pedido["muestras"]:
            cuerpo_v = {"store": True, "voice": {"model": "gemini-3.8-flash-tts", "type": "prompted", "display_name": "Jambo-serie · " + m["clave"],
                                                 "gender": m["genero"], "language_code": "es-ES", "prompted": {"input": m["descripcion"]}}}
            req = urllib.request.Request(f"{API}/voices", data=json.dumps(cuerpo_v).encode(), method="POST", headers={"x-goog-api-key": clave, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=240) as r:
                    rv = json.loads(r.read())
                au = rv.get("sample_audio") or rv.get("sampleAudio") or {}
                if au.get("data"):
                    open(f"{out}/muestra_{m['clave']}.wav", "wb").write(base64.b64decode(au["data"]))
                hechas[m["clave"]] = rv.get("id")
            except urllib.error.HTTPError as e:
                hechas[m["clave"]] = "ERROR " + e.read().decode("utf-8", "replace")[:300]
            except Exception as e:
                hechas[m["clave"]] = f"ERROR {type(e).__name__}: {e}"[:300]
            print("muestra", m["clave"], hechas[m["clave"]], flush=True); time.sleep(3)
        json.dump(hechas, open(f"{out}/muestras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if pedido.get("sin_generar"):
        return 0
    for ep in [fusionar(pedido)]:
        n = "lote"; plan = {"slug": ep["slug"], "personajes": {}}
        for quien in dict.fromkeys(e["h"] for e in ep["escenas"] if e.get("h")):
            if pedido.get("solo") and quien not in pedido["solo"]:
                continue
            candidatas = list((pedido.get("voces") or {}).get(quien) or [])
            d = (pedido.get("disenar") or {}).get(quien)
            if d:   # voz nueva a partir de una descripción (no gasta la cuota de peticiones de voz)
                cuerpo_v = {"store": True, "voice": {"model": "gemini-3.8-flash-tts", "type": "prompted", "display_name": d.get("nombre") or f"Jambo-serie · {quien} v2",
                                                     "gender": d["genero"], "language_code": "es-ES", "prompted": {"input": d["descripcion"]}}}
                req = urllib.request.Request(f"{API}/voices", data=json.dumps(cuerpo_v).encode(), method="POST", headers={"x-goog-api-key": clave, "Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(req, timeout=240) as r:
                        rv = json.loads(r.read())
                    m = rv.get("sample_audio") or rv.get("sampleAudio") or {}
                    if m.get("data"):
                        open(f"{out}/{n}_diseno_{quien}.wav", "wb").write(base64.b64decode(m["data"]))
                    plan.setdefault("disenadas", {})[quien] = rv.get("id"); candidatas.insert(d.get("orden", 0), rv.get("id"))
                except urllib.error.HTTPError as e:
                    plan.setdefault("disenadas", {})[quien] = "ERROR " + e.read().decode("utf-8", "replace")[:300]
                except Exception as e:
                    plan.setdefault("disenadas", {})[quien] = f"ERROR {type(e).__name__}: {e}"[:300]
            candidatas = [c for c in candidatas if c] + [CFG["voces"].get(quien)]
            voz = candidatas[0]
            if not voz:
                plan["personajes"][quien] = {"error": "sin voz diseñada"}; todo_bien = False; continue
            partes = []
            for k, (i, e) in enumerate(lineas_de(ep, quien)):
                texto = e.get("voz_tts") or e["v"]
                if quien == "jambo":   # 27/11/2026: ceceo solo en el texto que va al TTS; «v» (subtítulos, control) queda intacto
                    texto = ceceo(texto)
                    texto = alargar(texto)
                for j, f in enumerate(frases(texto)):
                    partes.append({"text": ("<long pause> " if k and j == 0 else "") + f, "speech_metadata": {"style": estilo(quien, e.get("emo"), f)}})
            cuerpo = {"contents": [{"role": "user", "parts": partes}],
                      "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"voice": voz}}}}
            info = None
            for voz, modelo in [(v_, m_) for v_ in dict.fromkeys(candidatas) for m_ in modelos]:
                cuerpo["generationConfig"]["speechConfig"]["voiceConfig"]["voice"] = voz
                if info and info.get("http") == 429 and info.get("modelo") == modelo:
                    continue   # ese modelo ya no tiene cuota hoy: no la gastes con otra voz
                for intento in range(2):
                    req = urllib.request.Request(f"{API}/models/{modelo}:generateContent", data=json.dumps(cuerpo).encode(), method="POST",
                                                 headers={"x-goog-api-key": clave, "Content-Type": "application/json"})
                    try:
                        with urllib.request.urlopen(req, timeout=240) as r:
                            resp = json.loads(r.read())
                        ps = (((resp.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
                        datos = [p.get("inlineData") or p.get("inline_data") for p in ps]; datos = [d["data"] for d in datos if d and d.get("data")]
                        if not datos:
                            info = {"modelo": modelo, "error": "respuesta sin audio: " + json.dumps(resp)[:300]}; break
                        pcm = b""
                        for d in datos:
                            raw = base64.b64decode(d); pcm += raw[44:] if raw[:4] == b"RIFF" else raw
                        wav = (b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, 24000, 48000, 2, 16) + b"data" + struct.pack("<I", len(pcm)) + pcm)
                        open(f"{out}/{n}_{quien}.wav", "wb").write(wav)
                        info = {"modelo": modelo, "voz": voz, "archivo": f"{n}_{quien}.wav", "segundos": round(len(pcm) / 48000, 2), "frases": len(partes)}; break
                    except urllib.error.HTTPError as e:
                        msg = e.read().decode("utf-8", "replace")[:500]; info = {"modelo": modelo, "voz": voz, "http": e.code, "error": msg}
                        if e.code in (500, 503) and intento == 0:
                            time.sleep(15); continue
                        break
                    except Exception as e:
                        info = {"modelo": modelo, "error": f"{type(e).__name__}: {e}"[:300]}; break
                if info and info.get("archivo"):
                    break
            plan["personajes"][quien] = info; todo_bien = todo_bien and bool(info and info.get("archivo"))
            print(quien, json.dumps(info, ensure_ascii=False)[:400], flush=True); time.sleep(8)
        json.dump(plan, open(f"{out}/plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0 if todo_bien else 1


# ----------------------------------------------------------------------------------------------- cortar
def _norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", w)


def _norm_ceceo(w):
    """Como _norm pero sin distinguir s/z/c(e,i): Whisper oye «ezo» donde el guion dice «eso» (ceceo de Jambo, 27/11/2026)."""
    return re.sub(r"c(?=[ei])", "s", _norm(w)).replace("z", "s")


def _palabras(texto):
    texto = re.sub(r"<[^>]+>", " ", texto)
    return [w for w in texto.split() if _norm(w)]


def cortar(pedido, out, modelo_whisper="small"):
    import numpy as np
    from faster_whisper import WhisperModel
    ff = os.environ.get("FFMPEG", "ffmpeg"); wm = WhisperModel(modelo_whisper, device="cpu", compute_type="int8"); ok = True
    for ep in [fusionar(pedido)]:
        n = "lote"; manifiesto = {}; informe = {}
        for quien in dict.fromkeys(e["h"] for e in ep["escenas"] if e.get("h") and e.get("v")):
            wav = f"{out}/{n}_{quien}.wav"; ls = lineas_de(ep, quien)
            nz = _norm_ceceo if quien == "jambo" else _norm   # Jambo cecea: se alinea sin distinguir s/z/c(e,i)
            if not os.path.exists(wav):
                informe[quien] = "falta el audio"; ok = False; continue
            raw = subprocess.run([ff, "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
            x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; total = len(x) / 16000
            segs, _ = wm.transcribe(x, language="es", word_timestamps=True)
            rec = [(w.word, w.start, w.end) for s in segs for w in s.words if _norm(w.word)]
            esp = [(k, w) for k, (_, e) in enumerate(ls) for w in _palabras(e["v"])]
            sm = difflib.SequenceMatcher(None, [nz(w) for _, w in esp], [nz(w) for w, _, _ in rec], autojunk=False)
            t = [None] * len(esp)
            for a, b, size in sm.get_matching_blocks():
                for d in range(size):
                    t[a + d] = (rec[b + d][1], rec[b + d][2])
            casadas = sum(1 for v in t if v); informe[quien] = {"palabras": len(esp), "casadas": casadas, "oido": " ".join(w.strip() for w, _, _ in rec)}
            # límites de cada réplica: del primer al último tiempo conocido; los cortes van en mitad del hueco entre réplicas
            lim = []
            for k in range(len(ls)):
                ts = [v for (kk, _), v in zip(esp, t) if kk == k and v]
                lim.append((min(a for a, _ in ts), max(b for _, b in ts)) if ts else None)
            if any(l is None for l in lim):
                informe[quien]["error"] = "alguna réplica no se ha localizado en el audio"; ok = False; continue
            cortes = [0.0] + [(lim[k][1] + lim[k + 1][0]) / 2 for k in range(len(ls) - 1)] + [total]
            env = np.sqrt(np.convolve(x ** 2, np.ones(320) / 320, mode="same")); umbral = max(env.max() * 0.03, 1e-4)
            for k, (i, e) in enumerate(ls):
                a, b = int(cortes[k] * 16000), int(cortes[k + 1] * 16000); activos = np.nonzero(env[a:b] > umbral)[0]
                ini = max(cortes[k], (a + activos[0]) / 16000 - 0.06) if len(activos) else lim[k][0]
                fin = min(cortes[k + 1], (a + activos[-1]) / 16000 + 0.12) if len(activos) else lim[k][1]
                ini = min(ini, lim[k][0]); fin = max(fin, lim[k][1])
                pal = [(w, v) for (kk, w), v in zip(esp, t) if kk == k]
                seg = x[int(ini * 16000):int(fin * 16000)].copy(); quitar = []
                # "quitar": [[a, b], ...] = palabras (índices, ambos incluidos) que se eliminan del audio ya grabado
                for qa, qb in sorted(e.get("quitar") or [], reverse=True):
                    ta = max(v[1] for _, v in pal[:qa] if v) + 0.08 if qa and any(v for _, v in pal[:qa]) else ini
                    tb = min(v[0] for _, v in pal[qb + 1:] if v) - 0.06 if any(v for _, v in pal[qb + 1:]) else fin
                    quitar.append((ta, tb)); pal = pal[:qa] + pal[qb + 1:]
                for ta, tb in quitar:   # de atrás hacia delante: los índices anteriores no se mueven
                    seg = np.concatenate([seg[:max(0, int((ta - ini) * 16000))], seg[max(0, int((tb - ini) * 16000)):]])
                # pausas internas: ninguna pasa de PAUSA_MAX (retención)
                ev = np.sqrt(np.convolve(seg ** 2, np.ones(320) / 320, mode="same")); callado = ev < max(ev.max() * 0.025, 1e-4)
                trozos = []; q0 = 0; maxm = int(PAUSA_MAX.get(quien, PAUSA_MAX[None]) * 16000)
                while q0 < len(seg):
                    q1 = q0
                    while q1 < len(seg) and callado[q1] == callado[q0]:
                        q1 += 1
                    trozos.append(seg[q0:q1] if not callado[q0] or q1 - q0 <= maxm else np.concatenate([seg[q0:q0 + maxm // 2], seg[q1 - maxm // 2:q1]])); q0 = q1
                seg = np.concatenate(trozos); dur = len(seg) / 16000
                objetivo = PAL_S.get(quien, PAL_S[None]); pps = len(pal) / max(dur, 0.1)
                tempo = 1.0 if pps >= objetivo else min(TEMPO_MAX.get(quien, TEMPO_MAX[None]), objetivo / pps)
                # el corte se hace sobre el wav original (24 kHz) con los mismos instantes, para no perder calidad
                mp3 = f"{out}/{e['_n']}_{e['_i']}.mp3"
                alta = np.frombuffer(subprocess.run([ff, "-v", "error", "-ss", f"{ini:.3f}", "-t", f"{fin - ini:.3f}", "-i", wav, "-ac", "1", "-ar", "48000", "-f", "s16le", "-"],
                                                    capture_output=True).stdout, np.int16).astype(np.float32) / 32768
                for ta, tb in quitar:
                    alta = np.concatenate([alta[:max(0, int((ta - ini) * 48000))], alta[max(0, int((tb - ini) * 48000)):]])
                ea = np.sqrt(np.convolve(alta ** 2, np.ones(960) / 960, mode="same")); ca = ea < max(ea.max() * 0.025, 1e-4); tz = []; q0 = 0; mm = maxm * 3
                while q0 < len(alta):
                    q1 = q0
                    while q1 < len(alta) and ca[q1] == ca[q0]:
                        q1 += 1
                    tz.append(alta[q0:q1] if not ca[q0] or q1 - q0 <= mm else np.concatenate([alta[q0:q0 + mm // 2], alta[q1 - mm // 2:q1]])); q0 = q1
                alta = np.concatenate(tz)
                subprocess.run([ff, "-v", "error", "-y", "-f", "s16le", "-ar", "48000", "-ac", "1", "-i", "-", "-af",
                                f"afade=t=in:d=0.02,atempo={tempo:.3f},loudnorm=I=-17:TP=-2:LRA=11", "-ac", "1", "-ar", "44100", "-b:a", "128k", mp3],
                               input=(np.clip(alta, -1, 1) * 32767).astype(np.int16).tobytes(), check=True)
                # tiempos de palabra medidos sobre el mp3 FINAL (segunda pasada de Whisper, solo esa réplica)
                fin_raw = subprocess.run([ff, "-v", "error", "-i", mp3, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
                y = np.frombuffer(fin_raw, np.int16).astype(np.float32) / 32768; real = len(y) / 16000
                s2, _ = wm.transcribe(y, language="es", word_timestamps=True); r2 = [(w.word, w.start, w.end) for sg in s2 for w in sg.words if _norm(w.word)]
                m2 = difflib.SequenceMatcher(None, [nz(w) for w, _ in pal], [nz(w) for w, _, _ in r2], autojunk=False); tiempos = [None] * len(pal)
                for a_, b_, size in m2.get_matching_blocks():
                    for d in range(size):
                        tiempos[a_ + d] = (r2[b_ + d][1], r2[b_ + d][2])
                j = 0
                while j < len(tiempos):
                    if tiempos[j] is None:
                        h = j
                        while h < len(tiempos) and tiempos[h] is None:
                            h += 1
                        t0 = tiempos[j - 1][1] if j else 0.03; t1 = tiempos[h][0] if h < len(tiempos) else real - 0.05; paso = max(t1 - t0, 0.05) / (h - j)
                        for q in range(j, h):
                            tiempos[q] = (t0 + paso * (q - j), t0 + paso * (q - j + 1))
                        j = h
                    else:
                        j += 1
                words = [{"w": w.strip(".,;:¡!¿?…«»"), "s": round(max(0, s_), 3), "e": round(min(max(en, s_ + 0.05), real), 3)} for (w, _), (s_, en) in zip(pal, tiempos)]
                manifiesto.setdefault(e["_n"], {})[f"{e['_n']}_{e['_i']}"] = {"quien": quien, "archivo": os.path.basename(mp3), "duration": round(real, 3), "words": words, "tempo": round(tempo, 3),
                                          "pal_s": round(len(pal) / real, 2), "texto": " ".join(w for w, _ in pal), "oido": " ".join(w.strip() for w, _, _ in r2)}
        for nn, mm in manifiesto.items():
            json.dump(mm, open(f"{out}/{nn}_voces.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(informe, open(f"{out}/informe.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for q, v in informe.items():
            print(q, json.dumps(v, ensure_ascii=False)[:500])
    return 0 if ok else 1


def empaquetar(pedido, out):
    """Mete los mp3 y los <n>_voces.json en voces.tar y, si hay ZERNIO_API_KEY, lo sube a una URL pública temporal para
    que el sandbox del estudio lo baje con curl (el repo es privado). Escribe listo.json con la URL."""
    import tarfile, glob
    ns = sorted({ep["slug"][:3] for ep in pedido["episodios"]}); ruta = f"{out}/voces.tar"; listo = {"episodios": ns, "url": None}
    with tarfile.open(ruta, "w") as tar:
        for nn in ns:
            for f in sorted(glob.glob(f"{out}/{nn}_[0-9]*.mp3")) + glob.glob(f"{out}/{nn}_voces.json"):
                tar.add(f, arcname=os.path.basename(f))
    listo["archivos"] = len(tarfile.open(ruta).getnames()); clave = os.environ.get("ZERNIO_API_KEY")
    if clave and listo["archivos"]:
        try:
            req = urllib.request.Request("https://zernio.com/api/v1/media/presign", data=json.dumps({"filename": f"voces_{'_'.join(ns)}.mp3", "contentType": "audio/mpeg"}).encode(),
                                         method="POST", headers={"Authorization": "Bearer " + clave, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                pre = json.loads(r.read())
            put = urllib.request.Request(pre["uploadUrl"], data=open(ruta, "rb").read(), method="PUT", headers={"Content-Type": "audio/mpeg"})
            with urllib.request.urlopen(put, timeout=300):
                pass
            listo["url"] = pre["publicUrl"]
        except Exception as e:
            listo["error"] = f"{type(e).__name__}: {e}"[:300]
    json.dump(listo, open(f"{out}/listo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1); print(json.dumps(listo, ensure_ascii=False))
    return 0 if listo["archivos"] else 1


if __name__ == "__main__":
    modo, ruta, salida = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(salida, exist_ok=True)
    ped = json.load(open(ruta, encoding="utf-8"))
    sys.exit({"generar": generar, "cortar": cortar, "empaquetar": empaquetar}[modo](ped, salida))
