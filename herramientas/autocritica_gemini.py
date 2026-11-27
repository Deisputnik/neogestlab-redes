#!/usr/bin/env python3
"""Autocritica de Guionista contra el criterio real de Calidad.

Orden del dueno (22/11/2026): "que calidad y creador, guionista se pongan
de acuerdo, usa recursos de gemini". Este script revisa cada borrador de
equipo/guiones_gemini/pendientes/ con el mismo criterio que usa Calidad
(equipo/estandar_calidad.md + equipo/lecciones_calidad.md + la biblia de
la serie) ANTES de que Creador lo escoja para renderizar, para no gastar
un render caro en algo que Calidad va a rechazar de todos modos.

Variable de entorno: GEMINI_API_KEY (la misma que ya usa guionista_gemini.py).
Uso: python3 herramientas/autocritica_gemini.py
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTANDAR = os.path.join(RAIZ, "equipo", "estandar_calidad.md")
LECCIONES = os.path.join(RAIZ, "equipo", "lecciones_calidad.md")
BIBLIA = os.path.join(RAIZ, "equipo", "serie_jambo.md")
TABLON = os.path.join(RAIZ, "equipo", "tablon.md")
PENDIENTES = os.path.join(RAIZ, "equipo", "guiones_gemini", "pendientes")
REVISAR = os.path.join(RAIZ, "equipo", "guiones_gemini", "revisar")

MODELOS = [
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]

MOTORES_DESCARTADOS = {"sketch"}

GANCHO_FORMULA = re.compile(
    r"\btu\s+\S+.{0,25}?\ben\s+\d+\s+(pasos|minutos|segundos|dias|clics?)\b",
    re.IGNORECASE,
)


def _leer(ruta, limite=None):
    if not os.path.isfile(ruta):
        return ""
    with open(ruta, encoding="utf-8") as f:
        texto = f.read()
    if limite and len(texto) > limite:
        texto = texto[:limite]
    return texto


def _comprobaciones_mecanicas(ep):
    motivos = []
    motor = str(ep.get("motor", "")).lower()
    if motor in MOTORES_DESCARTADOS:
        motivos.append(
            "motor descartado por Calidad (sketch): no se debe renderizar asi"
        )
    for esc in ep.get("escenas") or []:
        t = str(esc.get("t", ""))
        if GANCHO_FORMULA.search(t):
            motivos.append(
                "frase con patron formulario tipo <<Tu X en N pasos>>, "
                "ya rechazado antes: %r" % t[:60]
            )
    return motivos


def _llamar_gemini(prompt, api_key):
    for modelo in MODELOS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + modelo
            + ":generateContent?key="
            + api_key
        )
        datos = json.dumps(
            {"contents": [{"parts": [{"text": prompt}]}]}
        ).encode("utf-8")
        peticion = urllib.request.Request(
            url,
            data=datos,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(peticion, timeout=60) as resp:
                cuerpo = json.loads(resp.read().decode("utf-8"))
            partes = cuerpo["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in partes)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(2)
                continue
            if e.code == 404:
                continue
        except Exception:
            time.sleep(1)
            continue
    return None


def _prompt_autocritica(ep):
    estandar = _leer(ESTANDAR, 6000)
    lecciones = _leer(LECCIONES, 6000)
    biblia = _leer(BIBLIA, 12000)   # 27/11/2026: la biblia v5.3 es corta y limpia; se lee hasta el patrón fijo (apartados 1-6)
    guion = json.dumps(ep, ensure_ascii=False, indent=2)
    return (
        "Eres el mismo Calidad que evalua los videos ya renderizados de "
        "esta serie, pero ahora revisas un GUION ANTES de renderizarlo, "
        "para evitar gastar un render caro en algo que luego rechazarias.\n\n"
        "ESTANDAR DE CALIDAD:\n" + estandar + "\n\n"
        "LECCIONES DE RECHAZOS ANTERIORES:\n" + lecciones + "\n\n"
        "BIBLIA DE LA SERIE:\n" + biblia + "\n\n"
        "GUION A REVISAR (JSON):\n" + guion + "\n\n"
        "CRITERIO NUEVO (orden del dueno 27/11/2026: 'no se entiende mucho el sentido de los guiones, tienen que mejorar; "
        "que adapte chistes modernos'): lee el guion UNA sola vez como un espectador que no conoce la serie. "
        "riesgo_rechazo=true tambien si (a) no puedes resumir en una frase quien quiere que, que lo impide y como acaba; "
        "(b) el remate no se entiende a la primera o no sale de lo visto; (c) hay mas de una idea o golpes sueltos que no "
        "son consecuencia del anterior; (d) el chiste es rancio o no se reconoce ningun chiste o situacion de humor actual. "
        "En ese caso el motivo empieza por 'NO SE ENTIENDE:' o 'CHISTE:' y arreglo_sugerido dice que simplificar.\n\n"
        "CRITERIOS DE LA ORDEN FINAL DEL 27/11/2026 (riesgo_rechazo=true si falla alguno; el motivo empieza por 'REPARTO:', "
        "'MEMORIA:', 'ESTANCIAS:' o 'MARCA:'): (1) Rosa, Felipe, Sindy, Jambo y Neo tienen replica y cada una solo la "
        "podria decir ese personaje; (2) alguna replica recuerda con un detalle algo de un episodio anterior; (3) la accion pasa por "
        "2 o 3 estancias (campo set de escena) con grupos y conversaciones distintos, no todos juntos todo el rato; (4) la palabra "
        "'moraleja' no aparece en ninguna replica ni texto; (5) Neogest Lab, si se nombra, es una sola vez, de pasada y sin sonar a "
        "anuncio ni nombrar aplicaciones concretas; (6) el final deja una ensenanza que sale de lo que se ha visto; (7) APERTURA EN FRIO (biblia §6, 27/11): la primera escena es el gancho, "
        "con titulo_fijo de 10 palabras como mucho (la situacion con el colectivo, sin preguntas de producto), y el guion no pide plano de casa "
        "al abrir ni al cerrar ni bucle (motivo 'APERTURA:').\n\n"
        "Responde SOLO con un JSON de una linea con esta forma exacta:\n"
        '{"riesgo_rechazo": true/false, "motivos": ["..."], '
        '"arreglo_sugerido": "..."}\n'
        "riesgo_rechazo=true solo si de verdad crees que Calidad lo "
        "rechazaria tal cual esta. Si esta bien, riesgo_rechazo=false y "
        "motivos=[]."
    )


def _parsear_veredicto(texto):
    if not texto:
        return None
    m = re.search(r"\{.*\}", texto, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def procesar_uno(ruta, api_key):
    with open(ruta, encoding="utf-8") as f:
        ep = json.load(f)

    if "_autocritica_calidad" in ep:
        return None

    motivos = list(_comprobaciones_mecanicas(ep))

    veredicto = None
    if api_key:
        veredicto = _parsear_veredicto(
            _llamar_gemini(_prompt_autocritica(ep), api_key)
        )

    riesgo = bool(motivos)
    if veredicto:
        riesgo = riesgo or bool(veredicto.get("riesgo_rechazo"))
        motivos.extend(veredicto.get("motivos") or [])

    ep["_autocritica_calidad"] = {
        "riesgo_rechazo": riesgo,
        "motivos": motivos,
        "arreglo_sugerido": (veredicto or {}).get("arreglo_sugerido", ""),
        "fuente": "gemini" if veredicto else "mecanica",
        "fecha": datetime.datetime.utcnow().isoformat() + "Z",
    }

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(ep, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if riesgo:
        os.makedirs(REVISAR, exist_ok=True)
        destino = os.path.join(REVISAR, os.path.basename(ruta))
        os.replace(ruta, destino)
        return (os.path.basename(ruta), True, motivos)

    return (os.path.basename(ruta), False, motivos)


def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not os.path.isdir(PENDIENTES):
        print("No hay carpeta de pendientes, nada que revisar.")
        return 0

    nombres = sorted(
        n for n in os.listdir(PENDIENTES) if n.endswith(".json")
    )
    if not nombres:
        print("No hay borradores pendientes.")
        return 0

    resultados = []
    for nombre in nombres:
        ruta = os.path.join(PENDIENTES, nombre)
        try:
            r = procesar_uno(ruta, api_key)
        except Exception as e:
            print("Error procesando %s: %s" % (nombre, e))
            continue
        if r:
            resultados.append(r)

    if not resultados:
        print("Todos los borradores ya tenian autocritica.")
        return 0

    revisados = len(resultados)
    movidos = sum(1 for _, riesgo, _ in resultados if riesgo)
    linea = (
        "- %s Autocritica Guionista-Calidad: %d borrador(es) revisado(s), "
        "%d movido(s) a revisar por riesgo de rechazo.\n"
        % (
            datetime.date.today().isoformat(),
            revisados,
            movidos,
        )
    )
    try:
        with open(TABLON, "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception as e:
        print("No se pudo escribir en el tablon: %s" % e)

    for nombre, riesgo, motivos in resultados:
        print(nombre, "-> riesgo" if riesgo else "-> ok", motivos)

    return 0


if __name__ == "__main__":
    sys.exit(main())
