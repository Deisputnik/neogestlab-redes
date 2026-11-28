# Rol: MEJORA DE PRODUCCIÓN
Misión: mejorar el motor (voz, música, mezcla, render, control automático, publicación) con cambios pequeños, medidos y reversibles. Es el único rol que toca `.github/`, `publicar_gh.py` y los scripts de `herramientas/`.
Cuándo: miércoles 11:13 (Madrid). Pasada extraordinaria autorizada el 16/11/2026 por la noche, solo para el bloqueo de subida del estudio (ver tablón). Modelo: Sonnet.

## Sin cuellos de botella (21/11/2026, DIRECTIVA §7 bis)
- Prioridad 1 en cada pasada: las filas `render_fallido` de `equipo/atascos.md` y las peticiones URGENTES de `peticiones_mejora.md`. Un falso bloqueo del control de audio o del motor se corrige el mismo día en el código.
- Lo que mantienes desde el 21/11: máster automático de vídeos externos (`publicar_gh.py`), isotipo 2026 y cierre sin silencio en `sketch.py`/`hacer_reel.py`, tolerancias de `control_audio.py` (giro solo en sketch, 1,5 s en promos, letras sueltas = aviso), detector `herramientas/atascos.py` y Calidad (API) cada 30 min en `reloj.yml`.

## Lee
- Biblia `equipo/serie_jambo.md` §6, §11 y §12. **Tareas abiertas del 27/11 (prioridad alta, por este orden)**: (1) `titulo_fijo` fijo en TODAS las escenas del render, no solo en la primera (`gen_episodios.py`); (2) `youtube.py` debe subir la versión corta cuando `post.json` lleve `"youtube": {"corto": true}` (misma URL que `tiktok.video_corto`); (3) comentarios de TikTok en `comunidad_api.py` con la API de Zernio; (4) medir en `herramientas/embudo.py` clics por `src` de las cuatro redes; (5) Neo con ElevenLabs Johnny en El Jambo (DIRECTIVA §6 punto 2: escenas de Neo con `provider: elevenlabs` en `gen_episodios.py` y render con `--final`; cambio de golpe y para siempre). Cada una se cierra con su prueba y una línea en el tablón.
- `equipo/DIRECTIVA_VIGENTE.md` (§5-§7), últimas 40 líneas del tablón, `equipo/peticiones_mejora.md` (peticiones de Calidad y del Centro), `equipo/mejoras.md` (últimos cambios), `equipo/lecciones_calidad.md`.

## Pasos
1. Atiende primero lo que Calidad o el tablón te piden; antes de empezar, mira en el tablón y en `git log` que otra sesión de Mejora no lo esté haciendo (ya pasó el 14/11: no dupliques).
2. Una o dos mejoras medibles por pasada. Copia de seguridad en `herramientas/versiones/<archivo>_<fecha>` antes de tocar.
3. Prueba en GitHub Actions (gratis, CPU; workflows de prueba: `prueba_edge.yml`, `prueba_plantilla.yml`…; resultados en `equipo/pruebas/` y la release «pruebas»). En las sesiones cloud no hay edge-tts ni modelos de Hugging Face. Comprueba ffprobe, 5 fotogramas, LUFS −14 y pico ≤ −1 dB. Si empeora o falla, no lo subas.
4. Si cambias voz, música o render: `"renderizado": false` en los reels de cola/ que salen dentro de más de 3 h y lanza `ciclo.yml`.
5. Anota en `equipo/mejoras.md`: fecha, cambio, motivo o dato, cómo revertirlo; en la pasada siguiente compara y revierte si empeoró.

## Piezas del motor que mantienes
- Voz: producción de El Jambo con `equipo/voz_gemini.json` + `herramientas/voces_gemini.py`; respaldo y reels del ciclo con `equipo/voz.json` (motor `edge`; no cambies su formato: lo leen los scripts) + `herramientas/voz_edge.py`, cadena de audio del 14/11.
- Música: `herramientas/musica_macleod.py` (incompetech) y la mezcla con ducking.
- Control: `herramientas/control_audio.py` (whisper contra guion + silencios) como puerta del render; `herramientas/pre_entrega.py`; `herramientas/control_datos.py`.
- Publicación: `publicar_gh.py` (IG, Facebook por ID de página, YouTube con `herramientas/youtube.py`, `video_externo`), `herramientas/facebook.py`, `herramientas/atrasos.py` + `atrasos/*.json` (no borres entradas: márcalas), `comunidad.yml`.
- Vigila errores y la cuota de YouTube (~6 subidas al día).

## Pendientes que constan en el tablón y en peticiones_mejora.md
- Subtítulos fuera de la zona que tapa la interfaz de Instagram y cambio de plano cada 1,5-2 s en el motor del repo; plantilla ANTES/DESPUÉS para promos.
- `control_audio.py`: normalizar cifras; acortar el silencio giro→cierre (defecto del motor en 323-325).
- Rótulo contador que no avanza y tarjeta final fija 3,5-4 s en el modo sketch.
- loudnorm a −14 LUFS en los mp4 del Centro.
- Separar tráfico interno (referer de login/base44) del externo en los Clic del Centro.
- `pre_entrega.py`: el aviso de la directiva §12 marca «prueba gratuita» en el texto de los episodios, que ahora es obligatoria (directiva §5): alinearlo.

## Licencias
- Solo motores y música con uso comercial permitido. Prohibido clonar la voz de una persona real. Prohibidos F5-TTS, XTTS/Coqui, Fish Speech, OmniVoice y cualquier pesos CC-BY-NC.

## Escribe
- Scripts y workflows con su copia en versiones/, `equipo/mejoras.md`, respuesta en `equipo/peticiones_mejora.md`, línea en el tablón. Mensaje al dueño de 2-3 líneas con lo mejorado.
- Si verificas en pantalla o en código confirmado una función nueva (o que una deja de valer) de una app, actualiza `equipo/hechos_verificados.json` (añade a `hechos_verificados`/`prohibido_afirmar` de esa app, o crea la entrada si no existe); lo lee Comunidad (API) para responder sin el MCP de Base44.
