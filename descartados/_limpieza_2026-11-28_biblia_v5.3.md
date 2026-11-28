# Limpieza del 28/11/2026 · orden del dueño

Orden: «actualiza y elimina todas las versiones antiguas que no se adaptan a la nueva biblia» (biblia v5.3, `equipo/serie_jambo.md`).
Criterio (biblia v5.3 §6 y DIRECTIVA_VIGENTE §5): un episodio necesita `titulo_fijo` (apertura en frío) y entre 2 y 3 estancias (al menos dos valores de `set`). Además, no lleva el bucle de casa al abrir y cerrar. Lo que no cumple se descarta; no se arregla.

## Retirado de cola/ → descartados/ (formato v5.2: sin titulo_fijo, solo salón, bucle de casa)
- cola/530_jambo_fuga_banera_rebosando
- cola/531_jambo_paquete_aviso_fantasma
- cola/535_jambo_menu_lentejas_nevera

## Retirado de equipo/guiones_gemini/ → guiones_gemini/descartados/
- equipo/guiones_gemini/pendientes/2026-11-25_523_fontanero_factura_fuga.json
- equipo/guiones_gemini/pendientes/2026-11-25_524_repartidor_turnos_paquetes.json
- equipo/guiones_gemini/pendientes/2026-11-25_525_cuidado_mayores_turno_noche.json
- equipo/guiones_gemini/pendientes/2026-11-25_526_camarero_inventario_roturas.json
- equipo/guiones_gemini/pendientes/2026-11-25_barrio_cuenta_fiada.json
- equipo/guiones_gemini/pendientes/2026-11-25_cuidador_turno_domingo.json
- equipo/guiones_gemini/pendientes/2026-11-25_fontanero_madrugada_factura.json
- equipo/guiones_gemini/pendientes/2026-11-25_repartidor_paquete_fantasma.json
- equipo/guiones_gemini/revisar/2026-11-23_jambo_camarero_cierre.json
- equipo/guiones_gemini/revisar/2026-11-23_jambo_cuidado_turnos_ia.json
- equipo/guiones_gemini/revisar/2026-11-23_jambo_fontanero_tuberia.json
- equipo/guiones_gemini/revisar/2026-11-23_jambo_repartidor_domingo.json
- equipo/guiones_gemini/revisar/2026-11-27_jambo_clave_wifi_router.json
- equipo/guiones_gemini/revisar/2026-11-27_jambo_derrama_ascensor_junta.json
- equipo/guiones_gemini/revisar/2026-11-27_jambo_disfraz_colegio_manana.json
- equipo/guiones_gemini/revisar/2026-11-27_jambo_reunion_comunidad_derrama.json
- equipo/guiones_gemini/revisar/2026-11-27_jambo_suscripcion_oculta_gimnasio.json
- equipo/guiones_gemini/revisar/2026-11-27_jambo_suscripcion_olvidada.json
- equipo/guiones_gemini/revisar/2026-11-27_jambo_wifi_secuestrado.json

## Se quedan
- 801_recepcionista_horario y 802_recepcionista_que_hace: son promos de app, no episodios. Aviso: llevan voz edge-tts y la DIRECTIVA §5 pide ElevenLabs Johnny en la versión final de las promos. Hay que rehacerlas con Eleven antes de que salgan.

## Siguiente paso
El Guionista ya no tiene borradores viejos que le frenen y escribe guiones v5.3 nuevos; el Creador los renderiza con `gen_episodios.py`.
