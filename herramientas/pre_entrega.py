#!/usr/bin/env python3
"""PRE-ENTREGA: revisa en segundos, antes de pasar a Calidad, lo que se puede comprobar sin ver el vídeo.
Uso: python3 herramientas/pre_entrega.py [cola/NNN_carpeta ...]   (sin argumentos: toda cola/)
         --stats   ademas escribe equipo/lecciones_calidad.md (aprobacion, motivos de rechazo mas repetidos)
Sale con codigo 1 si hay algun ERROR. Gratis, CPU, sin red. Cubre B1 (gancho > 8 palabras), B6 (cierres antiguos «comenta X»),
B8 (comentario fijado, avance), B9 (marcas ajenas), voz del dueño prohibida, textos repetidos y reels a la misma hora.
Desde el 14/11 (cambio 66) también la lista de Calidad del 13/11 para reels que salen antes de diciembre: ≤ 20 s (ERROR > 35 s en la serie),
reenvío a una persona, sin enlace en el texto, sin venta dentro del vídeo, rótulo marca_serie desde el 16/11, APP/WEB en el comentario fijado y personaje en el segundo 0.
Los AVISOS no bloquean; los ERRORES se corrigen antes de entregar. Lo que Calidad rechaza dos veces por el mismo motivo
se convierte aqui en una comprobacion nueva (ver equipo/BUCLE_APRENDIZAJE.md)."""
import sys, os, re, json, glob, unicodedata, collections
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
def cargar(p):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return None
def textos(o):
    """Todas las cadenas de un guion o post (texto, voz, subtitulos...), sin las claves que empiezan por _."""
    if isinstance(o, str): yield o
    elif isinstance(o, list):
        for x in o: yield from textos(x)
    elif isinstance(o, dict):
        for k, v in o.items():
            if not str(k).startswith("_"): yield from textos(v)
MARCAS = [norm(m) for m in (cargar(os.path.join(RAIZ, "equipo", "marcas_prohibidas.json")) or {}).get("marcas", [])]
CIERRE_ANTIGUO = re.compile(r"\b(comenta|escr[ií]beme|escribeme)\s+[«\"“]?[A-ZÁÉÍÓÚÑ]{3,}", re.I)

def revisar(carpeta):
    e, a = [], []
    post = cargar(os.path.join(carpeta, "post.json")) or cargar(os.path.join(carpeta, "post.pendiente.json")) or {}
    guion = cargar(os.path.join(carpeta, "guion.json")) or {}
    tipo = post.get("tipo")
    todo = norm(" ".join(textos(post) )) + " " + norm(" ".join(textos(guion)))
    for m in MARCAS:
        if re.search(r"(?<![a-z0-9])" + re.escape(m) + r"(?![a-z0-9])", todo): e.append("B9 marca ajena en texto/guion: «%s»" % m)
    crudo = json.dumps(guion, ensure_ascii=False) + json.dumps(post, ensure_ascii=False)
    for pal in ("voz_dueno", "referencia_usuario", "clon_dueno"):
        if pal in crudo and not pal in json.dumps({k: v for k, v in post.items() if str(k).startswith("_")}, ensure_ascii=False):
            e.append("VOZ del dueño prohibida: aparece «%s»" % pal)
    if guion.get("modo") == "datos":   # modo datos: ficha completa y verificada, sin ensayo (herramientas/datos.py, equipo/FORMATO_DATOS.md)
        try:
            sys.path.insert(0, os.path.join(RAIZ, "herramientas")); import datos
            est, ver = datos.problemas_ficha(guion)
            for m in est + ver: e.append("DATOS ficha: " + m)
        except Exception as ex: a.append("DATOS no se pudo revisar la ficha: %s" % str(ex)[:80])
    if tipo == "reel":
        t = post.get("texto", "")
        if CIERRE_ANTIGUO.search(t): e.append("B6 cierre antiguo «comenta/escríbeme X» en el texto del post")
        if any(CIERRE_ANTIGUO.search(x) for x in textos(guion)): e.append("B6 cierre antiguo «comenta/escríbeme X» en la voz o el texto del guion")
        if not post.get("monetizacion"): a.append("MONETIZACIÓN falta el bloque «monetizacion» en post.json: {\"objetivo\": \"visita_perfil|clic_enlace|solicitud|dm\", \"oferta\": \"qué se ofrece\", \"paso_embudo\": \"el paso de equipo/embudo.md que mueve\"}")
        if not post.get("comentario_fijado"): a.append("B8 falta comentario_fijado")
        if not post.get("avance_siguiente"): a.append("B8 falta avance_siguiente")
        esc = guion.get("escenas") or []
        g = next((x for x in esc if x.get("estilo") in ("gancho", None) and x.get("texto")), None)
        txt = (guion.get("gancho_corto") or (g or {}).get("texto") or "")
        n = len(re.sub(r"[*¡!¿?«»]", "", txt).split())
        if txt and n > 8: a.append("B1 gancho de %d palabras (máximo 8): «%s»" % (n, txt[:60]))
        # Directiva 15/11 §5: el post de un episodio de El Jambo cierra con la prueba gratuita (con enlace /solicitar) y la pregunta
        if "jambo" in os.path.basename(carpeta) and not re.search(r"prueba gratuita", t, re.I):
            a.append("§5 el texto del post de un episodio no lleva el cierre «Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso» con el enlace /solicitar")
        revisar_14(carpeta, post, guion, e, a)
        revisar_26(carpeta, post, guion, e, a)
    return e, a

def revisar_26(carpeta, post, guion, e, a):
    """26/11/2026 (orden del dueño: «Calidad siempre rechaza al Creador»): los motivos de rechazo más repetidos del 20-26/11
    que se pueden ver sin abrir el vídeo pasan a ERROR aquí, para que el Creador los corrija ANTES de entregar."""
    nombre = os.path.basename(carpeta)
    jambo = "jambo" in nombre
    mv = str(post.get("motor_voz") or "")
    nota_voz = bool(post.get("_voz_nota"))
    if jambo and str(post.get("motor") or "") == "neogest-studio":
        if mv != "voz_disenada" and not nota_voz:
            e.append("VOZ episodio con motor_voz «%s»: debe ser \"voz_disenada\" (voces Gemini, LEEME «Voces nuevas») o llevar _voz_nota con el fallo/cuota" % (mv or "falta"))
        if "scenes" in guion and "escenas" not in guion:
            e.append("GUION guion.json es el spec de render (scenes/format): guarda el guion del episodio (escenas, moraleja, giro, recuerdo)")
        if not guion.get("giro"):
            e.append("GIRO falta el campo «giro» en guion.json (6-14 palabras: qué se creía y qué resulta ser; estándar retención v12)")
        if not guion.get("recuerdo"):
            e.append("RECUERDO falta el campo «recuerdo» en guion.json (episodio anterior ya publicado, dicho en una réplica)")
        elif not (lambda cl: not cl or any(sum(w in norm(x) for w in cl) >= max(1, len(cl) // 2) for x in textos(guion.get("escenas") or [])))(
                [w for w in re.findall(r"[a-z]{5,}", norm(guion["recuerdo"])) if w not in ("mismo", "misma", "vecino", "todos", "mundo")]):   # palabras clave, admite paráfrasis
            a.append("RECUERDO el campo «recuerdo» no aparece en ninguna réplica: tiene que decirlo un personaje")
        dif = (cargar(os.path.join(RAIZ, "equipo", "voz_palabras_dificiles.json")) or {}).get("palabras") or {}
        voz = " ".join(str(x.get("v") or x.get("t") or "") for x in (guion.get("escenas") or []) if isinstance(x, dict))
        if not isinstance(post.get("renderizado"), str):   # solo lo que aún no se ha renderizado (lo ya renderizado lo juzga Calidad)
            for w in dif:
                if re.search(r"(?<![a-z])" + re.escape(norm(w)) + r"(?![a-z])", norm(voz)):
                    e.append("VOZ palabra que la voz diseñada dice mal: «%s» (equipo/voz_palabras_dificiles.json): cámbiala antes del pedido de voces" % w)
            for x in (guion.get("escenas") or []):
                if isinstance(x, dict) and x.get("h") == "jambo" and len(str(x.get("v") or x.get("t") or "").split()) > 10:
                    a.append("VOZ réplica de Jambo de más de 10 palabras: más riesgo de fallo de dicción")
        if (post.get("musica") or guion.get("musica")) and not re.search(r"m[uú]sica\s*:", post.get("texto", ""), re.I):
            e.append("MÚSICA falta la atribución «Música: …» en el texto del post (rechazo automático de Calidad)")
    elif (not jambo and (post.get("app") or post.get("app_slug")) and str(post.get("motor") or "") == "neogest-studio"
          and not (isinstance(post.get("renderizado"), str) and post["renderizado"][:10] < "2026-11-24")):   # orden 23/11: renders desde el 24/11
        if mv != "elevenlabs" and not nota_voz:
            e.append("VOZ promo de app con motor_voz «%s»: debe ser \"elevenlabs\" (gen_promos.py + render.mjs --final) o llevar _voz_nota de cuota agotada" % (mv or "falta"))

# ---- Lista de Calidad del 13/11 (virales_13_11_navegador.md §6 y DIRECTIVA §14), la parte que se puede medir sin ver el vídeo ----
VENTA_EN_VIDEO = re.compile(r"prueba gratuita|sin compromiso|sin tarjeta|pide tu|ajreparacion|maqueta|m[aá]s asequibles|\bdesde\s+\d+\s?€|\d+\s?€\s?/\s?mes", re.I)   # «presupuesto» y las cifras en euros del gag NO cuentan: son tema de la historia, no venta
ENLACE = re.compile(r"https?://|www\.|\b[a-z0-9-]+\.(com|es|app|net|org)\b", re.I)
REENVIO = re.compile(r"\b(env[ií]aselo|m[aá]ndaselo|p[aá]saselo|reenv[ií]aselo|comp[aá]rtelo|env[ií]alo|m[aá]ndalo|reenv[ií]alo)\b|\b(env[ií]a|manda|reenv[ií]a|pasa)\w*\s+(esto|este|este reel|el reel)?\s*a\b", re.I)
HUECO_INICIO_DIA = "2026-12-01"   # lo aparcado para después (31/12, diciembre) no se avisa: aún no hay decisión sobre ello

def duracion_s(carpeta, guion):
    """Duración real del último render (voz_musica.json) o, si no hay render, la suma de lo que dura cada escena según locucion.json."""
    post = cargar(os.path.join(carpeta, "post.json")) or {}
    vm = cargar(os.path.join(carpeta, "voz_musica.json")) or {}
    if post.get("renderizado") is False:   # el vídeo está obsoleto (pendiente de re-render): se estima desde el guion, regla del Creador 14/11: 1,1 s + 0,35 s por palabra de voz
        esc = (guion or {}).get("escenas") or []
        if esc:
            t = sum(float(x["duracion"]) if isinstance(x.get("duracion"), (int, float)) else 1.1 + 0.35 * len((x.get("voz") or "").split()) for x in esc)
            return t, "estimada desde el guion"
    if isinstance(vm.get("duracion_s"), (int, float)): return float(vm["duracion_s"]), "render"
    loc = cargar(os.path.join(carpeta, "locucion.json"))
    if isinstance(loc, list) and loc:
        try: return max(float(x["inicio"]) + float(x["duracion"]) for x in loc), "locución"
        except Exception: pass
    return None, ""

def revisar_14(carpeta, post, guion, e, a):
    """Solo para reels que salen antes de HUECO_INICIO_DIA. Todo AVISO salvo > 35 s en la serie (límite duro de Calidad)."""
    cuando = str(post.get("cuando") or "")
    if not cuando or cuando[:10] >= HUECO_INICIO_DIA: return
    nombre = os.path.basename(carpeta)
    serie = bool(guion.get("serie")) or "jambo" in nombre or "ias_oficina" in nombre
    texto = post.get("texto", "")
    d, de = duracion_s(carpeta, guion)
    salon = (guion.get("set") == "salon")
    if serie and d is not None and salon and not (40 <= d <= 70):   # directiva 22/11 §5: episodios de salón de 45-70 s
        a.append("§5 dura %.1f s (%s): el formato de salón pide 45-70 s" % (d, de))
    elif serie and d is not None and not salon and d > 70:
        e.append("§5 dura %.1f s (%s): pasa de 70 s" % (d, de))
    if not REENVIO.search(texto) and not REENVIO.search(" ".join(textos(guion))):
        a.append("§14 sin reenvío a una persona concreta (p. ej. «Envíaselo a ese compañero que…»)")
    if serie:
        # La venta va solo en el comentario fijado y la bio: ni en las escenas del vídeo ni en el texto
        venta = [x for x in textos(guion) if VENTA_EN_VIDEO.search(x)]
        if venta: a.append("§14 venta dentro del vídeo (precio, prueba gratuita, presupuesto, dominio…): «%s»" % venta[0][:50])
        if guion.get("modo") == "sketch" and cuando[:10] >= "2026-11-16" and not guion.get("marca_serie"):
            a.append("§13 falta marca_serie («@neogestlab · episodio nuevo cada día») en un episodio que sale desde el 16/11")
    esc = guion.get("escenas") or []
    if guion.get("modo") in ("app", "datos") and not serie:
        a.append("§14 sin personaje en el segundo 0 (reel de %s sin personaje): hueco libre salvo permiso de Calidad" % guion.get("modo"))
    elif guion.get("modo") == "sketch" and esc and guion.get("estilo") != "texto" and esc[0].get("estilo") != "texto":
        if not ((esc[0].get("dibujo") or {}).get("personajes")): a.append("§14 la primera escena no tiene personaje (dibujo.personajes vacío)")

def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    cs = [a.rstrip("/") for a in args] or sorted(glob.glob(os.path.join(RAIZ, "cola", "*")))
    tot_e = 0; primeras = collections.defaultdict(list); cuando = collections.defaultdict(list)
    for c in cs:
        if not os.path.isdir(c): continue
        e, a = revisar(c)
        post = cargar(os.path.join(c, "post.json")) or cargar(os.path.join(c, "post.pendiente.json")) or {}
        if post.get("tipo") == "reel" and post.get("cuando"): cuando[post["cuando"]].append(os.path.basename(c))
        l1 = norm((post.get("texto") or "").split("\n")[0]).strip()
        if l1: primeras[l1].append(os.path.basename(c))
        for m in e: print("ERROR  %s: %s" % (os.path.basename(c), m))
        for m in a: print("AVISO  %s: %s" % (os.path.basename(c), m))
        tot_e += len(e)
    for l1, v in primeras.items():
        if len(v) > 1: print("AVISO  primera línea repetida en %s" % ", ".join(v)); 
    for k, v in cuando.items():
        if len(v) > 1: print("ERROR  reels a la misma hora %s: %s" % (k, ", ".join(v))); tot_e += 1
    print("pre_entrega: %d carpetas, %d errores" % (len(cs), tot_e))
    if "--stats" in sys.argv: stats()
    sys.exit(1 if tot_e else 0)

def stats():
    n = ok = 0; notas = []; motivos = collections.Counter(); ult = []
    for f in sorted(glob.glob(os.path.join(RAIZ, "cola", "*", "calidad.json"))):
        c = cargar(f) or {}; n += 1; ok += bool(c.get("aprobado")); 
        if isinstance(c.get("nota"), (int, float)): notas.append(c["nota"])
        if not c.get("aprobado"):
            for m in c.get("motivos") or []:
                cods = set(re.findall(r"\bB[1-9]\b", m))
                if re.search(r"cierre antiguo|comenta/escr", m, re.I): cods.add("CIERRE (comenta/escríbeme X)")
                if re.search(r"marca (bancaria )?ajena|CaixaBank", m, re.I): cods.add("B9")
                for cod in cods or {"otro"}: motivos[cod] += 1
            ult.append((os.path.basename(os.path.dirname(f)), c.get("nota"), (c.get("motivos") or [""])[0][:140]))
    L = ["# Lecciones de Calidad (generado por herramientas/pre_entrega.py --stats; no editar a mano)", "",
         "Piezas con calidad.json: %d · aprobadas: %d (%.0f %%) · nota media: %.1f" % (n, ok, 100.0 * ok / max(1, n), sum(notas) / max(1, len(notas))), "",
         "## Motivos de rechazo más repetidos (los que no están en pre_entrega.py como comprobación automática, hay que añadirlos)"]
    for k, v in motivos.most_common(): L.append("- %s: %d" % (k, v))
    L += ["", "## Rechazadas ahora mismo"] + ["- %s (%s): %s" % u for u in ult]
    open(os.path.join(RAIZ, "equipo", "lecciones_calidad.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("equipo/lecciones_calidad.md escrito")
if __name__ == "__main__": main()
