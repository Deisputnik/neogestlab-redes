# Serie «El Jambo que sabe» · biblia v5.3 (27/11/2026)

Esta es la única versión vigente. Recoge las órdenes del dueño hasta el 27/11/2026 por la noche y sustituye a todo lo anterior (oficina, jefa y empleados, episodios de 15-25 s, créditos de reparto, voz arrastrada o cantarina de Jambo): eso ya no vale y se ha borrado de aquí para no confundir. El historial está en git. La cadencia de publicación es la de `equipo/DIRECTIVA_VIGENTE.md` §8.

## 1. Qué es la serie
Una comedia de barrio de 45-70 s, de humor negro sobre lo cotidiano, al estilo de las comedias americanas de casa. Una inteligencia artificial, Neo, resuelve los líos de la casa y de la vida diaria. Quien la ve tiene que pensar «eso me pasa a mí» y «anda, para eso sirve la IA».

## 2. De qué van los episodios
- De cada tanda de guiones, **como mucho uno** va de trabajo, negocio o papeleo. El resto son líos de casa y de vida cotidiana, cada uno de un ámbito distinto (campo `ambito`):
  - **casa**: la compra y el menú de la semana, qué cenar con lo que hay en la nevera, el turno de limpiar, la lavadora, la avería y el manual que nadie lee, la mudanza, las plantas, la mascota, la contraseña del wifi, las fotos del móvil, la tele y las plataformas;
  - **familia**: los deberes de los críos, el disfraz del colegio para mañana, el móvil de la abuela, el grupo de la familia, el cumpleaños que se olvida, quién recoge a quién;
  - **compras**: comparar precios, la garantía, devolver un paquete, la letra pequeña, la suscripción que nadie recuerda;
  - **salud_y_citas**: pedir cita, acordarse de la pastilla de un mayor, entender un papel del médico, la dieta, el plan para moverse;
  - **dinero_de_casa**: llegar a fin de mes, la factura de la luz o del teléfono, el recibo que sube, el alquiler, repartir gastos;
  - **ocio_y_viajes**: organizar un viaje, la ruta en coche, traducir una carta o un menú, el plan del fin de semana, la boda del primo;
  - **barrio**: la reunión de la comunidad, el vecino del ruido, reclamar algo, la cita previa, un mensaje difícil al casero, al profesor o a la compañía.
- **Neo es la IA en lo cotidiano**: resuelve haciendo algo que una inteligencia artificial hace de verdad en esa situación (ordenar, resumir, recordar y avisar, calcular, comparar, redactar, traducir, planificar con lo que hay) y lo dice en concreto. Nunca magia, nunca consejo médico, legal ni financiero: organiza y explica, no diagnostica ni promete.
- A veces el lío nace de que alguien usa o se inventa una aplicación de IA genérica y ficticia que sale mal, hasta que llega Neo. Nunca se nombran aplicaciones reales, ni de Neogest Lab ni de terceros.

## 3. Cómo se construye la historia
- **Punto de partida**: un chiste o una situación de humor ACTUAL (la de los vídeos cortos, memes y grupos de mensajes) o una noticia de estos días, convertidos en un lío de la casa. Prohibido el chiste rancio y copiar el número de un cómico. De una noticia nunca se nombra a personas, partidos, empresas ni tragedias reales, ni se da un dato suyo como cierto. El chiste que se adapta va en `chiste_base`.
- **Una sola idea** por episodio. El gancho deja claro quién quiere qué y cuál es el problema; cada golpe es consecuencia del anterior; el remate se pilla a la primera sin conocer la serie.
- **Final con enseñanza**: el episodio deja una enseñanza clara que sale de lo visto, pero **la palabra «moraleja» no se dice ni se escribe nunca** en el vídeo. El campo del guion se sigue llamando `moraleja` y es una frase de 6-9 palabras que podría decir cualquiera en la barra de un bar.
- **Prueba del resumen**: el campo `resumen` cuenta el episodio en una frase que entendería un niño de doce años. Si no se puede escribir, el guion está mal.
- **Antes de escribir se mira qué ha funcionado y por qué**: los vídeos propios que más se vieron y más retuvieron (`estadisticas.json`), las fórmulas virales del Cazador (`equipo/virales_semana.md`) y las noticias de la semana (`equipo/noticias_semana.md` y la búsqueda de Gemini). Cada guion dice en `por_que_funcionara` qué aplica.

## 4. Tono: humor negro de lo cotidiano
- Frialdad y naturalidad ante lo que da rabia o apuro de verdad; no indignación disfrazada de chiste. La pobreza es el escenario (un barrio humilde), nunca el chiste. Se castiga con ironía a quien manda y se escaquea (Rosa) y a quien sentencia sin saber (Felipe).
- Prueba de cada golpe: si al quitarle la gracia queda una frase que incomoda de verdad, es humor negro; si solo queda una queja normal, es sarcasmo blanco y hay que subirlo. Al menos un golpe por episodio es del primer tipo.
- Ejemplo de sarcasmo blanco (no basta): «Ya puestos, tráete también a mi suegra, que así hacemos piña.» Ejemplos de humor negro real, llevados a casa: tratar algo importante con frialdad de trámite («Mamá, el sábado me caso. ¿Quién friega ese día, o lo cuento como falta?»), aceptar como normal lo injusto («Tranquila, que aquí el frío nos iguala a todos») o nombrarlo en seco.
- Registro: castellano de barrio, vulgar y muy mal hablado (tacos comunes del español de España entre exclamaciones), con réplicas más listas de lo que su forma de hablar haría esperar. Neo es el único culto y habla siempre con respeto. Se llaman por su nombre entre ellos.
- **Líneas rojas (no cambian)**: nada contra personas ni colectivos reales; nada de suicidio, autolesión, enfermedades o muertes reales ni víctimas; sin política de partidos; sin marcas ni aplicaciones de terceros; sin consejos médicos, legales o financieros.

## 5. Personajes
Si una réplica la podría decir otro personaje sin que se note, está mal escrita.
- **Rosa Melano**. Manda en la casa igual que mandaría en un negocio: reparte tareas, pone normas absurdas, se escaquea, se lleva el mérito y jamás reconoce un error. Tacaña con los demás y generosa consigo misma. Cursi hasta que se le cae la máscara y suelta un exabrupto de barrio. Móvil siempre en la mano.
- **Felipe Lotas**. El cuñado enterado: no sabe nada y cree saberlo todo; sentencia cosas falsas con seguridad total («eso lo sé yo de buena tinta») y la realidad o Neo le dejan en evidencia. Cara de empanado, reacciona un segundo tarde. Un ligón al que todo le sale mal.
- **Sindy Entes**. Le faltan todos los dientes salvo tres y sonríe igual. Directa, sin filtros, jerga de calle; la única que dice la verdad a la cara, con un argumento que no se puede rebatir.
- **Concha Quetón** (no sale siempre). Siempre tiene frío. Pide plazos y favores imposibles y nunca paga a tiempo. Coletilla fija: «Eso lo arreglamos la semana que viene».
- **Jambo Reseco, «el Pintas» o «el Piezas»**. El gorrón caradura del barrio, de poca confianza: se apunta a todo, nunca paga, pide (un euro, veinte duros, un cigarro, que le fíen) o vende algo de procedencia dudosa y luego te lo pide prestado. Listo a lo pícaro: se sabe las deudas de todos y las trampas de todo. Rasgos de toxicómano de barrio de los años ochenta que se ven y se oyen sin que nadie los nombre: flaco, ojeroso, el más desaliñado del reparto (dibujo `scruffy`), con un estado normal de colocado y con sueño que ni él ni nadie comenta; se rasca, se queda traspuesto, cambia de humor en seco. El más mal hablado.
  - *Cómo habla*: como la calle de verdad, sin teatro, sin cantar y sin caricatura. Frases muy cortas, a medio hacer, acabadas en vocativo («…, tronco.», «…, colega.», «…, quillo.») o abiertas con «Illo,» / «Chacho,», y argot de entonces («pa», «na», «pelas», «duros», «qué mal rollo», «menuda movida», «al loro», «el menda»). Réplicas de 10 palabras como mucho. El guion va en ortografía normal, sin vocales alargadas: el ceceo y el arrastre los pone la voz.
  - *Lo que nunca*: nadie dice «Jambo» en voz (la voz sintética lo lee mal): se le llama «el Pintas», «el Piezas», «el Reseco», «este», «el vecino». No dice la enseñanza final ni «Que lo resuelva el Neo». No se nombra, se enseña ni se describe ninguna sustancia, dosis ni consumo; nada de sobredosis, enfermedad ni muerte; nadie le llama «yonqui» ni «drogadicto»; no se le marca de ninguna etnia ni colectivo; no dice que tiene sueño. El chiste es su cara dura, jamás la adicción de la gente real.
- **Neo**. La inteligencia artificial de la casa, un prototipo de Neogest Lab. Culto, seco y tranquilo: no opina, resuelve con hechos y deja en evidencia a quien se lo merece. Entra en el remate.
- **Frase de la serie**: «Que lo resuelva el Neo», la dice Felipe o Sindy justo antes del remate.
- **Todos aportan**: Rosa, Felipe, Sindy, Jambo y Neo tienen al menos una réplica en cada episodio, y cada una empuja la historia con lo que solo ese personaje haría (Rosa manda, Felipe la lía sentenciando, Sindy lo destapa, Jambo saca tajada, Neo lo resuelve).
- **Memoria**: se acuerdan de lo que les pasó en episodios anteriores (deudas, rencores, normas de Rosa, meteduras de pata de Felipe) y lo sacan con un detalle concreto. El Guionista recibe la lista de lo ocurrido y no inventa pasados que no estén en ella; el campo `recuerdo` dice cuál usa.
- **Nombres y apellidos**: no hay créditos, así que se dicen en el diálogo. En cada episodio alguien llama a otro por su nombre y apellido una vez, con naturalidad (una bronca, pasar lista, con sorna), y se va rotando a quién le toca (`nombre_completo_dicho`). El nombre nunca es la primera palabra de una frase. Además, cada personaje muestra su nombre y apellido en una etiqueta la primera vez que aparece.
- **Coletillas**: en cada tanda el Guionista inventa coletillas nuevas y más graciosas por personaje, sin repetir las recientes (`coletillas_nuevas`).
- *Bit* (la esfera dorada) no pertenece a esta serie: vive en los vídeos de trucos de aplicaciones.

## 6. El patrón fijo de cada episodio
1. **Apertura**: plano de la casa por fuera («Cosas de Casa», 1,6 s) con un gancho de texto de 8 palabras como mucho. Es el primer fotograma del bucle.
2. **Gancho** en mitad del lío: quién quiere qué y qué hay en juego, reconocible en el primer segundo. Abre una pregunta (`promesa`) que solo se responde en el remate.
3. **Escalada** de 5 a 8 golpes, cada uno peor y consecuencia del anterior, con un giro sembrado a mitad (`giro`).
4. **Estancias**: la acción pasa por 2 o 3 estancias de la casa o del barrio; siempre hay al menos un cambio y como mucho dos (campo `set` en la escena donde se cambia). **No están todos juntos todo el capítulo**: en cada estancia hay un grupo distinto, de dos o tres, con su conversación, y lo que se dice en una no lo saben en la otra. Cada cambio hace avanzar la historia.
5. **Transición**: entre estancia y estancia va un plano corto de la casa por fuera, cada vez con un encuadre distinto del mismo plano de la apertura. Lo pone el render solo; no se escribe en el guion.
6. **Remate de Neo**: reúne lo que pasó en las distintas estancias, responde a la pregunta del gancho con algo concreto y deja la enseñanza.
7. **Cierre**: 3 s de promo de la empresa y, como último plano, la casa por fuera IDÉNTICA a la de la apertura (bucle sin costura). **No hay créditos de reparto.**
- Ritmo: réplicas cortas, cambio de plano constante, primer plano en reacciones y remates, plano general solo para situar, reacciones de una a tres palabras tras los golpes fuertes. El guion puede fijar quién sale (`p`), la acción (`a`), la emoción de la voz (`emo`) y el plano (`plano`). Risas de público en 1-3 golpes como mucho (`risas`).

## 7. Neogest Lab dentro de la serie
- Neo es un prototipo de Neogest Lab, la empresa que hace aplicaciones con inteligencia artificial.
- **En la imagen**: el logo 2026 y el nombre van de forma discreta en el propio decorado (un objeto pequeño y creíble) o en una prenda de ropa. Que se vea si te fijas; nunca un cartel publicitario. Además, la marca de agua fija de arriba a la derecha y la promo de 3 s antes del plano final.
- **En el diálogo**: en uno de cada tres episodios (`marca: true`) un personaje nombra a Neogest Lab UNA vez y de pasada, como quien habla del fabricante de la lavadora («Esto es cosa del Neo, el invento ese de Neogest Lab»). Nunca eslogan, precios, «descárgala», aplicaciones concretas ni funciones. En el resto nadie la nombra.
- Marca: logo 2026 (isotipo «N» de circuitos + «NEOGEST LAB»), tipografía Montserrat. Prohibido el logo antiguo «NL neón».

## 8. Imagen, decorados y sonido
- **Dibujo**: vector plano tipo avatar de Neogest Studio (cabeza redonda grande, ojos ovalados enormes de contorno negro, torso de color liso); Neo es una cápsula con cara de pantalla brillante. Ropa de ir por casa. Subtítulos palabra a palabra.
- **Decorados**: con profundidad (fondo lejano por una ventana o puerta, pared con muebles y objetos, primer término que tapa parcialmente) y de barrio humilde. Estancias para los guiones nuevos: `salon2` (salón con pasillo al fondo, ventana al patio y sofá en primer término; calendario de pared con el logo), `cocina2` (cocina con suelo de damero; imán de nevera con el logo), `portal` (portal del bloque con buzones, escalera y la calle al fondo; folleto en el tablón de anuncios), `terraza` (terraza con toldo, barandilla y azoteas; bolsa de tela con el logo), más `dormitorio`, `bar` y `calle`. Los antiguos `salon` y `cocina` solo se usan para guiones ya escritos. La casa por fuera (`casa`) es el plano de apertura, cierre y transiciones. Prenda con marca: en uno de cada tres episodios Felipe lleva la camiseta de «NEOGEST LAB» (lo hace `gen_episodios.py` solo).
- **Voces**: una voz diseñada por personaje (`equipo/voz_gemini.json`), naturales, distintas y expresivas; la de Jambo es voz real de calle, del sur y con ceceo (bloque `jambo_voz_calle`). Respaldo edge-tts si falla: Rosa es-ES-ElviraNeural −4 Hz; Felipe es-ES-AlvaroNeural −4 % / −2 Hz; Sindy es-ES-XimenaNeural +8 % / +4 Hz; Neo es-ES-AlvaroNeural; Concha es-ES-ElviraNeural −6 % / +2 Hz; Jambo es-ES-AlvaroNeural −18 % / −12 Hz.
- **Música**: de más calidad y sin repetir pista en episodios seguidos; se oye, pero nunca tapa la voz. Hasta el 27/11 todos los episodios llevaban la misma pista; ahora `gen_episodios.py` rota entre las cuatro pistas de comedia de la biblioteca del estudio (Pixabay, MP3 a 256 kb/s), de forma que dos episodios seguidos nunca comparten música. Pendiente del equipo: ampliar la biblioteca con pistas de comedia mejores (gratis y con licencia apta) y retirar las que suenen pobres.

## 9. Quién hace qué (flujo)
1. **Guionista** (`herramientas/guionista_gemini.py`, 09:15 y 15:15): lee esta biblia, la memoria de episodios, los datos propios, los virales y las noticias, y escribe los guiones. Su validador rechaza el guion sin `chiste_base` o `resumen`, sin réplica de alguno de los cinco, sin cambio de estancia, con la palabra «moraleja» o con Neogest Lab nombrada más de una vez.
2. **Autocrítica** (`herramientas/autocritica_gemini.py`): aparta a `revisar/` el guion que no se entiende o no cumple el patrón, antes de gastar un render.
3. **Creador** (`equipo/roles/creador.md`, `herramientas/estudio/LEEME.md`): elige guion (priorizando casa y vida cotidiana), pide las voces (`herramientas/voces_gemini.py`), genera el spec con `herramientas/estudio/gen_episodios.py` (sin créditos, con estancias y transición de la casa) y renderiza en Neogest Studio. Copia tal cual del guion `emo`, `p`, `a`, `plano` y `set`. Si escribe él el guion, mismas reglas.
4. **Control de audio y Calidad** (`herramientas/control_audio.py`, `equipo/estandar_calidad.md`): comprueban que se entiende lo que se dice y que el episodio cumple este formato.
5. **Publicación**: la del repo (`equipo/DIRECTIVA_VIGENTE.md` §7 y §8).
- Cambios en el dibujo o en los decorados: `src/studio/characters.js` y `engine.js` de Neogest Studio, siempre con punto de restauración antes y nunca con el builder IA de Base44.
- Vídeo real de la casa: nunca personas identificables, marcas ni direcciones reconocibles.

## 10. Anexo: cifras verificadas (solo para el episodio de trabajo de cada tanda; confirmar la fuente antes de reutilizar)
| Cifra | Dato | Fuente leída | Matiz |
|---|---|---|---|
| Horas extra no pagadas | 2,5 millones de horas a la semana en el 1T 2026; el 42 % de las horas extra no se cobra (5,89 M semanales, 3,38 M pagadas) | El Español, 26/05/2026, citando la EPA del INE | Confirmar en ine.es. Cifras en euros y empleos del mismo texto son estimaciones de UGT/CCOO sin metodología: no usarlas. |
| Administración en pymes | El 55 % de las empresas cree que las tareas administrativas le quitan tiempo para lo estratégico | Forbes España 22/04/2026, informe Qonto + IO Investigación | Lo encarga una fintech: decir siempre «según un informe de Qonto». |
| Plazo legal de pago | 30 días por defecto y, por pacto entre empresas, nunca más de 60 días naturales | BOE, Ley 3/2004 art. 4 | Información general, no asesoramiento legal. |
| Registro de jornada | Obligatorio para todas las empresas desde el 12/05/2019 | Estatuto de los Trabajadores, art. 34.9, Real Decreto-ley 8/2019 | Información general, no asesoramiento legal. |

## Registro de cambios
- 2026-11-27 · biblia v5.3 · órdenes del dueño de ese día, en este orden: (1) la voz de Jambo no se entendía → voz de calle real, del sur y con ceceo, tras pasar por una plana y una cantarina que sonaba impostada; «el Pintas» / «el Piezas»; coletillas nuevas; mejora de planos; (2) el Guionista adapta chistes modernos y los guiones tienen que entenderse; (3) temas de casa y vida cotidiana en vez de oficina; (4) orden final: decorados con profundidad, humor negro cotidiano con gancho y enseñanza sin la palabra «moraleja», identidad y memoria de los personajes, todos aportan, noticias y aprender de lo que funciona, mejor música, fuera los créditos, nombres en el diálogo, Neogest Lab discreta en decorado o ropa y nombrada a veces, estancias con transición de la casa por fuera y más dinamismo; biblia reescrita y limpia de todo lo anterior.
- Versiones anteriores (v1 a v5.2, del 13/11 al 23/11/2026): en el historial de git de este archivo.
