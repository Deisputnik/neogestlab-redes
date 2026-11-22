#!/usr/bin/env python3
"""Autocritica de Guionista contra el criterio real de Calidad (orden del dueno, 22/11/2026:
"que calidad y creador, guionista se pongan de acuerdo, usa recursos de gemini").

Motivo: Guionista (herramientas/guionista_gemini.py) solo valida la FORMA del guion (numero
de escenas, personajes validos, longitud de la moraleja...). El contenido real que Calidad
rechaza despues de un render completo (motor "sketch" descartado, logo antiguo, cifra sin
fuente, gancho formulario tipo "Tu X en N pasos", declaracion de postura en vez de frase
hablada) nunca se comprueba antes de gastar ese render. Este script cierra ese hueco: llama a
Gemini (misma cuenta/capa gratis que Guionista, GEMINI_API_KEY) para que autocritique cada
borrador ya guardado en equipo/guiones_gemini/pendientes/ contra el MISMO criterio que usa
Calidad (equipo/estandar_calidad.md y equipo/lecciones_calidad.md), antes de que el Creador
elija uno para renderizar.

No sustituye a Calidad real (esa sigue viendo el video terminado): es un filtro previo,
gratis y rapido, para que lo que llega a render ya este de acuerdo con lo que Calidad exige.

Si Gemini ve riesgo de rechazo, el borrador se mueve de pendientes/ a revisar/ (no se borra)
con el veredicto escrito dentro, para que el Creador no lo elija por error y pueda corregirlo
o descartarlo. Si Gemini no esta disponible, no bloquea nada: el borrador se queda en
pendientes/ tal cual, como hasta ahora.

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

def _leer(ruta, limite=None):
      if not os.path.exists(ruta):
                return ""
            with open(ruta, encoding="utf-8") as f:
                      txt = f.read()
                  return txt[:limite] if limite else txt


# Misma lista e identica logica de reintento que herramientas/guionista_gemini.py, para no
# depender de un modelo que ese dia este saturado o retirado.
MODELOS = [
      "gemini-3.7-flash", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-flash-latest",
      "gemini-3.1-flash-lite", "gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-2.5-flash",
]
MOTORES_DESCARTADOS = {"sketch"}  # 21-22/11: "motor sketch descartado" (327_jambo_black_friday_70)
GANCHO_FORMULA = re.compile(
      r"\btu\s+\S+.{0,25}?\ben\s+\d+\s+(pasos|minutos|segundos|dias|clics?)\b", re.IGNORECASE
)


def _comprobaciones_mecanicas(ep):
      """Lo que no hace falta preguntarle a Gemini: igual de barato que pre_entrega.py."""
    motivos = []
    if str(ep.get("motor", "")).lower() in MOTORES_DESCARTADOS:
              motivos.append("motor descartado por Calidad (sketch): no se debe renderizar asi")
          for esc in ep.get("escenas") or []:
                    t = str(esc.get("t", ""))
                    if GANCHO_FORMULA.search(t):
                                  motivos.append("frase con patron formulario tipo <<Tu X en N pasos>>, ya rechazado antes: %r" % t[:60])
                          return motivos


def _llamar_gemini(prompt, api_key):
      body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
      }
    for modelo in MODELOS:
              url = (f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}"
                                    f":generateContent?key={api_key}")
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                                                           headers={"Content-Type": "application/json"}, method="POST")
        for intento in range(2):
                      try:
                                        with urllib.request.urlopen(req, timeout=25) as resp:
                                                              data = json.loads(resp.read().decode("utf-8"))
                                                          texto = data["candidates"][0]["content"]["parts"][0]["text"]
                                        texto = re.sub(r"^```(json)?|```$", "", texto.strip(), flags=re.MULTILINE).strip()
                                        return json.loads(texto)
except urllib.error.HTTPError as e:
                if e.code == 503 and intento == 0:
                                      time.sleep(8)
                                      continue
                                  break
except Exception:
                if intento == 0:
                                      time.sleep(5)
                                      continue
                                  break
    return None


def _prompt_autocritica(ep):
      return (
                "Eres el rol CALIDAD de Neogest Lab revisando un guion ANTES de que se renderice "
                "(no hay video todavia: juzga solo el texto). Aplica exactamente el mismo criterio "
                "que Calidad usa sobre videos ya terminados, para detectar ahora lo que luego "
                "rechazaria, y asi no gastar un render en algo que no va a pasar.\n\n"
                "ESTANDAR DE CALIDAD (equipo/estandar_calidad.md):\n---\n"
                + _leer(ESTANDAR, 6000) + "\n---\n\n"
                "MOTIVOS DE RECHAZO MAS REPETIDOS EN PIEZAS YA RENDERIZADAS (equipo/lecciones_calidad.md):\n---\n"
                + _leer(LECCIONES, 3000) + "\n---\n\n"
                "CIFRAS VERIFICADAS QUE SI SE PUEDEN CITAR (tabla de la biblia; cualquier otra cifra "
                "que aparezca en el guion y no este aqui es una cifra SIN FUENTE y debe senalarse):\n---\n"
                + _leer(BIBLIA, 4000) + "\n---\n\n"
                "GUION A REVISAR (JSON):\n"
                + json.dumps(ep, ensure_ascii=False, indent=1) + "\n\n"
                'Responde SOLO un objeto JSON (sin texto fuera, sin comillas triples): '
                '{"riesgo_rechazo": true/false, "motivos": ["razon concreta citando la frase o cifra '
                'exacta del guion, una por motivo"], "arreglo_sugerido": "que cambiar para que pase, '
                'o cadena vacia si riesgo_rechazo es false"}\n'
                "Se estricto: en caso de duda sobre una cifra o una frase, marca riesgo_rechazo=true "
                "y dilo en motivos en vez de darla por buena. No inventes motivos que no esten "
                "respaldados por el texto de arriba."
      )


def procesar_uno(ruta, api_key):
      ep = json.load(open(ruta, encoding="utf-8"))
    if "_autocritica_calidad" in ep:
              return None

    motivos = _comprobaciones_mecanicas(ep)
    veredicto = None
    if api_key:
              veredicto = _llamar_gemini(_prompt_autocritica(ep), api_key)

    if veredicto and isinstance(veredicto, dict):
              riesgo = bool(veredicto.get("riesgo_rechazo")) or bool(motivos)
        motivos_todos = motivos + [str(m) for m in (veredicto.get("motivos") or [])]
        arreglo = veredicto.get("arreglo_sugerido") or ""
        fuente = "gemini"
else:
        riesgo = bool(motivos)
        motivos_todos = motivos
        arreglo = ""
        fuente = "solo mecanico (Gemini no respondio)"

    ep["_autocritica_calidad"] = {
              "riesgo_rechazo": riesgo,
              "motivos": motivos_todos,
              "arreglo_sugerido": arreglo,
              "fuente": fuente,
              "fecha": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    destino_dir = REVISAR if riesgo else os.path.dirname(ruta)
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, os.path.basename(ruta))
    with open(destino, "w", encoding="utf-8") as f:
              json.dump(ep, f, ensure_ascii=False, indent=2)
    if destino != ruta:
              os.remove(ruta)
    return {"slug": ep.get("slug", os.path.basename(ruta)), "riesgo_rechazo": riesgo,
                        "motivos": motivos_todos, "movido": destino != ruta}


def main():
      api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
              print("GEMINI_API_KEY no esta en el entorno: solo se hacen las comprobaciones mecanicas.")

    if not os.path.isdir(PENDIENTES):
              print("No hay equipo/guiones_gemini/pendientes/: nada que autocriticar.")
        return 0

    resultados = []
    for nombre in sorted(os.listdir(PENDIENTES)):
              if not nombre.endswith(".json"):
                            continue
                        r = procesar_uno(os.path.join(PENDIENTES, nombre), api_key)
        if r:
                      resultados.append(r)

    if not resultados:
              print("Autocritica Guionista/Calidad: nada nuevo que revisar.")
        return 0

    riesgo_n = sum(1 for r in resultados if r["riesgo_rechazo"])
    detalle = "; ".join(
              f"{r['slug']}: {', '.join(r['motivos'][:2]) or 'ok'}" for r in resultados if r["riesgo_rechazo"]
    )[:400]
    linea = (
              f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC . Autocritica Guionista/Calidad (Gemini) . "
              f"revisados {len(resultados)}, {riesgo_n} movidos a equipo/guiones_gemini/revisar/ por riesgo de rechazo"
              + (f" ({detalle})" if detalle else "")
    )
    with open(TABLON, "a", encoding="utf-8") as f:
              f.write(linea + "\n")
    print(linea)
    return 0


if __name__ == "__main__":
      sys.exit(main())
