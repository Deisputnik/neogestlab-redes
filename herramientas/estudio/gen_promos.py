"""Genera los spec.json de Neogest Studio para PROMOS DE APP (no El Jambo): clips reales de la
Biblioteca + tomas reales de la app, voz edge-tts con marcas de palabra y cierre con el logo 2026.
Creado el 22/11/2026 para desatascar 108, 107, 801 y 802 (ver LEEME.md, apartado «Promos de app»).
Uso (sandbox de Neogest Studio): pip install edge-tts; python3 gen_promos.py promos.json /tmp/pr
  node scripts/render.mjs /tmp/pr/<n>.json /tmp/pr/<n>.mp4 --hoja
promos.json: [{"slug","musica","escenas":[{"q":narr|asis|cli,"v":texto de voz,"bg":{fondo del estudio},
"textos":[...],"tr":transición}]}]. La última escena debe ser {"outro": true, "v": "Enlace en el perfil."}.
"""
import json, asyncio, random, sys, os, edge_tts
EPS = json.load(open(sys.argv[1])); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
VOZ = {"narr": ("es-ES-ElviraNeural", 10, 0), "asis": ("es-ES-XimenaNeural", 4, 0), "cli": ("es-ES-AlvaroNeural", 4, -4)}
uid = lambda: "%08x" % random.getrandbits(32)

async def tts(text, who, path):
    v, r, p = VOZ[who]
    c = edge_tts.Communicate(text, v, rate=f"{r:+d}%", pitch=f"{p:+d}Hz", boundary="WordBoundary"); words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7; words.append({"w": ch["text"].strip(".,;:¡!¿?«»"), "s": round(s, 3), "e": round(s + ch["duration"] / 1e7, 3)})
    return words

async def main():
    for ep in EPS:
        n = ep["slug"][:3]; scenes = []; total = 0
        for i, e in enumerate(ep["escenas"]):
            path = f"{OUT}/{n}_{i}.mp3"; words = await tts(e["v"], e.get("q", "narr"), path)
            dur = words[-1]["e"] + 0.05
            voice = {"text": e["v"], "provider": "edge", "speaker": e.get("q", "narr"), "url": path, "duration": dur, "words": words, "offset": 0.08, "tail": 0.1}
            sc = {"id": uid(), "duration": round(dur + (0.75 if e.get("outro") else 0.3), 2), "transition": e.get("tr", "slide" if i else "none"), "voice": voice,
                  "texts": [dict(t, id=uid()) for t in e.get("textos", [])]}
            if e.get("outro"): sc["kind"] = "outro"; sc["background"] = {"type": "gradient"}
            else: sc["background"] = e["bg"]
            if e.get("overlays"): sc["overlays"] = [dict(o, id=uid()) for o in e["overlays"]]
            if e.get("sfx"): sc["sfx"] = e["sfx"]
            total += sc["duration"]; scenes.append(sc)
        spec = {"version": 1, "format": "9:16", "fps": 30, "music": {"track": ep.get("musica", "corporativo:1"), "volume": 0.3, "duck": True, "duckLevel": 0.45},
                "subtitles": {"enabled": True, "words": 3, "style": "amarillo", "emojis": False, "size": 0.07},
                "brand": {"watermark": True, "watermarkPos": "right", "progress": True}, "sfx": {"enabled": True, "volume": 0.5}, "scenes": scenes}
        json.dump(spec, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False); print(n, len(scenes), "escenas", round(total, 1), "s")

asyncio.run(main())
