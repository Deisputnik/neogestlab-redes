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
1. **Apertura en frío** (orden del dueño 27/11 noche, por los datos del §11.2):
   - El primer fotograma es la escena del gancho, en mitad del lío.
   - Encima va el título fijo (`titulo_fijo`): la situación con el colectivo que se reconoce («CUANDO TU JEFA FICHA POR DOS»), en grande y con 10 palabras como mucho.
   - La frase más fuerte del conflicto se oye en los 2 primeros segundos.
   - Justo después van 1,6 s de la casa por fuera, **sin texto**, como cabecera de comedia americana. La pone el render solo.
2. **Gancho** en mitad del lío: quién quiere qué y qué hay en juego, reconocible en el primer segundo. Abre una pregunta (`promesa`) que solo se responde en el remate.
3. **Escalada** de 5 a 8 golpes, cada uno peor y consecuencia del anterior, con un giro sembrado a mitad (`giro`).
4. **Estancias**: la acción pasa por 2 o 3 estancias de la casa o del barrio; siempre hay al menos un cambio y como mucho dos (campo `set` en la escena donde se cambia). **No están todos juntos todo el capítulo**: en cada estancia hay un grupo distinto, de dos o tres, con su conversación, y lo que se dice en una no lo saben en la otra. Cada cambio hace avanzar la historia.
5. **Transición**: entre estancia y estancia va un plano corto de la casa por fuera, cada vez con un encuadre distinto del plano de la cabecera. Lo pone el render solo; no se escribe en el guion.
6. **Remate de Neo**: reúne lo que pasó en las distintas estancias, responde a la pregunta del gancho con algo concreto y deja la enseñanza.
7. **Cierre**: remate de Neo y 3 s de promo de la empresa, que es el último plano. Ya no hay plano de casa al cierre ni bucle obligatorio. **No hay créditos de reparto.**
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

## 11. Adaptación por red (el mismo episodio, empaquetado para cada red)
Cada red premia cosas distintas. El episodio (guion, render y patrón del §6) es el mismo para todas; lo que cambia por red es cómo se presenta: título, texto en pantalla, descripción, comentario fijado, lista y orden. Se estudia y se cierra una red cada vez. Hecho: YouTube, Instagram y Facebook (27/11/2026). Pendiente: TikTok.
- 2026-11-27 (noche) · §11.1 aprobado por el dueño entero, incluida la prueba de la versión corta de 20-35 s en YouTube (1 de cada 5 episodios).

### 11.1 YouTube Shorts (estudio del 27/11/2026, orden del dueño)
**Lo que dicen nuestros datos** (canal @neogestlab, 60 vídeos, 216 suscriptores, vistas leídas el 27/11):
- Lo que más funcionó: «Parte 2» de una historia (1,1 K y 1 K), el Short con la coletilla de la serie y emoji en el título (1.061), «La reunión rápida que no lo fue» (901), «¿Quién paga las botellas rotas?» (586) y «Cobrar por respirar: el cuñado lo defiende» (500).
- Lo que no funcionó: los títulos de anuncio con pregunta sobre un producto («¿Apuntas el stock en una libreta?», «¿Y si tu teléfono se cogiera solo?», «¿Cuántas llamadas pierdes al día?»): 0-4 vistas. Los episodios de barrio recientes con título descriptivo y sin emoji: 32-133 vistas.
- La duración no explica la diferencia: «botellas rotas» (63 s, 586 vistas) y «El domingo que nadie cobra» (64 s, 79 vistas) duran lo mismo. Lo que cambia es el título y lo claro que es el conflicto.
- Nadie comenta: 0 comentarios y 1-8 me gusta por Short. YouTube no recibe ninguna señal de que el vídeo interese.

**Lo que hacen los virales del nicho** (humor de autónomos, curro y vida cotidiana en España):
- Nachter (6,55 M suscriptores): «Ventajas de ser autónomo en España 🫠🤣» tiene 411 K vistas, 12 K me gusta y 246 comentarios con 8 s de duración. «Autónomos en la cena de empresa 🍽🤣» tiene 367 K vistas y 30 K me gusta con 35 s. Otros del mismo estilo («Cuando te tomas vacaciones pero eres autónomo», «Autónomos vs políticos») tienen entre 183 K y 217 K. Su serie numerada «Millennial en el año 2060 · Capítulo 8» tiene 1,6 M.
- Los cuatro rasgos que comparten:
  1. **El título nombra a un colectivo que se reconoce** (autónomos, el cuñado, la madre, el que paga a 90 días) y una situación. Quien es de ese colectivo lo comenta y lo comparte.
  2. **El título va escrito en el vídeo, fijo arriba, desde el primer fotograma hasta el último.** Quien entra a mitad sabe al momento de qué va.
  3. **El título y el vídeo son irónicos**: dicen «ventajas» y enseñan lo contrario. Termina en seco, sin explicaciones, y vuelve a empezar (bucle).
  4. **Las series van numeradas** («Capítulo 9»). En nuestro canal, «Parte 2» también es lo que más se vio.
- Los Shorts genéricos de «humor con IA» del mismo nicho se quedan en 300-1.200 vistas: poner «IA» en el título no atrae a nadie. Lo que atrae es la situación de la gente.

**Reglas para YouTube (las cumple quien rellena el bloque `youtube` de `post.json` y quien publica):**
1. **Título** de 45 caracteres como mucho, más « #Shorts». La fórmula es: colectivo o personaje que se reconoce + situación + 1 o 2 emojis (🫠🤣, 😂, 💀, 🍽…). Moldes que valen:
   - «Cuando eres autónomo y…»
   - «Ventajas de [ser X / tener un cuñado así]»
   - «[X] en [la cena / la reunión / el grupo de la familia]»
   - «[X] ANTES vs AHORA»
   - «El cuñado que…»
   - Si el episodio sigue a otro: «… · Parte N».
   
   Prohibido:
   - las preguntas de anuncio sobre un producto;
   - «IA», «Neogest», «app» o el nombre de una función en el título;
   - los nombres de los personajes en el título (nadie los conoce todavía), salvo «el cuñado» o «la vecina» como tipo de persona;
   - los títulos de más de 60 caracteres.
2. **Texto fijo en pantalla**: el título (sin el emoji ni #Shorts) va escrito arriba, en grande y legible, durante todo el vídeo y no solo en el plano de la casa. No puede tapar las caras ni los subtítulos. *Tarea de Mejora, prioridad alta (aprobada por el dueño el 27/11): implementarlo en el render: campo `titulo_fijo` del episodio en `gen_episodios.py`, que pinte un texto persistente en todas las escenas. Hasta que esté, `gancho_casa` debe ser ese mismo título.*
3. **Ironía en el gancho**: el título promete lo contrario de lo que pasa, o pone en duda algo que el público ya vive. El remate de Neo contesta de verdad a esa promesa.
4. **Comentarios**:
   - El comentario fijado de YouTube es SIEMPRE una pregunta que se contesta con una cifra o con una experiencia propia («¿A ti cuántos días te pagan? Una cifra.», «¿Quién es el cuñado de tu familia? Etiquétalo.»). Nunca un enlace ni una venta.
   - Comunidad contesta en la primera hora todos los comentarios de YouTube.
5. **Descripción**:
   - Primera línea: la situación en una frase con el colectivo («Para todos los que alguna vez han…»).
   - Segunda línea: «Más episodios de El Jambo que sabe 👉 lista de la serie».
   - Después, la prueba gratuita (`/solicitar?…&src=youtube`), «Web: neogestlab.com» y «By Neogest Lab».
   - Como mucho 3 hashtags: #humor, el del colectivo (#autonomos, #cuñados, #vecinos…) y #shorts.
6. **Serie y orden**:
   - Cada episodio entra en la lista de reproducción «El Jambo que sabe», en orden.
   - Cuando un episodio continúa otro, el anterior lleva como «vídeo relacionado» el siguiente. Así quien termina uno pasa al otro.
   - Las historias que dan para más se cortan en partes («Parte 1 / Parte 2»): es lo que mejor nos ha funcionado en YouTube.
7. **Duración (aprobado por el dueño el 27/11/2026)**: el episodio sigue siendo de 45-70 s (§6) en todas las redes. Además, en YouTube se prueba una **versión corta de 20-35 s en 1 de cada 5 episodios**: con la misma apertura en frío del §6, 3 golpes, el remate de Neo y la promo de 3 s. Funciona así:
   - El Creador marca en `cola/<pieza>/post.json` `"youtube": {"corto": true}` y genera un segundo render solo con esas escenas.
   - Ese segundo render es el que se sube a YouTube; Instagram, Facebook y TikTok publican el largo.
   - A los 7 días, Analista compara en `equipo/virales_semana.md` las vistas, los me gusta y los comentarios de los cortos con la media de los largos de la misma semana.
   - Si los cortos ganan dos semanas seguidas, YouTube pasa a publicar solo versiones cortas. Si pierden, se retira la prueba. En los dos casos se anota aquí.
8. **Medir**: Analista apunta cada semana, por Short de YouTube, las vistas, los me gusta, los comentarios y qué molde de título llevaba, y deja en `equipo/virales_semana.md` qué molde gana. El molde que pierde dos semanas seguidas se retira de esta lista.

### 11.2 Instagram Reels (estudio del 27/11/2026, orden del dueño)
**Lo que dicen nuestros datos** (insights de @neogestlab vía Buzzfy, leídos el 27/11):
- **Lo que mejor funcionó**:
  - «Parte 2: el cliente que paga a 90 días. La ley dice 60.»: 1.389 vistas, 1.101 cuentas alcanzadas y un 29,5 % de gente que se va en los primeros segundos (en adelante, «salidas»).
  - «Parte 2: le diste el bar entero a la IA…»: 710 vistas y 22,2 % de salidas.
  
  Los dos abrían directamente en el conflicto, con la frase del lío en pantalla desde el primer fotograma.
- **El formato de barrio actual**, que abre con 1,6 s de la casa por fuera:
  - «El vecino que no devuelve el taladro»: 134 vistas y 70 % de salidas.
  - «El perro del vecino»: 130 vistas y 80 % de salidas.
  - «Cobrar por respirar»: 48 vistas y 57 % de salidas.
  - Los dos últimos episodios: 8-11 vistas y 100 % de salidas.
  
  Quien llega desde Explorar ve una casa, no un lío, y se va. Instagram deja de enseñar el reel.
- **Las promos con pregunta de producto** («¿Apuntas el stock…?», «¿Y si tu teléfono…?»): 9-13 vistas y 62-75 % de salidas.
- **En toda la cuenta**: 0 comentarios y casi 0 veces compartido. Nadie lo manda a nadie, que es justo lo que Instagram premia.

**Lo que hacen los virales del nicho** (biblioteca de Buzzfy, sketches de humor sobre jefes, clientes y vida cotidiana):
- **Sketches con actores**:
  - «Cuando llega la jefa» (@zeebra.chile): 64 K vistas, 14 s.
  - «EL CLIENTE QUE LE HICISTE FRENOS DICE QUE AHORA NO ARRANCA» (@avalos.racing): 36 K vistas, 29 s, 176 veces compartido y una pregunta para comentar.
  - «El paciente más tranquilo de España» (@xavi.rigau): 16,8 K vistas, 40 s.
  
  En los tres, el texto en pantalla del primer fotograma ES la situación («Cuando…», en mayúsculas o en grande) y la primera frase dicha ya está en mitad del lío.
- **Sketches animados con IA sobre la vida de casa** (familia, vecinos, el marido que ronca, el que se pasa el día en el móvil): 18 K, 57 K y 223 K vistas con 14-32 s. Son gags visuales que se entienden sin sonido y se comparten mucho (294 veces el de 223 K).
- **Reglas del Playbook de Buzzfy** (531 K cuentas, cada una comparada consigo misma):
  1. Si en los 3 primeros segundos se va menos del 30 %, el reel despega 1 de cada 3 veces; lo normal es que se vaya el 57 %.
  2. Los que despegan se comparten 1 vez por cada 8 me gusta.
  3. El reel que se publica justo después de uno que despega tiene 1,8 veces más opciones de despegar también.
  4. Subtítulos quemados.
  5. Como mucho 5 hashtags.
  6. Sábado y domingo rinden un 10 % más.

**Reglas para Instagram:**
1. **Texto del primer fotograma**:
   - Grande y con la situación, al estilo «Cuando…»: «CUANDO TU JEFA FICHA POR DOS», «EL VECINO QUE NO DEVUELVE EL TALADRO»…
   - Como mucho 10 palabras. Se queda fijo durante todo el reel: es el mismo `titulo_fijo` de §11.1, sin emoji.
   - Prohibido abrir con una pregunta de producto.
2. **Apertura en el lío (aprobado por el dueño el 27/11 noche, para TODOS los episodios y todas las redes)**:
   - El vídeo arranca en la escena del gancho, con la frase más fuerte del conflicto en los 2 primeros segundos y el texto del punto 1 en pantalla.
   - La casa por fuera va después, sin texto, como cabecera.
   - No hay plano de casa al cierre.
   - Está en el §6.
3. **Hecho para mandarlo**: cada episodio tiene un «a quién se lo mandas» evidente (la jefa, el cuñado, el vecino, el que paga tarde). La primera línea del texto lo dice: «Mándaselo a tu cuñado, el que lo sabe todo».
4. **Texto del post (caption)**:
   - Línea 1: la situación con el colectivo, la misma idea que el texto en pantalla.
   - Línea 2: a quién mandárselo.
   - Línea 3: la pregunta para comentar, que se contesta con una cifra o con una palabra.
   - Después, la prueba gratuita y los avisos de IA y ficción.
   - Nunca la palabra «Moraleja» (tampoco en el texto del post, igual que en el vídeo, §3).
   - Nunca el reparto entero («Rosa, Felipe, Sindy, Jambo…»): nadie lo conoce y le quita sitio al gancho.
   - 3-5 hashtags: #humor o #humornegro, el del colectivo (#autonomos, #cuñados, #vecinos, #hosteleria…) y #serieeljambo.
5. **Reel que despega**: si un reel supera el doble de la mediana de vistas de la cuenta, en las 24-48 h siguientes se publica su «Parte 2» o un episodio del mismo tema. Es la regla de las rachas, y aquí ya funcionó con «Parte 2».
6. **Segunda vida**: «Parte 2: el cliente que paga a 90 días» (1.389 vistas) y «Parte 2: el bar» (710) se rehacen con el reparto vigente y el mismo arranque, como episodios nuevos. El vídeo viejo no se vuelve a subir: lleva el reparto retirado.
7. **Comentarios**: Comunidad contesta todos en la primera hora y fija el que tenga más gracia. Si nadie comenta en 1 h, el comentario fijado de la cuenta repite la pregunta con un ejemplo propio («Yo empiezo: 120 días»).
8. **Medir**: Analista apunta cada semana, por reel, las salidas, las veces compartido, los comentarios, qué texto llevaba en el primer fotograma y si era feed o reel de prueba. Lo deja en `equipo/virales_semana.md` con qué texto y qué apertura ganan.

### 11.3 Facebook Reels (estudio del 27/11/2026, orden del dueño)
**Lo que dicen nuestros datos** (página Neogest Lab, leídos el 27/11):
- **Últimos 28 días**: 972 visualizaciones en toda la página, 30 interacciones y 49 seguidores.
- **Por reel**: casi todos los episodios y promos se quedan entre 0 y 6 visualizaciones. Las únicas excepciones son el reel de marca «Nueva imagen, la misma misión» (269) y dos reels con 243.
- **Estado de la página**: correcto, sin restricciones. El problema no es un castigo, es que Facebook no ve motivo para recomendar.
- **Volumen**: hoy se suben hasta 12 reels al día más los atrasos (`herramientas/atrasos.py`, orden del 12/11 «subir de forma masiva»). Con tan poco alcance total, cada reel nuevo se reparte las mismas pocas visualizaciones.

**Lo que dice Meta** (anuncio «Rewarding Original Creators on Facebook», marzo de 2026, y su guía de contenido):
- Facebook da prioridad en el Feed y en Reels al contenido original, el que produce la propia página, y le baja el alcance al contenido sin originalidad.
- Meta saca una huella de cada vídeo y apunta qué cuenta lo subió primero.
- Se considera sin originalidad volver a subir algo sin cambios de valor (poner bordes, subtítulos o cambiar la velocidad no cuenta como cambio).
- Las cuentas que lo hacen a menudo pueden quedar fuera de las recomendaciones.
- Nuestros episodios son nuestros y originales; lo que hay que cuidar es no subir dos veces el mismo vídeo ni copias con cambios mínimos.

**Reglas para Facebook:**
1. **Mismo episodio, misma apertura en frío** (§6) y mismo `titulo_fijo` en pantalla. Se sube el archivo del render propio, nunca una copia descargada de Instagram (que lleva marca de agua).
2. **Una sola subida por vídeo**: un mismo vídeo no se sube dos veces a Facebook, ni como reel ni como vídeo del Feed ni desde atrasos. Si hay que repetir un tema, se hace un episodio nuevo.
3. **Texto del post para el público de Facebook** (más adulto, comparte por WhatsApp y Messenger):
   - Línea 1: la situación con el colectivo, igual que en Instagram.
   - Línea 2: «Compártelo con [quien sea] 😂».
   - Línea 3: la pregunta que se contesta con una cifra o con una experiencia.
   - Sin la palabra «Moraleja» ni el reparto entero. Como mucho 3 hashtags.
4. **El enlace de la prueba gratuita va en el primer comentario de la página, no en el texto del post.** Así el post se ve como contenido y no como anuncio. Comunidad lo publica nada más salir el reel. Analista compara durante 2 semanas el alcance con enlace en el texto y sin él.
5. **Comentarios**: Comunidad contesta todos en la primera hora. Una conversación en los comentarios es la señal que más empuja a un reel en Facebook. Además, los que comparte el propio dueño desde su perfil personal (David Marín) cuentan como reparto real: 1 o 2 por semana, los mejores.
6. **Volumen (cambio pendiente del visto bueno del dueño)**: pasar de «12 al día más atrasos» a **como mucho 4 reels al día**: los episodios nuevos del día y una promo, sin vaciar atrasos. Durante 2 semanas se miden las visualizaciones medias por reel frente a las 2 semanas anteriores. Hasta que el dueño lo apruebe, `atrasos.py` sigue igual.
7. **Reel de marca**: el único formato que ha pasado de 200 visualizaciones en Facebook es el de imagen de marca. Se publica uno al mes, con novedades reales de Neogest Lab, nunca inventadas.
8. **Medir**: Analista apunta cada semana, por reel de Facebook, las visualizaciones, el tiempo medio, las interacciones, las veces compartido y si llevaba enlace en el texto. Lo deja en `equipo/virales_semana.md`.

## 10. Anexo: cifras verificadas (solo para el episodio de trabajo de cada tanda; confirmar la fuente antes de reutilizar)
| Cifra | Dato | Fuente leída | Matiz |
|---|---|---|---|
| Horas extra no pagadas | 2,5 millones de horas a la semana en el 1T 2026; el 42 % de las horas extra no se cobra (5,89 M semanales, 3,38 M pagadas) | El Español, 26/05/2026, citando la EPA del INE | Confirmar en ine.es. Cifras en euros y empleos del mismo texto son estimaciones de UGT/CCOO sin metodología: no usarlas. |
| Administración en pymes | El 55 % de las empresas cree que las tareas administrativas le quitan tiempo para lo estratégico | Forbes España 22/04/2026, informe Qonto + IO Investigación | Lo encarga una fintech: decir siempre «según un informe de Qonto». |
| Plazo legal de pago | 30 días por defecto y, por pacto entre empresas, nunca más de 60 días naturales | BOE, Ley 3/2004 art. 4 | Información general, no asesoramiento legal. |
| Registro de jornada | Obligatorio para todas las empresas desde el 12/05/2019 | Estatuto de los Trabajadores, art. 34.9, Real Decreto-ley 8/2019 | Información general, no asesoramiento legal. |

## Registro de cambios
- 2026-11-27 (noche) · §11.3 nuevo, Facebook: datos de la página (972 visualizaciones en 28 días, de 0 a 6 por reel) y la política de originalidad de Meta (marzo de 2026). Reglas: una sola subida por vídeo, texto pensado para compartir, enlace en el primer comentario, comentarios en la primera hora, reel de marca mensual. Bajar el volumen a 4 al día queda pendiente del dueño.
- 2026-11-27 (noche) · Orden del dueño: **apertura en frío para todos los episodios**. Se empieza en el lío con `titulo_fijo` en grande, la casa va después sin texto y no hay casa al cierre. §6 reescrito y borrado lo que lo contradecía: el bucle de casa al abrir y cerrar y la prueba con reels de prueba del §11.2. `gen_episodios.py`, el Guionista (campo `titulo_fijo` obligatorio, `bucle_visual` opcional), Calidad y el Creador están alineados.
- 2026-11-27 (noche) · §11.2 nuevo, Instagram, a partir de los insights propios (los reels que abren en el lío tienen un 22-30 % de salidas; el formato con la casa al abrir, un 57-100 %) y de los virales del nicho (Buzzfy). Prueba con reels de prueba de la apertura en frío en 1 de cada 5 episodios, sin tocar el feed. Fuera la palabra «Moraleja» y el reparto entero del texto del post.
- 2026-11-27 (noche) · §11 nuevo, «Adaptación por red», empezando por YouTube (orden del dueño: estudiar por qué funcionan los virales del nicho y adaptar cada red). Basado en los datos del canal propio y en los Shorts virales de autónomos y curro (Nachter). Pendiente: Instagram, Facebook y TikTok.
- 2026-11-27 · biblia v5.3 · órdenes del dueño de ese día, en este orden: (1) la voz de Jambo no se entendía → voz de calle real, del sur y con ceceo, tras pasar por una plana y una cantarina que sonaba impostada; «el Pintas» / «el Piezas»; coletillas nuevas; mejora de planos; (2) el Guionista adapta chistes modernos y los guiones tienen que entenderse; (3) temas de casa y vida cotidiana en vez de oficina; (4) orden final: decorados con profundidad, humor negro cotidiano con gancho y enseñanza sin la palabra «moraleja», identidad y memoria de los personajes, todos aportan, noticias y aprender de lo que funciona, mejor música, fuera los créditos, nombres en el diálogo, Neogest Lab discreta en decorado o ropa y nombrada a veces, estancias con transición de la casa por fuera y más dinamismo; biblia reescrita y limpia de todo lo anterior.
- Versiones anteriores (v1 a v5.2, del 13/11 al 23/11/2026): en el historial de git de este archivo.
