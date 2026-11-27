# Zernio — tercera vía de TikTok (21/11/2026)

El dueño conectó la cuenta de TikTok (@neogest.lab) y la de Instagram (@neogestlab) en Zernio
mediante el MCP de Zernio dentro de una sesión de Claude ("mcp zernio", orden del dueño). Ese
mismo día: cuenta de TikTok creada y conectada a Buffer, pero Buffer estaba caído por su propia
incidencia. Zernio queda como tercera vía (además de Buffer y Metricool) y, a diferencia de
Metricool, publica/programa de verdad desde el primer día — no solo borrador — porque su API
tiene documentación pública confirmada (`docs_search` del propio MCP) y el post de prueba pasó
`validate_post` sin avisos con el vídeo del Jambo ya subido a Base44.

## Hecho (22/11/2026)

Secreto `ZERNIO_API_KEY` ya creado y guardado en `Deisputnik/neogestlab-redes` (Settings → Secrets
and variables → Actions). Primer run manual de prueba (#2) con la clave real: autenticación OK,
pero falló con 404 `account_not_found` porque la cuenta de TikTok `6b00b30e062d3d918320d801` fijada
en `config.json` ya no existe — se había reconectado bajo un ID nuevo. Corregido: `account_id`
actualizado a `6b01dae0a3545a8f6bb38ad6` (usuario `neogestlab`, sin punto) en `config.json`, leído
en directo con `accounts_list` del MCP de Zernio. Pendiente: relanzar el workflow para confirmar que
ahora programa de verdad.

Nota: este documento mencionaba antes el repo `ajreparacion/instagram` — ese repo quedó abandonado
tras la suspensión de esa cuenta de GitHub (21/11/2026); todo el pipeline vive ahora en
`Deisputnik/neogestlab-redes` (ver `equipo/github-cuenta` o la memoria del proyecto).

## Cómo funciona

> Vigente (27/11/2026, biblia §11.4): `modo: espejo` (publica lo que Instagram ya ha publicado, no hay 2 pasadas fijas) y, si la pieza lleva `"tiktok": {"video_corto": "https://…"}`, se sube esa versión corta (≤ 25 s, sin promo final) en vez del largo; el texto se limpia de «Moraleja» y del reparto (`texto_tiktok`).

- Workflow `.github/workflows/redes_zernio.yml`, dos pasadas al día (12:45 y 19:45, hora de Madrid).
- Reutiliza la misma selección de piezas y el mismo texto por canal que Buffer/Metricool
  (`herramientas/redes_buffer.py`), para que las 3 vías no publiquen nunca el mismo vídeo dos veces.
- Publica con `POST /v1/posts` (contenido + `scheduledFor` + `platforms: [{platform: tiktok,
  accountId}]`), sin forzar `tiktokSettings` — si Zernio algún día exige privacidad/consentimiento
  explícitos, el error de la API lo dirá con el campo exacto y se añade entonces.
- Cuenta ya fijada en `config.json` (`account_id`): `6b01dae0a3545a8f6bb38ad6` (usuario `neogestlab`).

## Si algo falla

`equipo/zernio/estado.json` → `ultimo_error` tiene el mensaje exacto de la última llamada a la
API de Zernio. El Supervisor lo revisa en cada pasada.
