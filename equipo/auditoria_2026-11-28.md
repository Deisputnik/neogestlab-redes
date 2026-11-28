# Auditoría completa del equipo de redes · 28/11/2026

Orden del dueño: «haz una auditoría completa y que nada entre en conflicto; revisa los flujos y deja todo escrito». Manda `equipo/DIRECTIVA_VIGENTE.md`. Lo revisado: los 39 workflows de Actions y sus 529 ejecuciones desde el 26/11, las tareas programadas de Claude, los 12 roles frente a la biblia, el código (compilación, tests y referencias a archivos) y las ramas del repo.

## 1. Estado de los flujos (ejecuciones del 26 al 28/11)
| Flujo | Resultado | Nota |
|---|---|---|
| Ciclo Instagram | 62 bien, 2 fallos | Los 2 fallos son del 26/11: choque de push con otro rol; su trabajo quedó en la rama `rescate/ciclo-45888985231` y ya lo han superado ciclos posteriores |
| Reloj | 43 bien | En la práctica corre cada hora (lo lanza la tarea externa «Redes · Reloj externo», 07:07-23:07 Madrid); el cron de GitHub de cada 30 min casi nunca llega a su hora. Sin publicación de 23:07 a 07:07, que queda fuera de la parrilla (08:30-21:30) |
| Calidad API, Comunidad, Respuestas del chat, Repescador, Zernio, Creador API, Supervisor API, Guionista, Autocrítica, Guardia de marca | todos bien | Zernio publica TikTok en espejo con `ZERNIO_API_KEY` ya puesta |
| Voces Gemini | 25 bien, 4 fallos | Fallos por cuota diaria de Gemini TTS agotada (HTTP 429 «exceeded your current quota»). El reintento por minuto ya existe; la cuota diaria no se puede reintentar. Plan B vigente: edge-tts con `"motor_voz": "edge"` (roles/creador.md) |
| Narración del /demo | ARREGLADO hoy | Fallaba por falta de edge-tts tras retirar Kokoro/Melo; ya instala edge-tts y la última ejecución salió bien |
| Metricool | ARREGLADO hoy | Fallaba al guardar un `estado.json` que no existe (sin claves no se genera). Ahora termina bien sin hacer nada. Sigue DESACTIVADO (§2) |
| Buffer | bien, inactivo | Espera `BUFFER_API_KEY` |

## 2. Corregido hoy (en main)
- **Limpieza de motores de voz retirados** (Chatterbox, MeloTTS, Kokoro, Pocket y Piper): fuera de `publicar_gh.py`, `ciclo.yml`, `voz.json` y de los workflows del /demo, revozear y presentador; borrados sus scripts, pruebas y audiciones, y los de clonación de la voz del dueño.
- **Guionista sin embudo** (PR #22 fusionado): las frases largas se recortan una a una y, si queda alguna, el guion llega con `ajustar`.
- **Protección de `main`**: prohibido borrarla y prohibido el push forzado. El push normal sigue igual para todos los roles y las Actions.
- **Biblia §2, §4, §5, §6, §7, §7 bis y §12, alineados con lo que de verdad corre**: horas del Guionista (4 pasadas) y del Repescador tal como las lanza `reloj.yml`; Zernio cada hora sin clave pendiente; Buffer inactivo; Cazador los lunes (así están sus dos tareas programadas); voces de El Jambo = voces diseñadas de Gemini con edge-tts de respaldo; `prueba_no_seguidores` falso salvo orden del dueño; monetización anotada en `equipo/monetizacion.md` (el archivo `estrategia_monetizacion.md` no existía); fuera de §12 los puntos ya decididos.
- **Roles alineados con la biblia**:
  - **Calidad:** cada 30 min; bloqueos B1-B6 y B9; nuevo rechazo de una promo de app con edge-tts sin la nota de saldo agotado.
  - **Supervisor:** horarios reales, parrilla de 6 huecos y vigilancia del saldo de ElevenLabs.
  - **Centro:** se gasta entero el saldo mensual de ElevenLabs (antes tope de 30.000) y prioridades sin fechas viejas.
  - **Creador:** sin calendario archivado; biblia v5.3; Jambo 10 palabras; línea de ElevenLabs en el tablón.
  - **Mejora:** voces de producción, sin `prueba_voz.yml`, y tarea abierta de pasar a Neo a ElevenLabs Johnny.
  - **Repescador:** horas reales.
  - **Analista y Comunidad:** cuatro redes; sin reel de prueba; pasada de las 19:37.
  - **Estratega:** fecha del bucle de §12.
- **Otros archivos**: `pendiente_usuario.md` (Zernio marcado como hecho; la cuenta buena es @neogestlab, sin punto) y título de `estandar_calidad.md` (@neogestlab).
- Comprobado: todo el código Python compila, los tests pasan (7/7), todos los workflows son YAML válido y no queda ninguna referencia a archivos borrados.

## 3. Pendiente del dueño (no lo puede hacer ningún agente)
1. **Desactivar las 11 tareas programadas ANTIGUAS que siguen activas en paralelo con sus «· v2»**. Corren dos veces cada rol, gastan límite y pueden chocar al escribir en main. Ningún agente puede tocarlas: se crearon fuera de un agente. Hay que desactivar estas (sin el «· v2» en el nombre):
   - IG nube · Creador (repo): https://claude.ai/code/routines/trig_017GNtAYqjjfjrUsyDvPVWGW
   - IG nube · Respaldo de Calidad API (Deisputnik, 12:41 y 18:41): https://claude.ai/code/routines/trig_011yXgX84tQBFTREsTSZMZaY
   - IG nube · Supervisor (repo): https://claude.ai/code/routines/trig_01CWpdx3i2MXLhQBuPe23xpt
   - IG nube · Mejora de producción (repo): https://claude.ai/code/routines/trig_01UcnUmobjb9bUfXJiesvZ8Y
   - IG nube · Remasterizador (repo): https://claude.ai/code/routines/trig_01CFkvf9SimiFmbYWSJs5qA8
   - Centro · Mejora continua de vídeos y demos (repo): https://claude.ai/code/routines/trig_01TJBawmtgVbWRj9xPWtguDX
   - IG nube · Estratega (repo): https://claude.ai/code/routines/trig_01J1GEx1xbiFYjQ7KrbeY1xZ
   - IG nube · Analista de monetización (repo): https://claude.ai/code/routines/trig_01KhSAuahbcKFQ6kGDGECM69 (además habla de @iafacil.trucos)
   - IG nube · Analista (repo): https://claude.ai/code/routines/trig_011L4Xmv4cj8bh6sjrzsw6oD
   - IG nube · Cazador de virales (repo): https://claude.ai/code/routines/trig_01FHb2UCLLzSKH8M3LSJ1kSk
   - Redes · Comunidad y monetización (repo): https://claude.ai/code/routines/trig_014A8AZAcr3zJMerP33XD8fj

   Mientras sigan activas, la biblia (§3, punto 0 bis) les manda terminar sin hacer nada. Pero el Creador antiguo trabajó hoy a las 07:51, así que no basta con fiarse de eso.
2. **«IG nube · Analista de monetización (repo) · v2»** (creada hoy, domingos 18:17) choca con la biblia §2: la monetización está fusionada en el Analista de los domingos y su prompt lee `roles/monetizacion.md`, que no existe. Se recomienda desactivarla también (trig_01WMTetmjJhVcromLqvBRUD6); si el dueño la quiere, hay que crear ese rol y anotarlo en §2.
3. `BUFFER_API_KEY` (LinkedIn y Google) y, solo si se quiere esa vía, los 3 secretos de Metricool.
4. **Ramas viejas**: hay 67 ramas además de main (`claude/*` y `voces/*`, del 22 al 28/11, ya integradas o de pedidos de voces ya servidos) y una de rescate. No molestan a la producción. Se pueden borrar desde https://github.com/Deisputnik/neogestlab-redes/branches; los agentes no tienen permiso para borrarlas.

## 4. Para decidir (Estratega o dueño; no se ha tocado)
- Duración de las versiones cortas: la biblia deroga «20, 22 o 35 s» (§5), pero `serie_jambo.md` habla de una versión corta de 20-35 s en YouTube y de ≤ 20 s para las promos en TikTok. En la práctica se usa una sola versión corta de ≤ 25 s para TikTok y YouTube. Propuesta: fijar «versión corta ≤ 25 s en todas las redes; promos en TikTok ≤ 20 s» en §5.
- LinkedIn y Google Business dependen solo de Buffer, que está parado: hace falta otra vía (Zernio, si las admite) o marcarlas como bloqueadas.
- Precios: §9 permite «desde 150 € al mes» para Recepcionista 24h, mientras §12 prohíbe publicar precios. Propuesta: que la prohibición de §12 valga solo para Gestión Integral 7D.
- Cuota diaria de Gemini TTS: con 5 episodios al día y una petición por personaje, se llega al límite. Si se repite, conviene repartir los pedidos de voces entre las pasadas del Creador o pasar más personajes a ElevenLabs con el saldo mensual.
