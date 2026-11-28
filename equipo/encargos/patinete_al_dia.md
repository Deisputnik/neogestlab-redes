# Encargo · Patinete al Día (orden del dueño 28/11/2026)

App: https://patinete-al-dia-5f6b9504.base44.app · ficha Producto `patinete-al-dia` del Centro (hechos_verificados / prohibido_afirmar).

| Pieza | Carpeta | Hueco | Regla |
|---|---|---|---|
| P1 promo (44,5 s) | `cola/708_patinete_al_dia_promo` | 29/11/2026 13:40 | Nombra la cuenta atrás: SOLO antes del 22-1-2027. Si el 21-1-2027 sigue sin publicar, a `descartados/`. |
| P2 tutorial perenne (59,7 s) | `cola/709_patinete_al_dia_tutorial` | 01/12/2026 13:40 | Sin cuenta atrás (cabecera difuminada; texto con fecha del paso 1 tapado). Vale siempre. |
| P3 «Mis vencimientos» (42 s) | `equipo/encargos/patinete_al_dia/710_patinete_al_dia_vencimientos` | 23/01/2027 13:40 | Fuera de `cola/` a propósito para que ningún relevo la adelante. El 22-1-2027 (o después) se mueve a `cola/` tal cual. |

- Vídeo: composición HTML (HyperFrames: `index.html` + GSAP) con capturas reales de la app publicada a 3x y datos ficticios («Patinete de ejemplo (demo)», «SERIE-EJEMPLO-0000»); P3 grabada simulando el 5-2-2027 (la cabecera ya muestra los días para el próximo vencimiento). El render del CLI de HyperFrames se quedaba colgado en la captura en este entorno, así que los fotogramas se capturaron con Playwright sobre la misma composición (seek del timeline) y se codificaron con FFmpeg.
- Voz ElevenLabs Johnny (eleven_multilingual_v2), 1.738 caracteres; mp3 guardados en https://base44.app/api/apps/6ae5244d4e2b32702f0a3cd6/files/mp/public/6ae5244d4e2b32702f0a3cd6/2bd742e2f1a87a1347c6527f8969d4aa_voces_patinete_al_dia_johnny.tgz (frases comunes reutilizables: «Patinete al Día. Enlace en el perfil.», cierre de prueba gratuita de 7D).
- Música MacLeod (Investigations en P1, Life of Riley en P2 y P3) con atribución en el post. −14 LUFS, pico real ≤ −2 dB.
- Portadas (icono neón del Centro + logo 2026, Montserrat): `portada_url` de cada post.json.
- Control: Whisper contra el guion en las tres; sin silencios > 1,5 s; pre_entrega sin errores.
- Pendiente para el Creador si se quiere TikTok: versión ≤ 20 s de P1 (biblia §11.4).
