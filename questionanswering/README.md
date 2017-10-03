El sistema maneja Una entidad y una propiedad, salvo en caso Booleanos
donde se admiten dos entidades y se busca la relacion entre ellos

####Flujo de ejecución

#####Caso Pregunta NO Booleana

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
	
