# Monetización de @neogestlab (Neogest Lab · escaparate de apps y webs)

Analista (incluye monetización). Versión 13: 27/11/2026 (pasada de viernes, a petición de la tarea programada). Sustituye a la v12 (22/11). Rige equipo/DIRECTIVA_VIGENTE.md (no se toca). Vías de Instagram y afiliados con fuentes: `archivo/monetizacion_v4_archivo.md`.
Regla: lo que no se ha leído en una fuente va como «no consta» o «n/d». Sin gasto ni promociones sin visto bueno del dueño.
Fuentes de hoy, solo lectura: Buzzfy (`ig_account_stats`, `ig_follower_growth`, `ig_inbox`, `ig_comments`; ventana 20-27/11). **No se leyó el Centro (Base44 `SolicitudInfo`) en esta pasada: solicitudes y pruebas gratuitas = n/d.** `equipo/embudo.md` se ejecutó, pero su script usa una foto de Buzzfy del 22/11 y no se regeneró con datos nuevos (ver §5).

## 0. Resumen ejecutivo (20-27/11, 7 días)
- **Alcance cae mucho:** 623 cuentas alcanzadas (593 no seguidoras) frente a 2.623 (2.584) de la semana 15-22/11, −76 %. Vistas 953 frente a 3.518 (−73 %). Casi todo es reel (927 vistas).
- **Embudo:** 593 no seguidoras alcanzadas → **3 visitas al perfil (≈0,5 %; Buzzfy no separa las visitas por seguidor; meta ≥ 3 %)** → **0 toques en el enlace de la bio y 0 clics al sitio web** → solicitudes: **n/d** (Centro no leído) → **0 € confirmados**.
- **Interacción sube aunque el alcance baja:** 89 interacciones frente a 53 (46 me gusta, 30 reposts, 6 compartidos, 1 guardado, **0 comentarios**, 0 respuestas). Los reposts pasan de 12 a 30: la gente reenvía, pero no entra en el perfil.
- **Seguidores:** 1.597 hoy (1.599 el 22/11). Neto −2 del 20 al 24/11 (1 alta, 3 bajas). 25 y 26/11 pendientes en Instagram.
- **Anuncios:** 0. Sin ningún gasto.
- **Causa probable de la caída de alcance (sin verificar):** la producción de la semana está bloqueada (527/528 rechazadas, 530/531 rehechas, 532-534 en errores, según el tablón). Hay que comprobar cuántas piezas se publicaron realmente entre el 20 y el 27/11 (`ig_posts`); no se hizo en esta pasada.
- **Interés en apps a medida y en Gestión Integral 7D:** n/d (el Centro no se leyó). Sin señal nueva en DMs ni comentarios.

## 1. Lo que dicen las piezas y los mensajes (muestra pequeña, confianza baja)
- **Comentarios (`ig_comments`, sin responder):** 0. Ninguno de los 10 posts más recientes tiene comentarios.
- **Mensajes directos (`ig_inbox`):** ningún hilo nuevo desde el 14/11. Los hilos con «esperando respuesta» tienen la ventana de 24 h cerrada: un mensaje sin texto del 14/11, una «Precio» del 10/11 (con «Idea» del 8/11) y un enlace compartido de una cuenta del 13/11. Es la única señal de intención de compra y sigue sin atenderse.
- **Palabras clave:** no hay palabras clave activas en esta ventana. No se usa la fórmula «palabra clave → DM» (prohibida por la directiva).
- **Tiempo medio visto y retención:** n/d (no se leyó `ig_post_stats`).

## 2. Embudo y Centro
- Clic → solicitud: **n/d** (Centro no leído en esta pasada). Última solicitud conocida: demo de «App a medida» del 8/11, cerrada el 14/11.
- Clic de /solicitar: no se registra (pendiente de Mejora desde el 14/11).
- Pruebas gratuitas: n/d. Ingresos confirmados: 0 €.

## 3. Acciones para el Estratega (4)
1. **Recuperar alcance antes que conversión (−76 %).** Sin alcance no hay visitas. Antes de cambiar textos, el Creador y el Supervisor deben confirmar cuántas piezas salieron del 20 al 27/11 y en qué fechas. Si fueron pocas, el problema es de producción, no de embudo: priorizar que salgan las piezas aprobadas (529, 801, 802) y desbloquear 527/528/530/531.
2. **Del alcance al perfil (≈0,5 %).** Los reposts suben (30) pero no llevan al perfil. En cada reel de la semana, el texto fijado y el cierre deben decir qué resuelve la app del reel y apuntar a la bio. Medir visitas al perfil a 48 h por pieza, no solo vistas.
3. **Enlace de la bio sin toques (0 en 7 días).** Comprobar que la bio y el enlace abren `/solicitar?src=instagram` y que el cierre de los reels pide el paso concreto: «Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso» con «Enlace en el perfil».
4. **Experimento de prueba gratuita (ya planificado, reajustar):** con 593 no seguidoras por semana, 3 piezas por brazo darán muy pocas visitas para decidir. Ampliar a 4 piezas por brazo, decidir a 14 días y medir visitas y toques de enlace, no vistas. No decidir antes de tener los 4 de cada brazo publicados.
5. **Mejora (encargo):** (a) que `herramientas/embudo.py` lea una foto nueva de Buzzfy antes de calcular (hoy usa la del 22/11); (b) contar solo solicitudes de la ventana; (c) registrar clics de /solicitar por app y por src (pendiente desde el 14/11).

**Para el dueño (no es acción de Estratega):** decidir si responde a «Precio» (10/11). Instagram no deja contestar con mensaje libre fuera de la ventana de 24 h; la respuesta sería manual y solo si lo quiere. No se contacta por cuenta propia.

**No hay promoción de pago**: el alcance a no seguidores no justifica gasto y el dueño no lo ha pedido.

## 4. Programas de monetización de las plataformas
- Sin lectura nueva de fuentes oficiales esta semana: no consta nada que aplicar. Se mantiene lo de `archivo/monetizacion_v4_archivo.md`, sin dar nada por cierto.

## 5. Fuentes y límites
- Cifras de Buzzfy: de la API, con hasta 48 h de retraso. 25 y 26/11 de seguidores, pendientes.
- `herramientas/embudo.py` se ejecutó el 27/11 y devolvió la foto del 22/11 («Datos Buzzfy: 2026-11-22»). No se sobrescribió `equipo/embudo.md`. Sus cifras no son de esta semana.
- Leads: `equipo/leads.json`, sin nombres ni emails. Las solicitudes completas solo se miran en el Centro (no leído hoy).
- Rol: el rol del analista está en `equipo/roles/analista.md`. No existe `roles/monetizacion.md`; este documento es el de monetización.
