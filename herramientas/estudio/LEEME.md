# El Jambo en Neogest Studio · receta del Creador (biblia v5.2, actualizada 22/11/2026)

Fuente de verdad del formato: `equipo/DIRECTIVA_VIGENTE.md` §5-§7 y `equipo/serie_jambo.md`. Este archivo es solo la receta técnica.
Cada episodio se renderiza en Neogest Studio (Base44 `6af862101565c330cf06389f`, `node scripts/render.mjs spec.json salida.mp4 --hoja`) y se entrega en `cola/NNN_jambo_<slug>/` con `post.json` → `"video_externo": "<URL media.base44.com>"`, `"renderizado": false`, `"motor": "neogest-studio"`. El ciclo descarga el vídeo, lo remasteriza y lo sube a la release; después lo evalúa Calidad.

## Formato (lo que Calidad comprueba)
- **Duración real 45-70 s** (mídela con ffmpeg antes de entregar). Unas 140-170 palabras de voz en 10-11 réplicas dan 62-68 s.
- **Bucle**: apertura y ÚLTIMO plano = la misma tarjeta «Cosas de Casa» (`bookend()`); la apertura lleva el gancho de texto (≤ 8 palabras). Orden de escenas: apertura → episodio → créditos REPARTO → tarjeta de casa. Si el último plano son los créditos, Calidad rechaza. Compara el primer y el último fotograma con ffmpeg.
- **Set** `salon` para los diálogos; reparto Rosa, Felipe, Sindy, Neo, Concha Quetón y Jambo Reseco (Jambo sale en TODO episodio).
- **Registro (22/11, orden del dueño)**: todos muy mal hablados y vulgares, con tacos en casi cada réplica (en mitad de frase o entre exclamaciones, NUNCA como primera palabra de frase); Neo es el único culto y respetuoso. Roles fijos: Felipe = cuñado enterado (sentencia con seguridad cosas falsas), Jambo = gorrón caradura (se apunta a todo, no paga, exige). Humor negro real (frialdad). Un conflicto, escalada en 3 golpes, giro de Neo, moraleja de 6-9 palabras, recuerdo de un episodio anterior.
- **Voz que pasa el control**: cifras en letra, cero inglés («aplicación», no «app»), sin «IA» ni deletreos, ningún nombre propio ni «¡Illo!» como primera palabra de frase, frases cortas. Voces edge-tts por personaje (`VOZ` en `gen_episodios.py`; Jambo −18 % / −12 Hz, rasgada).
- Subtítulos palabra a palabra, logo 2026 y «By Neogest Lab» en los créditos, −14 LUFS, pico ≈ −1 dB, silencios ≤ 0,6 s (el render ya masteriza).

## Pasos (sesión en la nube, MCP `mcp__Base44__*`)
1. En el sandbox: `pip install edge-tts imageio-ffmpeg` y `ln -sf $(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") /usr/local/bin/ffmpeg` (no hay ffmpeg de serie). Playwright/Chrome los instala `render.mjs` solo (minutos la primera vez).
2. Copia `gen_episodios.py` y un `eps.json` a `/tmp/jb/`. Cada episodio: `slug` (empieza por el número), `set`, `hora`, `moraleja`, `escenas` con `e` (gancho|gag|remate|cierre), `h` (hablante), `v` (voz), `t` (texto en pantalla, igual que `v`), `p` (≤ 2 personajes en plano), `a` ({personaje: habla|desespera|delega|presume|fria}), `sello` (remate), `risas`.
3. `python3 gen_episodios.py eps.json /tmp/jb` (imprime la duración de cada spec; ajusta el guion si sale de 45-70 s) y `node scripts/render.mjs /tmp/jb/NNN.json /tmp/jb/<slug>.mp4 --hoja`.
4. Subida: copiar el mp4 a `public/entregas/`, `create_checkpoint`, `POST /api/apps/6af862101565c330cf06389f/deploy` (cuerpo `{}`), esperar a que `https://neogest-studio-cf06389f.base44.app/entregas/<slug>.mp4` dé 200, `upload_app_asset` con esa `fileUrl` → URL `media.base44.com` = `video_externo`. Después borrar el mp4 de `public/entregas/`, checkpoint y deploy.
5. Nota: el sandbox responde a ratos «busy saving background changes»; espera un minuto y repite (no pierde el trabajo de `/tmp`). Los comandos largos se lanzan con `nohup … &` y se consulta el log.
6. Antes de entregar: ffmpeg para medir duración y extraer el primer y el último fotograma; `python3 herramientas/pre_entrega.py` sin ERRORES.

## Promos de app en el estudio (22/11/2026)
Las promos de app que no son El Jambo (108, 107, 801, 802) se generan con `gen_promos.py` y un JSON de guiones como `promos_2026-11-22.json` (clips de la Biblioteca + tomas reales de la app con `camera`, voz edge-tts, cierre `outro` con el logo 2026): `python3 gen_promos.py promos.json /tmp/pr` y luego `node scripts/render.mjs /tmp/pr/<n>.json /tmp/pr/<nombre>.mp4`. Mismo paso 4 para subir. Dos avisos: el sandbox responde «busy saving» varios minutos después de cada render (copia el mp4 a `public/entregas/`): lanza los renders con `nohup` y espera; y si se vuelve a renderizar una pieza, cambia el nombre del mp4 (la URL de `/entregas/` se sirve con caché). El zoom de `camera` sobre una toma de app no debe pasar de 1,3 o el texto se corta.
