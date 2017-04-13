# Trabajo Práctico 1
##### Nicolazzi Robertino, 2017, FaMAF

## Ejercicio 1

Se utilizaron distintos libros de la saga Harry Potter para armar el corpus,
el cual esta en idioma español, en un archivo ubicado en 
/languagemodeling/Corpus/corpusTrain.txt. Se utilizo un sent_tokenizer brindado
 por nltk para el idioma español y una expresion regular como word_tokenizer 
 para atrapar abreviaturas, siglas y demas.

## Ejercicio 2
Se construye una clase para definir modelos N-Gram. Se utiliza una lista de
con elementos de la forma (n tokens: #cantidad) y (n-1 tokens: #cantidad), 
donde por cada oración se van obteniendo sucesivas tuplas de n elementos, 
con su correspondiente tupla de n-1 elementos anteriores eliminando el ultimo
de la anterior obtenida. De esta forma el calculo de probabilidades condicio-
nales sale de forma directa, ya que se tiene el conteo. Se agregan marcadores
de inicio y final de sentencia, para evitar problemas de underflow, por 
ejemplo al calcular probabilidades condicionales de una primer palabra de una 
oración.Para calcular la probabilidad de una sentencia, se utiliza la regla de
la cadena. Y su equivalencia utilizando la probabilidad logaritmo de la 
sentencia

## Ejercicio 3

Se mantiene dos listas de la forma:
(prev_token:{next_token1: prob1, next_token2:prob2}) que se construyen agarrando
las tuplas de n elementos que se encuentran contabilizadas en el model, donde 
prev_token es de largo n-1, y las probabilidades se utiliza el calculo de 
probabilidad condicional provisto por el model. 
Cada palabra se genera utilizando el metodo de transformada a la inversa de
variables aleatorias, de esta forma se elige la palabra o token siguiente en 
base a tokens previos.

#### Oraciones generadas
##### 1-GRAM
#
* anillo segunda encogiéndose Barnabás de fue sospecha Harry de mencionaras llamó dicho mandan por dijo Harry
* torre Harry estaba Ron a Gryffindor DÓNDE de puede
* Quidditch preguntéis , una aguardaron Harry inmediato
* Pero Filch sobre varita
* Hagrid y mirando faltado Harry ataque Y unas la Así repuso

##### 2-GRAM
#
* Bueno , mirando a sangrar por entre las orejeras .
* Qué es la vista antes que hayas sido dado una risa malvada y le importa que Colagusano .
* Moody se estaba de la taza de Neville lloriqueaba en voz alta .
* Él puso la puso mucho si no acabó con una varita .
* Animados por la portada , que podéis comprarme una fuente y ruidosa de aplastarlo ?

##### 3-GRAM
#
* Y cuando ya había saltado para coger la Descurainia sophia y centinodia murmuró , dónde estás .
* Ya sabes , Harry ; te importa ?
* Se supone que estamos desgnomizando , salen a curiosear .
* Ah , bueno , salvo Dumbledore y Zacharias Smith , que estoy deseando que los niños por otra parte .
* Te asustas al oír que los tiró contra el suelo ; él y Ginny fueron a la Orden del Fénix ... Harry aguzaba el oído por casualidad lo interrumpió Dumbledore hay una cantidad de vendajes , apesta .


##### 4-GRAM
#
* Antes de que Harry les enseñaba ; arrugaba la regordeta cara en una mueca de asco .
* La reina blanca volvió su cara sin rostro hacia Ron.
* Les debemos tanto ... Hombres nobles que trabajaron sin descanso para ayudar a Ginny?
* 'Romilda Vane' dijo Ron , que parecía estar lleno de nargles.
* No lo sé, señor respondió temblorosa la primera voz.


## Ejercicio 4 Add One

En la inicializacion de la clase, se crea un **set** de python para ir 
agregando las palabras que ocurren, de esta manera nos aseguramos unicidad de
las mismas, luego procedemos a calcular el largo de este **set** y guardamos
el valor en V.
Por definicion el calculo de la probabilidad condicional de un token dado
tokens previo, se modifica sumando uno al numerador y sumando V al denominador

## Ejercicio 5 Perplexity
Se crea una clase Evaluacion, la cual utilizando el calculo de la log probability de un modelo y su cross entropy obtenemos la perplexity del mismo

| Modelo | 1 | 2 | 3 | 4 |
| ------ | ------ | ------ | ------ | ------ |
| ADDONE | 1172.888 | 2992.226 | 19154.502 | 34630.520 |

