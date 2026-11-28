"""Genera los spec.json de Neogest Studio para PROMOS DE APP (no El Jambo): clips reales de la
Biblioteca + tomas reales de la app, cierre con el logo 2026 y VOZ DE ELEVENLABS.
23/11/2026 (orden del dueño: «en las aplicaciones usamos Eleven siempre»): las promos de app llevan SIEMPRE
ElevenLabs (narrador Martin Osborne, desde el 28/11/2026). Antes salían con edge-tts porque los agentes no tenían la clave; ahora la pone
el propio estudio (render.mjs --final usa el secreto de la app por /api/render-voz, la clave no pasa por ti).
Uso (sandbox de Neogest Studio):
  python3 gen_promos.py promos.json /tmp/pr
  node scripts/render.mjs /tmp/pr/<n>.json /tmp/pr/<n>.mp4 --hoja --final      <- --final es OBLIGATORIO
render.mjs avisa de los caracteres gastados y se para (código 3) si se pasa del presupuesto mensual (30.000,
directiva §6). SOLO en ese caso: python3 gen_promos.py promos.json /tmp/pr --voz edge (pip install edge-tts) y
anota en post.json "motor_voz": "edge" y "_voz_nota": "presupuesto ElevenLabs agotado". En el caso normal,
post.json lleva "motor_voz": "elevenlabs".
promos.json: [{"slug","musica","escenas":[{"q":narr|asis|cli,"v":texto de voz,"bg":{fondo del estudio},
"textos":[...],"tr":transición,"emo":normal|energia|calma|sorpresa|cercano}]}]. La última escena debe ser
{"outro": true, "v": "Enlace en el perfil."}.
Escribe para la voz: frases cortas, una idea por frase, alguna pregunta y alguna exclamación (ElevenLabs las
interpreta); las cifras en letra; «Ajota» para AJ y «Éxcel» para Excel; la voz no dice «Neogest Lab».
"""
import json, asyncio, random, sys, os
EPS = json.load(open(sys.argv[1])); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
EDGE = "--voz" in sys.argv and sys.argv[sys.argv.index("--voz") + 1] == "edge"
# ElevenLabs («Mis voces», acento peninsular): narrador Martin Osborne (28/11/2026, antes Johnny); asistente Lydia; quien llama Raquel.
ELEVEN = {"narr": "D7dkYvH17OKLgp4SLulf", "asis": "SDVJaMLoJa7wc3s2sn7d", "cli": "1eHrpOW5l98cxiSRjbzJ"}
# expresión por escena: (stability, style, speed). Menos estabilidad y más estilo = más interpretación.
EMO = {"normal": (0.40, 0.40, 1.03), "energia": (0.30, 0.60, 1.07), "calma": (0.55, 0.25, 0.97),
       "sorpresa": (0.28, 0.65, 1.04), "cercano": (0.45, 0.45, 1.0)}
VOZ_EDGE = {"narr": ("es-ES-ElviraNeural", 10, 0), "asis": ("es-ES-XimenaNeural", 4, 0), "cli": ("es-ES-AlvaroNeural", 4, -4)}
uid = lambda: "%08x" % random.getrandbits(32)

async def tts_edge(text, who, path):
    import edge_tts
    v, r, p = VOZ_EDGE[who]
    c = edge_tts.Communicate(text, v, rate=f"{r:+d}%", pitch=f"{p:+d}Hz", boundary="WordBoundary"); words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7; words.append({"w": ch["text"].strip(".,;:¡!¿?«»"), "s": round(s, 3), "e": round(s + ch["duration"] / 1e7, 3)})
    return words

async def main():
    for ep in EPS:
        n = ep["slug"][:3]; scenes = []; total = 0; chars = 0
        for i, e in enumerate(ep["escenas"]):
            q = e.get("q", "narr"); pad = 0.75 if e.get("outro") else 0.36
            if EDGE:
                path = f"{OUT}/{n}_{i}.mp3"; words = await tts_edge(e["v"], q, path); dur = words[-1]["e"] + 0.05
                voice = {"text": e["v"], "provider": "edge", "speaker": q, "url": path, "duration": dur, "words": words, "offset": 0.08, "tail": 0.1}
                sc = {"id": uid(), "duration": round(dur + pad, 2)}
            else:
                st, sy, sp = EMO.get(e.get("emo", "normal"), EMO["normal"])
                voice = {"text": e["v"], "provider": "elevenlabs", "voiceId": ELEVEN[q], "model": "eleven_multilingual_v2",
                         "stability": st, "style": sy, "speed": sp, "speaker": q, "offset": 0.08, "tail": 0.1}
                chars += len(e["v"].replace("*", ""))
                # la duración real la pone render.mjs cuando tiene el audio (durationAuto); esto es solo una estimación
                sc = {"id": uid(), "duration": round(len(e["v"]) / 15 + pad, 2), "durationAuto": True, "pad": pad}
            if e.get("outro"): voice["subtitles"] = False
            sc.update({"transition": e.get("tr", "slide" if i else "none"), "voice": voice, "texts": [dict(t, id=uid()) for t in e.get("textos", [])]})
            if e.get("outro"): sc["kind"] = "outro"; sc["background"] = {"type": "gradient"}
            else: sc["background"] = e["bg"]
            if e.get("overlays"): sc["overlays"] = [dict(o, id=uid()) for o in e["overlays"]]
            if e.get("sfx"): sc["sfx"] = e["sfx"]
            total += sc["duration"]; scenes.append(sc)
        spec = {"version": 1, "format": "9:16", "fps": 30, "final": not EDGE, "music": {"track": ep.get("musica", "corporativo:1"), "volume": 0.3, "duck": True, "duckLevel": 0.45},
                "subtitles": {"enabled": True, "words": 2, "style": "amarillo", "emojis": False, "size": 0.066},
                "brand": {"watermark": True, "watermarkPos": "right", "progress": True}, "sfx": {"enabled": True, "volume": 0.5}, "scenes": scenes}
        json.dump(spec, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False)
        print(n, len(scenes), "escenas", "~%.1f s" % total, "· voz edge-tts (respaldo)" if EDGE else f"· ElevenLabs: {chars} caracteres (render.mjs --final)")

asyncio.run(main())
