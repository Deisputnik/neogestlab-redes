## HyperFrames (herramienta de vídeo, orden del dueño 26/11/2026)
Framework de código abierto de HeyGen (Apache 2.0, https://github.com/heygen-com/hyperframes) para componer y renderizar vídeo. La composición se escribe en HTML/CSS/JS con atributos `data-*` para tiempo y pistas (compatible con GSAP/CSS/Lottie/Three.js, sin React); el CLI captura cada fotograma con Chrome headless y lo codifica con FFmpeg. Paquete npm `hyperframes`, requiere Node 22+ (el sandbox de Neogest Studio ya tiene v24) y FFmpeg.

**Estado:** instalado y probado de extremo a extremo el 26/11/2026 en el sandbox de Neogest Studio (Base44 `6af862101565c330cf06389f`): `npx hyperframes init` → `npm run check` → `npm run render` produjo un MP4 real (1920×1080, H.264, 10 s) sin errores. Ningún formato de producción (El Jambo, promos de app) está migrado todavía — por ahora es la herramienta estándar disponible para cualquier vídeo nuevo, a partir de ahora.

**Dependencias del sandbox (no persisten entre arranques en frío — instalar cada vez antes de usar):**
```
apt-get update && apt-get install -y ffmpeg \
  libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
  libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libasound2 libpango-1.0-0 libcairo2 libatspi2.0-0
```
Sin esto, `npm run check`/`npm run render` fallan porque Chrome headless no encuentra sus librerías compartidas (`libnspr4.so: cannot open shared object file`).

**Comandos:**
- `npx hyperframes init <nombre> --non-interactive` — nuevo proyecto de vídeo (scaffold con `index.html`, `package.json`, `hyperframes.json`).
- `npx hyperframes preview` / `npm run dev` — previsualizar en el navegador.
- `npx hyperframes lint` / `npm run check` — validar la composición ANTES de renderizar (pistas solapadas, `data-composition-id` que falte, contraste WCAG, si hay audio). Pásalo siempre antes de `render`.
- `npx hyperframes render` / `npm run render` — exporta a MP4 (queda en `renders/`).
- `npx hyperframes add <bloque>` — instala un bloque del catálogo (~450: transiciones, subtítulos, gráficos…).

**La voz NO cambia:** sigue siendo ElevenLabs (Johnny) o edge-tts exactamente como dice la Directiva §6 — HyperFrames solo compone la imagen/vídeo y renderiza; el clip de audio ya generado se mete en la composición como cualquier otro recurso de la pista de audio.

**Subida a Base44, igual que siempre:** copiar el MP4 de `renders/` a `public/entregas/` → `create_checkpoint` → deploy → esperar 200 en la URL pública de `entregas/` → `upload_app_asset` con ese `fileUrl` → URL de `media.base44.com` → borrar de `entregas/`, checkpoint, deploy otra vez. Verificar con ffprobe antes de dar el vídeo por bueno.

---

# El Jambo en Neogest Studio · receta del Creador (biblia v5.2, actualizada 22/11/2026)

Fuente de verdad del formato: `equipo/DIRECTIVA_VIGENTE.md` §5-§7 y `equipo/serie_jambo.md`. Este archivo es solo la receta técnica.
Cada episodio se renderiza en Neogest Studio (Base44 `6af862101565c330cf06389f`, `node scripts/render.mjs spec.json salida.mp4 --hoja`) y se entrega en `cola/NNN_jambo_<slug>/` con `post.json` → `"video_externo": "<URL media.base44.com>"`, `"renderizado": false`, `"motor": "neogest-studio"`. El ciclo descarga el vídeo, lo remasteriza y lo sube a la release; después lo evalúa Calidad.

## Formato (lo que Calidad comprueba)
- **Duración real 45-70 s** (mídela con ffmpeg antes de entregar). Unas 140-170 palabras de voz en 10-11 réplicas dan 62-68 s.
- **Bucle**: apertura y ÚLTIMO plano = la misma tarjeta «Cosas de Casa» (`bookend()`); la apertura lleva el gancho de texto (≤ 8 palabras). Orden de escenas: apertura → episodio → créditos REPARTO → **promo de empresa de 3 s** (`promo_empresa()`, orden del dueño 23/11: logo 2026 + «Pide tu prueba gratuita») → tarjeta de casa. Música a 0,34 (0,45 bajo la voz), `MUSICA` en `gen_episodios.py`. Si el último plano son los créditos, Calidad rechaza. Compara el primer y el último fotograma con ffmpeg.
- **Set** `salon` para los diálogos; reparto Rosa, Felipe, Sindy, Neo, Concha Quetón y Jambo Reseco (Jambo sale en TODO episodio).
- **Registro (22/11, orden del dueño)**: todos muy mal hablados y vulgares, con tacos en casi cada réplica (en mitad de frase o entre exclamaciones, NUNCA como primera palabra de frase); Neo es el único culto y respetuoso. Roles fijos: Felipe = cuñado enterado (sentencia con seguridad cosas falsas), Jambo = gorrón caradura (se apunta a todo, no paga, exige). Humor negro real (frialdad). Un conflicto, escalada en 3 golpes, giro de Neo, moraleja de 6-9 palabras, recuerdo de un episodio anterior.
- **Voz que pasa el control**: cifras en letra, cero inglés («aplicación», no «app»), sin «IA» ni deletreos, ningún nombre propio ni «¡Illo!» como primera palabra de frase, frases cortas. Voces diseñadas por personaje (sección «Voces nuevas»); edge-tts (`VOZ` en `gen_episodios.py`) solo de respaldo. Jambo: 12 palabras como mucho por réplica y nadie dice «Jambo» en voz.
- **Expresividad de voz (v6, 23/11/2026, orden del dueño)**: `gen_episodios.py` parte cada réplica en frases y da a cada una su entonación (velocidad, tono y volumen) según la emoción. Pon en cada escena `"emo"`: `grita`, `enfado`, `sorpresa`, `ironia`, `chulea`, `cansado`, `susurra`, `miedo`, `llora`, `rie`, `seco`, `pregunta` o `normal` (los guiones del Guionista ya lo traen: cópialo tal cual). Además manda la puntuación: una exclamación con taco se grita, una pregunta sube, «…» se arrastra con sorna y un golpe de dos o tres palabras sale seco. Por eso el texto se escribe en 2-3 frases cortas por réplica, con interjecciones («¡Buah!», «Pff…», «A ver…»), nunca una frase larga con comas. Necesita ffmpeg (paso 1). Medido: la entonación de una réplica de Rosa pasa de 2,5 a 3,3 semitonos de desviación.
- Subtítulos palabra a palabra, logo 2026 y «By Neogest Lab» en los créditos, −14 LUFS, pico ≈ −1 dB, silencios ≤ 0,6 s (el render ya masteriza).

## Pasos (sesión en la nube, MCP `mcp__Base44__*`)
1. En el sandbox: `pip install edge-tts imageio-ffmpeg` y `ln -sf $(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") /usr/local/bin/ffmpeg` (no hay ffmpeg de serie). Playwright/Chrome los instala `render.mjs` solo (minutos la primera vez).
2. Copia `gen_episodios.py` y un `eps.json` a `/tmp/jb/`. Cada episodio: `slug` (empieza por el número), `set`, `hora`, `moraleja`, `escenas` con `e` (gancho|gag|remate|cierre), `h` (hablante), `v` (voz), `t` (texto en pantalla, igual que `v`), `p` (≤ 2 personajes en plano), `a` ({personaje: habla|desespera|delega|presume|fria}), `sello` (remate), `risas`.
3. `python3 gen_episodios.py eps.json /tmp/jb` (imprime la duración de cada spec; ajusta el guion si sale de 45-70 s) y `node scripts/render.mjs /tmp/jb/NNN.json /tmp/jb/<slug>.mp4 --hoja`.
4. Subida: copiar el mp4 a `public/entregas/`, `create_checkpoint`, `POST /api/apps/6af862101565c330cf06389f/deploy` (cuerpo `{}`), esperar a que `https://neogest-studio-cf06389f.base44.app/entregas/<slug>.mp4` dé 200, `upload_app_asset` con esa `fileUrl` → URL `media.base44.com` = `video_externo`. Después borrar el mp4 de `public/entregas/`, checkpoint y deploy.
5. Nota: el sandbox responde a ratos «busy saving background changes»; espera un minuto y repite (no pierde el trabajo de `/tmp`). Los comandos largos se lanzan con `nohup … &` y se consulta el log.
6. Antes de entregar: ffmpeg para medir duración y extraer el primer y el último fotograma; `python3 herramientas/pre_entrega.py` sin ERRORES.

## Voces nuevas de El Jambo (en producción desde el 23/11/2026, orden del dueño)
Una voz diseñada por personaje con Gemini TTS, gratis con la clave del Guionista (secreto de Actions; no hace falta ninguna clave en la sesión). Límite: 10 peticiones por modelo y día (20 con los dos modelos), y se gasta UNA por personaje y pedido: mete TODOS los episodios de la pasada en el mismo pedido.
1. Escribe `equipo/voces_gemini/pedido.json`: `{"modelos": ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"], "episodios": [<los mismos objetos de eps.json>]}` y súbelo a una rama `voces/<fecha>-<pasada>` (solo ese archivo; desde main no se lanza). Opcional por escena: `voz_tts` (texto para la voz distinto del subtítulo, p. ej. vocales alargadas de Jambo: «Primaaa…»).
2. Espera al workflow «Voces Gemini de un episodio (El Jambo)» (3-8 min): `gh api "repos/Deisputnik/neogestlab-redes/actions/runs?branch=<rama>&per_page=1"`. Cuando acabe, baja el artefacto `voces-gemini` (`gh api repos/.../actions/artifacts/<id>/zip`) y lee `listo.json` (`url`) e `informe.json` (qué se oyó en cada pista; si falta un personaje o `url` es null, usa edge para ese pedido).
3. En el sandbox: `mkdir -p /tmp/jb && cd /tmp/jb && curl -s -o voces.tar "<url>" && tar xf voces.tar` (deja `<n>_<i>.mp3` y `<n>_voces.json`).
4. `VOCES_PREFAB=/tmp/jb/<n>_voces.json python3 gen_episodios.py eps.json /tmp/jb` (un episodio cada vez: el eps.json de esa llamada lleva solo ese episodio) y render como siempre. Sin `edge-tts` instalado también funciona.
5. Comprueba la duración (45-70 s). Jambo va lento a propósito: si te pasas, recorta réplicas, no aceleres.
Si algo falla en los pasos 1-3, sigue con edge-tts (paso 3 de «Pasos») y anótalo en `post.json`: nunca se deja de producir por la voz.

## Promos de app en el estudio (22/11/2026; voz ElevenLabs SIEMPRE desde el 23/11)
Las promos de app que no son El Jambo (108, 107, 801, 802) se generan con `gen_promos.py` y un JSON de guiones como `promos_2026-11-22.json` (clips de la Biblioteca + tomas reales de la app con `camera`, **voz ElevenLabs**, cierre `outro` con el logo 2026): `python3 gen_promos.py promos.json /tmp/pr` y luego `node scripts/render.mjs /tmp/pr/<n>.json /tmp/pr/<nombre>.mp4 --hoja --final`. Mismo paso 4 para subir. Dos avisos: el sandbox responde «busy saving» varios minutos después de cada render (copia el mp4 a `public/entregas/`): lanza los renders con `nohup` y espera; y si se vuelve a renderizar una pieza, cambia el nombre del mp4 (la URL de `/entregas/` se sirve con caché). El zoom de `camera` sobre una toma de app no debe pasar de 1,3 o el texto se corta.


**Voz de las promos de app = ElevenLabs, siempre (orden del dueño 23/11/2026: «en las aplicaciones usamos Eleven siempre»).** `gen_promos.py` ya no genera audio: escribe las escenas con `provider: elevenlabs` (narrador Johnny; asistente Lydia y quien llama Raquel en las recreaciones) y `render.mjs --final` las genera con el secreto `ELEVENLABS_API_KEY` de la app, a través de la ruta local `/api/render-voz` (solo existe en el servidor de desarrollo del sandbox). **No hace falta ninguna clave ni pedirla a nadie**; sin `--final` la voz sale con Piper y la pieza no vale. El render dice cuántos caracteres ha gastado y se para con código 3 si se pasaría del presupuesto mensual (30.000, directiva §6): solo entonces se usa `gen_promos.py … --voz edge` y se anota en `post.json` `"motor_voz": "edge"` y `"_voz_nota": "presupuesto ElevenLabs agotado"`. En el caso normal: `"motor_voz": "elevenlabs"`. Saldo en cualquier momento, desde el sandbox: `curl -s http://localhost:5173/api/render-voz`. Cada escena admite `"emo"`: `normal`, `energia`, `calma`, `sorpresa` o `cercano`. Las frases ya generadas se guardan en caché mientras viva el sandbox (repetir el render no vuelve a gastar).
