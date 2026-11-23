"""Voces de El Jambo con Gemini TTS (plan gratuito): una petición por personaje y episodio.

El plan gratuito da 10 peticiones por día y por modelo, así que no se puede pedir réplica a réplica. Se hace en dos pasos:
  generar <pedido.json> <salida>   (necesita GEMINI_API_KEY; solo biblioteca estándar)
      Por cada episodio y personaje manda TODAS sus réplicas en una sola petición, cada frase con su intención
      (emoción de la escena + carácter del personaje). Guarda <n>_<personaje>.wav y <n>_plan.json.
  cortar <pedido.json> <salida>    (necesita faster-whisper, numpy y ffmpeg)
      Localiza cada palabra con Whisper, corta el audio por réplica, ajusta ritmo y volumen y escribe <n>_<i>.mp3 y
      <n>_voces.json (duración y tiempos de cada palabra, lo que necesita gen_episodios.py para los subtítulos).
Voces y estilos: equipo/voz_gemini.json. Creado el 23/11/2026 (orden del dueño: voces naturales, distintas, expresivas y gratis).
"""
import base64, difflib, json, os, re, struct, subprocess, sys, time, unicodedata, urllib.error, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(RAIZ, "equipo", "voz_gemini.json"), encoding="utf-8"))
API = "https://generativelanguage.googleapis.com/v1beta"
# carácter fijo de cada personaje al decir cualquier frase (se suma a la emoción de la escena)
CARACTER = {"rosa": "bossy, theatrical", "felipe": "smug know-it-all, laid-back", "sindy": "cheeky, streetwise, fast",
            "neo": "calm, polite, composed", "conchaqueton": "whiny, wheedling",
            "jambo": "very slow drowsy drawl, hoarse, slurred, dragging and hissing every S sound, spaced-out",
            "cliente": "impatient"}
RITMO = "fast, lively sitcom pace"
# Orden del dueño 23/11 22:27: «el Jambo tiene que arrastrar más las eses y hablar más lento, tipo yonqui, y un poco de
# velocidad en el resto de voces». Jambo nunca se acelera; el resto se lleva a unas 3 palabras por segundo.
LENTOS_QUIEN = {"jambo"}
PAL_S_OBJETIVO, TEMPO_MAX = 3.0, 1.3


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
    partes = [CARACTER.get(quien, ""), base]
    if quien not in LENTOS_QUIEN:
        partes.append(RITMO)
    return ", ".join(p for p in partes if p)


def lineas_de(ep, quien):
    return [(i, e) for i, e in enumerate(ep["escenas"]) if e.get("h") == quien and e.get("v")]


def generar(pedido, out):
    clave = os.environ["GEMINI_API_KEY"]; modelos = pedido.get("modelos") or CFG["modelos"]; todo_bien = True
    for ep in pedido["episodios"]:
        n = ep["slug"][:3]; plan = {"slug": ep["slug"], "personajes": {}}
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
        json.dump(plan, open(f"{out}/{n}_plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0 if todo_bien else 1


# ----------------------------------------------------------------------------------------------- cortar
def _norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", w)


def _palabras(texto):
    texto = re.sub(r"<[^>]+>", " ", texto)
    return [w for w in texto.split() if _norm(w)]


def cortar(pedido, out, modelo_whisper="small"):
    import numpy as np
    from faster_whisper import WhisperModel
    ff = os.environ.get("FFMPEG", "ffmpeg"); wm = WhisperModel(modelo_whisper, device="cpu", compute_type="int8"); ok = True
    for ep in pedido["episodios"]:
        n = ep["slug"][:3]; manifiesto = {}; informe = {}
        for quien in dict.fromkeys(e["h"] for e in ep["escenas"] if e.get("h") and e.get("v")):
            wav = f"{out}/{n}_{quien}.wav"; ls = lineas_de(ep, quien)
            if not os.path.exists(wav):
                informe[quien] = "falta el audio"; ok = False; continue
            raw = subprocess.run([ff, "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
            x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; total = len(x) / 16000
            segs, _ = wm.transcribe(x, language="es", word_timestamps=True)
            rec = [(w.word, w.start, w.end) for s in segs for w in s.words if _norm(w.word)]
            esp = [(k, w) for k, (_, e) in enumerate(ls) for w in _palabras(e["v"])]
            sm = difflib.SequenceMatcher(None, [_norm(w) for _, w in esp], [_norm(w) for w, _, _ in rec], autojunk=False)
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
                ini = min(ini, lim[k][0]); fin = max(fin, lim[k][1]); dur = fin - ini
                pal = [(w, v) for (kk, w), v in zip(esp, t) if kk == k]
                pps = len(pal) / max(dur, 0.1)
                tempo = 1.0 if (quien in LENTOS_QUIEN or pps >= PAL_S_OBJETIVO) else min(TEMPO_MAX, PAL_S_OBJETIVO / pps)
                mp3 = f"{out}/{n}_{i}.mp3"
                subprocess.run([ff, "-v", "error", "-y", "-ss", f"{ini:.3f}", "-t", f"{dur:.3f}", "-i", wav, "-af",
                                f"afade=t=in:d=0.02,atempo={tempo:.3f},loudnorm=I=-17:TP=-2:LRA=11", "-ac", "1", "-ar", "44100", "-b:a", "128k", mp3], check=True)
                # tiempos de palabra: los casados tal cual; los no casados, repartidos entre sus vecinos
                tiempos = [((v[0] - ini) / tempo, (v[1] - ini) / tempo) if v else None for _, v in pal]; real = dur / tempo
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
                words = [{"w": w.strip(".,;:¡!¿?…«»"), "s": round(max(0, s), 3), "e": round(min(max(en, s + 0.05), real), 3)} for (w, _), (s, en) in zip(pal, tiempos)]
                manifiesto[f"{n}_{i}"] = {"quien": quien, "archivo": os.path.basename(mp3), "duration": round(real, 3), "words": words, "tempo": round(tempo, 3), "pal_s": round(len(pal) / real, 2)}
        json.dump(manifiesto, open(f"{out}/{n}_voces.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(informe, open(f"{out}/{n}_informe.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for q, v in informe.items():
            print(q, json.dumps(v, ensure_ascii=False)[:500])
    return 0 if ok else 1


if __name__ == "__main__":
    modo, ruta, salida = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(salida, exist_ok=True)
    ped = json.load(open(ruta, encoding="utf-8"))
    sys.exit(generar(ped, salida) if modo == "generar" else cortar(ped, salida))
