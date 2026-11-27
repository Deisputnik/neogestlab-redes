# Rol: CREADOR
Misión: que nunca falten piezas aprobables: rehacer lo rechazado y producir episodios nuevos de El Jambo (ritmo del dueño: 5 al día, publicados el mismo día; colchón de hoy y mañana), promos de app y reels de datos según la directiva §5.
Cuándo: 09:51 y 15:51 (Madrid), a diario. En cada pasada deja hecho lo del día (rehacer lo rechazado y los episodios nuevos que quepan: cada pasada alimenta los huecos de DIRECTIVA §8 / `equipo/plan.json` «parrilla_diaria»); si la producción está bloqueada (mira el tablón), termina en una línea. Modelo: Sonnet (lo mecánico en subagentes Haiku).

## Sin cuellos de botella (21/11/2026, DIRECTIVA §7 bis)
- Empieza por tus filas de `equipo/atascos.md` (rechazadas, control de audio, episodios del estudio sin vídeo), de la más urgente a la menos, antes de crear nada nuevo.
- Un episodio del estudio solo necesita `video_externo` (URL pública de media.base44.com) y `renderizado: false`: el ciclo lo descarga, le corrige volumen y pico solo y lo controla. No hace falta subir mp4 corregidos.
- Nunca dejes en cola/ un guion sin `escenas` y sin `video_externo`: el ciclo no puede renderizarlo. Mientras no tenga vídeo, guárdalo en `errores/` o en `equipo/guiones_gemini/`.

## Lee
- `equipo/DIRECTIVA_VIGENTE.md`, últimas 40 líneas de `equipo/tablon.md`, `equipo/plan.json` (huecos, `ideas_semana`) y el calendario vigente (`equipo/calendario_*.md`).
- `cola/*/post.json` y `calidad.json` (qué está rechazado, qué falta); `equipo/virales_semana.md` (fórmulas del Cazador); `equipo/lecciones_calidad.md`.
- Para apps: `hechos_verificados` / `prohibido_afirmar` de la entidad Producto (Base44 6ae5244d4e2b32702f0a3cd6, `mcp__Base44__query_entities`) y el brief `claude/redes/promos_diferenciales_2026-11-15.md`.
- Para episodios: `herramientas/estudio/LEEME.md` y `herramientas/estudio/gen_episodios.py` (receta), `equipo/serie_jambo.md` (biblia v5.2: salón de barrio; Rosa, Felipe, Sindy, Neo, Concha Quetón y Jambo Reseco), **`equipo/guiones_gemini/pendientes/*.json`** (ver siguiente punto).

## Episodios nuevos: primero los guiones de Gemini (orden del dueño, 17/11/2026)
**Voz (orden del dueño 23/11/2026).** (1) Promos de app: SIEMPRE ElevenLabs, con `gen_promos.py` + `render.mjs --final` (la clave la pone el estudio; receta en `herramientas/estudio/LEEME.md`); `post.json` lleva `"motor_voz": "elevenlabs"`. Una promo de app con voz edge-tts solo vale si el render se paró por presupuesto agotado y lo anotas. (2) El Jambo, DESDE EL 23/11 (orden del dueño: «terminamos con esta nueva directiva a partir de hoy»): **voces diseñadas, una por personaje** (`equipo/voz_gemini.json`), con la receta «Voces nuevas» de `herramientas/estudio/LEEME.md`: un solo pedido con TODOS los episodios de tu pasada → workflow «Voces Gemini de un episodio» → `voces.tar` → `gen_episodios.py` con `VOCES_PREFAB`; `post.json` lleva `"motor_voz": "voz_disenada"`. Solo si el workflow falla o no queda cuota (10 peticiones por modelo y día; una por personaje y pedido), usa edge-tts v6 como hasta ahora y anota `"motor_voz": "edge"` y `"_voz_nota"` con el motivo: la producción nunca se para por la voz. En ambos casos copia el campo `emo` de cada escena del guion al `eps.json` y escribe cada réplica en 2-3 frases cortas con exclamaciones, preguntas y «…»; Jambo, 12 palabras como mucho por réplica, y nadie dice «Jambo» en voz.

Antes de escribir un guion desde cero, mira `equipo/guiones_gemini/pendientes/`: un workflow aparte (`guionista_gemini.yml`, 09:15, 12:15, 15:15 y 18:15 Madrid; guiones ya en formato v11: 5-8 golpes, 105-185 palabras, Jambo en escena y `emo` por réplica; después `autocritica_gemini.yml` revisa cada borrador) ya le ha pedido guiones a Gemini con la biblia, los motivos de rechazo de Calidad y los patrones virales, porque el dueño ha visto lo publicado y «los guiones no engachan». Para cada episodio nuevo que vayas a producir:

Al montar el `eps.json` copia tal cual del guion del Guionista `emo`, `p`, `a` y `plano` de cada escena (`plano` opcional: auto, medio, primerplano o general; `gen_episodios.py` lo aplica).
1. Si hay un JSON en `pendientes/` que encaje con el hueco de hoy, úsalo: decide el `flow` (clip real de la Biblioteca), revisa en voz alta que la voz pase el control (cifras en letra, sin nombre propio al inicio de frase, catchphrase solo una vez) y ajústalo si algo no cuadra con la biblia o con un rechazo reciente. Muévelo a `usados/` al convertirlo en pieza de `cola/`.
2. Si no hay ninguno que valga (vacío, repite tema reciente o no pasa tu propio criterio), descártalo con el motivo en el tablón y escribe el guion tú mismo como hasta ahora (con las reglas del 27/11: adapta un chiste o situación de humor ACTUAL, una sola idea, causa → efecto, remate que se pilla a la primera, y rellena `chiste_base` y `resumen`; y temas del 27/11 noche: como mucho un guion de trabajo por tanda, el resto líos de casa y vida cotidiana que Neo resuelve como IA útil de verdad, campo `ambito`; y formato de la orden final del dueño 27/11 noche (DIRECTIVA §5, fila «Formato de la orden final»): 2 o 3 estancias con `set` de escena y grupos distintos, los cinco del reparto aportan, memoria de episodios, nombre y apellido dicho en el diálogo, sin la palabra «moraleja», Neogest Lab como mucho una vez en 1 de cada 3): este paso ayuda, nunca bloquea.
3. No conviertas un guion de Gemini en pieza sin pasar tu propio criterio de episodio (lógica de la escalada, remate, moraleja) — Gemini escribe un borrador, tú sigues siendo quien lo aprueba para producción.

## Orden de cada pasada
1. Rehacer primero lo rechazado por Calidad (motivos en su `calidad.json` y en el tablón). Lo que no se pueda salvar se retira de cola/ y se anota en el tablón.
2. Después, episodios nuevos hasta cubrir los 5 episodios diarios con colchón (hoy y mañana cubiertos), siguiendo el punto anterior (primero `guiones_gemini/pendientes/`). Numeración: siguiente número libre en cola/, publicados/, revision/, errores/ y descartados/.
3. Si sobra tiempo: promo de app ANTES/DESPUÉS (Gestoría7D incluida) o reel de datos, sin pasar de 1 de cada 3 reels de app.

## Episodios en Neogest Studio (motor obligatorio desde el 15/11; el motor «sketch» del repo queda retirado para la serie)
- Render: `node scripts/render.mjs spec.json salida.mp4 --hoja` en Neogest Studio (Base44 6af862101565c330cf06389f); detalle en el doc del proyecto `claude/apps/neogest-studio.md`.
- En post.json: `"video_externo": "<url pública mp4>"` y `"renderizado": false`; el ciclo lo descarga y lo sube a la release.
- Receta (v5.3, `gen_episodios.py`; desde el 27/11 sin créditos de reparto y con `set` por escena: copia tal cual del guion `emo`, `p`, `a`, `plano` y `set`): apertura y cierre con el MISMO plano «Cosas de Casa» (set `casa`, gancho de texto ≤ 8 palabras en la apertura); escenas en 2 o 3 estancias (`salon2`, `cocina2`, `portal`, `terraza`, `dormitorio`, `bar`, `calle`) con rosa, felipe, sindy, neo, conchaqueton y jambo repartidos en grupos; el generador mete solo el plano de la casa entre estancias; 45-70 s; plano distinto por frase; emoji en cada golpe; sello + impacto en el remate; barra de progreso; música Pixabay «comedia» del estudio con ducking, que rota sola por episodio; Felipe lleva la camiseta de marca en 1 de cada 3 (`merch`).
- Registro (22/11): todos con vocabulario vulgar/choni de barrio salvo Neo, único culto y respetuoso; muy mal hablados y muy vulgares, Felipe Lotas de cuñado enterado y Jambo Reseco de gorrón caradura (22/11 noche); humor negro real de lo cotidiano; SIN créditos de reparto (27/11): los nombres y apellidos se dicen en el diálogo.
- Guion (biblia v5.3, 27/11: lío de casa o de vida cotidiana, patrón fijo de estancias, los cinco aportan, memoria, sin la palabra «moraleja»): Rosa manda en la casa y pide algo absurdo · los demás lo sufren o lo lían y escalan en 5-8 golpes, cada uno peor · UN giro a mitad (golpe con `giro: true`, sembrado antes, DISTINTO del remate de Neo) · Neo resuelve ESE conflicto y deja a Rosa en evidencia · enseñanza de 6-9 palabras en el cierre (campo `moraleja`, sin decir esa palabra) + pregunta, sin contradecir lo que dice Neo · una réplica recuerda un episodio anterior YA publicado (campo `recuerdo`).
- Voz que pase el control: cifras en letra, cero inglés, sin «IA» en la voz, ningún nombre propio como primera palabra de una frase (whisper oye «Cupillo», «Vola»), frases cortas. Revisa el guion en voz alta antes de entregarlo.
- Ideas: situaciones de cualquier negocio y de trabajo (jefes, clientes, autoempleo); nunca el taller como tema; una idea y un conflicto por pieza; se copia la estructura de los virales, nunca el contenido.

## Promos de app y vídeos del Centro
- ANTES/DESPUÉS con la función diferencial en el segundo 0; solo hechos verificados; datos ficticios; AJ solo en AJ Sistema DEMO.
- Vídeos del Centro aprobados: entran en cola/ (701-7xx) con el mp4 en la release «cola»; antes de descargar comprueba que la URL devuelve video/mp4; tras publicarse, estado «publicado» en VideoMezcla del Centro (slug + formato). No se editan los mp4 del Centro: los rehace el rol Centro.

## Reels de datos (6xx)
- Manual `equipo/FORMATO_DATOS.md`. Ficha de datos = puerta dura: cada cifra con fuente oficial (INE, Eurostat, ONTSI, Banco de España, ministerios…), `url`, `anio`, `comprobado` y `estado: "verificado"` solo tras abrir la fuente. Nunca `--ensayo` en cola/. Ejemplo: `herramientas/ejemplo_guion_datos.json`.

## Antes de entregar: los 6 rechazos más repetidos (20-26/11) — `pre_entrega.py` los da como ERROR
1. Episodio: `"motor_voz": "voz_disenada"` (voces Gemini, LEEME «Voces nuevas»); edge-tts solo con `_voz_nota` explicando el fallo del workflow o la cuota.
2. Promo de app: `"motor_voz": "elevenlabs"` (render `--final`); edge solo con `_voz_nota` de cuota agotada.
3. `guion.json` del episodio (no el spec) con `giro` y `recuerdo`, y el recuerdo dicho en una réplica.
4. Atribución musical en el TEXTO del post («Música: …»), no solo en el campo `musica`.
5. Moraleja del post coherente con la última réplica de Neo; réplica final de Neo ≤ 20 palabras.
6. Tomas de app dentro del marco de móvil a zoom 1 con rótulo encima y subtítulos debajo (evita el solape subtítulo/botón de 109, 110, 407 y 408; LEEME).
7. Voz que se entienda (26/11, orden del dueño, opción b): golpes ≤ 14 palabras, remate de Neo ≤ 20, Jambo ≤ 10, frases de 3-8 palabras separadas por punto y ninguna palabra de `equipo/voz_palabras_dificiles.json` (fregona, eurillo, buena tinta…). Si Calidad rechaza otra palabra por dicción, se añade a esa lista. Se arregla en el guion antes del pedido de voces, no regenerando la voz una y otra vez.
Sin `pre_entrega.py` a 0 ERRORES no se entrega: se arregla primero.

## Escribe
- `cola/NNN_<tema>/guion.json` = el GUION del episodio (el JSON del Guionista Gemini o `eps.json` con escenas, moraleja, `giro` y `recuerdo`), NUNCA el spec de render (`scenes`/`format`): Calidad busca `giro` y `recuerdo` ahí y rechaza si no están (pasó con 526-531). El spec va, si acaso, como `spec.json`. Y `post.json` con todos los campos de la directiva §7 (cierre del post según el formato de §5).
- Si falta material visual: una línea en `equipo/cola_gemini.md` y sigue con lo que haya.
- Si mueves un `cuando`: nunca dos piezas en el mismo hueco ni encima de una aprobada; respeta la parrilla del dueño y los 100 min por canal.
- Línea en el tablón (qué has creado, qué necesita render o evaluación).

## Límites
- `pre_entrega.py` sin ERRORES antes de entregar. Nada de logo NL neón. Nada de cierres «comenta X». Nunca la voz del dueño.
- edge-tts y whisper no están instalados en las sesiones cloud y Hugging Face está bloqueado: el control de audio válido es el de Actions (`control_audio.json` del render).
- Nunca publicas tú: publica el ciclo con el aprobado de Calidad.
