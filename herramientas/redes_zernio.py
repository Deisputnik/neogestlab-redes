#!/usr/bin/env python3
"""Redes vía Zernio (API con documentación pública confirmada) — TERCERA vía de publicación en
TikTok, independiente de Buffer (caído por su propia incidencia el 21/11/2026) y de Metricool
(solo borradores, a la espera de confirmar tiktokData). El dueño ya tiene la cuenta @neogestlab (sin punto; «neogest.lab» es otra cuenta, no se usa)
conectada en Zernio (MCP, sesión del 21/11/2026) — mcp zernio, orden del dueño.

Uso: python3 herramientas/redes_zernio.py tiktok [--simular]

A diferencia de Metricool, la API de Zernio SÍ publica/programa de verdad (no solo borrador):
POST https://zernio.com/api/v1/posts con scheduledFor (fecha exacta) + platforms:[{platform,
accountId}]. Sin ajustes de tiktokSettings el post pasa validate_post sin avisos (comprobado en
vivo el 21/11/2026), así que no se fuerzan privacy_level/consentimientos a mano: si Zernio los
exige algún día, el error de la API lo dirá y se añade entonces (cero alucinaciones).

Reutiliza TAL CUAL la selección de piezas, el texto por canal y la subida a la release pública
«redes» de herramientas/redes_buffer.py (misma fuente de verdad, canal nuevo: equipo/zernio/).
No repite nunca lo que Buffer o Metricool ya mandaron a la misma cuenta de TikTok.

Secretos: ZERNIO_API_KEY (obligatorio; se crea una sola vez en https://zernio.com/dashboard/api-keys
y lo pega el dueño en el repo — ver equipo/zernio/LEEME.md). Sin él, o sin canal conectado, no hace
nada y termina bien: el canal queda en espera. --simular enseña qué enviaría, sin llamar a nada.
"""
import glob  # noqa: F401  (se usa dentro de candidatos(), importado vía redes_buffer)
import json
import urllib.parse
import re
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redes_buffer import RAIZ, candidatos, huecos_libres, leer, escribir, texto_canal, medio_publico  # noqa: E402

ZERNIO = "https://zernio.com/api/v1"


def _pedir(metodo, ruta, api_key, cuerpo=None):
    req = urllib.request.Request(
        ZERNIO + ruta,
        data=json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None,
        method=metodo,
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"Zernio {metodo} {ruta}: HTTP {e.code} — {detalle}")


def cuenta_tiktok(api_key, usuario):
    """Id de la cuenta de TikTok conectada en Zernio por nombre de usuario; None si no está."""
    datos = _pedir("GET", "/accounts?platform=tiktok", api_key)
    for c in datos.get("accounts", datos if isinstance(datos, list) else []):
        if usuario.lstrip("@").lower() in str(c.get("username", "")).lower():
            return c.get("id") or c.get("_id")
    return None


def _clave_texto(texto):
    """Arranque del texto sin signos ni mayúsculas: sirve para reconocer el mismo vídeo aunque el texto se retocara a mano."""
    return re.sub(r"[^a-z0-9áéíóúñü]", "", str(texto).lower())[:30]


def ya_en_zernio(api_key):
    """Claves de texto de lo que Zernio ya tiene publicado, publicándose o programado en la cuenta.
    23/11/2026: el 21-22/11 se cruzaron a mano 36 vídeos a TikTok desde una sesión con el MCP de Zernio y este script no lo
    sabía (su estado.json solo recuerda lo que programa él): volvió a programar 6 vídeos que ya estaban en TikTok («El
    presupuesto cerrado» iba por la cuarta copia). Ahora se pregunta a Zernio antes de programar. Si la consulta falla, se
    devuelve None y el script NO programa nada en esa pasada (mejor un hueco vacío que un duplicado)."""
    claves = set()
    try:
        primero_anterior = None
        for pagina in range(1, 21):
            datos = _pedir("GET", f"/posts?limit=50&page={pagina}", api_key)
            posts = datos.get("posts") or datos.get("data") or []
            primero = (posts[0].get("_id") or posts[0].get("id")) if posts else None
            if not posts or primero == primero_anterior:   # sin más páginas (o la API ignora «page»)
                break
            primero_anterior = primero
            for p in posts:
                if str(p.get("status", "")).lower() in ("failed", "cancelled", "draft"):
                    continue
                plataformas = p.get("platforms") or []
                if plataformas and not any(str(x.get("platform", "")).lower() == "tiktok" for x in plataformas):
                    continue
                c = _clave_texto(p.get("content", ""))
                if c:
                    claves.add(c)
            paginas = (datos.get("pagination") or {}).get("pages")
            if paginas and pagina >= int(paginas):
                break
        print(f"zernio: {len(claves)} textos distintos ya publicados o programados en la cuenta")
    except Exception as e:
        print("zernio: no se pudo leer lo ya publicado:", str(e)[:300])
        return None
    return claves


def medio_zernio(api_key, nombre, post, res, canal):
    """URL pública del vídeo para Zernio. 23/11/2026: antes se subía a la release «redes» de GitHub (medio_publico), pero el
    repo es PRIVADO desde la migración y esa URL da 404 a quien no tenga sesión: ningún vídeo programado por este script podía
    publicarse. Ahora el vídeo se baja de Instagram (el reel ya publicado y aprobado) y se sube al almacenamiento de Zernio
    (POST /media/presign + PUT), que devuelve una URL pública. Si Instagram no da el fichero (música con licencia), se usa el
    vídeo externo original de la pieza, que ya es público (media.base44.com)."""
    fichero = "/tmp/%s_%s.mp4" % (canal, nombre)
    try:
        pub = leer(os.path.join(RAIZ, "equipo", "config_publico.json"), {})
        url = "https://graph.facebook.com/%s/%s?%s" % (pub.get("version", "v27.0"), res["media_id"], urllib.parse.urlencode(
            {"fields": "media_url", "access_token": os.environ["PAGE_TOKEN"]}))
        with urllib.request.urlopen(url, timeout=60) as r:
            media = json.load(r).get("media_url")
        if not media:
            raise RuntimeError("Instagram no da media_url")
        urllib.request.urlretrieve(media, fichero)
        if os.path.getsize(fichero) < 200_000:
            raise RuntimeError("vídeo descargado demasiado pequeño")
        pre = _pedir("POST", "/media/presign", api_key, {"filename": os.path.basename(fichero), "contentType": "video/mp4"})
        with open(fichero, "rb") as f:
            datos = f.read()
        req = urllib.request.Request(pre["uploadUrl"], data=datos, method="PUT", headers={"Content-Type": "video/mp4"})
        with urllib.request.urlopen(req, timeout=600):
            pass
        return pre["publicUrl"]
    except Exception as e:
        externo = post.get("video_externo") or post.get("_video_externo_usado")
        if isinstance(externo, str) and externo.startswith("https://"):
            print(f"{nombre}: sin copia de Instagram ({str(e)[:120]}); se usa el vídeo externo de la pieza")
            return externo
        raise


def crear_post(api_key, account_id, texto, cuando_iso, url):
    cuerpo = {
        "content": texto,
        "mediaItems": [{"type": "video", "url": url}],
        "scheduledFor": cuando_iso,
        "platforms": [{"platform": "tiktok", "accountId": account_id}],
    }
    r = _pedir("POST", "/posts", api_key, cuerpo)
    post = r.get("post") or r.get("data") or r
    pid = r.get("id") or post.get("id") or post.get("_id")
    if not pid:
        raise RuntimeError(f"Zernio no confirmó el id del post creado: {json.dumps(r)[:300]}")
    return pid


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    canal = args[0] if args else ""
    if canal not in ("tiktok",):
        raise SystemExit("Uso: redes_zernio.py tiktok [--simular]  (de momento solo tiktok)")
    simular = "--simular" in sys.argv
    carpeta = os.path.join(RAIZ, "equipo", "zernio")
    cfg = leer(os.path.join(carpeta, "config.json"), {})
    ruta_estado = os.path.join(carpeta, "estado.json")
    estado = leer(ruta_estado, {"enviados": {}, "ultimo_error": ""})
    ahora = datetime.now(timezone.utc)
    ahora_iso = ahora.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    pendientes = sum(1 for v in estado["enviados"].values() if v.get("dueAt", "") > ahora_iso)
    cupo = max(0, cfg.get("max_pendientes", 8) - pendientes)
    # MISMA cuenta de TikTok que Buffer/Metricool (equipo/tiktok y equipo/metricool): nunca repetir
    # lo que ya se mandó por esas vías, para que las 3 vías sean respaldo/variedad, no duplicado.
    estado_buffer = leer(os.path.join(RAIZ, "equipo", canal, "estado.json"), {"enviados": {}})
    estado_metricool = leer(os.path.join(RAIZ, "equipo", "metricool", "estado.json"), {"enviados": {}})
    estado_para_elegir = {"enviados": {**estado_buffer.get("enviados", {}), **estado_metricool.get("enviados", {}),
                                        **estado["enviados"]}}
    lista = candidatos(cfg, estado_para_elegir)
    print(f"zernio/{canal}: {pendientes} programados, cupo {cupo}, {len(lista)} piezas disponibles")
    if simular:
        for (nombre, post, _), cuando in zip(lista, huecos_libres(cfg, estado, ahora)):
            print(f"\n=== {nombre} · {cuando}\n{texto_canal(nombre, post, cfg, canal)}")
        return
    api_key = os.environ.get("ZERNIO_API_KEY")
    if not api_key:
        print(f"zernio/{canal} en espera: falta el secreto ZERNIO_API_KEY (ver equipo/zernio/LEEME.md).")
        return
    antes = json.dumps(estado, sort_keys=True)
    try:
        account_id = cfg.get("account_id") or cuenta_tiktok(api_key, cfg.get("usuario", "neogestlab"))
        if not account_id:
            print(f"zernio/{canal} en espera: esa cuenta no está conectada en Zernio todavía.")
            return
        existentes = ya_en_zernio(api_key)
        if existentes is None:
            estado["ultimo_error"] = f"{ahora_iso} · no se pudo leer de Zernio lo ya publicado; no se programa nada en esta pasada"
            lista = []
        else:
            nuevas = []
            for nombre, post, res in lista:
                if _clave_texto(texto_canal(nombre, post, cfg, canal)) in existentes:
                    estado["enviados"][nombre] = {"dueAt": "", "ya_en_tiktok": True, "enviado": ahora_iso}
                    print(f"{nombre}: ya está en TikTok (o programado) según Zernio; no se repite")
                else:
                    nuevas.append((nombre, post, res))
            lista = nuevas
        if cfg.get("modo") == "espejo":
            # 23/11/2026 (orden del dueño: «los mismos 5 vídeos en las 3 redes»): TikTok publica lo mismo que Instagram y el
            # mismo día. Cada pasada (una por hora, desde reloj.yml) manda lo que Instagram ya ha publicado y TikTok aún no
            # tiene: la primera pieza sale en 5 minutos y, si hay más de una pendiente, las siguientes cada 100 minutos.
            cupo = min(cupo, int(cfg.get("max_por_pasada", 3)))
            cuandos = ((ahora + timedelta(minutes=5 + 100 * i)).strftime("%Y-%m-%dT%H:%M:%S.000Z") for i in range(cupo))
        else:
            cuandos = huecos_libres(cfg, estado, ahora)
        for (nombre, post, res), cuando in zip(lista[:cupo], cuandos):
            try:
                url = medio_zernio(api_key, nombre, post, res, canal)
                pid = crear_post(api_key, account_id, texto_canal(nombre, post, cfg, canal), cuando, url)
            except Exception as e:   # una pieza que falla no bloquea a las demás; se reintenta en la pasada siguiente
                estado["ultimo_error"] = f"{ahora_iso} · {nombre}: {e}"[:500]
                print(f"ERROR zernio/{canal} en {nombre}:", str(e)[:300])
                continue
            estado["enviados"][nombre] = {"dueAt": cuando, "zernio_id": pid, "enviado": ahora_iso,
                                          "fichero": os.path.basename(url)}
            estado["ultimo_error"] = ""
            escribir(ruta_estado, estado)
            print(f"{nombre}: programado en Zernio/{canal} para {cuando}")
    except Exception as e:
        estado["ultimo_error"] = f"{ahora_iso} · {e}"[:500]
        print(f"ERROR zernio/{canal}:", estado["ultimo_error"])
    if json.dumps(estado, sort_keys=True) != antes:
        escribir(ruta_estado, estado)


if __name__ == "__main__":
    main()
