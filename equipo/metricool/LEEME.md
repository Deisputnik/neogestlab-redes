# TikTok @neogestlab vía Metricool · segunda vía (20/11/2026)

> **BLOQUEADO (22/11/2026, comprobado en directo):** la API de Metricool solo está disponible en
> sus **planes de pago avanzados** — el plan gratis NO incluye acceso a la API (pantalla
> "Configuración de la cuenta > API" muestra "Acceso a la API: planes avanzados y personalizados" +
> botón "Mejora tu plan"). Por tanto `METRICOOL_TOKEN` no se puede conseguir gratis y esta vía
> **no es viable sin pagar**. Se deja el código tal cual (no hace nada sin los 3 secretos, termina
> bien), pero no se persigue más esta ruta salvo que el dueño decida pagar el plan de Metricool.
> Alternativa gratis real para TikTok: la cuenta @neogestlab ya está conectada gratis en Zernio
> (2ª cuenta, sin tarjeta); falta solo crear una API key de Zernio (acción que requiere
> autorización explícita del dueño) y un script `herramientas/redes_zernio.py` que llame a
> `POST https://zernio.com/api/v1/posts` igual que `facebook.py` llama a Graph API.

Creado por orden del dueño: no depender de una sola herramienta (Buffer) ni de la aprobación de
TikTok for Developers para publicar. Manda `equipo/DIRECTIVA_VIGENTE.md` para la cadencia.

## Qué hace
`herramientas/redes_metricool.py tiktok` (workflow `redes_metricool.yml`) coge las mismas piezas
que Buffer (`publicados/`, calidad aprobada, render desde el 14/11), pero **nunca repite** lo que
Buffer ya programó en `equipo/tiktok/estado.json` para no duplicar el mismo vídeo en la misma
cuenta de TikTok. Es decir: es una segunda cola para el mismo canal, no una copia de la primera.

## AVISO IMPORTANTE — queda en borrador, no se publica solo
La documentación pública de Metricool no especifica los campos exactos que exige TikTok
(privacidad, aviso de "generado por IA", dúo/comentarios). Por eso, de momento, cada pieza se
crea como **borrador** en Metricool: entra en tu panel de Metricool, pero no sale a TikTok hasta
que tú (o quien lo revise) la completes y publiques a mano la primera vez. En cuanto se confirme
el esquema exacto (abriendo una vez en el navegador `https://app.metricool.com/api/swagger.json`,
bloqueado para las herramientas de Claude por robots.txt, o por el primer error real de la API),
se quita el `draft=true` del código y pasa a publicar solo como Buffer.

## Qué necesita (una sola vez, lo haces tú)
1. Cuenta de Metricool (plan gratis) con tu TikTok de @neogestlab conectado.
2. En Metricool: Configuración de la cuenta > API, copiar el token.
3. Crear los 3 secretos en GitHub: `METRICOOL_TOKEN`, `METRICOOL_USER_ID`, `METRICOOL_BLOG_ID`
   (userId y blogId los da la propia Metricool, visibles en esa misma pantalla o en la URL del
   panel). Sin los tres, el workflow no hace nada y termina bien.

## Límites conocidos
- Plan gratis de Metricool: hasta 20 publicaciones/mes programadas en total (todas las redes de
  esa cuenta), así que esta vía es complementaria a Buffer, no para duplicar volumen.
- Huecos: 11:15 y 18:15 (Madrid), distintos de los de Buffer (13:30/20:30) para no agolpar todo
  en el mismo momento. Se cambian en `equipo/metricool/config.json`.
- `ultimo_error` no vacío en `equipo/metricool/estado.json` = algo falló (lo mira el Supervisor).
