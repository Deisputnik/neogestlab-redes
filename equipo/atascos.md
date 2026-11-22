# Atascos de la cola (generado por herramientas/atascos.py; no editar a mano)
Actualizado: 2026-11-22 23:16 UTC · 10 piezas paradas.
Regla (DIRECTIVA §7 bis): cada rol empieza su pasada por SUS filas de aquí, de arriba abajo.

Por rol: Calidad 6, Creador 2, Mejora 1, Supervisor 1

| Urgencia | Pieza | Sale | Tipo | Rol | Motivo | Arreglo |
|---|---|---|---|---|---|---|
| URGENTE (hora pasada) | 328_jambo_inmobiliaria_decima_visita | 2026-11-21T19:00:00+01:00 | render_fallido | Mejora | KeyError: 'escenas' | si el guion no tiene escenas es un episodio del estudio: poner video_externo; si no, arreglar el generador |
| URGENTE (hora pasada) | 351_jambo_wifi_robado | 2026-11-21T21:15:00+01:00 | rechazada | Creador | Audio roto (control_audio.json aprobado:false, bloqueo real no es jerga): 'J-A-M-B-O-movil' se pronuncia 'JMM o móvil' (deletreo ilegible, rompe el gancho) y las dos líneas con '¡Illo...!' de Rosa y de Jambo se oyen como 'Y yo...', perdiendo la interjección y  | Requiere RE-RENDER (no es solo texto): 1) Regenerar audio de las frases que fallan control_audio.json, en especial el deletreo 'J-A-M-B-O-movil' (probar separarlo con guiones/pausas distintas o decirlo de otra forma que el motor sí pronuncie) y las dos líneas  |
| URGENTE (hora pasada) | 353_jambo_coche_mal_aparcado | 2026-11-21T21:45:00+01:00 | rechazada | Creador | Duración 36.97 s: el formato vigente de El Jambo (v11, DIRECTIVA §5) exige 45-70 s; este render se queda por debajo del mínimo (faltan ~8-33 s de episodio).; Falta el bucle de cierre: el plano «Cosas de Casa» con el gancho «Esta casa del barrio tiene truco» ap | RE-RENDER (no basta con texto del post): 1) Alargar el episodio a 45-70 s añadiendo o ampliando algún golpe de escalada (p.ej. un intercambio más entre Sindy/Jambo o un comentario de Rosa) para llegar al mínimo de 45 s manteniendo los 3 golpes de escalada. 2)  |
| sale en < 24 h | 517_jambo_concha_cobro | 2026-11-23T08:30:00+01:00 | sin_nota | Calidad | renderizada hace 0.1 h sin calidad.json vigente | la Calidad (API) corre cada hora desde reloj.yml; si pasa de 2 h, lanzar calidad_api.yml a mano |
| sale en < 24 h | 108_cobrar_facturas_reel | 2026-11-23T11:30:00+01:00 | sin_nota | Calidad | renderizada hace 0.1 h sin calidad.json vigente | la Calidad (API) corre cada hora desde reloj.yml; si pasa de 2 h, lanzar calidad_api.yml a mano |
| sale en < 24 h | 107_catalogo_stock_reel | 2026-11-23T17:10:00+01:00 | sin_nota | Calidad | renderizada hace 0.1 h sin calidad.json vigente | la Calidad (API) corre cada hora desde reloj.yml; si pasa de 2 h, lanzar calidad_api.yml a mano |
| sale en < 24 h | 518_jambo_impuesto_aire | 2026-11-23T19:40:00+01:00 | sin_nota | Calidad | renderizada hace 0.1 h sin calidad.json vigente | la Calidad (API) corre cada hora desde reloj.yml; si pasa de 2 h, lanzar calidad_api.yml a mano |
| sale en < 24 h | 519_jambo_sindy_receta | 2026-11-23T21:30:00+01:00 | sin_nota | Calidad | renderizada hace 0.0 h sin calidad.json vigente | la Calidad (API) corre cada hora desde reloj.yml; si pasa de 2 h, lanzar calidad_api.yml a mano |
| sale en < 72 h | 801_recepcionista_horario | 2026-11-29T19:40:00+01:00 | sin_nota | Calidad | renderizada hace 0.0 h sin calidad.json vigente | la Calidad (API) corre cada hora desde reloj.yml; si pasa de 2 h, lanzar calidad_api.yml a mano |
| más adelante | 802_recepcionista_que_hace | 2026-11-30T12:40:00+01:00 | sin_render | Supervisor | esperando al ciclo (descarga del vídeo externo) | si pasa de 1 h, lanzar ciclo.yml |
