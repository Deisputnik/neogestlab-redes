# Monetización de @neogestlab (Neogest Lab · escaparate de apps y webs)

Analista (incluye monetización). Versión 12: 22/11/2026 (pasada dominical nocturna, 23:23 Madrid). Las cifras de 15-22/11 son las de la v11 de las 17:19 UTC; cambia que `equipo/kpi_buzzfy.json` y `equipo/embudo.md` ya se han actualizado con ellas. Sustituye a la v11. Rige equipo/DIRECTIVA_VIGENTE.md (no se toca). Vías de Instagram y afiliados con fuentes: `monetizacion_v4_archivo.md`.
Regla: lo que no se ha leído en una fuente va como «no consta» o «n/d». Sin gasto ni promociones sin visto bueno del dueño.
Fuentes de hoy, solo lectura: Buzzfy (`ig_account_stats`, `ig_follower_growth`, `ig_inbox`, `ig_comments`; ventana 15-22/11) y Base44 del Centro (`SolicitudInfo`, app 6ae5244d4e2b32702f0a3cd6). `equipo/embudo.md` no se regeneró en esta pasada (su script cuenta mal el último paso, ver §5).

## 0. Resumen ejecutivo (15-22/11, 7 días)
- **Pasada nocturna (22/11, 23:23):** misma foto. El paso más débil sigue siendo alcance → visita (0,08 %). Ninguna pieza de la ventana llega a 2× la mediana (115 de alcance, 144,5 vistas): sin secuela que lanzar por cifras. Aviso del embudo (`herramientas/embudo.py`, Mejora): el último paso compara solicitudes acumuladas con clics de la ventana; hasta que se corrija, el 100 % de ese paso no es una tasa real.
- **Embudo:** 2.584 cuentas no seguidoras alcanzadas → **2 visitas al perfil (0,08 %; meta ≥ 3 %)** → **0 clics al enlace de la bio** → **0 solicitudes nuevas en el Centro** → **0 €**.
- **Peor semana del periodo medido en el paso alcance → perfil:** 0,1 % la semana anterior (2 de 3.913) y ahora 0,08 % (2 de 2.584). El alcance no llega al perfil.
- **Enlace sin uso:** 0 clics en el sitio web y 0 toques en el enlace en 7 días. Con 2 visitas al perfil no hay muestra, pero el paso visita → enlace ha bajado de 50 % a 0 %.
- **Seguidores:** 1.599 hoy; neto −2 en 15-19/11 (4 altas, 6 bajas; 20 y 21/11 pendientes en Instagram). Sin caída brusca.
- **Alcance:** 2.623 cuentas, casi todas no seguidoras (2.584). Vistas 3.518, de ellas 3.482 en reel. Anuncios: 0. Sin ningún gasto.
- **Interacción:** 53 interacciones (38 me gusta, 12 reposts, 1 guardado, 1 compartido). **Comentarios: 0** (ninguno en los 10 posts más recientes).
- **Interés en apps a medida y en Gestión Integral 7D:** n/d en esta ventana. Solo consta la solicitud de «App a medida» de demo del 8/11 (cerrada el 14/11). Ninguna solicitud de Gestión Integral 7D. `/solicitar` no registra por qué app se entra.

## 1. Lo que dicen las piezas y los mensajes (muestra pequeña, confianza baja)
- **Mensajes directos (`ig_inbox`):** no hay hilos nuevos con texto en 15-22/11. Quedan dos hilos recientes sin respuesta con la ventana de 24 h cerrada: un mensaje sin texto del 14/11 y una «Precio» del 10/11 (con «Idea» del 8/11 en el mismo hilo). Es la única señal de intención de compra y no consta que se haya atendido. Los demás hilos son de 2024-2025 o ya contestados.
- **Palabras clave:** no hay palabras clave activas en esta ventana. No se usa la fórmula «palabra clave → DM» (prohibida por la directiva).
- **Tiempo medio visto y retención:** n/d en esta pasada (no se leyó `ig_post_stats`).

## 2. Embudo y Centro
- Clic → solicitud: **0 nuevas**. Única solicitud histórica: demo de «App a medida» del 8/11, cerrada el 14/11. Sin contacto a nadie que no lo haya pedido (LSSI art. 21).
- Clic de /solicitar: no se registra (pendiente de Mejora desde el 14/11).
- Pruebas gratuitas: n/d. Ingresos confirmados: 0 €.

## 3. Acciones para el Estratega (4)
1. **Del alcance al perfil (0,08 %).** En cada reel de la semana, el texto fijado y el cierre deben decir qué resuelve la app del reel y apuntar a la bio. Medir visitas al perfil a 48 h por pieza, no solo vistas. Meta: 3 % de no seguidores → perfil antes de decidir nada más.
2. **Enlace de la bio sin clics (0 en 7 días).** Antes de tocar el texto, comprobar que la bio y el enlace abren `/solicitar?src=instagram` (la bio ya lo indica) y que el cierre de los reels pide el paso concreto: «Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso» con el enlace «Enlace en el perfil».
3. **Experimento de la semana 27/11 (ya planificado):** un episodio con oferta de prueba gratuita en el último plano frente a otro igual sin ella, 3 piezas por brazo, decisión por visitas al perfil y clics, no por vistas.
4. **Cierre de prueba gratuita con `app=<slug>` en cada enlace de Gestión Integral 7D y de App a medida** (`/solicitar?app=<slug>&src=instagram`, directiva §9), para saber qué producto genera cada solicitud. Coordinar el slug con el Centro.
5. **Mejora: registrar los clics de /solicitar por app y por src** (pendiente desde el 14/11). Sin eso el paso clic → solicitud seguirá en «n/d».

**Para el dueño (no es acción de Estratega):** decidir si responde a «Precio» (10/11, sin respuesta, ventana cerrada). Instagram no deja contestar con mensaje libre fuera de la ventana; la respuesta sería manual y solo si lo quiere. No se contacta por cuenta propia.

**No hay promoción de pago**: el alcance a no seguidores no justifica gasto y el dueño no lo ha pedido.

## 4. Programas de monetización de las plataformas
- Sin lectura nueva de fuentes oficiales esta semana: no consta nada que aplicar. Se mantiene lo de `monetizacion_v4_archivo.md`, sin dar nada por cierto.

## 5. Fuentes y límites
- Cifras de Buzzfy: de la API, con hasta 48 h de retraso (20 y 21/11 de seguidores, pendientes).
- Leads: `equipo/leads.json`, sin nombres ni emails. Las solicitudes completas solo se miran en el Centro.
- `equipo/embudo.md` compara solicitudes acumuladas con clics de la ventana; por eso su último paso sale 100 % con una sola solicitud antigua. Corregir el script para contar solo solicitudes de la ventana (Mejora).
- Rol: el archivo de rol del analista está en `equipo/roles/analista.md` (no existe `roles/monetizacion.md`).
