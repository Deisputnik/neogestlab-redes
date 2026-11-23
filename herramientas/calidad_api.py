#!/usr/bin/env python3
"""Calidad vía API directa de Anthropic (piloto, orden del dueño 16/11/2026: "todo lo que se
pueda usar con la API y no gastar tokens, se hace"), siguiendo el mismo patrón que
`herramientas/supervisor_api.py` para el rol Supervisor.

Sustituye, para este rol, la tarea programada de Claude Code (gasta límite semanal del plan
Max) por una llamada directa a la API de Anthropic con tool use real (gasta créditos de pago
por uso, separados del plan Max). Mismo rol, mismo horario (11:41 y 17:41 Madrid), mismo
criterio (`equipo/estandar_calidad.md` v9 y `equipo/roles/calidad.md`).

Alcance de este piloto v1 (deliberadamente reducido, como hizo Supervisor):
  - SÍ: para cada pieza de cola/ renderizada sin calidad.json o con uno anterior a su render,
    descarga el vídeo (asset de la release "cola" o video_externo), ffprobe + silencedetect +
    una medida de LUFS/pico + 3 fotogramas, y deja que el modelo (Sonnet, con tool use) decida
    aprobado/rechazado y escriba calidad.json con el mismo formato que usa Calidad hoy.
  - NO todavía: no lee `hechos_verificados`/`prohibido_afirmar` de Base44 (ese MCP no existe
    fuera de una sesión de Claude Code): para reels de apps, el modelo solo contrasta con las
    fuentes que el propio post.json ya cita (_fuentes/_comprobado) y, si no puede verificar
    una cifra, dejarlo anotado en vez de aprobar. No relanza `ciclo.yml` ni mueve `cuando`
    (eso lo sigue haciendo Calidad en Claude Code hasta validar varias pasadas sin fallos).
  - Límite de piezas por pasada (MAX_PIEZAS) para acotar coste y tiempo de cada ejecución.

Variables de entorno: ANTHROPIC_API_KEY (secreto del repo). Usa `gh` (GITHUB_TOKEN) para leer
la release "cola" — ya autenticado dentro de GitHub Actions.
Uso: python3 herramientas/calidad_api.py
"""
import base64
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLA = os.path.join(RAIZ, "cola")
TABLON = os.path.join(RAIZ, "equipo", "tablon.md")
ROL = os.path.join(RAIZ, "equipo", "roles", "calidad.md")
ESTANDAR = os.path.join(RAIZ, "equipo", "estandar_calidad.md")
LECCIONES = os.path.join(RAIZ, "equipo", "lecciones_calidad.md")
DIRECTIVA = os.path.join(RAIZ, "equipo", "DIRECTIVA_VIGENTE.md")

MODELO = "claude-sonnet-5"
RELEASE = "cola"
REPO = os.environ.get("GITHUB_REPOSITORY", "Deisputnik/neogestlab-redes")
MAX_PIEZAS = 4          # tope de piezas evaluadas por pasada (coste/tiempo)
MAX_TURNOS = 6          # tope de turnos de tool-use por pieza


def _leer(ruta):
    if not os.path.exists(ruta):
        return ""
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def _leer_json(ruta):
    if not os.path.isfile(ruta):
        return None
    try:
        return json.load(open(ruta, encoding="utf-8"))
    except Exception:
        return None


def _fecha_ok(fecha_texto, referencia_texto):
    """True si `fecha_texto` (calidad.json) es posterior o igual a `referencia_texto`
    (renderizado). Si no se puede comparar, se considera caducado (False) para forzar revisión."""
    try:
        f = datetime.datetime.fromisoformat(fecha_texto.replace("Z", "+00:00"))
        r = datetime.datetime.fromisoformat(referencia_texto.replace("Z", "+00:00"))
        return f >= r
    except Exception:
        return False


def piezas_pendientes():
    """Determinista (sin API): qué carpetas de cola/ están renderizadas y necesitan
    calidad.json nuevo (igual que el punto 1 de 'Qué se revisa en cada pasada' de roles/calidad.md)."""
    pendientes, al_dia, sin_render = [], [], []
    if not os.path.isdir(COLA):
        return pendientes, al_dia, sin_render
    for pid in sorted(os.listdir(COLA)):
        pdir = os.path.join(COLA, pid)
        post = _leer_json(os.path.join(pdir, "post.json"))
        if not post:
            continue
        renderizado = post.get("renderizado")
        tiene_render = bool(renderizado) or bool(post.get("video_externo"))
        if not tiene_render:
            sin_render.append(pid)
            continue
        cal = _leer_json(os.path.join(pdir, "calidad.json"))
        if cal and cal.get("aprobado_por") == "dueño":
            al_dia.append(pid)  # visto bueno del dueño: no se reevalúa (roles/calidad.md)
            continue
        ref = renderizado if isinstance(renderizado, str) else None
        if cal and cal.get("fecha") and (ref is None or _fecha_ok(cal["fecha"], ref)):
            al_dia.append(pid)
            continue
        pendientes.append(pid)
    return pendientes, al_dia, sin_render


# ---------------------------------------------------------------- vídeo: descarga e inspección

def _gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:2])}: {r.stderr.strip()[-400:]}")
    return r.stdout


def descargar_video(pid, post, destino):
    url = post.get("video_externo")
    if url:
        req = urllib.request.Request(url, headers={"User-Agent": "calidad-api/1.0"})
        with urllib.request.urlopen(req, timeout=180) as resp, open(destino, "wb") as f:
            shutil.copyfileobj(resp, f)
        return "video_externo"
    nombre = post.get("asset")
    if not nombre:
        raise RuntimeError("post.json no tiene 'asset' ni 'video_externo': nada que descargar")
    aid = _gh("api", f"repos/{REPO}/releases/tags/{RELEASE}",
               "--jq", f'.assets[] | select(.name=="{nombre}") | .id').strip()
    if not aid:
        raise RuntimeError(f"no encuentro el asset {nombre} en la release {RELEASE}")
    salida = subprocess.run(
        ["gh", "api", "-H", "Accept: application/octet-stream",
         f"repos/{REPO}/releases/assets/{aid}"],
        capture_output=True, timeout=180)
    if salida.returncode != 0:
        raise RuntimeError(f"descarga del asset {nombre}: {salida.stderr.decode()[-400:]}")
    with open(destino, "wb") as f:
        f.write(salida.stdout)
    return "asset"


def _ffprobe(video):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=width,height,codec_name,codec_type",
         "-of", "json", video], capture_output=True, text=True, timeout=60)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"error": r.stderr.strip()[-300:]}


def _silencios(video, umbral="-45dB", minimo=0.5):
    r = subprocess.run(
        ["ffmpeg", "-i", video, "-af", f"silencedetect=noise={umbral}:d={minimo}",
         "-f", "null", "-"], capture_output=True, text=True, timeout=90)
    tramos, inicio = [], None
    for linea in r.stderr.splitlines():
        m1 = re.search(r"silence_start:\s*([\d.]+)", linea)
        m2 = re.search(r"silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)", linea)
        if m1:
            inicio = float(m1.group(1))
        if m2 and inicio is not None:
            tramos.append({"inicio_s": round(inicio, 2), "fin_s": round(float(m2.group(1)), 2),
                           "duracion_s": round(float(m2.group(2)), 2)})
            inicio = None
    return tramos


def _lufs_pico(video):
    r = subprocess.run(
        ["ffmpeg", "-i", video, "-af", "loudnorm=I=-14:TP=-1:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True, timeout=90)
    bloque = r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1]
    try:
        m = json.loads(bloque)
        return {"lufs_medido": float(m.get("input_i", "nan")),
                "pico_real_medido_db": float(m.get("input_tp", "nan"))}
    except Exception:
        return {"error": "no se pudo medir LUFS/pico"}


LOGO_REFERENCIA = os.path.join(RAIZ, "equipo", "perfil_kit", "logo_neogest_lab_oficial.png")


def _logo_referencia():
    """Logo oficial 2026 en base64 (PNG), para que el modelo compare la marca con el original y no de memoria."""
    try:
        with open(LOGO_REFERENCIA, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except OSError:
        return None


def _fotogramas(video, duracion):
    out = []
    if not duracion or duracion <= 0:
        instantes = [0.5]
    else:
        # 21/11/2026 (cuellos de botella): 6 fotogramas y SIEMPRE el último; con 3 (8 %, 50 %, 90 %) nunca se veía la
        # tarjeta de cierre y el bloqueo 11 (isotipo 2026) se rechazaba «sin poder verificar» (329).
        instantes = sorted({round(min(0.3, duracion / 10), 2)} | {round(duracion * f, 2) for f in (0.25, 0.5, 0.75)}
                           | {round(max(0.0, duracion - 1.2), 2), round(max(0.0, duracion - 0.25), 2)}
                           # 23/11/2026: y uno ~4 s antes del final: en las promos es el plano con la frase de cierre («Pide tu
                           # prueba gratuita…»), que va justo antes de la tarjeta del logo y con 6 fotogramas no se veía (801, 802).
                           | {round(max(0.0, duracion - 4.0), 2)})
    with tempfile.TemporaryDirectory() as tmp:
        for i, t in enumerate(instantes):
            jpg = os.path.join(tmp, f"f{i}.jpg")
            subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", video, "-frames:v", "1",
                             "-vf", "scale=480:-1", "-q:v", "4", jpg],
                            capture_output=True, timeout=60)
            if os.path.isfile(jpg):
                with open(jpg, "rb") as f:
                    out.append({"t": t, "b64": base64.b64encode(f.read()).decode()})
    return out


def inspeccionar_video(pid, post):
    with tempfile.TemporaryDirectory() as tmp:
        video = os.path.join(tmp, "pieza.mp4")
        origen = descargar_video(pid, post, video)
        info = _ffprobe(video)
        duracion = None
        try:
            duracion = float(info.get("format", {}).get("duration"))
        except Exception:
            pass
        datos = {
            "origen": origen,
            "ffprobe": info,
            "duracion_s": duracion,
            "silencios": _silencios(video),
            "audio": _lufs_pico(video),
        }
        fotos = _fotogramas(video, duracion)
    return datos, fotos


# ---------------------------------------------------------------- Anthropic (tool use)

HERRAMIENTAS = [
    {
        "name": "inspeccionar_video",
        "description": ("Descarga el mp4 de la pieza indicada (asset de la release «cola» o "
                         "video_externo de su post.json), y devuelve ffprobe (resolución, "
                         "duración), silencedetect a -45 dB, una medida de LUFS/pico real "
                         "(loudnorm) y 6 fotogramas (segundo 0, 25 %, 50 %, 75 % y los dos últimos, con la tarjeta de cierre) como imágenes. "
                         "Úsala una vez por pieza; no hace falta más de una llamada."),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "escribir_calidad",
        "description": ("Escribe el calidad.json final de la pieza (sustituye cualquier "
                         "versión anterior). Debe seguir el formato de equipo/roles/calidad.md: "
                         "si aprobado=true, nota debe ser >= 90."),
        "input_schema": {
            "type": "object",
            "properties": {
                "aprobado": {"type": "boolean"},
                "nota": {"type": "integer"},
                "motivos": {"type": "array", "items": {"type": "string"},
                            "description": "obligatorio si aprobado=false"},
                "como_arreglarlo": {"type": "string"},
                "comentario": {"type": "string", "description": "si aprobado=true"},
            },
            "required": ["aprobado", "nota"],
        },
    },
]


def _bloque_contexto(pid, post, cal_anterior, guion, control_audio):
    resumen_post = {k: post.get(k) for k in (
        "formato", "texto", "cuando", "app", "app_slug", "comentario_fijado",
        "avance_siguiente", "youtube", "_fuentes", "_comprobado", "musica", "control_audio")}
    return (
        f"Pieza: {pid}\n\npost.json (resumen):\n```json\n"
        + json.dumps(resumen_post, ensure_ascii=False, indent=1)
        + "\n```\ncalidad.json anterior (si lo había):\n```json\n"
        + json.dumps(cal_anterior, ensure_ascii=False, indent=1)
        + "\n```\nguion.json o spec (resumen, puede faltar):\n```json\n"
        + json.dumps(guion, ensure_ascii=False, indent=1)[:4000]
        + "\n```\ncontrol_audio.json de Actions (whisper contra guion, ya generado por el ciclo):\n```json\n"
        + json.dumps(control_audio, ensure_ascii=False, indent=1)
        + "\n```\nLlama a `inspeccionar_video` para ver el vídeo y después a `escribir_calidad` "
          "con tu decisión final. Si algo te lo impide (vídeo no descargable, formato raro), "
          "dilo en un texto final en vez de inventar una nota."
    )


def evaluar_pieza(cliente, sistema, pid):
    pdir = os.path.join(COLA, pid)
    post = _leer_json(os.path.join(pdir, "post.json")) or {}
    cal_anterior = _leer_json(os.path.join(pdir, "calidad.json"))
    guion = _leer_json(os.path.join(pdir, "guion.json")) or _leer_json(os.path.join(pdir, "spec.json"))
    control_audio = _leer_json(os.path.join(pdir, "control_audio.json"))

    mensajes = [{"role": "user", "content": _bloque_contexto(pid, post, cal_anterior, guion, control_audio)}]
    resultado = {"pid": pid, "escrito": False, "resumen": ""}

    for _ in range(MAX_TURNOS):
        resp = cliente.messages.create(
            model=MODELO, max_tokens=2000, system=sistema, tools=HERRAMIENTAS,
            thinking={"type": "disabled"}, messages=mensajes,
        )
        mensajes.append({"role": "assistant", "content": resp.content})
        llamadas = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not llamadas:
            textos = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
            resultado["resumen"] = "\n".join(textos).strip()[:500]
            break

        bloques_resultado = []
        for llamada in llamadas:
            if llamada.name == "inspeccionar_video":
                try:
                    datos, fotos = inspeccionar_video(pid, post)
                    contenido = [{"type": "text", "text": json.dumps(datos, ensure_ascii=False)}]
                    for foto in fotos:
                        contenido.append({"type": "text", "text": f"Fotograma t={foto['t']}s"})
                        contenido.append({"type": "image", "source": {
                            "type": "base64", "media_type": "image/jpeg", "data": foto["b64"]}})
                    ref = _logo_referencia()
                    if ref:
                        contenido.append({"type": "text", "text": "REFERENCIA (no es un fotograma del vídeo): logo oficial 2026 de "
                                          "Neogest Lab, el VÁLIDO. Si la insignia o la tarjeta de cierre coinciden con él, la marca es correcta."})
                        contenido.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": ref}})
                    bloques_resultado.append({"type": "tool_result", "tool_use_id": llamada.id,
                                               "content": contenido})
                except Exception as e:
                    bloques_resultado.append({"type": "tool_result", "tool_use_id": llamada.id,
                                               "content": f"ERROR: {e}", "is_error": True})
            elif llamada.name == "escribir_calidad":
                datos = dict(llamada.input)
                if datos.get("aprobado") and int(datos.get("nota", 0)) < 90:
                    bloques_resultado.append({"type": "tool_result", "tool_use_id": llamada.id,
                                               "content": "ERROR: aprobado=true exige nota >= 90",
                                               "is_error": True})
                    continue
                datos["fecha"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                datos["revisor"] = "Calidad (API)"
                if post.get("renderizado"):
                    datos["render"] = post["renderizado"]
                with open(os.path.join(pdir, "calidad.json"), "w", encoding="utf-8") as f:
                    json.dump(datos, f, ensure_ascii=False, indent=2)
                resultado["escrito"] = True
                resultado["nota"] = datos.get("nota")
                resultado["aprobado"] = datos.get("aprobado")
                resultado["resumen"] = (datos.get("comentario") or "; ".join(datos.get("motivos", [])))[:300]
                bloques_resultado.append({"type": "tool_result", "tool_use_id": llamada.id,
                                           "content": "calidad.json escrito"})
            else:
                bloques_resultado.append({"type": "tool_result", "tool_use_id": llamada.id,
                                           "content": "ERROR: herramienta desconocida", "is_error": True})
        mensajes.append({"role": "user", "content": bloques_resultado})
        if resultado["escrito"]:
            break
    return resultado


# 22/11/2026 (Coordinación, auditoría): Calidad rechazaba en falso el formato vigente citando órdenes derogadas
# (351: «40,1 s > 20 s»; 353: la foto de la casa con gancho = intro obligatoria). Este bloque va PRIMERO en el prompt y manda
# sobre cualquier duración o ejemplo antiguo que aparezca en estandar_calidad.md o lecciones_calidad.md.
FORMATO_VIGENTE = (
    "FORMATO VIGENTE (manda sobre TODO lo que leas abajo si choca; DIRECTIVA §5, biblia v5.2): los episodios de El Jambo que sabe "
    "(slug con 'jambo', guion con set 'salon') son sitcom de barrio de 45-70 s. Los límites de 20, 25, 30 o 35 s de las órdenes "
    "del 13/11 y 15/11 y el Jambo de oficina de 15-25 s están DERROGADOS: nunca rechaces un episodio de 45-70 s por duración, "
    "y las lecciones antiguas de 502-515 que citan 20 s no valen. El plano de casa «Cosas de Casa» con gancho de texto ≤ 8 palabras "
    "(p. ej. «Esta casa del barrio tiene truco») es la INTRO OBLIGATORIA del episodio, y el último plano debe repetir exactamente ese "
    "mismo plano (bucle): que apertura y cierre sean iguales es lo correcto, no un gancho ajeno. Evalúa además (orden del dueño 22/11): "
    "todos hablan con vocabulario vulgar/choni de barrio y tacos comunes; Neo es el ÚNICO culto y habla con respeto; los demás MUY mal hablados y muy vulgares (no un taco suelto), Felipe Lotas como cuñado enterado y Jambo Reseco como gorrón caradura (orden del dueño 22/11 noche); humor negro "
    "real; Jambo Reseco presente cuando toque; giro de Neo, moraleja y recuerdo. «illo», «pa» y los tacos que Whisper no transcribe "
    "NO son error de voz. El listón de 90 se mantiene. Cierre fijo del post: «Pide tu prueba gratuita: sin tarjeta, sin datos "
    "bancarios y sin compromiso»; prohibido cualquier embudo («comenta X y te envío»). Repo vivo: Deisputnik/neogestlab-redes."
)


# 23/11/2026 (orden del dueño: «no quiero fallos ni embudos», «arregla todo»): Calidad rechazaba en falso por la marca.
# 518 (70), 801 (58) y 802 (70) se tumbaron por «logo antiguo» cuando llevan EXACTAMENTE la misma insignia y la misma
# tarjeta de cierre que 517, 519, 107 y 108, aprobadas con 91-93 (comprobado fotograma a fotograma). Lo que el modelo
# llamaba «recuadro oscuro NEOGESTLAB antiguo» es el logo oficial 2026. Este bloque y la imagen de referencia
# (equipo/perfil_kit/logo_neogest_lab_oficial.png, que se adjunta con los fotogramas) fijan qué es válido.
MARCA_VIGENTE = (
    "MARCA Y CIERRE VIGENTES (manda sobre lo que leas abajo si choca; DIRECTIVA §4 y §5). LOGO OFICIAL 2026 = recuadro oscuro de "
    "esquinas redondeadas con la «N» hecha de pistas de circuito (azul-turquesa con nodos verdes) encima del rótulo «NEOGESTLAB» "
    "(«NEOGEST» en blanco, «LAB» en turquesa) y, debajo, el lema pequeño «Sistemas Digitales, Automatización e IA a Medida». "
    "Ese conjunto completo ES el logo nuevo y es CORRECTO en sus dos usos: como insignia pequeña arriba a la derecha en todos los "
    "planos, y como tarjeta central del cierre. El isotipo «N» de circuitos puede ir solo o con el rótulo y el lema: las dos formas "
    "cumplen el bloqueo 11. Nunca lo llames «logo antiguo», «recuadro antiguo» ni «cuadrado NEOGESTLAB antiguo». EL ÚNICO LOGO "
    "PROHIBIDO (bloqueo 10) son las letras «NL» en neón, SIN la N de circuitos. Con los fotogramas recibes una imagen de referencia "
    "del logo oficial: compara con ella; si lo que ves coincide, la marca está bien. "
    "TARJETA DE CIERRE del vídeo (DIRECTIVA §5): plano estático de hasta 3 s con el logo 2026, «By Neogest Lab» y el botón «Enlace en "
    "el perfil» (nunca una URL en pantalla). Esa tarjeta es la plantilla vigente: no la rechaces por no llevar escrita la frase de "
    "prueba gratuita; el cierre fijo («Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso», o «Solicita "
    "información gratuita…» en Recepcionista 24h) se exige en el TEXTO del post y suele ir además en el plano anterior a la tarjeta. "
    "RECREACIONES (Recepcionista 24h): el rótulo «Recreación · voces sintéticas» se exige mientras suena la llamada recreada (las voces "
    "del asistente y de quien llama), no en la locución del narrador que la presenta o la cierra. Ves pocos fotogramas sueltos: solo "
    "puedes rechazar por el rótulo si falta en un fotograma en el que claramente se está dentro de la llamada. "
    "COHERENCIA: no rechaces por marca o por cierre una pieza que lleva la misma insignia y la misma tarjeta que otras ya aprobadas."
)


def _lecciones_vigentes():
    """lecciones_calidad.md se genera sola con todos los motivos pasados: se quitan los de duración derogados (20/25/30 s)."""
    txt = _leer(LECCIONES) or ""
    return "\n".join(l for l in txt.split("\n")
                     if not re.search(r"supera los 20 s|más del doble del límite de 20 s|margen de 35 s|15-25 s", l))

def _sistema():
    return (
        "Eres el rol CALIDAD del equipo de redes de Neogest Lab, ejecutado vía API directa "
        "(piloto de créditos, ver cabecera de herramientas/calidad_api.py). Sigue el criterio "
        "de los archivos de abajo. Evalúas UNA pieza por turno de usuario: usa la herramienta "
        "`inspeccionar_video` para ver el vídeo (ffprobe, silencios, LUFS/pico y 7 fotogramas, el último es el cierre) "
        "y después `escribir_calidad` con tu veredicto final (aprobado solo con nota >= 90). "
        "No tienes acceso a hechos_verificados/prohibido_afirmar de Base44 en este piloto: para "
        "reels de apps, contrasta solo con las fuentes que el propio post.json ya cita "
        "(_fuentes/_comprobado); si una cifra o afirmación no tiene fuente citada y no puedes "
        "verificarla, trátala como no verificada (no la aprueba el estándar v9/A3) y dilo en "
        "los motivos, no inventes ni la des por buena. Sé estricto: el mínimo real para publicar "
        "es 90, y si 'suena a IA' el máximo es 89. No relances ciclo.yml ni muevas 'cuando': "
        "eso lo decide otra pasada.\n\n" + FORMATO_VIGENTE + "\n\n" + MARCA_VIGENTE
        + "\n\n--- equipo/roles/calidad.md ---\n" + _leer(ROL)
        + "\n\n--- equipo/estandar_calidad.md ---\n" + _leer(ESTANDAR)
        + "\n\n--- equipo/lecciones_calidad.md (motivos de rechazo repetidos) ---\n" + _lecciones_vigentes()
    )


def _linea_tablon(resultados, sin_render_n, al_dia_n):
    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not resultados:
        return (f"{ahora} · Calidad (API) · pasada sin piezas pendientes de evaluar "
                f"({al_dia_n} al día, {sin_render_n} sin render todavía) · nada")
    partes = []
    for r in resultados:
        if r["escrito"]:
            estado = f"aprobada ({r['nota']})" if r["aprobado"] else f"rechazada ({r.get('nota')})"
            partes.append(f"{r['pid']} {estado}: {r['resumen']}")
        else:
            partes.append(f"{r['pid']} SIN calidad.json nuevo ({r['resumen'] or 'sin resumen'})")
    cuerpo = " · ".join(partes)
    return (f"{ahora} · Calidad (API) · evaluadas {len(resultados)} piezas: {cuerpo} · "
            f"Creador/Remasterizador: ver motivos arriba; necesito: nada del dueño")


def main():
    try:
        import anthropic
    except ImportError:
        print("Falta el paquete anthropic (pip install anthropic)", file=sys.stderr)
        sys.exit(1)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Falta ANTHROPIC_API_KEY en el entorno", file=sys.stderr)
        sys.exit(1)

    pendientes, al_dia, sin_render = piezas_pendientes()
    resultados = []
    if pendientes:
        cliente = anthropic.Anthropic(api_key=api_key)
        sistema = _sistema()
        for pid in pendientes[:MAX_PIEZAS]:
            try:
                resultados.append(evaluar_pieza(cliente, sistema, pid))
            except Exception as e:
                resultados.append({"pid": pid, "escrito": False, "resumen": f"error: {e}"})

    if not resultados and os.environ.get("CALIDAD_SILENCIOSA"):
        # 21/11/2026: las pasadas horarias que lanza el reloj no ensucian el tablón cuando no hay nada que evaluar
        print(f"Calidad (API): nada pendiente ({len(al_dia)} al día, {len(sin_render)} sin render)")
        return
    linea = _linea_tablon(resultados, len(sin_render), len(al_dia))
    with open(TABLON, "a", encoding="utf-8") as f:
        f.write(linea + "\n")
    print(linea)


if __name__ == "__main__":
    main()
