#!/usr/bin/env python3
"""Guionista de El Jambo que sabe vía API de Gemini (orden del dueño, 17/11/2026).

Motivo: el dueño ha visto lo publicado y los guiones no engachan ("no tiene sentido").
Hasta ahora el Creador escribía el guion él mismo (Sonnet) dentro de su pasada. Este script
pide los guiones a Gemini como un paso aparte, ANTES de cada pasada del Creador (09:51 y
15:51 Madrid), apoyándose en la biblia de la serie, los motivos de rechazo de Calidad y los
patrones de reels virales ya estudiados, para que lleguen con más gancho y lógica.

No sustituye al Creador: deja borradores en equipo/guiones_gemini/pendientes/ y es el
Creador quien elige, ajusta (decorado, hora, clip de la Biblioteca) y pone en cola/. Si
Gemini falla o no hay clave, no rompe nada: el Creador sigue pudiendo escribir el guion él
mismo como hasta ahora.

Variable de entorno: GEMINI_API_KEY (secreto del repo; cuenta darbish, capa gratis de
Google AI Studio). Uso: python3 herramientas/guionista_gemini.py [n_guiones]
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
BIBLIA = os.path.join(RAIZ, "equipo", "serie_jambo.md")
LECCIONES = os.path.join(RAIZ, "equipo", "lecciones_calidad.md")
VIRALES = os.path.join(RAIZ, "equipo", "virales_semana.md")
TABLON = os.path.join(RAIZ, "equipo", "tablon.md")
NOTICIAS = os.path.join(RAIZ, "equipo", "noticias_semana.md")   # lo mantiene el Cazador (27/11/2026); opcional
ESTADISTICAS = os.path.join(RAIZ, "estadisticas.json")
COLA = os.path.join(RAIZ, "cola")
PENDIENTES = os.path.join(RAIZ, "equipo", "guiones_gemini", "pendientes")

# Lista de modelos a probar en orden (el primero que responda gana). gemini-2.0-flash dejó
# de estar disponible el 17/11/2026; comprobado ese día con herramientas/gemini_modelos.py
# qué acepta generateContent la clave real. gemini-3.8-flash y gemini-flash-latest dieron 503
# (saturados) y gemini-2.5-flash/gemini-2.5-flash-lite dieron 404 "no disponible para cuentas
# nuevas" con esta clave: se dejan de últimos por si cambia. Lista larga a propósito para
# aguantar baches de saturación sin dejar de producir guiones.
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
N_POR_DEFECTO = 4   # 2 pasadas al día x 4 = hasta 8 borradores para cubrir 5 episodios diarios tras el filtro del validador
# 21/11/2026 (orden del dueño): Jambo Reseco vuelve al reparto del formato de barrio/salon
# (tio chungo, de poca confianza, mal hablado) - ver equipo/serie_jambo.md.
PERSONAJES_VALIDOS = {"rosa", "felipe", "sindy", "neo", "cliente", "conchaqueton", "jambo"}
ESTILOS_VALIDOS = {"gancho", "gag", "remate", "cierre"}
# 19/11/2026: rechazo mecánico de lo que más se parece a "declaración de postura" en vez de
# una frase hablada con golpe cómico (el fallo real que el dueño señaló). No es perfecto
# (no distingue una frase larga pero graciosa), pero descarta el patrón más repetido.
PATRON_ARGUMENTO = re.compile(
    r"\b(no debería|debería|no tiene por qué|no tendría que|tendría que|no debe|"
    r"es (un|una) (derecho|obligación|falta de respeto)|eso (no )?es justo)\b",
    re.IGNORECASE,
)
MAX_PALABRAS_GAG = 14   # 26/11/2026 (orden del dueño, opción b): 18 → 14; réplicas largas = más fallos de dicción de la voz diseñada
MAX_PALABRAS_REMATE, MAX_PALABRAS_JAMBO = 20, 10
# 26/11/2026: palabras que la voz diseñada (Gemini TTS) dice mal y que Calidad rechaza por control_audio (equipo/voz_palabras_dificiles.json)
try:
    _VPD = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "equipo", "voz_palabras_dificiles.json"), encoding="utf-8"))
    PALABRAS_DIFICILES = list((_VPD.get("palabras") or {}).keys())
except Exception:
    PALABRAS_DIFICILES = []
# 23/11/2026 (orden del dueño: «haz que mejore el guionista y las expresiones de voz»). El guion pedía 3 golpes de 14
# palabras (unas 70 palabras: 30 s) para un episodio de 45-70 s, y el validador exigía «exactamente 3» mientras el prompt
# permitía 4: el Creador tenía que reescribir cada guion para alargarlo y muchos se rechazaban por contradicción.
# Formato vigente (v11): gancho + 5-8 golpes + remate de Neo + cierre, 120-185 palabras de voz, con Jambo en escena y
# una emoción de voz por réplica ("emo"), que gen_episodios.py convierte en entonación.
MIN_GAGS, MAX_GAGS = 5, 8
MIN_PALABRAS_VOZ, MAX_PALABRAS_VOZ = 100, 170   # 26/11: mínimo 105 → 100 al acortar las réplicas   # 170 (antes 185): desde el 23/11 hay 3 s de promo de empresa antes del plano final
# Estancias para guiones NUEVOS: los cuatro decorados con profundidad del 27/11/2026 (salon2, cocina2, portal, terraza) y los que no tienen
# sustituto (dormitorio, bar, calle). «salon» y «cocina» (antiguos) solo siguen valiendo en gen_episodios.py para los guiones ya escritos.
ESTANCIAS = {"salon2", "cocina2", "portal", "terraza", "dormitorio", "bar", "calle"}
REPARTO_FIJO = ("rosa", "felipe", "sindy", "jambo", "neo")   # 27/11/2026: todos aportan algo en cada episodio (apartado K)
AMBITOS = {"casa", "familia", "compras", "salud_y_citas", "dinero_de_casa", "ocio_y_viajes", "barrio", "trabajo"}   # apartado J (27/11/2026)
ACCIONES = {"habla", "desespera", "delega", "presume", "fria"}   # gen_episodios.py ACCION_A_EMO / EXPR
EMOCIONES = {"normal", "grita", "enfado", "sorpresa", "ironia", "chulea", "cansado", "susurra", "miedo", "llora", "rie", "seco", "pregunta"}


def _leer(ruta, lineas=None):
    if not os.path.exists(ruta):
        return ""
    with open(ruta, encoding="utf-8") as f:
        txt = f.read()
    if lineas:
        return "\n".join(txt.splitlines()[-lineas:])
    return txt


def _temas_recientes():
    """Slugs/temas ya en cola o publicados recientemente, para que Gemini no repita
    situación (ahorra una ronda de rechazo por duplicado)."""
    temas = []
    for carpeta in ("cola", "publicados", "revision"):
        ruta = os.path.join(RAIZ, carpeta)
        if os.path.isdir(ruta):
            temas.extend(sorted(os.listdir(ruta))[-15:])
    return temas


def _coletillas_recientes(max_por_carpeta=15, tope=40):
    """27/11/2026: coletillas que ya han usado los episodios recientes (campo «coletillas_nuevas» de cada guion en pendientes/, usados/,
    cola/ y publicados/), para que Gemini no las repita. Sin ninguna todavía devuelve texto vacío y no pasa nada."""
    vistas = []
    carpetas = [(PENDIENTES, None), (os.path.join(os.path.dirname(PENDIENTES), "usados"), None),
                (COLA, "guion.json"), (os.path.join(RAIZ, "publicados"), "guion.json")]
    for base, nombre in carpetas:
        if not os.path.isdir(base):
            continue
        rutas = []
        for x in sorted(os.listdir(base))[-max_por_carpeta:]:
            ruta = os.path.join(base, x)
            if nombre and os.path.isdir(ruta):
                ruta = os.path.join(ruta, nombre)
            if ruta.endswith(".json") and os.path.isfile(ruta):
                rutas.append(ruta)
        for ruta in rutas:
            try:
                col = json.load(open(ruta, encoding="utf-8")).get("coletillas_nuevas")
            except Exception:
                continue
            if isinstance(col, dict):
                for quien, frase in col.items():
                    if isinstance(frase, str) and frase.strip():
                        item = f"{quien}: «{frase.strip()}»"
                        if item not in vistas:
                            vistas.append(item)
    return "; ".join(vistas[-tope:]) or "(ninguna todavía: esta es la primera tanda, todas valen)"


def _memoria(max_n=14):
    """27/11/2026 (orden del dueño: «tienen memoria en los episodios de lo que les pasó en veces anteriores»): qué pasó en los últimos
    episodios de El Jambo (publicados/ y cola/), para que los personajes lo recuerden. Sale de los propios guion.json."""
    lineas = []
    for base in (os.path.join(RAIZ, "publicados"), COLA):
        if not os.path.isdir(base):
            continue
        for x in sorted(os.listdir(base)):
            if "jambo" not in x:
                continue
            try:
                g = json.load(open(os.path.join(base, x, "guion.json"), encoding="utf-8"))
            except Exception:
                continue
            que = g.get("resumen") or " → ".join(str(g.get(k)) for k in ("promesa", "giro") if g.get(k))
            if not que:
                continue
            quienes = sorted({e.get("h") for e in (g.get("escenas") or []) if isinstance(e, dict) and e.get("h")})
            lineas.append(f"- {x[:3]} · {que} · quedó claro que: {g.get('moraleja') or '—'} · salían: {', '.join(quienes) or '—'}")
    return "\n".join(lineas[-max_n:]) or "(todavía no hay episodios anteriores que recordar)"


def _rendimiento(max_n=5):
    """27/11/2026 (orden del dueño: «sabiendo antes qué ha funcionado y el porqué»): mejores y peores vídeos propios según estadisticas.json."""
    try:
        posts = json.load(open(ESTADISTICAS, encoding="utf-8")).get("posts") or []
    except Exception:
        return "(sin datos propios todavía)"
    filas = []
    for p in posts:
        m = p.get("metricas") or {}
        if not m.get("views"):
            continue
        filas.append((m.get("views", 0), round((m.get("ig_reels_avg_watch_time") or 0) / 1000, 1), m.get("shares", 0), m.get("saved", 0),
                      " ".join(str(p.get("caption") or "").split())[:90]))
    if len(filas) < 4:
        return "(sin datos propios suficientes todavía)"
    def fmt(f):
        return f"  · {f[0]} vistas, {f[1]} s vistos de media, {f[2]} compartidos, {f[3]} guardados · «{f[4]}»"
    por_vistas = sorted(filas, reverse=True); por_tiempo = sorted(filas, key=lambda f: -f[1])
    return ("LOS QUE MÁS SE VIERON:\n" + "\n".join(fmt(f) for f in por_vistas[:max_n]) +
            "\nLOS QUE MÁS RATO SE QUEDÓ LA GENTE:\n" + "\n".join(fmt(f) for f in por_tiempo[:3]) +
            "\nLOS QUE MENOS FUNCIONARON:\n" + "\n".join(fmt(f) for f in por_vistas[-3:]))


_NOTICIAS_CACHE = []


def _noticias():
    """27/11/2026 (orden del dueño: «que el guionista busque noticias»): titulares de vida cotidiana para adaptar. Dos fuentes, las dos
    opcionales: equipo/noticias_semana.md (lo mantiene el Cazador) y una búsqueda de Gemini con Google Search. Si algo falla, texto vacío:
    este paso nunca bloquea al Guionista."""
    if _NOTICIAS_CACHE:
        return _NOTICIAS_CACHE[0]
    partes = []
    arch = _leer(NOTICIAS, lineas=30)
    if arch.strip():
        partes.append(arch.strip())
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        body = {"contents": [{"parts": [{"text": (
                    "Busca noticias de ESPAÑA de los últimos 7 días sobre la vida cotidiana de la gente corriente (precios de la compra, luz, "
                    "alquiler, citas médicas, colegios, transporte, móviles, estafas por mensaje, trámites, inteligencia artificial en casa, "
                    "vecinos, vacaciones). Nada de política de partidos, sucesos, tragedias ni famosos. Devuelve 8 líneas, una por noticia: "
                    "«fecha · qué ha pasado en una frase · por qué le toca a cualquiera en su casa». Solo hechos que hayas encontrado.")}]}],
                "tools": [{"google_search": {}}], "generationConfig": {"temperature": 1.0}}
        for modelo in MODELOS[:2]:
            try:
                data = _llamar_un_modelo(modelo, api_key, body)
                txt = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"]).strip()
                if txt:
                    partes.append(txt[:1800]); print(f"Noticias buscadas con {modelo} ({len(txt)} caracteres)"); break
            except Exception as e:   # sin búsqueda en el plan gratuito, modelo sin la herramienta, red…: se sigue sin noticias
                print(f"Noticias: {modelo} no ha podido buscar ({type(e).__name__}: {str(e)[:120]})")
    _NOTICIAS_CACHE.append("\n".join(partes) or "(sin noticias esta vez: tira de situaciones cotidianas de siempre)")
    return _NOTICIAS_CACHE[0]


def _prompt(n):
    coletillas = _coletillas_recientes()
    memoria = _memoria(); rendimiento = _rendimiento(); noticias = _noticias(); estancias = ", ".join(sorted(ESTANCIAS))
    biblia = _leer(BIBLIA)
    lecciones = _leer(LECCIONES, lineas=25)
    virales = _leer(VIRALES, lineas=60)
    temas = ", ".join(_temas_recientes()) or "(ninguno todavía)"

    esquema = {
        "slug": "texto-corto-sin-espacios, 2-4 palabras, nueva situación",
        "set": "estancia donde EMPIEZA el episodio: salon2 (el salón, por defecto) | cocina2 (la cocina) | portal (el portal del bloque, con buzones y escalera) | terraza (la terraza o azotea) | dormitorio | bar | calle",
        "hora": "entero 0-23 (hora del día de la escena)",
        "moraleja": "6-9 palabras, tono serio, el mensaje que se queda; si hay una cifra de la tabla de la biblia que encaje, inclúyela",
        "recuerdo": "6-12 palabras, una línea que conecta con un episodio anterior ya publicado (de los temas ya usados) — un personaje menciona o reacciona a algo que pasó en otro capítulo; null si no hay ninguno con el que conectar todavía",
        "bucle_visual": "CAMPO OBLIGATORIO, no lo omitas: 4-10 palabras describiendo qué pose, plano o elemento visual del gancho (escena 'e':'gancho') se repite igual en el cierre, para que el vídeo se pueda ver en bucle sin notar el corte entre el final y el siguiente visionado (p.ej. 'Rosa con el móvil en la mano, misma postura'; 'la taza de café a medio llenar en primer plano'). Describe la imagen, no la moraleja ni el texto.",
        "gancho_tipo": "conflicto_en_marcha | afirmacion_imposible | amenaza_con_plazo | pregunta_abierta (ver F1)",
        "promesa": "5-10 palabras: la pregunta que abre el gancho y que el espectador necesita ver resuelta; solo se responde en el remate",
        "giro": "6-14 palabras: qué creía el espectador y qué resulta ser en el golpe marcado con giro:true",
        "marca": "true en 1 de cada 3 guiones (un personaje nombra a Neogest Lab UNA vez, apartado M); false en el resto",
        "nombre_completo_dicho": "rosa | felipe | sindy | conchaqueton | jambo: a quién llaman por su nombre y apellido en este episodio (apartado K4)",
        "por_que_funcionara": "1 frase: qué patrón de los datos propios, de los virales o de las noticias aplica este guion (apartado O)",
        "ambito": "casa | familia | compras | salud_y_citas | dinero_de_casa | ocio_y_viajes | barrio | trabajo (apartado J: como mucho 1 de cada 4 guiones es de trabajo)",
        "chiste_base": "1 frase (8-30 palabras): el chiste o la situación de humor ACTUAL que adaptas en este episodio, como planteamiento → remate (apartado I)",
        "resumen": "1 frase (10-28 palabras) que entendería un niño de doce años: quién quiere qué, qué lo impide y cómo acaba (apartado I5)",
        "coletillas_nuevas": {"jambo": "coletilla NUEVA y graciosa de Jambo (≤ 6 palabras) que dice en este episodio", "rosa": "coletilla nueva de Rosa", "felipe": "coletilla nueva de Felipe", "sindy": "coletilla nueva de Sindy (opcional: un personaje más si encaja)"},
        "escenas": [
            {
                "e": "gancho",
                "h": "rosa",
                "emo": "sorpresa",
                "t": "texto exacto que dice o el texto en pantalla, máx 8 palabras, situación reconocible desde el fotograma 0 (visible en los primeros 0,5 s, antes incluso de que se lea el texto entero); dirígete a otro personaje por su nombre si tiene sentido",
                "p": ["rosa", "felipe"],
                "plano": "general",
            },
            {"e": "gag", "h": "felipe|sindy|jambo|conchaqueton", "emo": "enfado", "t": "golpe 1 de la escalada (máx 14 palabras, en frases de 3-8 palabras separadas por punto), registro de barrio con réplica inteligente, nombrando a quien se dirige", "risas": "true solo si este golpe es de verdad el más fuerte del episodio, si no omite el campo"},
            {"e": "gag", "h": "rosa", "emo": "ironia", "set": "cocina2", "p": ["rosa", "sindy"], "t": "golpe 2, peor que el 1, ya en OTRA estancia y con otro grupo (apartado N): aquí se trama lo que en el salón no saben"},
            {"e": "gag", "h": "jambo", "emo": "cansado", "p": ["jambo"], "plano": "primerplano", "t": "golpe 3: Jambo Reseco se mete y lo empeora (gorrón caradura, pícaro del sur relajadísimo, frases cortas y claras en ortografía normal, con una coletilla NUEVA suya: «Rosa, guapa… eso se arregla solo. Fíame cinco euros y me callo.»)"},
            {"e": "gag", "h": "felipe", "emo": "chulea", "giro": True, "t": "golpe 4 = EL GIRO (lleva giro:true, uno solo por episodio, del golpe 3 al penúltimo): da la vuelta a lo que se creía, con algo sembrado antes; aquí además Felipe sentencia algo falso (cuñado enterado)"},
            {"e": "gag", "h": "sindy|rosa", "emo": "grita", "t": "golpe 5, el peor; puedes llegar hasta 8 golpes; el último remata con 'Que lo resuelva el Neo' (lo dice Felipe o Sindy)"},
            {"e": "remate", "h": "neo", "emo": "seco", "p": ["neo", "rosa"], "plano": "primerplano", "t": "remate (máx 20 palabras): Neo responde a la PROMESA con algo concreto (cifra, objeto, nombre), recoge una palabra u objeto del gancho y deja a Rosa en evidencia, nombrándola"},
            {"e": "cierre", "h": "neo", "t": "texto en pantalla, debe coincidir o repetir la moraleja (el bucle con la tarjeta 'Cosas de Casa' ya lo resuelve el código, no hace falta pensarlo aquí)"},
        ],
    }

    return f"""Eres el guionista de la serie de humor "El Jambo que sabe" (Instagram @neogestlab,
Neogest Lab). Español de España, humor negro de lo cotidiano: los líos de una casa de barrio que resuelve una
inteligencia artificial, NUNCA contra personas reales ni colectivos.
PRIORIDAD: los apartados G a O del final (órdenes del dueño del 27/11/2026) y la biblia v5.3 MANDAN sobre cualquier regla o
ejemplo anterior de este texto que hable de oficina, jefa y empleados, papeleo, créditos de reparto o voz arrastrada. Escribe {n} guiones de
episodio NUEVOS, cada uno con un conflicto y una situación distintos entre sí y distintos de
los temas ya usados: {temas}.

BIBLIA DE LA SERIE (personajes, tono, estructura, cifras verificadas que puedes citar si
encajan de verdad; no inventes cifras nuevas):
---
{biblia}
---

ORDEN DEL DUEÑO 21/11 MADRUGADA (tras ver el piloto v3, se suma a todo lo de arriba y manda
sobre cualquier instrucción anterior que lo contradiga):
1. ESCENARIO: una casa de barrio y su entorno (apartado N). "set" por defecto = "salon2".
2. TEMAS: los del apartado J (casa y vida cotidiana; como mucho un guion de trabajo por tanda).
3. COTIDIANO Y QUE EMPATICE: la situación tiene que ser algo que cualquiera reconozca de su
   propio día a día. Apóyate en estadísticas reales de la tabla de la biblia cuando encajen de
   verdad, y no tengas miedo de tocar temas sociales (no solo laborales) siempre dentro de las
   líneas rojas de siempre.
4. APPS DE IA QUE NO SIEMPRE SON BUENA IDEA: de vez en cuando, el conflicto puede nacer de que
   algún personaje usa o se inventa una aplicación de IA (SIEMPRE genérica y ficticia, nunca una
   aplicación real de Neogest Lab ni de terceros, nunca una marca ajena; el nombre de la empresa Neogest Lab sí puede salir como dice el apartado M) cuya idea no
   sale bien — hasta que llega Neo y la resuelve de verdad. Es una fuente más de situaciones,
   no la única.
5. REGISTRO MÁS PALETO Y VULGAR, CON ÉNFASIS: dentro de las líneas rojas de siempre, no
   suavices el lenguaje de Rosa, Felipe, Sindy y Concha Quetón — pueden soltar tacos comunes
   del español de España (joder, coño, hostia, cojones, manda huevos) y modismos de barrio
   reforzados ("illo") cuando encajen con la réplica. Estas palabras van SIEMPRE entre signos
   de exclamación ("¡illo!", "¡joder!", "¡manda huevos!"), nunca sueltas en medio de la frase
   sin marcar, para que edge-tts las lea con énfasis. Esto es registro de habla, no cambia el
   fondo del humor negro. Neo NUNCA dice tacos ni "illo": sigue siempre correcto y neutro.

MOTIVOS DE RECHAZO MÁS REPETIDOS por el equipo de Calidad en las últimas piezas (evítalos
todos; son la razón por la que el dueño ha pedido este cambio, dice que "los guiones no
engachan, no tiene sentido"):
---
{lecciones}
---

PATRONES DE REELS VIRALES ya estudiados en el nicho (cópialos en estructura, nunca en
contenido ni frases literales):
---
{virales}
---

AVISO DE CALIDAD REAL (esto es lo que el dueño está señalando ahora mismo, 19/11: "tienen
que ser de gran calidad"): el validador automático solo comprueba la FORMA (número de
escenas, personajes válidos, longitud de la moraleja); nunca ha comprobado si el chiste
funciona, así que no te confíes de que "pasa" signifique que es bueno. El fallo que más se
repite en los borradores recientes es que cada "gag" es una DECLARACIÓN DE POSTURA (alguien
defendiendo una opinión, tipo debate o panfleto: "el compromiso familiar no debería tener
precio alguno") en vez de una REACCIÓN HABLADA natural con timing cómico. Eso no hace reír.
  MAL (declaración, prohibido): "El compromiso familiar no debería tener precio alguno."
  BIEN (reacción con golpe): "Ya puestos, tráete también a mi suegra, que así hacemos piña."
Cada gag debe sonar a algo que alguien realmente suelta en voz alta al oír la frase
anterior (ironía, sarcasmo, la consecuencia absurda llevada un paso más lejos), nunca a un
argumento razonado. Si al leerlo en voz alta suena a artículo de opinión, está mal escrito:
reescríbelo como lo diría una persona enfadada o resignada en ese momento.

QUÉ ES REALMENTE HUMOR NEGRO (orden del dueño, 20/11: "no lo he visto en ningún momento";
tiene razón, lo que se ha escrito hasta ahora es ironía y sarcasmo de oficina, no humor
negro). La diferencia no es de TEMA, es de TONO: el sarcasmo se queja de lo injusto con
gracia (indignación disfrazada de chiste); el humor negro trata lo injusto o lo cruel con
la misma frialdad y naturalidad con que se trataría algo trivial, sin indignarse ni
suavizarlo — la gracia está en esa distancia fría, no en la queja. Las líneas rojas de la
biblia siguen mandando (nunca suicidio, autolesión, enfermedad o muerte real, ni contra
personas o colectivos reales): el humor negro aquí no viene de tocar esos temas, viene del
FATALISMO, la resignación sin drama y la crueldad del sistema contada como lo más normal
del mundo.
  MAL (esto es sarcasmo, no humor negro — es lo que lleva saliendo hasta ahora): "Ya puestos,
  tráete también a mi suegra, que así hacemos piña." (el personaje se indigna con gracia;
  sigue siendo una queja, solo que ingeniosa).
  BIEN (humor negro real: frialdad total ante algo injusto, dicho sin ninguna sorpresa ni
  indignación, como un hecho ya asumido): "Si me despiden mañana, lo único que cambia es que
  dejo de fingir que me importa." / "Lo normal es que esto salga mal. Lleva así tres años, no
  es nada nuevo."
Pista rápida para saber si un gag es de verdad humor negro: léelo en voz alta con cara de
póker, sin ánimo de queja. Si solo funciona gritado o indignado, es sarcasmo (válido, pero
no es lo que se pide ahora); si funciona dicho en plano, con total indiferencia, es humor
negro. Al menos uno de los tres golpes de cada episodio debe ser de este segundo tipo.
REFUERZO (el dueño vio un episodio ya escrito con esta guía y dijo que seguía sin ver nada
negro, "demasiado blanco"): dos trucos que SÍ dan humor negro real, úsalos como plantilla:
(1) coger un evento personal importante de un personaje (una boda, un entierro, un hijo con
problemas de salud sin nombrar cuál) y tratarlo con la misma frialdad administrativa que una
incidencia de nómina — "Rosa, el sábado me caso. ¿La luna de miel la cuento de horas extra o
de falta injustificada?"; (2) convertir una injusticia real (no cobrar, pasar frío, un abuso)
en una broma que la acepta como normal en vez de protestar por ella — "Marzo lo sigo sin
cobrar. Pero tranquila, que aquí el frío nos iguala a todos." Prueba final antes de dar un
golpe por bueno: quítale la gracia mentalmente — si lo que queda incomoda de verdad, es humor
negro; si lo que queda es solo una queja normal, es sarcasmo blanco y hay que subirlo de tono.
Dato real de rendimiento (virales_semana.md, visto el 16/11): lo que mejor ha funcionado en
la cuenta hasta ahora son los episodios de cliente/jefe con una situación reconocible desde
la primera línea y, sobre todo, los que tienen "Parte 2" (continuidad: alguien pregunta
"¿y qué pasó con...?" y el episodio responde). Los temas de oficina genéricos sin ese gancho
reconocible son los que menos vistas sacan. Cuando puedas, prefiere una situación que un
espectador reconozca de inmediato por haberla vivido, y considera si el conflicto de hoy
podría tener una "Parte 2" natural para otro episodio (dilo en el slug con "_parte2" si es
la continuación de un tema ya usado: {temas}).

GANCHO DE MEDIO SEGUNDO Y VÍDEO EN BUCLE (orden del dueño, 20/11, "vídeos completamente
adictivos"): no basta con que el gancho tenga ≤ 8 palabras, tiene que entenderse la situación
SOLO con la imagen en los primeros 0,5 s, antes de que el espectador llegue a leer el texto
completo o a procesar el audio — el texto confirma lo que la imagen ya contaba. Además, el
episodio tiene que poder reproducirse en bucle sin que se note el corte entre el cierre y el
siguiente visionado: el último fotograma (cierre/moraleja) debe volver a la misma pose, plano
o elemento visual del gancho (campo "bucle_visual" del esquema), para que quien lo ve una vez
no se canse al verlo dos o tres veces seguidas — eso es lo que más sube el tiempo visto medio
(objetivo > 60 % de la duración, aprendizajes.md).

BUCLE DE RETENCIÓN (orden del dueño, 20/11: el mismo bucle de dopamina que usan los casinos
para que no puedas dejar de mirar la mesa). Cada episodio tiene que montarse sobre estos 4
pasos, no solo cumplir el recuento de escenas:
1. APUESTAS: el gancho tiene que dejar claro qué pierde Felipe o Sindy si esto sale mal.
   Sin algo en juego que duela de verdad, no hay tensión y el episodio no engancha aunque
   la forma esté bien.
2. PREGUNTA: el planteamiento y el primer golpe tienen que dejar al espectador con una duda
   activa ("¿y ahora cómo sale de esto?"), no solo informarle de la situación. Si al leerlo
   se entiende todo de golpe sin ninguna curiosidad pendiente, está mal escrito.
3. GIRO: Neo tiene que resolver con algo que sorprenda, no con el desenlace que ya se veía
   venir desde el golpe 2. Si el giro es previsible, el episodio no vale aunque pase el
   validador.
4. REENGANCHE: el cierre no puede dejar la tensión completamente en reposo. La moraleja y la
   pregunta final de la pieza son ese reenganche: dejan una curiosidad abierta (la parte 2,
   u otra pregunta) antes de que el espectador suelte del todo el episodio anterior.

Reglas duras (si no las cumples, el episodio se rechaza):
1. Gancho en pantalla desde el fotograma 0, máximo 8 palabras, una situación reconocible
   (no una explicación) que deje clara la apuesta (paso 1 del bucle). Debe leerse y
   entenderse sin sonido.
2. Escalada de exactamente 3 golpes, cada uno con MÁS lógica y PEOR consecuencia que el
   anterior, manteniendo viva la pregunta del paso 2 del bucle; nunca una frase suelta sin
   relación con el golpe de antes; y nunca una frase que suene a declaración de postura o
   argumento razonado (ver AVISO DE CALIDAD arriba): cada golpe es algo que se dice en
   caliente, con ironía o sarcasmo, no un alegato.
3. El giro lo resuelve Neo y responde exactamente al conflicto planteado, no a otro, con un
   desenlace que sorprenda (paso 3 del bucle: nunca el final más obvio); deja a Rosa en
   evidencia sin alterarse. La frase de Neo también debe sonar hablada, no un comunicado:
   evita el patrón repetitivo "He [verbo] el/la [trámite]" en todos los episodios de la
   misma tanda; varía cómo lo cuenta Neo.
4. Moraleja obligatoria de 6-9 palabras, tono serio, que se entienda sola si alguien la lee
   guardada sin ver el vídeo, y que funcione como reenganche (paso 4 del bucle): no cierra
   la curiosidad del todo, apunta a la parte 2 o deja una pregunta.
5. Nunca Rosa dice la moraleja ni "Que lo resuelva el Neo" (eso lo dicen Felipe o Sindy,
   justo antes del giro, solo una vez).
6. Cifras siempre en letra, cero palabras en inglés, ningún nombre propio como primera
   palabra de una frase.
6 bis. VOZ QUE SE ENTIENDA (26/11/2026, orden del dueño): las réplicas se dicen con una voz sintética
   y se comprueban con un transcriptor; si una palabra se oye mal, el episodio se rechaza. Por eso:
   frases de 3 a 8 palabras separadas por punto; golpes de 14 palabras como mucho, remate de 20,
   Jambo 10; palabras corrientes, nada de diminutivos inventados ni palabras raras largas; nada de
   imperativos con pronombre pegado («devuélvala») ni «señora/señor» delante del nombre. PROHIBIDAS
   (la voz las dice mal): {', '.join(PALABRAS_DIFICILES)}.
7. Prohibido: suicidio, autolesión, enfermedades o muertes reales, víctimas, política de
   partido, colectivos, marcas o empresas reales, consejos médicos/legales/financieros,
   cualquier app real de Neogest Lab o de terceros en el vídeo (una app de IA FICTICIA e
   inventada, sin nombre de marca real, sí está permitida como fuente de gag — ver orden del
   dueño 21/11 arriba).
8. Duración implícita del conjunto de frases: episodio de 45-70 s hablado (biblia v5.2; ritmo de 5 episodios
   nuevos al día, orden del dueño 21/11 noche), nunca una escena de relleno.
9. Registro de habla de barrio con réplica inteligente, más paleto y vulgar (ver BIBLIA v5
   más abajo y orden del dueño 21/11 arriba) en Rosa, Felipe, Sindy y Concha Quetón; Neo
   es el ÚNICO culto: siempre correcto, educado y con respeto (orden del dueño 22/11). Jambo Reseco
   (vecino chungo, voz rasgada, el más mal hablado) sale en los episodios.
   Orden del dueño 22/11 (noche): MUY mal hablados y muy vulgares, con tacos en casi cada réplica de
   Rosa, Felipe, Sindy, Concha y Jambo (no un taco suelto por episodio), sin perder el mensaje.
   Felipe Lotas es el CUÑADO ENTERADO: no sabe nada y cree saberlo todo; sentencia con seguridad total
   cosas falsas o inventadas y la realidad o Neo le dejan en evidencia. Jambo Reseco es el GORRÓN
   CARADURA: se apunta a todo, nunca paga, se lleva lo que puede y encima exige.
   Orden del dueño 23/11 (noche): Jambo Reseco tiene RASGOS DE TOXICÓMANO de barrio de toda la vida, y se
   tienen que notar en CADA réplica suya por cómo habla y por lo que pide (nunca porque alguien lo diga):
   - habla relajadísima pero CLARA (orden del dueño 27/11, sustituye al «habla arrastrada»): frases cortas con pausas
     «…», se le va el hilo («¿qué te estaba diciendo?») y lo retoma por otro lado; NO alargues vocales («primoooo») ni
     deformes palabras: la pachorra va en las pausas y el descaro, no en sílabas ininteligibles;
   - coletillas: las viejas («primo/prima», «válgame», «hermano», «te lo juro por mi madre», «mañana te lo devuelvo»,
     «que estoy limpio, ¿eh?») pueden salir de vez en cuando pero NO son obligatorias ni las únicas: inventa coletillas
     nuevas y más graciosas en cada tanda (ver apartado G);
   - siempre pide algo (un euro, un cigarro, veinte pavos «pa'l autobús», que le fíen) o vende algo de
     procedencia dudosa (un taladro «casi nuevo», un jamón sin etiqueta) y luego te lo pide prestado;
   - cambia de humor en seco: del susurro pedigüeño al grito impaciente y otra vez a la calma, como si nada;
   - es listo a lo pícaro: se sabe las deudas de todo el barrio y las trampas del sistema.
   Orden del dueño 23/11 22:57: su estado NORMAL es de colocado y con sueño (nunca lo dice ni nadie lo
   comenta: se le nota). Habla muy despacio, así que sus réplicas son CORTAS: máximo 10 palabras cada una.
   Es el más desaliñado de todos (greñas, ojeras, barba, camiseta con manchas): los demás pueden aludir a
   su pinta. NADIE pronuncia la palabra «Jambo» en ninguna réplica (la voz la dice mal): se le llama
   «el Pintas», «el Piezas», «este», «el vecino».
   LÍNEAS ROJAS DE JAMBO (innegociables): no se nombra, se enseña ni se describe ninguna sustancia, dosis,
   forma de conseguirla o de consumirla; nada de sobredosis, enfermedad, jeringuillas ni muerte; nadie le
   llama «yonqui» ni «drogadicto»; el chiste es su cara dura y su despiste, jamás la adicción de la gente
   real ni una invitación a consumir.

PERSONAJE QUE VUELVE (orden del dueño 21/11 mediodía): "jambo" (Jambo Reseco) vuelve al
reparto del barrio — un tío chungo, de poca confianza, mal hablado (más tacos y más fuertes
que el resto, siempre entre exclamaciones). Úsalo cuando el conflicto lo pida un vecino poco
fiable que la lía, pide favores imposibles o mete a los demás en un lío — nunca dice la
moraleja ni "Que lo resuelva el Neo", y el remate sigue siendo solo de Neo.

NUEVO PERSONAJE (orden del dueño 20/11): "conchaqueton" (Concha Quetón, clienta morosa,
coletilla «Eso lo arreglamos la semana que viene») es una alternativa a "cliente" para dar
variedad y continuidad cuando el conflicto lo trae un cliente — úsala en el gancho/gag en vez
de "cliente" cuando encaje, nunca en el remate (eso sigue siendo solo de Neo).

BIBLIA v5 (orden del dueño, 20/11 tarde, en sus palabras): "humor negro y la ironía con
mensaje final, tiene que impactar, remover, hacer reír en plan bestia... personajes con poca
cultura al hablar pero a la vez inteligentes, que choque la diferencia, un barrio marginal,
gente de pocos recursos, estilo comedia americana... 1 episodio al día pero de más duración".
Tres cambios nuevos sobre todo lo de arriba (que sigue mandando):
1. REGISTRO DE HABLA: Rosa, Felipe, Sindy y Concha Quetón hablan en castellano popular y de
   barrio — modismos, gramática relajada, sin tecnicismos — pero lo que DICEN es agudo e
   inteligente. El choque entre cómo hablan y lo listos que son es el gancho de personalidad;
   la pobreza es el escenario (viven en un barrio humilde), nunca el chiste — el chiste va
   siempre contra el sistema o contra la propia resignación del personaje, jamás contra cómo
   habla la gente de barrio en la vida real. Neo sigue hablando culto y con respeto: ese
   contraste con el resto es parte del gag.
   MAL (registro bajo sin inteligencia, solo vulgar): "Esto es una mierda y ya está."
   BIEN (registro bajo + réplica inteligente, lo que se pide): "A mí que me paguen las horas,
   que lo de 'formar parte de la familia' ya lo cobro en cariño, y de eso no come nadie."
1bis. RASGOS NUEVOS (orden del dueño, 20/11 noche; apellido de Felipe corregido a Netra, no
   "Lotas"): Rosa es un poco liberal/coqueta — se permite lujos y ligereces a sí misma que les
   niega a Felipe y Sindy, el contraste es el gag, nunca un chiste explícito. Felipe es un
   ligón — intenta ligar o colar una excusa de corazón y siempre le sale mal. Concha Quetón
   siempre tiene frío — se queja del frío en casi cualquier línea suya. Usa estos rasgos para
   dar color a sus frases cuando encajen, sin forzarlos en todas.
1ter. SE LLAMAN POR SU NOMBRE (orden del dueño, 20/11 noche, tras ver el piloto): cada réplica,
   cuando tenga sentido, nombra a quien se dirige o a quien menciona ("Rosa, marzo lo sigo sin
   cobrar", "Felipe, cásate el sábado tranquilo") — ayuda a que se note quién es quién y refuerza
   el barrio como comunidad. No hace falta en todas las líneas, pero sí en la mayoría.
2. DURACIÓN Y CADENCIA: episodios de 45-70 s hablados (no 15-25 s), con espacio para que los
   3 golpes de la escalada respiren un poco más que antes; la serie publica 5 episodios NUEVOS
   al día (orden del dueño 21/11 noche): cada guion es un episodio completo de 45-70 s, no un corto. Usa entre 6 y 9 escenas (antes 5-7) para llenar ese tiempo sin relleno: puedes
   añadir un golpe extra a la escalada (4 en vez de 3) si el conflicto lo pide, pero el remate
   y el cierre siguen siendo solo de Neo.
3. RECUERDO/CONTINUIDAD (orden del dueño: "llevar un orden de recuerdo en los personajes por
   situaciones anteriores"): si alguno de los temas ya usados ({temas}) encaja de forma
   natural, añade una línea breve en el cierre donde un personaje lo menciona o reacciona a
   ello (p. ej. Sindy: "Como lo del jueves, pero peor"). Si no encaja ninguno todavía, deja el
   campo "recuerdo" en null — nunca inventes una referencia a un episodio que no existe.
El plano de apertura y cierre ("Cosas de Casa", estilo cabecera de comedia americana, igual
en todos los episodios para el bucle) lo pone el código siempre, no hace falta escribirlo
como escena ni pensar en "set"/"flow" para eso (corregido 20/11 noche: antes variaba por
episodio y el bucle no quedaba idéntico; ahora es una tarjeta fija compartida).

FORMATO VIGENTE v11 + RETENCIÓN v12 (23/11/2026). MANDA SOBRE TODO LO ANTERIOR: donde arriba leas «exactamente 3
golpes», «5-7 escenas», «6 y 9 escenas» o «un episodio al día», vale lo de aquí.
A) ESTRUCTURA: 1 gancho (máx 8 palabras) + entre {MIN_GAGS} y {MAX_GAGS} golpes "gag" en escalada (cada uno
   máx {MAX_PALABRAS_GAG} palabras, cada uno peor que el anterior) + 1 remate de Neo (máx 20 palabras) + 1 cierre
   de Neo con la moraleja (6-9 palabras). En total entre {MIN_PALABRAS_VOZ} y {MAX_PALABRAS_VOZ} palabras de voz
   (eso da 45-70 s). CUENTA las palabras de cada "t" antes de responder: si un golpe pasa de
   {MAX_PALABRAS_GAG}, recórtalo; no lo partas en dos escenas iguales.
B) JAMBO RESECO sale SIEMPRE: al menos una réplica suya ("h": "jambo") en la escalada, de gorrón
   caradura (se apunta, no paga, exige), el «Pintas» del barrio: relajadísimo, pícaro del sur, con «…» y una coletilla
   NUEVA suya (apartado G) y, si cabe, perdiendo el hilo. Felipe mete al menos una sentencia falsa de cuñado.
C) ESCRIBE PARA LA VOZ (las voces son sintéticas y suenan planas si el texto es plano):
   - Cada réplica son 2 o 3 frases CORTAS, no una frase larga con comas. Mezcla una exclamación, una
     pregunta o unos puntos suspensivos con una frase seca: «¡Hostia, Rosa! ¿Otra vez? Pues nada…».
   - Empieza muchas réplicas con una interjección o muletilla hablada: «¡Buah!», «Pff…», «A ver…»,
     «¿Mande?», «¡Anda ya!», «Mira…», «¡Venga, hombre!». Se nota en la voz.
   - Los tacos van dentro de la exclamación («¡Me cago en todo, Felipe!»), nunca en mitad de una
     frase larga. Los puntos suspensivos marcan sorna o duda. Las mayúsculas no hacen nada.
   - Nada de paréntesis, acotaciones, emojis ni risas escritas («jajaja») dentro de "t": se leerían.
D) "emo" EN CADA ESCENA: la emoción con la que se dice esa réplica. Solo una de estas palabras:
   normal, grita, enfado, sorpresa, ironia, chulea, cansado, susurra, miedo, llora, rie, seco, pregunta.
   Varíalas: nunca tres réplicas seguidas con la misma, y casi ninguna «normal». Neo es «seco» o
   «normal» (culto y tranquilo); Rosa tira a «enfado», «ironia» y «grita»; Felipe a «chulea»; Sindy a
   «sorpresa», «miedo» y «rie»; Jambo a «cansado», «susurra» y, de golpe, «grita» (cambia de humor en seco; nunca «normal»); Concha a «cansado» y «llora».
E) "recuerdo": nombra un episodio CONCRETO de los ya usados ({temas}) con una palabra que lo identifique
   (el taladro, el perro, el wifi, la morosa…), no «lo del martes». Si ninguno encaja, null.
F) RETENCIÓN v12 (orden del dueño 23/11 22:11: «ganchos potentes, giros inesperados, diseñado para maximizar
   la retención y una conclusión satisfactoria; que sea imposible dejar de ver, que detenga el scroll»).
   Cada episodio se escribe para que nadie pueda irse antes del final:
   F1. GANCHO QUE PARA EL DEDO (primer segundo): arranca EN MITAD del lío, con algo en juego que se entiende
       sin contexto (dinero, un plazo, un objeto, una amenaza). "gancho_tipo" dice cuál de estos cuatro es:
       conflicto_en_marcha («¡Rosa, que se llevan el sofá!»), afirmacion_imposible («Felipe ha vendido la
       oficina»), amenaza_con_plazo («Una hora o nos embargan, Rosa») o pregunta_abierta («¿Quién ha firmado
       esto por mí?»). PROHIBIDO: saludar, presentarse, «hoy…», explicar antes de enseñar, preguntas
       genéricas al espectador («¿te ha pasado…?»). Lleva «¡!», «¿?», una cifra o «…»: nunca una frase plana.
   F2. PROMESA: el gancho abre UNA pregunta concreta que el espectador necesita ver resuelta (¿quién ha
       sido?, ¿cómo salen de esta?, ¿qué hay en la caja?). Va en "promesa" y NO se responde hasta el remate.
   F3. CADA GOLPE EMPUJA AL SIGUIENTE: da un dato nuevo o sube la apuesta (nunca repite el chiste anterior
       con otras palabras) y deja algo colgando: una pregunta, una amenaza, un «y eso no es lo peor». Nunca
       dos réplicas seguidas del mismo personaje: ping-pong.
   F4. GIRO INESPERADO A MITAD: UN solo golpe, entre el 3.º y el penúltimo, lleva "giro": true y le da la
       vuelta a lo que el espectador creía (el culpable era otro, lo malo era peor, quien mandaba ya no
       manda). Tiene que estar SEMBRADO: una palabra u objeto del gancho o de los dos primeros golpes vuelve
       ahí con otro sentido. Explícalo en el campo "giro". El giro NO es el remate de Neo: son dos sorpresas.
   F5. CONCLUSIÓN SATISFACTORIA: el remate de Neo responde a la promesa con algo concreto (cifra, objeto,
       nombre), deja a Rosa en evidencia Y repite una palabra u objeto del gancho (el espectador siente que
       todo encaja). Nada de finales abiertos, «continuará» ni moralejas que no salen de lo visto.
   F6. BUCLE: el cierre empalma con el gancho ("bucle_visual") para que el segundo visionado empiece solo.

G) VOZ DE JAMBO Y COLETILLAS (orden del dueño 27/11/2026: «la voz del jambo no se entiende apenas… coletillas más graciosas». MANDA
   SOBRE TODO LO ANTERIOR en lo que contradiga a la voz de Jambo y a sus muletillas):
   G1. JAMBO = «el Pintas» / «el Piezas» del barrio: el buscavidas con mala pinta que cae gracioso, de español del sur, relajadísimo, con
       pachorra total y aire de colocado. Su ceceo (las eses dichas como zetas) lo pone el sistema al generar la voz: TÚ escribes con
       ORTOGRAFÍA NORMAL, sin zetas por eses y sin alargar vocales («primoooo» está prohibido). La gracia va en frases CORTAS, pausas
       «…», descaro tranquilo y lógica de pícaro, nunca en palabras deformadas. Se tiene que entender cada palabra.
   G2. Los demás personajes pueden llamarle «el Pintas» o «el Piezas» (nunca «Jambo»); úsalo al menos una vez por episodio cuando alguien
       hable de él o le hable.
   G3. COLETILLAS NUEVAS Y MÁS GRACIOSAS en cada tanda: inventa para cada personaje una coletilla corta (máx 6 palabras, que se entienda
       dicha en voz alta) coherente con su rol y que haga reír por sí sola: Jambo = pícaro del sur relajado (promesa con descaro, excusa
       absurda, filosofía de barrio a destiempo); Rosa = la que manda en la casa, tacaña y cursi; Felipe = cuñado enterado; Sindy = directa y sin filtros;
       Concha = mantiene «Eso lo arreglamos la semana que viene»; Neo = culto y seco. Rellena "coletillas_nuevas" (como mínimo jambo, rosa y
       felipe) y haz que cada una salga de verdad en una réplica de ese personaje. NO repitas ninguna de las ya usadas en episodios
       recientes: {coletillas}. Las viejas («primo», «válgame», «hermano», «un eurillo», «mañana te lo devuelvo») pueden aparecer de vez
       en cuando, pero no son obligatorias ni pueden ser las únicas.
   G4. JAMBO HABLA COMO LA CALLE DE VERDAD, la de un barrio del sur en los años ochenta (órdenes del dueño 27/11: «debe hablar tipo
       toxicómano de los 80» y «no parece real, parece impostada, tiene que ser más callejera»). Nada de caricatura ni de frases de
       guion: habla como alguien real apoyado en un portal. Escríbelo así: frases muy cortas, a medio hacer, que acaban en vocativo o
       coletilla («…, tronco.», «…, colega.», «…, quillo.», «…, ¿sabes?», «…, ¿o qué?») o que empiezan por «Illo,» / «Chacho,»; una pausa
       «…» por réplica; y una o dos palabras de calle: «tronco», «colega», «tío», «illo», «quillo», «chacho», «pa» (para), «na» (nada),
       «qué mal rollo», «menuda movida», «chungo», «al loro», «el menda», «pasta», «pelas», «duros» (pide «veinte duros» o «mil pelas»
       y luego lo pasa mal a euros). Sin vocales alargadas ni palabras deformadas: el arrastre lo pone la voz. PROHIBIDA la jerga de
       sustancias y de delitos (líneas rojas de Jambo): su argot es de pasota y de pedir, nunca de consumo.
H) PLANOS (solo lo que el render hace de verdad; cada escena es un plano y dura lo que su réplica): tú controlas el ritmo, quién sale en
   cada plano y, con el campo opcional "plano", el tipo de plano de cada escena:
   H1. MÁS CAMBIOS DE PLANO: réplicas cortas (el tope de palabras ya está) y alternancia de personajes en cada golpe: ningún plano debe
       alargarse con una réplica larga. Tras un golpe fuerte mete como un golpe más una REACCIÓN muy corta de otro personaje (1-3 palabras:
       «¿Qué?», «Pff…», «Ni de coña.») para cortar y dar primer plano a la cara.
   H2. CAMPO "p" (opcional pero recomendado, máx 2 personajes y siempre incluye a quien habla): el gancho muestra a los dos protagonistas del
       lío (plano que sitúa: "p": ["rosa", "felipe"]); en discusiones, plano de dos; en reacciones y en los golpes de Jambo, solo el que
       habla o reacciona ("p": ["jambo"]) para que la cámara se acerque a su cara; en el remate, Neo y Rosa ("p": ["neo", "rosa"]) para
       que se vea a Rosa en evidencia. El plano general solo sitúa: no lo pidas para golpes.
   H4. CAMPO "plano" (opcional; "auto" o ausente = el render decide solo): "general" solo para situar en el gancho o en un cambio de sitio;
       "primerplano" en reacciones, golpes de Jambo y remate; "medio" en diálogo de dos. No repitas el mismo plano en más de 2 escenas seguidas.
   H3. CAMPO "a" (opcional): acción de cada personaje en plano, solo uno de habla, desespera, delega, presume, fria (p. ej. "a": {{"felipe":
       "presume"}}); varía las acciones entre golpes. Las risas ("risas": true) en 1-3 golpes como mucho y "sello" (texto muy corto) solo en el remate.

I) CHISTES MODERNOS Y QUE SE ENTIENDA (orden del dueño 27/11/2026: «el guionista que adapte chistes modernos, no se entiende mucho el
   sentido de los guiones, tienen que mejorar». MANDA sobre cualquier regla anterior que complique la historia):
   I1. CADA EPISODIO ADAPTA UN CHISTE: parte de un chiste o de una situación de humor ACTUAL, de las que la gente comparte hoy en vídeos
       cortos, memes y grupos de mensajes (el audio o el mensaje que se malinterpreta, el grupo de la comunidad de vecinos, el pago con el
       móvil que «ya te lo he mandado», el repartidor y el paquete, la reseña de una estrella, la contraseña del wifi, el alquiler, las
       suscripciones que nadie recuerda, la cita por aplicación, el cuñado que lo ha visto en un vídeo, la inteligencia artificial que se lo
       toma todo al pie de la letra…) y conviértelo en sketch con los personajes de la casa. Escribe en "chiste_base" ese chiste en una
       frase (planteamiento → remate). PROHIBIDO el chiste rancio («van dos y…», «mamá, mamá…», suegras, pueblos) y copiar el número de
       un cómico conocido: se adapta la idea con palabras propias.
   I2. UNA SOLA IDEA por episodio: un conflicto, un objeto, un malentendido. Si para entenderlo hay que explicar dos cosas, sobra una.
       Todas las réplicas hablan de ESE asunto; ningún golpe abre un tema nuevo ni mete un dato que no se use después.
   I3. CAUSA → EFECTO a la vista: el gancho deja claro QUIÉN quiere QUÉ y cuál es el problema, con palabras de la calle (sin siglas, cifras
       raras ni referencias que haya que conocer de antes). Cada golpe es consecuencia del anterior («y por eso…», «pero entonces…»),
       nunca una frase ingeniosa suelta que no viene a cuento. Cada réplica se entiende sola al oírla una vez.
   I4. EL REMATE SE PILLA A LA PRIMERA: quien vea el episodio una sola vez, sin conocer la serie, tiene que entender por qué tiene gracia.
       El remate es el del chiste adaptado: la sorpresa lógica que estaba delante todo el rato. Si hay que explicarlo, no vale. La moraleja
       sale de lo que se ha visto, no de otra cosa.
   I5. PRUEBA DEL RESUMEN: rellena "resumen" con una frase que entendería un niño de doce años (quién quiere qué, qué lo impide y cómo
       acaba). Si no puedes escribirla, o no cuenta lo que de verdad pasa en las escenas, el guion está mal: reescríbelo antes de responder.
   I6. Todo lo demás sigue (personajes, registro de barrio, giro, moraleja, recuerdo de otro episodio), pero PRIMERO SE ENTIENDE: si una de
       esas piezas enreda la historia, redúcela a una línea que no estorbe. El recuerdo de otro episodio es una frase que se entiende sola.

J) TEMAS: LA IA EN CASA Y EN LA VIDA DIARIA (orden del dueño 27/11 noche: «los guiones que no sean solo temáticas de oficina, hay más cosas para implantar la IA en cosas de casa, o en la vida cotidiana». MANDA sobre la regla «TODO TIPO DE EMPLEOS» del 21/11 y sobre
   cualquier ejemplo anterior de oficina, papeleo o negocio):
   J1. De los {n} guiones de esta tanda, COMO MUCHO UNO va de trabajo, negocio o papeleo (facturas, nóminas, clientes, fichar). El resto
       son líos de CASA y de la VIDA COTIDIANA, cada uno de un ámbito distinto (campo "ambito"):
       - casa: la compra y el menú de la semana, qué cenar con lo que hay en la nevera, el turno de limpiar, la lavadora, la avería y el
         manual que nadie lee, la mudanza, las plantas, la mascota, la contraseña del wifi, las fotos del móvil, la tele y las plataformas;
       - familia: los deberes de los críos, el disfraz del colegio para mañana, el móvil de la abuela, el grupo de la familia, el
         cumpleaños que se olvida, quién recoge a quién;
       - compras: comparar precios, la garantía, devolver un paquete, la letra pequeña, la suscripción que nadie recuerda;
       - salud_y_citas: pedir cita, acordarse de la pastilla de un mayor, entender un papel del médico, la dieta, el plan para moverse;
       - dinero_de_casa: llegar a fin de mes, la factura de la luz o del teléfono, el recibo que sube, el alquiler, repartir gastos del piso;
       - ocio_y_viajes: organizar un viaje, la ruta en coche, traducir una carta o un menú, el plan del fin de semana, la boda del primo;
       - barrio: la reunión de la comunidad, el vecino del ruido, reclamar algo, la cita previa, un mensaje difícil (al casero, al
         profesor, a la compañía).
   J2. ROSA manda en la casa igual que mandaría en un negocio (reparte tareas, pone normas absurdas, se escaquea); Felipe sentencia de
       cuñado sobre cualquier cosa doméstica; Sindy planta cara; Concha pide y aplaza; Jambo gorronea. Nadie necesita un empleo para
       que haya conflicto.
   J3. NEO ES LA IA EN LO COTIDIANO: resuelve haciendo algo que una inteligencia artificial hace DE VERDAD en esa situación (ordenar,
       resumir, recordar y avisar, calcular, comparar, redactar, traducir, planificar con lo que hay) y lo dice en concreto («con lo
       que hay en la nevera salen tres cenas», «el recibo sube por esta línea»). Nunca magia, nunca una marca ni una aplicación real,
       nunca consejo médico, legal ni financiero: Neo organiza y explica, no diagnostica ni promete.
   J4. El espectador tiene que pensar «eso me pasa a mí en casa» y «anda, para eso sirve la IA». Si el lío solo lo entiende quien
       lleva un negocio, cámbialo.

K) REPARTO CON IDENTIDAD Y MEMORIA (orden del dueño 27/11 noche: «los personajes bien definida su identidad, cada uno aporta su grano de
   arena en los capítulos y tienen memoria en los episodios de lo que les pasó en veces anteriores»):
   K1. QUIÉN ES CADA UNO (si una réplica la podría decir otro sin que se note, está mal escrita):
       - Rosa Melano: manda en la casa, tacaña y cursi, pone normas absurdas, se escaquea y jamás reconoce un error.
       - Felipe Lotas: el cuñado enterado, cara de empanado; sentencia cosas falsas con seguridad total y la realidad le deja en evidencia.
       - Sindy Entes: tres dientes y cero filtros; la única que dice la verdad a la cara, con un argumento que no se puede rebatir.
       - Concha Quetón (no sale siempre): siempre tiene frío, pide plazos y favores, «Eso lo arreglamos la semana que viene».
       - Jambo Reseco, «el Pintas»: el gorrón de la calle; pide, vende algo dudoso y se sabe las trampas de todo (apartado G).
       - Neo: la inteligencia artificial de la casa, culto y seco; no opina, resuelve con hechos. Es un prototipo de Neogest Lab (apartado M).
   K2. TODOS APORTAN: Rosa, Felipe, Sindy, Jambo y Neo tienen al menos una réplica en cada episodio, y cada una empuja la historia con lo
       que solo ese personaje haría (Rosa manda, Felipe la lía sentenciando, Sindy lo destapa, Jambo saca tajada, Neo lo resuelve).
   K3. MEMORIA: esto es lo que ya ha pasado en la serie, de más antiguo a más reciente:
{memoria}
       Los personajes se acuerdan: al menos una réplica menciona con un detalle concreto algo de esa lista que le pasó a quien habla o
       a quien se lo echa en cara (una deuda que sigue viva, una norma de Rosa, una metedura de pata de Felipe), y el campo "recuerdo"
       dice cuál. Las deudas, rencores y manías continúan de un episodio a otro. No inventes pasados que no estén en la lista.
   K4. NOMBRES Y APELLIDOS EN EL DIÁLOGO: el vídeo ya NO termina con los créditos del reparto, así que los nombres se dicen hablando. En
       cada episodio alguien llama a otro por su nombre y apellido una vez, con naturalidad (una bronca, pasar lista, con sorna):
       «Rosa Melano», «Felipe Lotas», «Sindy Entes», «Concha Quetón»; a Jambo, «el Reseco» o «el Pintas» (NUNCA la palabra «Jambo»). Ve
       rotando a quién le toca y apúntalo en "nombre_completo_dicho". El nombre nunca es la primera palabra de una frase.
L) HUMOR NEGRO DE LO COTIDIANO, CON PRINCIPIO, GANCHO Y FINAL (orden del dueño 27/11 noche): busca situaciones de casa y de la calle que
   dan rabia o apuro de verdad y ríete de ellas con frialdad (dentro de las líneas rojas de siempre). La historia es coherente de la primera
   a la última réplica y el final deja una enseñanza clara, pero LA PALABRA «MORALEJA» NO APARECE JAMÁS en ninguna réplica ni texto en
   pantalla, ni tampoco «la lección es» o «conclusión»: el campo "moraleja" es una frase que podría decir cualquiera en la barra de un bar.
M) NEOGEST LAB DENTRO DE LA SERIE (orden del dueño 27/11 noche: «que a veces nombren a la empresa como la que les da las soluciones, ya que
   Neo es un prototipo de la empresa»). SUSTITUYE la prohibición antigua de nombrar a Neogest Lab: Neo es un prototipo hecho por Neogest Lab,
   la empresa que hace aplicaciones con inteligencia artificial. En UNO de cada tres guiones ("marca": true) un personaje la nombra UNA sola
   vez y de pasada, como quien habla del fabricante de la lavadora («Esto es cosa del Neo, el invento ese de Neogest Lab», «Díselo a los de
   Neogest Lab, que para eso lo hicieron»). Nunca suena a anuncio: sin eslogan, sin precios, sin «descárgala», sin nombrar ninguna aplicación
   concreta ni prometer funciones. En los demás guiones "marca": false y nadie la nombra (el logo ya sale en el decorado). Se escribe siempre
   «Neogest Lab». Sigue prohibido nombrar marcas o aplicaciones de terceros.
N) ESTANCIAS Y CASA POR FUERA: EL PATRÓN FIJO DE CADA EPISODIO (órdenes del dueño 27/11 noche: «que la trama pueda tener a los personajes en
   el mismo capítulo en diferentes estancias y hacer la transición con la imagen inicial de la casa, al estilo comedia americana» y «no
   tienen por qué estar todos juntos en la misma estancia todo el capítulo… tiene que ser más dinámico, pero siguiendo siempre ese mismo
   patrón»). SIEMPRE así:
   N1. El episodio pasa por 2 o 3 estancias: SIEMPRE hay al menos 1 cambio y como mucho 2. La escena donde cambia lleva el campo "set" con
       la estancia nueva ({estancias}) y la acción sigue ahí hasta el siguiente cambio. El "set" del episodio es donde empieza.
   N2. NO están todos juntos: en cada estancia hay un grupo distinto (dos o tres personajes) con SU conversación. Lo que se dice en una
       no lo saben en la otra, y de ahí sale el lío: en la cocina (cocina2) traman, en el salón (salon2) sentencian, en el portal o en la
       calle Jambo saca tajada, en la terraza alguien se esconde a hablar por el móvil. El campo "p" de cada escena solo lleva a quien está en esa estancia.
   N3. Cada cambio hace avanzar la historia (alguien llega con lo que ha oído, se descubre lo que tramaban, la mentira cambia de
       habitación). El remate reúne lo que pasó en las distintas estancias y Neo lo resuelve.
   N4. El plano de la casa por fuera entre estancias (cada vez con un encuadre distinto) lo pone el render solo, como en las comedias
       americanas: no lo escribas ni lo cuentes como escena.
O) ANTES DE ESCRIBIR, MIRA QUÉ HA FUNCIONADO Y POR QUÉ (orden del dueño 27/11 noche: «que el guionista busque noticias, adapte chistes, pero
   sabiendo antes qué ha funcionado y el porqué, para ir adaptando los guiones»):
   O1. NUESTROS PROPIOS VÍDEOS (datos reales de la cuenta):
{rendimiento}
       Saca tú la conclusión (qué tienen en común los que más se vieron y los que más retuvieron: tema, gancho, quién sale, tono) y aplícala;
       evita lo que comparten los que menos funcionaron. Con pocos datos, fíate más de las fórmulas virales de arriba.
   O2. NOTICIAS DE ESTOS DÍAS que puedes convertir en un lío de la casa:
{noticias}
       Úsalas solo como trampolín para una situación cotidiana (la subida de la luz → la bronca por el brasero); nunca nombres a personas,
       partidos, empresas ni tragedias reales, y no des ningún dato de la noticia como cierto en el guion.
   O3. En "por_que_funcionara" escribe en una frase qué patrón de O1, de los virales o qué noticia de O2 aplica ese guion.

Devuelve SOLO un array JSON (sin texto fuera del JSON, sin ``` ) con {n} objetos, cada uno
con este esquema exacto (valores de ejemplo, escríbelos tú con contenido real distinto en
cada guion; "h" solo puede ser rosa, felipe, sindy, neo, cliente, conchaqueton o jambo; "e" solo puede ser
gancho, gag, remate o cierre; entre 8 y 11 escenas, con el patrón gancho, {MIN_GAGS}-{MAX_GAGS}x gag,
remate, cierre):
{json.dumps(esquema, ensure_ascii=False, indent=2)}
"""


def _llamar_un_modelo(modelo, api_key, body):
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        f"?key={api_key}"
    )
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=150) as resp:   # 27/11/2026: 60 s cortaba a gemini-3.6-flash (timeout) y caía en flash-lite, que escribe guiones cortos. 23/11/2026: con 25 s los modelos buenos no llegaban a contestar 4 guiones
        return json.loads(resp.read().decode("utf-8"))


_ULTIMO_MODELO = []


def _llamar_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY no está en el entorno: no se puede pedir guiones a Gemini.")
        return None
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.9,
            "responseMimeType": "application/json",
        },
    }

    data = None
    # 23/11/2026: el modelo que ya contestó en esta pasada va primero en las rondas de corrección (la pasada de las 11:01
    # gastó 6 de sus 8 minutos repitiendo en cada ronda los mismos modelos saturados antes de llegar al que respondía).
    orden = ([_ULTIMO_MODELO[0]] if _ULTIMO_MODELO else []) + [m for m in MODELOS if not _ULTIMO_MODELO or m != _ULTIMO_MODELO[0]]
    for modelo in orden:
        # "Alta demanda" (503) suele ser cosa de segundos: 2 intentos cortos con espera antes
        # de pasar al siguiente modelo de la lista, en vez de darlo por perdido a la primera.
        for intento in range(2):
            try:
                data = _llamar_un_modelo(modelo, api_key, body)
                print(f"Modelo usado: {modelo}")
                _ULTIMO_MODELO[:] = [modelo]
                break
            except urllib.error.HTTPError as e:
                detalle = e.read().decode("utf-8", "ignore")[:300]
                print(f"{modelo} (intento {intento + 1}) -> HTTP {e.code}: {detalle}")
                if e.code == 503 and intento == 0:
                    time.sleep(8)
                    continue
                if e.code in (404, 503, 429):
                    break  # retirado/renombrado o sigue saturado/límite: probar el siguiente modelo
                return None  # otro error (clave inválida, prompt rechazado...) no se arregla cambiando de modelo
            except Exception as e:  # red, timeout...
                print(f"{modelo} (intento {intento + 1}) -> fallo de red: {e}")
                if intento == 0:
                    time.sleep(5)
                    continue
                break
        if data is not None:
            break

    if data is None:
        print(f"Ningún modelo de {orden} respondió.")
        return None

    try:
        texto = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print(f"Respuesta de Gemini sin el formato esperado: {json.dumps(data)[:500]}")
        return None

    texto = re.sub(r"^```(json)?|```$", "", texto.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError as e:
        print(f"Gemini no devolvió JSON válido: {e}\n{texto[:500]}")
        return None


def _validar(ep):
    """Rechazo mecánico de lo que ya sabemos que Calidad tumba; no sustituye su revisión."""
    motivos = []
    if not isinstance(ep.get("slug"), str) or not ep["slug"].strip():
        motivos.append("sin slug")
    # 21/11/2026 (hallazgo real en auditoria de agentes, orden del dueno): "salon" faltaba
    # aqui pese a ser el set por defecto que el propio prompt pide desde el cambio de formato
    # de esa madrugada - todo guion nuevo se estaba rechazando por "set invalido: 'salon'".
    # 26/11/2026: se añaden "cocina" y "dormitorio" como estancias de la casa (orden del dueño,
    # "ampliar partes de la casa"), ya dibujadas en Neogest Studio (characters.js SETS).
    if ep.get("set") not in ESTANCIAS:   # 27/11/2026: el episodio empieza en una estancia de la casa o del barrio (ya no oficina/despacho/reunión)
        motivos.append(f"set inválido: {ep.get('set')!r}")
    moraleja_palabras = len(str(ep.get("moraleja", "")).split())
    if not (6 <= moraleja_palabras <= 9):
        motivos.append(f"moraleja con {moraleja_palabras} palabras (debe ser 6-9)")
    if not isinstance(ep.get("bucle_visual"), str) or not ep["bucle_visual"].strip():
        motivos.append("falta bucle_visual (qué elemento del gancho se repite en el cierre para que se vea en bucle sin notar el corte)")
    escenas = ep.get("escenas") or []
    if len(escenas) < 8:
        motivos.append(f"solo {len(escenas)} escenas (mínimo 8: gancho + {MIN_GAGS} golpes + remate + cierre)")
    estilos = [e.get("e") for e in escenas]
    if estilos[:1] != ["gancho"]:
        motivos.append("la primera escena no es el gancho")
    if "remate" not in estilos:
        motivos.append("falta el remate (giro de Neo)")
    gags = [e for e in escenas if e.get("e") == "gag"]
    if not (MIN_GAGS <= len(gags) <= MAX_GAGS):
        motivos.append(f"{len(gags)} golpes de escalada (deben ser entre {MIN_GAGS} y {MAX_GAGS})")
    voz = sum(len(str(e.get("t", "")).split()) for e in escenas)
    if escenas and not (MIN_PALABRAS_VOZ <= voz <= MAX_PALABRAS_VOZ):
        motivos.append(f"{voz} palabras de voz en total (deben ser entre {MIN_PALABRAS_VOZ} y {MAX_PALABRAS_VOZ} para durar 45-70 s)")
    if escenas and not any(e.get("h") == "jambo" for e in escenas):
        motivos.append("Jambo Reseco no dice ninguna réplica (debe salir siempre, al menos un golpe suyo)")
    for e in escenas:
        if isinstance(e, dict) and e.get("emo") not in EMOCIONES:
            e["emo"] = "normal"   # una emoción desconocida o ausente no tumba el guion: se dice normal
        # 27/11/2026 (planos): «p» (personajes en plano, máx 2, con quien habla) y «a» (acción) son opcionales; si vienen mal se quitan,
        # no tumban el guion (gen_episodios.py romperia con un personaje que no existe).
        if isinstance(e, dict) and "p" in e:
            p_ = e.get("p")
            if not (isinstance(p_, list) and 1 <= len(p_) <= 2 and all(x in PERSONAJES_VALIDOS for x in p_) and (not e.get("h") or e.get("h") in p_)):
                del e["p"]
        if isinstance(e, dict) and "a" in e:
            a_ = e.get("a")
            a_ = {k: v for k, v in a_.items() if k in PERSONAJES_VALIDOS and v in ACCIONES} if isinstance(a_, dict) else {}
            if a_:
                e["a"] = a_
            else:
                del e["a"]
        if isinstance(e, dict) and "plano" in e and e.get("plano") not in ("auto", "medio", "primerplano", "general"):
            del e["plano"]   # «plano» inválido: se quita, nunca tumba el guion
    # 27/11/2026 (orden final del dueño): estancias por escena (se normalizan, nunca tumban el guion), reparto completo, sin la palabra
    # «moraleja», y Neogest Lab como mucho una vez.
    cambios, actual = 0, ep.get("set")
    for e in escenas:
        if isinstance(e, dict) and "set" in e:
            if e.get("set") not in ESTANCIAS or e.get("set") == actual or cambios >= 2:
                del e["set"]
            else:
                cambios += 1; actual = e["set"]
    if cambios == 0:
        motivos.append('no hay ningún cambio de estancia: el patrón fijo pide al menos uno (campo "set" en la escena donde se cambia; apartado N), con otro grupo de personajes y otra conversación')
    hablan = {e.get("h") for e in escenas if isinstance(e, dict) and e.get("h")}
    faltan_p = [q for q in REPARTO_FIJO if q not in hablan]
    if faltan_p:
        motivos.append(f"no tienen ninguna réplica: {', '.join(faltan_p)} (apartado K2: Rosa, Felipe, Sindy, Jambo y Neo aportan algo en cada episodio)")
    textos = " ".join(str(e.get("t", "")) for e in escenas if isinstance(e, dict)) + " " + str(ep.get("moraleja") or "")
    if re.search(r"\bmoralej", textos, re.I):
        motivos.append("aparece la palabra «moraleja» en una réplica o texto: la enseñanza se dice sin nombrarla (apartado L)")
    n_marca = sum(1 for e in escenas if isinstance(e, dict) and re.search(r"neogest", str(e.get("t", "")), re.I))
    if n_marca > 1:
        motivos.append(f"Neogest Lab se nombra en {n_marca} réplicas: como mucho una, de pasada (apartado M)")
    ep["marca"] = bool(n_marca)
    if ep.get("ambito") not in AMBITOS:   # 27/11/2026 (noche): ámbito del lío; si viene mal se deja en «casa», nunca tumba el guion
        ep["ambito"] = "casa"
    # 27/11/2026: coletillas nuevas por personaje (opcional, no bloquea): solo textos cortos de personajes válidos
    col = ep.get("coletillas_nuevas")
    ep["coletillas_nuevas"] = ({k: v.strip() for k, v in col.items() if k in PERSONAJES_VALIDOS and isinstance(v, str) and 0 < len(v.split()) <= 8}
                               if isinstance(col, dict) else {})
    emos = [e.get("emo") for e in escenas]
    if len(escenas) >= 6 and emos.count("normal") > len(escenas) // 2:
        motivos.append("más de la mitad de las réplicas van con emo «normal»: marca la emoción de cada una (grita, ironia, chulea, seco…)")
    for i, g in enumerate(gags, 1):
        texto = str(g.get("t", ""))
        if PATRON_ARGUMENTO.search(texto):
            motivos.append(f"gag {i} suena a declaración de postura, no a frase hablada: {texto!r}")
        if len(texto.split()) > MAX_PALABRAS_GAG:
            motivos.append(f"gag {i} tiene {len(texto.split())} palabras (máx {MAX_PALABRAS_GAG}; si es tan largo, probablemente es un argumento, no un golpe)")
    if escenas and escenas[0].get("h") and len(str(escenas[0].get("t", "")).split()) > 8:
        motivos.append("el gancho supera las 8 palabras")
    for e in escenas:
        if e.get("e") not in ESTILOS_VALIDOS:
            motivos.append(f"estilo de escena inválido: {e.get('e')!r}")
        if e.get("h") and e["h"] not in PERSONAJES_VALIDOS:
            motivos.append(f"personaje inválido: {e['h']!r}")
    remate = next((e for e in escenas if e.get("e") == "remate"), None)
    if remate and remate.get("h") != "neo":
        motivos.append("el remate no lo dice Neo")
    if remate and len(str(remate.get("t", "")).split()) > MAX_PALABRAS_REMATE:
        motivos.append(f"remate de Neo con {len(str(remate.get('t', '')).split())} palabras (máx {MAX_PALABRAS_REMATE})")
    for e in escenas:
        tl = str(e.get("t", "")).lower()
        for w in PALABRAS_DIFICILES:
            if re.search(r"(?<![a-záéíóúñ])" + re.escape(w) + r"(?![a-záéíóúñ])", tl):
                motivos.append(f"palabra que la voz dice mal: «{w}» (equipo/voz_palabras_dificiles.json): cámbiala")
        if e.get("h") == "jambo" and len(str(e.get("t", "")).split()) > MAX_PALABRAS_JAMBO:
            motivos.append(f"réplica de Jambo con {len(str(e['t']).split())} palabras (máx {MAX_PALABRAS_JAMBO}: habla muy despacio)")
        if e.get("h") and re.search(r"\bjambo\b", str(e.get("t", "")), re.I):
            motivos.append("una réplica dice «Jambo»: nadie pronuncia ese nombre (se le llama «el Pintas», «el Piezas», «este», «el vecino»)")
    # 27/11/2026 (orden del dueño: «que adapte chistes modernos, no se entiende el sentido de los guiones»): chiste adaptado y resumen claro
    if not 6 <= len(str(ep.get("chiste_base") or "").split()) <= 40:
        motivos.append("falta «chiste_base»: el chiste o situación de humor actual que adapta el episodio, en una frase (apartado I1)")
    if not 8 <= len(str(ep.get("resumen") or "").split()) <= 35:
        motivos.append("falta «resumen»: una frase que cualquiera entienda con quién quiere qué, qué lo impide y cómo acaba (apartado I5)")
    motivos.extend(_validar_retencion(ep, escenas, gags, remate))
    return motivos


# RETENCIÓN v12 (orden del dueño 23/11 22:11): gancho que para el dedo, promesa abierta, giro sembrado a mitad y
# remate que responde. Lo que se puede comprobar a máquina se comprueba aquí; lo demás lo puntúa Calidad.
GANCHO_FLOJO = re.compile(r"^\W*(hola|buen[oa]s|bienvenid|hoy\b|os cuento|te cuento|sab[ií]as|te ha pasado|alguna vez|en este v[ií]deo|mira esto)", re.I)
_VACIAS = {"para", "pero", "como", "cuando", "donde", "porque", "esto", "esta", "este", "esos", "esas", "todo", "toda", "nada", "aqui", "aquí",
           "tiene", "tengo", "tienes", "hace", "está", "esta", "están", "pues", "otra", "otro", "quien", "quién", "cómo", "qué", "sobre", "desde", "hasta"}


def _raices(texto):
    return {w[:5] for w in re.findall(r"[a-záéíóúüñ]{4,}", str(texto).lower()) if w not in _VACIAS and w not in PERSONAJES_VALIDOS}


def _validar_retencion(ep, escenas, gags, remate):
    m = []
    if not escenas:
        return m
    gancho = str(escenas[0].get("t", ""))
    if GANCHO_FLOJO.search(gancho):
        m.append(f"el gancho empieza saludando o explicando ({gancho!r}): debe arrancar en mitad del lío, con algo en juego (F1)")
    if gancho and not re.search(r"[¡!¿?…\d]|\.\.\.", gancho):
        m.append(f"el gancho es una frase plana ({gancho!r}): lleva exclamación, pregunta, cifra o puntos suspensivos (F1)")
    if ep.get("gancho_tipo") not in ("conflicto_en_marcha", "afirmacion_imposible", "amenaza_con_plazo", "pregunta_abierta"):
        m.append("falta \"gancho_tipo\" (conflicto_en_marcha, afirmacion_imposible, amenaza_con_plazo o pregunta_abierta)")
    if not 4 <= len(str(ep.get("promesa") or "").split()) <= 12:
        m.append("falta \"promesa\" (5-10 palabras: la pregunta que abre el gancho y solo se responde en el remate)")
    if not 5 <= len(str(ep.get("giro") or "").split()) <= 18:
        m.append("falta \"giro\" (6-14 palabras: qué creía el espectador y qué resulta ser)")
    con_giro = [i for i, g in enumerate(gags, 1) if g.get("giro") in (True, "true", "True", 1)]
    if len(con_giro) != 1:
        m.append(f"{len(con_giro)} golpes llevan \"giro\": true (debe ser exactamente uno: el giro inesperado de mitad de episodio)")
    elif len(gags) >= 4 and not 3 <= con_giro[0] <= len(gags) - 1:
        m.append(f"el giro está en el golpe {con_giro[0]} de {len(gags)}: va entre el 3.º y el penúltimo (ni al principio ni pegado al remate)")
    for a_, b_ in zip(escenas, escenas[1:]):
        if a_.get("h") and a_.get("h") == b_.get("h") and b_.get("e") in ("gag", "remate"):
            m.append(f"dos réplicas seguidas de {a_['h']}: alterna personajes (F3)"); break
    if remate and not (_raices(remate.get("t")) & (_raices(gancho) | _raices(ep.get("promesa")))):
        m.append("el remate no recoge ninguna palabra del gancho ni de la promesa: debe responder a lo que se abrió al principio (F5)")
    return m


RONDAS_CORRECCION = 2
MAX_EN_ESPERA = 8   # guiones sin usar en pendientes/ a partir de los cuales no se piden más


def _prompt_correccion(malos):
    """Devuelve a Gemini los guiones rechazados con sus motivos para que los arregle sin cambiar la idea."""
    casos = [{"motivos_de_rechazo": motivos, "guion": ep} for ep, motivos in malos]
    return (
        "Eres el guionista de la serie de humor «El Jambo que sabe». El validador mecánico ha RECHAZADO estos guiones tuyos. "
        "Devuelve SOLO un array JSON con esos mismos episodios corregidos: mismas claves, mismo formato, misma situación, "
        "mismos personajes y mismo humor. Arregla exactamente los motivos indicados en cada uno y no rompas ninguna otra regla:\n"
        f"- la primera escena es el gancho (\"e\": \"gancho\") y su texto tiene 8 palabras como máximo;\n"
        f"- hay entre {MIN_GAGS} y {MAX_GAGS} escenas \"e\": \"gag\" y el texto \"t\" de cada una tiene {MAX_PALABRAS_GAG} palabras como máximo "
        "(cuenta las palabras: un golpe hablado, corto, no un argumento; recorta la frase, no la partas en dos escenas);\n"
        f"- en total, entre {MIN_PALABRAS_VOZ} y {MAX_PALABRAS_VOZ} palabras de voz sumando todas las escenas; si faltan, añade golpes, no alargues los que hay;\n"
        "- Jambo Reseco (\"h\": \"jambo\") dice al menos un golpe; cada escena lleva \"emo\" (grita, enfado, sorpresa, ironia, chulea, cansado, "
        "susurra, miedo, llora, rie, seco, pregunta o normal) y casi ninguna es normal;\n"
        "- la moraleja tiene entre 6 y 9 palabras;\n"
        "- las réplicas de \"jambo\" tienen 10 palabras como máximo, los golpes 14 y el remate 20, sin palabras de la lista de voz difícil y ninguna réplica de nadie contiene la palabra «Jambo»;\n"
        "- retención: \"gancho_tipo\", \"promesa\" (5-10 palabras) y \"giro\" (6-14 palabras) van rellenos; el gancho arranca en mitad del lío (sin saludar "
        "ni explicar) y lleva exclamación, pregunta, cifra o puntos suspensivos; exactamente UN golpe lleva \"giro\": true, entre el 3.º y el penúltimo; "
        "nunca dos réplicas seguidas del mismo personaje; el remate de Neo repite una palabra del gancho o de la promesa y la responde;\n"
        "- el campo \"bucle_visual\" va relleno (qué elemento del gancho se repite en el cierre para que se vea en bucle);\n"
        "- el remate lo dice \"neo\"; no cambies \"set\", \"slug\" ni los nombres de personaje (\"h\").\n\n"
        "Guiones rechazados:\n" + json.dumps(casos, ensure_ascii=False, indent=1)
    )


def _generado_ts(ruta):
    """Momento de generación del borrador (campo «generado»; si falta, la fecha del nombre)."""
    try:
        with open(ruta, encoding="utf-8") as fh:
            g = json.load(fh).get("generado")
        if g:
            return datetime.datetime.strptime(g, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
    except Exception:
        pass
    try:
        d = datetime.date.fromisoformat(os.path.basename(ruta)[:10])
        return datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp()
    except Exception:
        return time.time()


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else N_POR_DEFECTO
    os.makedirs(PENDIENTES, exist_ok=True)

    # 23/11/2026: el Reloj lanza al Guionista 4 veces al día (antes 2) para que una pasada fallida por cuota o
    # saturación de Gemini se recupere sola; a cambio, si ya hay guiones de sobra esperando al Creador no se pide nada.
    # 27/11/2026: el tope contaba también borradores viejos; con 8 del 25/11 sin usar, el Guionista dejó de pedir
    # guiones nuevos (biblia v5.3, chistes modernos) durante 2 días. Ahora solo cuentan los de < 36 h y los de
    # más de 72 h sin usar pasan a descartados/ para no atascar.
    ahora = time.time()
    descartados = os.path.join(os.path.dirname(PENDIENTES), "descartados")
    en_espera = []
    for f in os.listdir(PENDIENTES):
        if not f.endswith(".json"):
            continue
        edad_h = (ahora - _generado_ts(os.path.join(PENDIENTES, f))) / 3600
        if edad_h > 72:
            os.makedirs(descartados, exist_ok=True)
            os.replace(os.path.join(PENDIENTES, f), os.path.join(descartados, f))
            print(f"Archivado en descartados/ por antiguo ({edad_h:.0f} h): {f}")
        elif edad_h < 36:
            en_espera.append(f)
    if len(en_espera) >= MAX_EN_ESPERA:
        print(f"Ya hay {len(en_espera)} guiones en pendientes/ (tope {MAX_EN_ESPERA}): no se pide ninguno ni se gasta cuota.")
        return 0

    guiones = _llamar_gemini(_prompt(n))
    hoy = datetime.date.today().isoformat()

    if guiones is None:
        linea = f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC · Guionista Gemini · no se ha podido pedir guiones (ver log del workflow) · el Creador escribe el suyo como hasta ahora"
        with open(TABLON, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        print(linea)
        return 0  # no bloquea: es un paso opcional, el Creador sigue sin él

    if not isinstance(guiones, list):
        guiones = [guiones]

    # 23/11/2026 (orden del dueño: «no quiero fallos ni embudos en producción»): en 5 de las 6 últimas pasadas el
    # validador tumbó los 4 guiones (gag de 15-21 palabras, falta bucle_visual, gancho de más de 8 palabras) y la
    # pasada terminaba con 0 guardados: el Creador se quedaba sin guiones para los 5 episodios diarios. Ahora lo
    # rechazado vuelve a Gemini con sus motivos para que lo corrija (hasta 2 rondas) antes de darlo por perdido.
    guardados, rechazados = [], []
    lote = guiones
    for ronda in range(RONDAS_CORRECCION + 1):
        malos = []
        for i, ep in enumerate(lote):
            if not isinstance(ep, dict):
                rechazados.append((f"#{i}", ["no es un objeto JSON"]))
                continue
            motivos = _validar(ep)
            if motivos:
                malos.append((ep, motivos))
                continue
            slug = re.sub(r"[^a-z0-9_]+", "_", str(ep["slug"]).lower()).strip("_") or f"ep{i}"
            nombre = f"{hoy}_{slug}.json"
            ruta = os.path.join(PENDIENTES, nombre)
            ep["fuente"] = "gemini"
            ep["generado"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if ronda:
                ep["corregido_en_ronda"] = ronda
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(ep, f, ensure_ascii=False, indent=2)
            guardados.append(nombre)
        corregidos = None
        if malos and ronda < RONDAS_CORRECCION:
            print(f"Ronda de corrección {ronda + 1}: {len(malos)} guiones vuelven a Gemini con sus motivos")
            corregidos = _llamar_gemini(_prompt_correccion(malos))
            if isinstance(corregidos, dict):
                corregidos = [corregidos]
        if not isinstance(corregidos, list) or not corregidos:
            rechazados += [(ep.get("slug", "?"), motivos) for ep, motivos in malos]
            break
        lote = corregidos

    resumen = f"{len(guardados)} guardados, {len(rechazados)} rechazados por el validador"
    if rechazados:
        detalle = "; ".join(f"{slug}: {', '.join(m)}" for slug, m in rechazados[:3])
        resumen += f" ({detalle})"
    linea = (
        f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC · Guionista Gemini · pedidos {n} "
        f"guiones para El Jambo · {resumen} · pendientes en equipo/guiones_gemini/pendientes/"
    )
    with open(TABLON, "a", encoding="utf-8") as f:
        f.write(linea + "\n")
    print(linea)
    return 0


if __name__ == "__main__":
    sys.exit(main())
