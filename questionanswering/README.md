El sistema maneja **Una entidad y una propiedad**, salvo en caso Booleanos
donde se admiten dos entidades y se busca la relacion entre ellos
### Problemas actuales
##### Obtencion entidades
posible solucion en Seccion

##### Definir orden de query
No se logra definir el orden de las entidades en una query 
por ejemplo 
Dame las peliculas dirigidas por Campanella
No hay criterio para definir
{ dbr:Campanella dbo:directer ?result }
o
{?result dbo:directed ?dbr:Campanella }

Actualmente se verifica la primero en caso de no haber datos obtenidos, se prueba en el orden inverso

##### Query con mas de una 3 -upla

Esta query, pide el hijo mayor de Meryl_Streep, la entidad es 1, pero requiere como una subbusqueda, actualmente no hay criterio para estos casos.
Un posible solucion seria fijarse la cantidad de palabras que definen las propiedad, por ejemplo
Dame la escuela de la hija de Obama (aca la propiedad la definen *hija de* y *escuela*). Pero hasta ahora no he podido implementar esto

{
res:Meryl_Streep dbo:child ?uri . 
?uri dbo:birthDate ?d .
}
ORDER BY ASC(?d)\nOFFSET 0 LIMIT 


### Notas
> Para obtener la propiedad se utiliza CountVectorizer y LogRegresion
> Para obtener el tipo de pregunta NaiveBayes con features

### Obtencion de Entidades

- Extraemos el tipo de pregunta 
- Extraemos los Sustantivos Propios como entidades desde los keywords
- **Si hay 2 ó mas Entidades no se puede procesar** (Solo en booleanos)

- Chequeamos que la entidad encontradas este en DBPEDIA ES

	- Si el keyword es entidad se guarda (**entities**)
	- Sino mediante parseo de dependencia se buscan ***name*** y el resto 	del texto se utilizara para desambiguar (entidad,texto desambiguacion)
	- Por último sino hay una etiqueta ***name*** se busca alguna palabra que sea sustativo Propio ***np000000*** y se guarda (entidad, texto desambiguacion)
	>En este último caso donde se buscan sustantivos propios, por ejemplo "presidente Chirac" utilizamos 

- Luego con la entidad obtenemos los **sameAs** utilizando los **wikiPageRedirects** por si acaso la entidad encontrada en *Es DBPEDIA* sea un Redirect. Ya que las propiedades aprendidas son en ingles, utilizando **sameAs** obtenemos el URI en DBPEDIA EN

- Una vez obtenido la referencia en Ingles  se obtiene la propiedad clasificando el resto de los ***Keywords***

- Verificamos que si la entidad es Entidad_(desambiguation), buscamos la propiedad requerida en los ***WikiPageDisambiguates***

- **Para entidades ambiguas, obtenemos el abstract, para poder analizar utilizando el contenido del mismo, mediante el contexto de la entidad, con cual respuesta nos quedamos**

#### Mejora posible 
> En lugar de utilizar Sustantivos Propios, utilizar los **noum.group** y entre todos ver cuales existen en dbpedia.
> De esta forma es posible que se abarquen preguntas que no tienen entidad propias por ejemplo

Dame los ingredientes de una **tarta de zanahoria**
> la cual actualmente no se puede procesar al no encontrar entidades propias

### Aggregation 

Para detectar el tipo de aggregation vemos la existencia de ciertas palabras en la pregunta
##### **count**
Si la pregunta es de tipo *number* y empieza con **Cuántos**

##### **Order** (no implementado)
Se buscan palabras como primer, ultima, mayor, grande

### Booleanas

**Se analiza con una o dos entidades**

#### 1 Entidad

Se detectan tres tipos 
###### Si entidad contiene propiedad
query: { Entidad dbo:property ?result } Filter(BOUND(?result)) 

###### Si entidad es de cierto tipo
se observo que generalmente el tipo solicitado se encuentra en ciertas posiciones fijas
¿La Coca Cola **es una** *bebida*?
¿Las ranas son un **tipo de** *anfibio* ?
Y obteniendo el abstract de la entidad, se observa si las palabras que definen el tipo se encuentran

###### Si existe una entidad 
Mediante la existencia de palabras como **Existe** o **Hay algun** se detectaron este tipo de preguntas. El tipo se encuentra generalmente acontinuacion de ciertas construcciones

Existe **un** Videojuego
Hay **algun** Videojuego

#### Booleanas 2 Entidades

Al igual que antes mediante la presencia de palabras se define el filtro comparativo entre la relacion entre ambas entidad


###### Misma propiedad ambas

Si existen palabras como misma, igual se define el query para ver si ambas propiedades tienen el mismo valor en la propiedad obtenida 
###### Comparaciones desiguales

Si existe palabras como mayor o menor, mas grande se define un filtro que compare el vlaor de la propiedad en ambas entidades

###### caso Default

en caso que ninguno de las anteriores ocurra se busca si hay alguna relación entre las entidades

{ dbr:Michele_Obama dbo:spouse dbr:Barack_Obama}


