"""Audición de voces Gemini TTS para El Jambo que sabe (23/11/2026, orden del dueño: «que sean todas las voces
naturales, diferentes y expresivas, busca soluciones gratis»; el Jambo, con rasgos de toxicómano en la voz).

Qué hace, con la clave gratuita GEMINI_API_KEY que ya usa el Guionista (solo biblioteca estándar de Python):
  1) apunta qué modelos de voz ve la clave y cuántas voces de España hay en la biblioteca ampliada;
  2) DISEÑA una voz propia por personaje a partir de una descripción escrita (voz sintética nueva: no es la voz
     de nadie ni un clon; la voz del dueño sigue prohibida) y guarda la muestra que devuelve el diseño;
  3) dice una frase de cada personaje con su voz y su intención (grito, sorna, cansancio…);
  4) lo deja todo en la carpeta de salida con resultado.json (identificadores, errores y cuotas tal cual llegan).
Si una voz ya está diseñada (mismo nombre) se reutiliza: repetir la pasada no crea duplicados.
Uso: GEMINI_API_KEY=… python3 herramientas/audicion_gemini.py /tmp/aud
"""
import base64, json, os, struct, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
KEY = os.environ.get("GEMINI_API_KEY", "")
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/aud"
MODELOS = ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"]
PREFIJO = "Jambo-serie · "
ES = "Castilian Spanish from Spain with a clear peninsular (Madrid) accent, never Latin American."

# personaje: (género, descripción de la voz para el diseño, estilo de la frase de prueba, frase de prueba)
PERSONAJES = {
    "rosa": ("female",
             f"A woman in her early 50s, owner of a small business, speaking {ES} Medium-low, slightly husky, commanding "
             "voice: affected, flirtatious and sugary on the surface, sharp and cutting underneath. Theatrical, confident delivery.",
             "sugary and bossy at first, then snaps into an angry shout",
             "Felipe, cariño, hoy te quedas hasta las diez. <short pause> ¡Y sin rechistar, coño, que para eso te pago! Bueno… te pagaré."),
    "felipe": ("male",
               f"A man in his late 30s from a working-class neighbourhood, speaking {ES} Warm, mid-pitched, slightly nasal voice; "
               "slow, laid-back and a bit dopey, the smug know-it-all brother-in-law at the bar. Relaxed street speech.",
               "slow, smug, completely sure of himself",
               "Eso lo sé yo de buena tinta, Sindy. <short pause> Hacienda, a los del barrio, ni nos mira. Me lo dijo un primo que casi fue gestor."),
    "sindy": ("female",
              f"A woman in her late 20s from a working-class barrio, speaking {ES} Bright, high, sharp and cheeky voice with a "
              "slight whistling lisp from missing teeth; fast, fearless, streetwise, always half laughing.",
              "fast, cheeky and mocking, laughing while she talks",
              "¡Anda ya, Rosa! <laugh> Tres dientes me quedan y los tres te dicen lo mismo: ¡que me pagues marzo, hostia!"),
    "neo": ("male",
            f"A calm, polished man around 35, speaking {ES} Standard educated pronunciation. Clear, smooth, warm baritone, "
            "measured pace, the friendly composure of a helpful assistant who never raises his voice.",
            "calm, polite, warm, perfectly composed",
            "Tranquilos. Ya está hecho: la factura está enviada, registrada y cobrada. No ha hecho falta gritar."),
    "conchaqueton": ("female",
                     f"A woman in her mid 60s from a humble neighbourhood, speaking {ES} Thin, quavering, whiny voice, always "
                     "cold and tired; drags her words, complains and wheedles, with a sly sharpness underneath.",
                     "whiny, tired, shivering with cold, wheedling",
                     "Ay, hija, qué frío hace aquí… <sigh> Lo de la factura, eso lo arreglamos la semana que viene, ¿eh?"),
    "jambo": ("male",
              f"A scrawny man in his late 40s who sounds much older, from a rough working-class barrio, speaking {ES} Street speech. "
              "Very hoarse, raspy, broken voice worn out by years of hard living on the street; slurred, dragging, sluggish "
              "delivery with a nasal whine, runs out of breath, then sudden bursts of agitated energy. A wheedling, shameless scrounger.",
              "hoarse and slurred, dragging the words, loses his thread, then a sudden impatient burst",
              "<cough> Rosa, prima… déjame veinte euros, que mañana te los devuelvo… <short pause> ¿Qué te estaba diciendo? ¡Ah, sí! ¡Que me los des ya, joder, que tengo prisa!"),
}
SOLO = [p for p in os.environ.get("AUDICION_SOLO", "").split(",") if p] or list(PERSONAJES)
REDISENAR = [p for p in os.environ.get("AUDICION_REDISENAR", "").split(",") if p]


def llamar(metodo, ruta, cuerpo=None, params=None, espera=180):
    url = API + ruta + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo, headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=espera) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, {"error": {"message": txt[:600]}}
    except Exception as e:  # red, tiempo agotado…
        return 0, {"error": {"message": f"{type(e).__name__}: {e}"[:300]}}


def error_de(resp):
    e = resp.get("error", {}) if isinstance(resp, dict) else {}
    return {"estado": e.get("status"), "mensaje": (e.get("message") or "")[:700]}


def guardar_audio(b64, ruta, mime=""):
    raw = base64.b64decode(b64)
    if raw[:4] != b"RIFF":  # PCM sin cabecera: 24 kHz, mono, 16 bits
        raw = (b"RIFF" + struct.pack("<I", 36 + len(raw)) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, 24000, 48000, 2, 16)
               + b"data" + struct.pack("<I", len(raw)) + raw)
    open(ruta, "wb").write(raw)
    return round((len(raw) - 44) / 48000, 2)


def g(d, *claves):
    for c in claves:
        if isinstance(d, dict) and c in d:
            return d[c]
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"fecha": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "modelos_tts": [], "biblioteca": {}, "voces": {}, "frases": {}, "sonda_cuota": None}
    if not KEY:
        res["error"] = "falta GEMINI_API_KEY"; json.dump(res, open(f"{OUT}/resultado.json", "w"), ensure_ascii=False, indent=1); return 1

    st, r = llamar("GET", "/models", params={"pageSize": 1000})
    res["modelos_tts"] = sorted(m["name"].split("/")[-1] for m in r.get("models", []) if "tts" in m.get("name", "")) if st == 200 else error_de(r)

    for etiqueta, filtro in (("es-ES", {"language_code": "es-ES"}), ("region_ES", {"region_code": "ES"}), ("es", {"language_code": "es"})):
        st, r = llamar("GET", "/voices", params={**filtro, "page_size": 1000})
        if st == 200:
            vs = r.get("voices", [])
            res["biblioteca"][etiqueta] = {"total": len(vs), "voces": [
                {k: v.get(k) for k in ("id", "display_name", "displayName", "type", "gender", "pitch", "accent", "language_code", "languageCode", "description") if v.get(k)} for v in vs[:400]]}
        else:
            res["biblioteca"][etiqueta] = {"http": st, **error_de(r)}

    # voces ya diseñadas en el proyecto (para no duplicar)
    mias = {}
    st, r = llamar("GET", "/voices", params={"type": "prompted", "page_size": 1000})
    if st == 200:
        for v in r.get("voices", []):
            nombre = g(v, "display_name", "displayName") or ""
            if nombre.startswith(PREFIJO):
                mias[nombre[len(PREFIJO):]] = v.get("id")
    else:
        res["listado_propias"] = {"http": st, **error_de(r)}

    for p in SOLO:
        genero, desc, _, _ = PERSONAJES[p]
        if p in mias and p not in REDISENAR:
            res["voces"][p] = {"id": mias[p], "reutilizada": True}; continue
        if p in mias:
            llamar("DELETE", f"/voices/{mias[p]}")
        info = None; intentos = []
        for modelo in ("gemini-3.8-flash-tts", None):
            voz = {"type": "prompted", "display_name": PREFIJO + p, "gender": genero, "language_code": "es-ES", "prompted": {"input": desc}}
            if modelo:
                voz["model"] = modelo
            st, r = llamar("POST", "/voices", {"store": True, "voice": voz})
            if st == 200 and r.get("id"):
                info = {"id": r["id"], "modelo_diseno": modelo or g(r, "model") or "por defecto", "intentos_fallidos": intentos}
                m = g(r, "sample_audio", "sampleAudio") or {}
                if m.get("data"):
                    info["muestra"] = f"diseno_{p}.wav"; info["muestra_s"] = guardar_audio(m["data"], f"{OUT}/diseno_{p}.wav")
                break
            intentos.append({"http": st, "modelo_diseno": modelo, **error_de(r)})
            info = {"sin_voz": True, "intentos_fallidos": intentos}
            time.sleep(5)
        res["voces"][p] = info
        time.sleep(2)

    def decir(vid, partes, archivo, modelo="gemini-3.8-flash-tts"):
        cuerpo = {"contents": [{"role": "user", "parts": [{"text": t, "speech_metadata": {"style": e}} if e else {"text": t} for t, e in partes]}],
                  "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"voice": vid}}}}
        st, r = llamar("POST", f"/models/{modelo}:generateContent", cuerpo)
        if st == 200:
            ps = (((r.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
            datos = [g(x, "inlineData", "inline_data") for x in ps]; datos = [d for d in datos if d and d.get("data")]
            if datos:
                seg = guardar_audio(datos[0]["data"], f"{OUT}/{archivo}") if len(datos) == 1 else None
                if seg is None:  # varias partes de audio: se guardan por separado
                    seg = [guardar_audio(d["data"], f"{OUT}/{archivo[:-4]}_{i}.wav") for i, d in enumerate(datos)]
                return {"modelo": modelo, "archivo": archivo, "segundos": seg, "partes_audio": len(datos), "tokens_audio": (g(r, "usageMetadata") or {}).get("candidatesTokenCount")}
            return {"modelo": modelo, "http": 200, "mensaje": "respuesta sin audio: " + json.dumps(r)[:400]}
        e = r.get("error", {}) if isinstance(r, dict) else {}
        return {"modelo": modelo, "http": st, **error_de(r), "detalles": json.dumps(e.get("details"), ensure_ascii=False)[:900] if e.get("details") else None}

    cfg = {}
    try:
        cfg = json.load(open(os.path.join(os.path.dirname(__file__), "..", "equipo", "audicion_gemini.json"), encoding="utf-8"))
    except Exception:
        pass
    for p, partes in (cfg.get("frases") or {}).items():
        vid = (res["voces"].get(p) or {}).get("id")
        if not vid:
            res["frases"][p] = {"omitida": "sin voz diseñada"}; continue
        res["frases"][p] = decir(vid, [tuple(x) for x in partes], f"frase_{p}.wav", cfg.get("modelo") or "gemini-3.8-flash-tts")
        time.sleep(7)

    # sonda de cuota: peticiones mínimas hasta que Google diga el límite diario (el mensaje 429 lo trae)
    n = int(cfg.get("sonda_cuota") or 0); vid = (res["voces"].get("neo") or {}).get("id"); sonda = {"ok": 0, "errores": []}
    esperas = 0
    for i in range(n):
        if not vid:
            break
        r1 = decir(vid, [("Vale.", "")], "sonda.wav")
        if r1.get("archivo"):
            sonda["ok"] += 1; time.sleep(4); continue
        sonda["errores"].append({"n": i, **{k: v for k, v in r1.items() if v}})
        txt = (r1.get("mensaje") or "") + (r1.get("detalles") or "")
        if r1.get("http") == 429 and ("PerMinute" in txt or "per minute" in txt.lower()) and "PerDay" not in txt and esperas < 6:
            esperas += 1; time.sleep(62); continue
        if r1.get("http") in (500, 503, 0) and esperas < 6:
            esperas += 1; time.sleep(20); continue
        break
    res["sonda_cuota"] = sonda

    json.dump(res, open(f"{OUT}/resultado.json", "w"), ensure_ascii=False, indent=1)
    resumen = {k: v for k, v in res.items() if k != "biblioteca"}
    resumen["biblioteca"] = {k: (v.get("total", v)) for k, v in res["biblioteca"].items()}
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
