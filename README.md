# neogestlab-redes · redes de Neogest Lab

Sistema automático de las redes de Neogest Lab (Instagram @neogestlab, Facebook Neogestlab, YouTube NeogestLab y TikTok @neogestlab). Funciona en la nube, sin ningún dispositivo encendido.

**Manda `equipo/DIRECTIVA_VIGENTE.md`** (la biblia). Si algo de este README o de otro archivo la contradice, gana la directiva. Cada rol tiene su archivo en `equipo/roles/`.

## Cómo funciona
- **Guionista y Autocrítica (Gemini, GitHub Actions):** borradores de episodios de *El Jambo que sabe* en `equipo/guiones_gemini/`.
- **Creador (Claude Code):** elige guion y renderiza en Neogest Studio (Base44); deja la pieza en `cola/<NNN_tema>/` (`post.json`, guion y vídeo en la release `cola`).
- **Calidad (`calidad_api.yml`):** aprueba con nota ≥ 90 (`calidad.json`).
- **Ciclo (`ciclo.yml`, lanzado por `reloj.yml` cada 30 min):** `publicar_gh.py` publica en Instagram, Facebook y YouTube lo aprobado, según la parrilla de `equipo/plan.json`, y actualiza `estadisticas.json` y `registro.log`.
- **TikTok:** Zernio en espejo (`redes_zernio.yml`). Buffer y Metricool quedan como vías secundarias.
- Coordinación entre roles: `equipo/tablon.md`. Atascos: `equipo/atascos.md`. Lo que solo puede hacer el dueño: `equipo/pendiente_usuario.md`.

## Carpetas
| Carpeta | Qué hay |
|---|---|
| `cola/` | Piezas pendientes (solo JSON; el vídeo está en la release `cola`) |
| `publicados/` | Piezas publicadas con su `resultado.json` |
| `revision/` · `errores/` · `descartados/` | No aprobadas · fallidas 3 veces · retiradas |
| `atrasos/` | Material aprobado que Facebook y YouTube publican cuando sobra hueco |
| `equipo/` | Directiva, roles, plan, estándar de calidad, voz, tablón; lo antiguo en `equipo/archivo/` (solo consulta) |
| `herramientas/` | Scripts del ciclo, de los agentes API y del estudio (`herramientas/estudio/LEEME.md`) |

## Voz
- Motor de los reels: **edge-tts** (`equipo/voz.json`, `herramientas/voz_edge.py`), una voz por personaje.
- Voces Gemini de los episodios: `herramientas/voces_gemini.py` y `equipo/voz_gemini.json`.
- ElevenLabs (Johnny) para promos de app, vídeos del Centro y reels de datos, desde Neogest Studio.
- Retirados: Chatterbox, MeloTTS, Kokoro, Pocket TTS y Piper. Prohibida la voz del dueño.

## Secretos
Solo en *Settings → Secrets and variables → Actions* (nunca en el repo, que es público): `PAGE_TOKEN`, `FACEBOOK_PAGE_TOKEN`, `YOUTUBE_*`, `PUENTE_TOKEN`, `BUFFER_API_KEY`, `GEMINI_API_KEY`, etc.

Ciclo a mano: *Actions → Ciclo Instagram → Run workflow*.
