"""Genera los spec.json de Neogest Studio para episodios de El Jambo que sabe (reparto Rosa/Felipe/Sindy/
Concha Quetón/Neo). v5.1 (20/11/2026 noche, orden del dueño tras ver el piloto v1):
  - Bucle "Cosas de Casa": apertura y cierre usan el MISMO objeto de escena (misma tarjeta, mismo plano,
    sin texto distinto por episodio) para que el bucle sea imperceptible. Se usa en TODOS los episodios,
    no varía por hora/noche ni depende de "flow" (eso se reserva para b-roll real dentro del episodio si
    algún día hace falta). Mientras no haya un vídeo real de fachada de barrio, usa el set vectorial "casa".
  - Etiqueta de nombre y apellido: la dibuja engine.js en espacio de pantalla, fuera del zoom de cámara
    (antes se recortaba en los primeros planos; corregido 20/11 noche).
  - Más expresividad de voz: modulación de velocidad/tono por emoción de la escena (EXPR_MOD), sobre la
    base de cada personaje (VOZ).
  - Risas de sitcom: marca "risas: true" en una escena de gag para añadir el sfx "risas" al final de la
    réplica (biblioteca ya incluida en Neogest Studio, src/studio/library.js).
v5.2 (21/11/2026 madrugada, orden del dueño):
  - Créditos finales: tras el bucle de cierre, una escena "REPARTO" con el nombre y apellido de cada
    personaje que ha salido en el episodio (por si la etiqueta al entrar pasa desapercibida).
  - Ropa de ir por casa para Rosa/Felipe/Sindy (sin corbata ni traje de oficina), acorde al set "salón"
    — ver src/studio/characters.js en el app de Neogest Studio.
  - Lenguaje más paleto y vulgar en los diálogos (biblia y guionista_gemini.py actualizados a la vez).
Uso (en el sandbox de Neogest Studio, Base44 6af862101565c330cf06389f):
  pip install edge-tts; python3 gen_episodios.py eps.json /tmp/jb
  node scripts/render.mjs /tmp/jb/<n>.json /tmp/jb/<n>.mp4 --hoja
eps.json: [{"slug","set","hora","moraleja","escenas":[{"e":gancho|gag|remate|cierre,"h":personaje,"v":voz,
"t":texto,"p":[personajes],"a":{personaje:accion},"emo":emoción de la voz (ver EMO_VOZ),"sello","risas"}]}]
Humor negro real (biblia v5, guionista_gemini.py): tono frío, nunca sobre pobreza/enfermedad/muerte reales;
los personajes se llaman por su nombre entre ellos (registro de barrio con réplica inteligente).
"""
import json, asyncio, random, sys, re, os, shutil, subprocess
try:
    import edge_tts
except ImportError:   # con voces ya hechas (VOCES_PREFAB) no hace falta edge-tts
    edge_tts = None
# Voces ya generadas fuera (Gemini TTS, herramientas/voces_gemini.py): VOCES_PREFAB=<n>_voces.json con, por escena
# "<n>_<i>": {"archivo", "duration", "words"}; los mp3 se dejan en la carpeta de salida con ese nombre de archivo.
PREFAB = json.load(open(os.environ["VOCES_PREFAB"], encoding="utf-8")) if os.environ.get("VOCES_PREFAB") else {}
EPS = json.load(open(sys.argv[1])); OUT = sys.argv[2]
# Vídeo real para "Cosas de Casa" (pedido en equipo/cola_gemini.md el 20/11: Gemini/Flow o,
# a mano, ChatGPT/Sora). En cuanto exista la URL pública, ponla aquí UNA vez y todos los
# episodios (presentes y futuros) pasan a usarla automáticamente; hasta entonces None = set
# vectorial "casa". No repetir el pedido por episodio.
COSAS_DE_CASA_VIDEO = "https://media.base44.com/videos/public/6af862101565c330cf06389f/4ae3afde4_cosas-de-casa-intro.mp4"
# voz base por personaje: (voz, rate% base, pitch Hz base)
VOZ = {"rosa": ("es-ES-ElviraNeural", 0, -4), "felipe": ("es-ES-AlvaroNeural", -4, -2), "sindy": ("es-ES-XimenaNeural", 8, 4),
       "neo": ("es-ES-AlvaroNeural", 0, 0), "cliente": ("es-ES-AlvaroNeural", -4, -10),
       "conchaqueton": ("es-ES-ElviraNeural", -6, 2), "jambo": ("es-ES-AlvaroNeural", -18, -12), None: ("es-ES-ElviraNeural", 0, 0)}
# modulacion por emocion de la escena (orden del dueño 20/11 noche: mas expresividad)
EXPR_MOD = {"habla": (0, 0), "desespera": (18, 10), "delega": (-12, -8), "presume": (10, 6), "fria": (-8, -10)}
EXPR = {"habla": "neutral", "desespera": "enfadado", "delega": "cansado", "presume": "chulo", "fria": "neutral"}
EMO = ["😤", "🤯", "😱", "💸", "🙄", "😳"]
uid = lambda: "%08x" % random.getrandbits(32)
# nombre y apellido completos, para los créditos finales (orden del dueño 21/11 madrugada:
# además de la etiqueta en pantalla al entrar cada personaje, que a veces pasa desapercibida,
# el reparto completo se repite siempre al final como créditos de cine).
NOMBRES = {"rosa": "Rosa Melano", "felipe": "Felipe Lotas", "sindy": "Sindy Entes", "neo": "Neo",
           "conchaqueton": "Concha Quetón", "bit": "Bit", "cliente": "Cliente", "jambo": "Jambo Reseco"}

# ---------------------------------------------------------------------------------------------------------
# EXPRESIVIDAD DE VOZ v6 (23/11/2026, orden del dueño: «haz que mejoren las expresiones de voz»).
# edge-tts solo deja mover velocidad, tono y volumen, y antes se fijaban UNA vez por réplica: toda la frase
# sonaba igual de plana. Ahora cada réplica se parte en frases y cada frase lleva su propia entonación:
#   1) la emoción que marca el guion en la escena (campo "emo": grita, enfado, sorpresa, ironia, chulea,
#      cansado, susurra, miedo, llora, rie, seco, pregunta, normal); si no viene, se deduce de la acción "a";
#   2) lo que pide la propia frase: una exclamación con taco se grita, una pregunta sube, unos puntos
#      suspensivos se arrastran con sorna, un golpe de dos o tres palabras se dice seco;
#   3) una pausa entre frases según el signo (más larga tras «…»), para que respire y no suene leído.
# Las frases se sintetizan por separado y se unen con ffmpeg (hace falta ffmpeg en el sandbox, ver LEEME);
# sin ffmpeg se vuelve a una sola pasada por réplica con la emoción de la escena.
# (velocidad %, tono en SEMITONOS, volumen %). El tono se pasa a Hz según la voz (F0_BASE) para que un grito suba lo
# mismo en una voz grave que en una aguda. MEDIDO el 23/11 con la misma réplica de Rosa: con los valores tímidos de
# la primera versión la entonación no cambiaba (2,5 → 2,6 semitonos de desviación); con estos sube a 3,3 semitonos y
# el rango pasa de 8,5 a 11 semitonos. ElevenLabs (promos de app) da 4,6: edge-tts no llega más lejos.
EMO_VOZ = {"normal": (0, 0, 0), "grita": (20, 2.5, 35), "enfado": (12, 1.5, 22), "sorpresa": (8, 3.0, 12),
           "ironia": (-14, -1.5, 0), "chulea": (7, 1.0, 10), "cansado": (-18, -2.0, -15), "susurra": (-10, -1.0, -45),
           "miedo": (16, 2.5, -5), "llora": (-12, 2.0, -10), "rie": (12, 2.0, 12), "seco": (-9, -2.0, 6), "pregunta": (3, 1.5, 0)}
F0_BASE = {"es-ES-ElviraNeural": 200, "es-ES-XimenaNeural": 215, "es-ES-AlvaroNeural": 120}
ACCION_A_EMO = {"habla": "normal", "desespera": "enfado", "delega": "cansado", "presume": "chulea", "fria": "seco"}
TACOS = re.compile(r"joder|hostia|co[ñn]o|cojon|mierda|put[ao]|cag[oaü]|leche|carajo|huevos|gilipoll|cabr[oó]n", re.I)
PAUSA = {"…": 0.30, "?": 0.18, "!": 0.10, ".": 0.14}
SR = 24000
FFMPEG = shutil.which("ffmpeg")
if not FFMPEG:
    try:
        import imageio_ffmpeg; FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        FFMPEG = None

def _frases(text):
    t = text.replace("*", "").replace("...", "…").strip()
    partes = [x.strip() for x in re.findall(r"[^.!?…]+[.!?…]+(?:[»\"')]+)?|[^.!?…]+$", t) if x.strip()]
    return partes or [t]

def _emo_de_frase(frase, emo_escena):
    """Emoción de UNA frase: manda lo que pide su puntuación; si no pide nada, la emoción de la escena."""
    limpia = frase.strip()
    if "¡" in limpia or limpia.endswith("!"):
        return "grita" if TACOS.search(limpia) else ("enfado" if emo_escena in ("normal", "seco", "cansado") else emo_escena)
    if limpia.endswith("…"):
        return "ironia"
    if "¿" in limpia or limpia.endswith("?"):
        return emo_escena if emo_escena in ("enfado", "grita", "sorpresa", "miedo", "chulea", "ironia") else "pregunta"
    if len(limpia.split()) <= 3 and emo_escena == "normal":
        return "seco"
    return emo_escena

def _prosodia(who, emo, i=0):
    voz, br, bp = VOZ[who]; mr, st, mv = EMO_VOZ.get(emo, EMO_VOZ["normal"])
    vaiven = (3, -2, 2, -3)[i % 4]   # ninguna frase suena exactamente igual que la anterior
    hz = F0_BASE.get(voz, 160) * (2 ** (st / 12) - 1)
    r = max(-40, min(50, br + mr + vaiven)); p = int(round(max(-45, min(70, bp + hz)))); v = max(-50, min(50, mv))
    return f"{r:+d}%", f"{p:+d}Hz", f"{v:+d}%"

async def _edge(text, voz, rate, pitch, volume, path):
    c = edge_tts.Communicate(text, voz, rate=rate, pitch=pitch, volume=volume, boundary="WordBoundary"); words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7; words.append({"w": ch["text"].strip(".,;:¡!¿?…«»"), "s": round(s, 3), "e": round(s + ch["duration"] / 1e7, 3)})
    return words

async def tts(text, who, path, accion="habla", emo=None):
    voz = VOZ[who][0]
    emo_escena = emo if emo in EMO_VOZ else ACCION_A_EMO.get(accion, "normal")
    frases = _frases(text)
    if not FFMPEG or len(frases) == 1:
        r, p, v = _prosodia(who, _emo_de_frase(frases[0], emo_escena) if len(frases) == 1 else emo_escena)
        return await _edge(text.replace("*", ""), voz, r, p, v, path)
    pcm = bytearray(); words = []; t0 = 0.0
    for i, fr in enumerate(frases):
        r, p, v = _prosodia(who, _emo_de_frase(fr, emo_escena), i)
        tmp = f"{path}.{i}.mp3"; w = await _edge(fr, voz, r, p, v, tmp)
        raw = subprocess.run([FFMPEG, "-v", "error", "-i", tmp, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
        os.remove(tmp)
        fin = (w[-1]["e"] + 0.09) if w else len(raw) / 2 / SR
        raw = raw[: int(min(fin, len(raw) / 2 / SR) * SR) * 2]
        for x in w: words.append({"w": x["w"], "s": round(x["s"] + t0, 3), "e": round(x["e"] + t0, 3)})
        pcm += raw; t0 += len(raw) / 2 / SR
        if i < len(frases) - 1:
            pausa = PAUSA.get(fr.rstrip("»\"')")[-1:], 0.12)
            pcm += b"\x00" * (int(pausa * SR) * 2); t0 += pausa
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "s16le", "-ac", "1", "-ar", str(SR), "-i", "-", "-c:a", "libmp3lame", "-b:a", "96k", path], input=bytes(pcm), check=True)
    return words

# Gancho de enganche sobre el plano de la casa (orden del dueño 21/11: SÍ overlay de texto en la
# apertura, pensado para la retención en los primeros 2s; sustituye la decisión anterior del 20/11
# noche de "nunca texto en pantalla". Solo en la apertura, nunca en el cierre, para no repetirlo).
HOOK_CASA = "Esta casa del barrio tiene truco 👀"

def bookend(hook=False, texto=None):
    # Misma tarjeta EXACTA en apertura y cierre de todos los episodios (bucle imperceptible); solo
    # cambia el overlay de texto, que va únicamente en la apertura (hook=True).
    bg = {"type": "video", "url": COSAS_DE_CASA_VIDEO, "start": 0.0} if COSAS_DE_CASA_VIDEO else {"type": "set", "set": "casa", "hour": 19, "night": False}
    texts = [{"id": uid(), "text": texto or HOOK_CASA, "style": "hook", "anim": "pop", "start": 0.1, "y": 0.18}] if hook else []
    return {"id": uid(), "duration": 1.6, "transition": "none", "voice": None, "background": bg, "texts": texts}

def creditos(elenco):
    # Reparto completo como créditos de cine al final de cada episodio (orden del dueño 21/11
    # madrugada), sobre el mismo set de salón pero de noche para diferenciarlo de la escena.
    textos = [{"id": uid(), "text": "REPARTO", "style": "badge", "anim": "pop", "start": 0.0, "y": 0.1, "sfx": "impacto"}]
    for i, who in enumerate(elenco):
        textos.append({"id": uid(), "text": NOMBRES.get(who, who), "style": "hook", "anim": "pop", "start": 0.3 + i * 0.35, "y": 0.24 + i * 0.12})
    fin = 0.3 + len(elenco) * 0.35
    textos.append({"id": uid(), "text": "By Neogest Lab", "style": "badge", "anim": "pop", "start": fin + 0.2, "y": 0.24 + len(elenco) * 0.12 + 0.14})
    dur = fin + 1.8
    bg = {"type": "set", "set": "salon", "hour": 22, "night": True}
    return {"id": uid(), "duration": dur, "transition": "fade", "voice": None, "background": bg, "characters": [], "texts": textos}

async def main():
    for ep in EPS:
        n = ep["slug"][:3]; bg = {"type": "set", "set": ep["set"], "hour": ep["hora"], "night": ep["hora"] >= 21}; scenes = []
        vistos = {}  # dict en vez de set para conservar el orden de aparición (créditos finales)
        for i, e in enumerate(ep["escenas"]):
            accion = e["a"].get(e["h"], "habla") if e.get("a") else "habla"
            path = f"{OUT}/{n}_{i}.mp3"; hecho = PREFAB.get(f"{n}_{i}")
            if hecho:
                words = hecho["words"]; dur = hecho["duration"]
            else:
                words = await tts(e["v"], e["h"], path, accion, e.get("emo")); dur = (words[-1]["e"] if words else 1.0) + 0.05
            voice = {"text": e["v"], "provider": "edge", "speaker": e["h"] or "narrador", "url": path, "duration": dur, "words": words, "offset": 0.05, "tail": 0.12}
            if e["e"] == "cierre":
                cierre_cast = [{"who": "felipe", "x": 0.3, "expr": "cansado"}, {"who": "neo", "x": 0.72, "expr": "feliz"}]
                for cc in cierre_cast:
                    if cc["who"] not in vistos: cc["intro"] = True; vistos[cc["who"]] = True
                scenes.append({"id": uid(), "duration": dur + 0.6, "transition": "zoom", "background": bg, "characters": cierre_cast, "shot": "general", "voice": voice,
                               "texts": [{"id": uid(), "text": ep["moraleja"], "style": "badge", "anim": "pop", "y": 0.12, "sfx": "impacto"}, {"id": uid(), "text": e["t"], "style": "hook", "anim": "pop", "start": 0.5, "y": 0.26}]}); continue
            p = e["p"] or [e["h"]]; xs = {}
            if "felipe" in p: xs["felipe"] = 0.3
            for w in p:
                if w not in xs: xs[w] = 0.72 if 0.72 not in xs.values() else 0.3
            cast = []
            for w in p[:2]:
                ex = EXPR.get((e.get("a") or {}).get(w, "habla"), "neutral")
                if e["e"] == "remate": ex = "chulo" if w == e["h"] else "sorprendido"
                entry = {"who": w, "x": xs[w], "expr": ex}
                if w not in vistos: entry["intro"] = True; vistos[w] = True
                cast.append(entry)
            # BUG corregido 20/11 noche (4.ª pasada): la duración estaba fijada a 0.4s sin importar el audio real,
            # así que la escena cambiaba antes de que acabara el audio Y antes de que la etiqueta de nombre
            # (fade de 1.1s en engine.js) llegara a mostrarse. Ahora dura lo que dura el audio + margen.
            sc = {"id": uid(), "duration": dur + 0.35, "transition": "slide" if i else "none", "background": bg, "characters": cast, "voice": voice, "shot": ["auto", "medio", "primerplano", "auto", "general"][i % 5], "texts": []}
            if i >= 1 and e["e"] == "gag" and e["h"] != "neo":
                sc["overlays"] = [{"id": uid(), "type": "emoji", "text": EMO[i % len(EMO)], "x": 0.82 if xs.get(e["h"], 0.3) < 0.5 else 0.18, "y": 0.32, "start": 0.25, "size": 0.12}]
            if e["e"] == "remate": sc["shot"] = "primerplano"; sc["transition"] = "flash"
            if e.get("sello"): sc["texts"].append({"id": uid(), "text": e["sello"], "style": "badge", "anim": "pop", "start": 0.4, "y": 0.3, "sfx": "impacto"})
            if e.get("risas"): sc["texts"].append({"id": uid(), "text": "😂", "style": "badge", "anim": "pop", "start": max(0.1, dur * 0.55), "y": 0.08, "sfx": "risas"})
            scenes.append(sc)
        # v5.3 (22/11): los créditos van ANTES del plano de cierre; el ÚLTIMO plano del vídeo es la tarjeta
        # «Cosas de Casa» idéntica a la de apertura (Calidad rechazó 351/353 por acabar en créditos).
        scenes.insert(0, bookend(hook=True, texto=ep.get("gancho_casa")))   # gancho propio del episodio (retención v12); si no viene, el fijo
        scenes.append(creditos(list(vistos.keys())))
        scenes.append(bookend())
        spec = {"version": 1, "format": "9:16", "fps": 30, "music": {"track": "comedia:1", "volume": 0.16, "duck": True, "duckLevel": 0.3}, "subtitles": {"enabled": True, "words": 3, "style": "amarillo", "emojis": True, "size": 0.07},
                "brand": {"watermark": True, "watermarkPos": "right", "progress": True}, "sfx": {"enabled": True, "volume": 0.6}, "scenes": scenes}
        json.dump(spec, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False); print(n, len(scenes), "escenas")

asyncio.run(main())
