# Auditoría de agentes · 22/11/2026 (Coordinación, orden del dueño)

## Directrices de producción y publicación vigentes desde el 22/11/2026
1. **El Jambo que sabe** es un sitcom de salón de barrio de **45-70 segundos**. Los formatos de 15-25 s y el Jambo de oficina están retirados para siempre.
2. **Intro y cierre iguales (bucle):** el vídeo abre y cierra con el MISMO plano de la casa «Cosas de Casa». La apertura lleva un gancho de texto de 8 palabras como máximo (por ejemplo «Esta casa del barrio tiene truco»). Que apertura y cierre coincidan es lo correcto.
3. **Reparto:** Rosa Melano, Felipe Lotas, Sindy Entes, Neo, Concha Quetón y Jambo Reseco (vecino chungo, de poca confianza, voz rasgada, el más mal hablado).
4. **Cómo hablan:** todos con vocabulario vulgar de barrio, sin perder el mensaje. Neo es el único culto y siempre habla con respeto. Humor negro de verdad, moraleja de 6-9 palabras y recuerdo de un episodio anterior.
5. **Ritmo:** 5 episodios nuevos al día, publicados el mismo día, más 1 promo de app aprobada.
6. **Parrilla fija (hora de Madrid):** 08:30, 11:30, 13:40 (promo de app), 16:30, 19:40 y 21:30. Máximo 6 publicaciones por canal y día y al menos 100 minutos entre piezas del mismo canal. Está en `equipo/plan.json`.
7. **Relevo:** si una pieza no tiene nota de 90 o más a 60 minutos de su hueco, ese hueco lo ocupa la siguiente aprobada y la pieza pasa al siguiente hueco libre. Nunca queda un hueco vacío habiendo piezas aprobadas.
8. **Calidad:** el listón sigue en 90. Ahora se evalúa contra este formato (ya no rechaza por «más de 20 s» ni por la foto de la casa del principio).
9. **Orden de las automatizaciones:** Guionista Gemini, Autocrítica (arranca sola al terminar el Guionista), Creador y render, Calidad, publicación en Instagram/Facebook/YouTube, redes extra (TikTok, LinkedIn, Google), Supervisor, Comunidad y Analista. Detalle en la directiva §2.
10. **Cierre fijo** de todo post: «Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso». Prohibido cualquier embudo («comenta X y te envío», «escríbeme X por privado»).
11. **Repo vivo:** `Deisputnik/neogestlab-redes`. El repo `ajreparacion/instagram` está muerto.
12. **Modelos:** Haiku para lo mecánico, Sonnet para redactar, evaluar y programar, Opus solo si Sonnet no basta, nunca Fable.

## Hallazgo n.º 1: por qué no salen episodios nuevos (cuello de botella)
Cadena real: guion → render → mp4 en la release «cola» → nota de Calidad → publicación.
- **Guion:** funciona. El Guionista Gemini deja 3 borradores en `equipo/guiones_gemini/pendientes/` (hoy 3 de 4 pasan el validador). Eslabón sano.
- **Render: es el eslabón roto.** El motor de los episodios (`render.mjs`, `engine.js`, `characters.js`) vive solo dentro de Neogest Studio en Base44 y lo ejecuta únicamente una sesión de Claude Code con el MCP de Base44 (Playwright, ffmpeg, edge-tts, despliegue y `upload_app_asset`). En `herramientas/estudio/` del repo solo están `gen_episodios.py` y el LEEME; no hay workflow que renderice. Creador API solo arregla texto. Resultado: hoy solo existen 2 mp4 nuevos del formato (351 y 353, de la noche del 21/11) y los dos fueron rechazados por Calidad por falsos motivos (ya corregidos).
- **Subida a la release:** automática para vídeos con `video_externo` (el ciclo lo descarga y lo sube).
- **Calidad y publicación:** corren solas, pero las rechazaba por criterios derogados (corregido en esta auditoría) y el control de audio bloqueaba por jerga (corregido).
- **Por qué no lo cerré en Actions:** el render necesita el código fuente de Neogest Studio, que no está en ningún repo ni se puede descargar sin un token de Base44. No se puede montar de forma segura en esta pasada.
- **Propuesta concreta:** (1) activar en Base44 la sincronización de GitHub de Neogest Studio (o exportar su código a `Deisputnik/neogestlab-redes`, carpeta `estudio/`); (2) workflow `render_episodios.yml` con `workflow_dispatch` y un cron moderado de 2 pasadas al día (después de Autocrítica), que instale Playwright, ffmpeg y edge-tts, ejecute `gen_episodios.py` + `render.mjs` sobre los guiones de `pendientes/` y suba el mp4 a la release «cola» creando `cola/NNN/post.json` con `video_externo`; sin bucles ni auto-relanzado. Capacidad: 5 renders de ~1 min por pasada caben de sobra en Actions.
- **Mientras tanto:** el ritmo lo marca la tarea del Creador (09:51 y 15:51). Con una sola pasada manual por tarea es imposible llegar a 5 al día de forma fiable.
- **Otro freno real:** los cron de GitHub se retrasan horas (el Guionista de las 08:15 UTC corrió a las 16:16; el de las 14:15 UTC a las 20:44). Por eso la Autocrítica ahora arranca por `workflow_run` y no por hora.

## Tabla de hallazgos
| Agente / rol / workflow | Hallazgo | Gravedad | Corregido | Commit |
|---|---|---|---|---|
| Directiva §5 (El Jambo) | Tabla con 15-25 s y estructura de oficina, contra la cabecera de 45-70 s | Alta | Sí | 3aae10e |
| Directiva §8 y §12 | «1 episodio al día» y duración 15-25 s | Alta | Sí (5 al día, 45-70 s) | 3aae10e |
| Calidad (`calidad_api.py`) | Prompt alimentado con lecciones de 502-515 («20 s») y sin el formato vigente | Alta | Sí: bloque «FORMATO VIGENTE» primero y filtro de lecciones derogadas | ea81d4c |
| `roles/calidad.md`, `estandar_calidad.md` | «> 30 s», 5 tiempos de oficina, sin criterios del 22/11 | Alta | Sí (estándar v11) | ea81d4c |
| 351 y 353 rechazadas en falso | 20 s derogado; la intro de casa tomada por gancho ajeno | Alta | Criterio corregido; piezas no tocadas (otra sesión) | ea81d4c |
| `control_audio.py` | Bloqueaba por «illo»/jerga y por letras deletreadas (J-A-M-B-O) | Alta | Sí: lista `jerga` y alias en `lexico_control.json`; 351 pasa con 0 diferencias y los 45 casos de prueba siguen OK | ea81d4c |
| `pre_entrega.py` | Avisaba/rechazaba episodios de salón > 25-30 s | Media | Sí (40-70 s para `salon`) | ea81d4c |
| Repo viejo en archivos vivos | Directiva, supervisor.md, publicar_gh.py, 4 scripts, pendiente_usuario, UA | Media | Sí | 80bf74b |
| `atrasos/facebook.json`, `youtube.json` | 22 URLs a la release `centro-v3` del repo viejo; en el repo nuevo esa release NO existe | Alta | No reescritas (los mp4 no están): re-subir a una release nueva o descartar | n/a |
| `cola/801` y `802` | `_video_externo_usado` apunta a rama del repo viejo (solo registro histórico) | Baja | No | n/a |
| Autocrítica Gemini | YAML inválido (llave de más); cron 5 min tras el Guionista | Alta | Sí: reescrito, encadenado por `workflow_run` | e636fcd |
| Comunidad, Calidad API, Metricool, Redes (push) | Fallaban en «Guardar» por `git pull --rebase` con cambios sin añadir | Alta | Sí: `--autostash` en 20 workflows; Calidad rebase con autostash | e636fcd |
| Redes vía Metricool | Falla siempre: faltan 3 secretos | Media | Cron desactivado (queda `workflow_dispatch`) | e636fcd |
| Respuestas del chat | Token de Meta caducado (190): fallaba cada 30 min; cron duplicado del Reloj | Media | Cron propio quitado; el 190 se avisa sin fallo; renovar token = dueño | e636fcd |
| Comunidad (cron) | Cada hora, duplicaba al Reloj | Baja | Respaldo a 4 al día | e636fcd |
| `concurrency` | Faltaba en explorar_web, facebook_prueba, logo_perfil, revozear_centro | Baja | Sí | e636fcd |
| `reloj.yml` | Sin cambios (correcto: pasada corta cada 30 min). Solo 3 ejecuciones programadas el 22/11 | Info | No tocar | n/a |
| Cola | 999 (oficina, nota 45), 349h y 350h (historias caducadas) | Media | Movidas a `descartados/`; mp4 de 18 MB fuera del árbol (sigue en el historial de git) | f37cc7c |
| Cola | 107 y 108 (reels de app sin render, notas 55 y 40) siguen en cola | Baja | No: decide el Creador | n/a |
| Directiva §2 | Mapa desfasado (Calidad 2 al día, cada 15 min, sin Autocrítica ni cadena real) | Media | Sí: reescrito con cron reales UTC/Madrid | 7a97311 |
| Parrilla (§7, §8, `plan.json`) | Huecos repartidos y 2 reels + 5 Jambo > tope de 6 | Media | Sí: `parrilla_diaria` única y relevo | 7a97311 |
| `guionista_gemini.py` | «1 episodio al día», «Neo correcto y neutro» | Media | Sí (5 al día, Neo culto y respetuoso, Jambo Reseco) | 7a97311 |
| `roles/creador.md` | ≥ 3 al día, decorados de oficina, biblia v3, receta de 1,3 s | Media | Sí | 7a97311 |
| `roles/mejora.md`, `roles/supervisor.md` | Menciones a sketch / repo viejo | Baja | Repo viejo sí; sketch es mantenimiento del motor antiguo, se deja | 80bf74b |
| `pre_entrega.py` avisos §14 | Avisos de una orden del 13/11 derogada («sin personaje en el segundo 0», «sin reenvío») | Baja | No: solo avisos, 0 errores | n/a |

## Tareas programadas de Claude (todas las listadas; solo se pueden editar las creadas por agente)
| Tarea | Hallazgo | Acción |
|---|---|---|
| Actualizar memoria - Neogest Lab y redes (cada 3 h) | Leía el repo viejo | **Corregido** el prompt (repo vivo) |
| IG nube · Calidad (repo), Calidad (noche), Ventas, Analista de monetización | Prompts con repo viejo y reglas de 30 s; las 3 primeras desactivadas, el Analista de monetización ACTIVO y duplicado | No editables por mí (creadas por API). Pendiente del dueño; recomiendo desactivar el Analista de monetización |
| IG nube · Cazador de virales | Corre a diario 08:23; el rol dice solo lunes | Recomiendo `0 8 * * 1` (ahorra 6 pasadas por semana) |
| Gemini: procesar cola | Usa Opus; la directiva pide Sonnet salvo necesidad | Recomiendo Sonnet; solo corre con el PC encendido |
| IG nube · Analista (repo) | Última ejecución el 19/11 (martes, jueves y domingo) | Normal; revisar tras el domingo |
| Respaldo de Calidad API (12:41 y 18:41) | Correcto, modelo Haiku | Sin cambios |
| Recordatorios y tareas TikTok (3) | «Revertir apodo/usuario TikTok» chocan con la directiva (@neogestlab es la cuenta de TikTok vigente) | Revisar si siguen vigentes antes del 24/11 |
Horarios ideales propuestos (Madrid, sin cambiar nada yo): Creador 07:51 y 14:51 (para llegar a los huecos de 11:30 y 19:40); Cazador solo lunes; Calidad de respaldo 12:41 y 18:41 como está.

## Solo puede hacerlo el dueño
- Renovar el PAGE_TOKEN de Meta (caducó el 22/11).
- Activar la sincronización de GitHub de Neogest Studio (o exportar su código) para poder renderizar en Actions.
- Pegar `ZERNIO_API_KEY` y `BUFFER_API_KEY`; crear los 3 secretos de Metricool solo si quiere esa vía.
- Editar a mano 4 tareas programadas (prompts viejos) y desactivar el Analista de monetización.
- Decidir qué hacer con los 22 vídeos de `atrasos/` cuyos mp4 estaban en el repo viejo.
