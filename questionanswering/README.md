#### Paquetes necesarios

>
dill==0.2.7.1
requests==2.18.4
numpy==1.13.3
googletrans==2.2.0
spacy==1.9.0
docopt==0.6.2
nltk==3.2.2
SPARQLWrapper==1.8.0
beautifulsoup4==4.6.0
scikit_learn==0.19.1

Instalación

> cd PLN-2017/questionanswering
pip install -r requirements.txt

##### Model español Spacy

1. Descargamos el Model en español

> https://github.com/explosion/spacy-models/releases/download/es_core_web_md-1.0.0/es_core_web_md-1.0.0.tar.gz
>

2. Instalamos via pip

> pip install /Users/you/es_core_web_md-1.0.0.tar.gz

3. Definimos Shortcut **MUY IMPORTANTE**

> python -m spacy link /Users/you/model es_default #MUY IMPORTANTE

### Filminas 

(ejemplos y mayor detalle)

[Filminas Question Answering](https://github.com/robertinonicolazzi/PLN-2017/blob/Practico4/questionanswering/filminas_QA.pdf).

### Descripción Tarea

Este proyecto se basa en la tarea propuesta en QALD-2017 Task 1 en el cuál se 
presentan preguntas con distintos niveles de dificultad y que precisan 
diferentes técnicas para procesar su respuesta.

Como referencia bibliográfica principal se utilizó un paper de una edición 
anterior sobre un sistema en francés [French Paper](https://project-hobbit.eu/wp-content/uploads/2017/05/QALD_Paper_3.pdf).

Se analizan 4 tipos de preguntas

- **Date**
- **Resource**
- **Number**
- **Boolean**

Las preguntas pueden requerir contabilizar resultados u ordenar las respuestas 
de acuerdo a algún criterio.

El **Corpus de entrenamiento** consiste de 220 preguntas, las cuales se utilizan en su totalidad
para entrenar el *Answer Type Detector* y 120 para el *Property Extractor*.

El **Corpus de evaluación** consiste de 62 preguntas donde se utilizan sinónimos de palabras conocidas
por el sistema.

### Tipo de pregunta 

Analizando las preguntas del Corpus de entrenamiento, se extrajeron diferentes keywords y patrones que ocurren en los distintos tipos de preguntas. A partir de los cuales se diseñaron features viendo la presencia en cierta ubicación o no de cada patrón para entrenar un NaiveBayes Classifier 

### Obtención de Entidades

El proceso en la selección de entidades utilizados es el siguiente:
    
- Se obtienen todos los Noun Group 
- Se verifica que el Noun Group sea una entidad en DBPEDIA Español        
	- Si se encuentra, utilizando sameAs, se obtiene su referencia en DBPEDIA Ingles
    - Sino se intenta encontrar la entidad utilizando la DBPEDIA Ingles directamente

- Entre las entidades encontradas se elige 1 ( o 2 en Booleanas) mediante cierto orden de prioridad            
	- Presencia de Sustantivos Propios
	- Tamaño del Grupo
	- Sustantivos Comunes

### Property Extractor

Mediante un **Pipeline** formado por **DictVectorizer** y **LogisticRegression** se intenta predecir 
la propiedad que se intenta obtener con la pregunta.

A partir del corpus de entrenamiento se obtienen diferentes features utilizando 
Bag of Words, presencia de sinónimos, igualdad de traducciones para poder lograr un mapping correcto 
entre las propiedad en español e ingles.


### Preguntas Simples

Utilizando el **Property Extractor** y los keywords asociados a la pregunta, se selecciona una propiedad



### Aggregation 

Para detectar el tipo de aggregation vemos la existencia de ciertas palabras en la pregunta

##### **Count**
Si la pregunta es de tipo *number* y empieza con **Cuántos**

##### **Order** (no implementado)
Se buscan palabras como primer, ultima, mayor, grande

### Booleanas

**Se analiza con una o dos entidades**

#### 1 Entidad

Se detectan tres tipos 

###### Si entidad contiene propiedad
¿Tiene hijos Barack Obama?

###### Si entidad es de cierto tipo
se observo que generalmente el tipo solicitado se encuentra en ciertas posiciones fijas
¿La Coca Cola **es una** *bebida*?
¿Las ranas son un **tipo de** *anfibio* ?

###### Si existe una entidad 
Mediante la existencia de palabras como **Existe** o **Hay algun** se detectaron este tipo de preguntas. El tipo se encuentra generalmente acontinuación de ciertas construcciones

Existe **un** Videojuego

Hay **algún** Videojuego

#### Booleanas 2 Entidades

Al igual que antes mediante la presencia de palabras se define el filtro comparativo entre la relación entre ambas entidad


###### Misma propiedad ambas
Si existen palabras como misma, igual se define el query para ver si ambas propiedades tienen el mismo valor en la propiedad obtenida 

###### Comparaciones desiguales
Si existe palabras como mayor o menor, mas grande se define un filtro que compare el valor de la propiedad en ambas entidades

###### caso Default
en caso que ninguno de las anteriores ocurra se busca si hay alguna relación entre las entidades