El sistema maneja Una entidad y una propiedad, salvo en caso Booleanos
donde se admiten dos entidades y se busca la relacion entre ellos

#### Flujo de ejecución

##### Caso Pregunta NO Booleana

- Extraemos el tipo de pregunta 
- Extraemos los Sustantivos Propios como entidades desde los keywords
- ==Si hay 2 ó mas Entidades no se puede procesar==

==**ASSERT ( Hay una única entidad )**==


- Chequeamos que la entidad encontradas este en DBPEDIA ES

	- Si el keyword es entidad se guarda (**entities**)
	- Sino mediante parseo semantico se buscan ***name*** y el resto 	del texto se utilizara para desambiguar (entidad,texto desambiguacion)
	- Por último sino hay una etiqueta ***name*** se busca alguna palabra que sea sustativo Propio ***np000000*** y se guarda (entidad, texto desambiguacion)
	>En este último caso donde se buscan sustantivos propios, por ejemplo "presidente Chirac" utilizamos 

- Luego con la entidad obtenemos los **sameAs** utilizando los **wikiPageRedirects** por si acaso la entidad encontrada en *Es DBPEDIA* sea un Redirect

- Una vez obtenido la referencia en Ingles  se obtiene la propiedad clasificando el resto de los ***Keywords***

- Verificamos que si la entidad es Entidad_(desambiguation), buscamos la propiedad requerida en los ***WikiPageDisambiguates***
	
### Aggregation 
---------
¿==Cuántos== idiomas se hablan en Colombia?
idiomas, Colombia
---------
¿== Cuántos == idiomas se hablan en Turkmenistán?
idiomas, Turkmenistán
---------
¿==Cuántas== veces ha estado casada Jane Fonda?
Jane Fonda, casada, cuántas veces
---------
¿==Cuántos== hijos tuvo Benjamin Franklin?
Benjamin Franklin, hijos
---------
¿==Cuántos== grupos étnicos viven en Eslovenia?
grupos étnicos, Eslovenia
---------
¿Cuál es el país más grande del mundo?
país, más grande mundo
---------
¿Cuál fue la última película con Alec Guinness?
última película, Alec Guinness
---------
¿Todavía vive Frank Herbert?
Frank Herbert, vive
---------
¿Fué la crisis de cuba antes de la invasión de bahía de cochinos?
Crisis de Cuba, anterior,Invasión de Bahía de Cochinos
---------
¿Tiene Breaking Bad más episodios que Game of Thrones?
Breaking Bad, episodios, más que, Game of Thrones
---------

¿Cuál es el hijo mas mayor de Meryl Streep?
hijo mas mayor, Meryl Streep
---------
¿Qué empresa de la India tiene el mayor número de empleados?
empresa India, mayor número empleados
---------
¿Que ciudad tiene la mayor población?
ciudad, mayor población
---------

¿Qué películas ha rodado Kurosawa?
película, rodada, Kurosawa
---------
¿Que libro tiene el mayor numero de paginas?
libro, mayor numero paginas
---------
¿Cuál fue el primer álbum de Queen?
primer álbum, Queen
---------
¿Qué puente tiene el mayor largo del vano?
puente, mayor largo del vano
---------
Quien es el jugador de baloncesto mas alto?
jugador baloncesto, mas alto
---------
¿Que ciudad tiene la menor población?
ciudad, menor población
---------
¿Qué museo en Nueva York tiene el mayor numero de visitantes?
museo Nueva York, mayor numero visitantes
---------
¿Quién es el jugador mas jóven de dardos?
jugador más jóven dardos

¿Cuál es el estadio más grande de España?
estadio más grande España
---------
