# Trabajo Práctico 1
##### Nicolazzi Robertino, 2017, FaMAF

## Ejercicio 1

##### Estadísticas básicas
Cantidad de Oraciones:    17378
Cantidad de Tokens:       517194
Cantidad de Palabras:     46501
Cantidad de Etiquetas:    85



##### Etiquetas Mas Frecuentes 


|   TAG     |  #Apariciones   |    Frecuencia    |        5 Palabras Mas Frecuentes              |
| --------  | --------------- | ---------------- | --------------------------------------------- |
|  sp000    |      79884      |      15.446      | de \ en \ a \ del \ con                       |
| nc0s000   |      63452      |      12.269      | presidente \ equipo \ partido \ país \ año    | 
|  da0000   |      54549      |      10.547      | la \ el \ los \ las \ El                      |
|  aq0000   |      33906      |      6.556       | pasado \ gran \ mayor \ nuevo \ próximo       | 
|    fc     |      30147      |      5.829       | ,                                             |
| np00000   |      29111      |      5.629       | Gobierno \ España \ PP \ Barcelona \ Madrid   | 
| nc0p000   |      27736      |      5.363       | años \ millones \ personas \ países \ días    | 
|    fp     |      17512      |      3.386       | .                                             |
|    rg     |      15336      |      2.965       | más \ hoy \ también \ ayer \ ya               |       
|    cc     |      15023      |      2.905       | y \ pero \ o \ Pero \ e                       |



##### Niveles de Ambiguedad


| Ambiguedad |  #Apariciones   |    Frecuencia    |       5 Palabras Mas Frecuentes        |
| ---------  | --------------- | ---------------- | -------------------------------------- |
|     1      |      43972      |      94.561      | , \ con \ por \ su \ El                |
|     2      |      2318       |      4.985       | el \ en \ y \ " \ los                  |
|     3      |       180       |      0.387       | de \ la \ . \ un \ no                  |
|     4      |       23        |      0.049       | que \ a \ dos \ este \ fue             |
|     5      |        5        |      0.011       | mismo \ cinco \ medio \ ocho \ vista   |
|     6      |        3        |      0.006       | una \ como \ uno                       |
|     7      |        0        |       0.0        |                                        |
|     8      |        0        |       0.0        |                                        |
|     9      |        0        |       0.0        |                                        |

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

| Modelo  | 1 | 2 | 3 | 4 |
| ------  | ------ | ------ | ------ | ------ |
| ADDONE  | 1172.888 | 2992.226 | 19154.502 | 34630.520 |
| INTER   | 1618.543 (G=600) | 745.688 (G=650) | 777.042 (G=850) | 842.837 (G=1300) |
| BACKOFF | 1618.543 (B=0.3)| 635.193 (B=0.8) | 571.247 (B=0.8)   | 567.263 (B=0.8)  |


## Ejercicio 6 Interpolated

Se crea un diccionario conteniendo las ocurrencias para N-Gram, (N-1)-Gram hasta 1-Gram.
Conteniendo las apareciciones de los delimitadores de inicio de oración, final de oración
y la cantidad total de palabras. Se contabiliza la cantidad de word types, ya que 
se utiliza suavizado addone para unigramas, si es requerido.

Gammas posibles (Elegidos a partir de observaciones)

[600.0,650.0,800.0,850.0,900.0,950.0,1200.0,1300.0]

## Ejercicio 7 BackOFF

Se crea un diccionario conteniendo las ocurrencias para N-Gram, (N-1)-Gram hasta 1-Gram.
Conteniendo las apareciciones de los delimitadores de inicio de oración, final de oración
y la cantidad total de palabras. Se contabiliza la cantidad de word types, ya que 
se utiliza suavizado addone para unigramas, si es requerido.
Se precalculan los denominadores y los alfas para optimizar el calculo de las
probabilidades condicionales, para ellos primero se debe realizar el conteo


Betas posibles (Elegidos a partir de observaciones)

[0.3,0.6,0.7,0.8,0.9]

### TEST

Se agrego un test de NGram para n de valor 3, se verifica su count y su 
probabilidad condicional

Se agrego un test que verifica el count para 3-GRAM en Interpolated
y en BackOff