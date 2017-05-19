# Trabajo Práctico 2 TAGGING
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

Significado Etiquetas

fuente: https://nlp.stanford.edu/software/spanish-faq.shtml#tagset

|   TAG     |  Significado    |
| --------  | --------------- |
|  sp000    |      Preposición      |
| nc0s000   |      Sustantivo común singular      |
|  da0000   |      Artículo definido      |
|  aq0000   |      Adjetivo descriptivo      |
|    fc     |      Coma ","      |
| np00000   |      Sustantivo Propio      |
| nc0p000   |      Sustantivo común plural      |
|    fp     |      Punto "."      |
|    rg     |      Adverbio general      |    
|    cc     |      conjuncion coordinante, unir palabras u oraciones      | 

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

## Ejercicio 2 BaseLine
Para elegir la etiqueta correspondiente a una palabra se genera una diccionario donde
por cada palabra vista, se contabilizan las ocurrencias de los distintos tags
que esten asociadas a esta.

Luego para elegir el tag de la misma, se selecciona el que mayor frecuencia tiene, es decir mayor cantidad de
ocurrencias. En caso de ser una palabra desconocida, es decir que no esta en la información de entrenamiento,
 fijamos el tag 'nc0s000' (sustantivo común singular)

## Ejercicio 3

Generación de scripts de entrenamiento y de evaluación.
En al evaluación se toma en cuenta el porcentaje de etiquetas evaluadas correctamente
por los distintos modelos 

RESULTADOS BASELINE 

Total Accuracy: 87.58%
Known Words: 95.26%
Unknown Words: 18.01%

|            |   sp000 |  nc0s000|   da0000|   aq0000|     fc  | nc0p000 |   rg    |  np00000|    fp   |     cc  |
|------------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
|      sp000 |  14.284 |   0.047 |   0 |   0 |   0 |   0 |   0.005 |   0 |   0 |   0 | 
|    nc0s000 |   0.002 |  12.223 |   0 |   0.252 |   0 |   0.001 |   0.025 |   0.001 |   0 |   0.001 | 
|     da0000 |   0 |   0.151 |   9.543 |   0 |   0 |   0 |   0 |   0 |   0 |   0 | 
|     aq0000 |   0.005 |   2.050 |   0 |   4.868 |   0 |   0.117 |   0.003 |   0 |   0 |   0 | 
|         fc |   0 |   0 |   0 |   0 |   5.850 |   0 |   0 |   0 |   0 |   0 | 
|    nc0p000 |   0 |   1.237 |   0 |   0.225 |   0 |   4.059 |   0 |   0 |   0 |   0 | 
|         rg |   0.018 |   0.314 |   0 |   0.044 |   0 |   0 |   3.273 |   0 |   0 |   0.022 | 
|    np00000 |   0.003 |   2.046 |   0 |   0.001 |   0 |   0.003 |   0 |   1.515 |   0 |   0.001 | 
|         fp |   0 |   0 |   0 |   0 |   0 |   0 |   0 |   0 |   3.550 |   0 | 
|         cc |   0.001 |   0.014 |   0 |   0 |   0 |   0 |   0.049 |   0.001 |   0 |   3.341 | 


## Ejercicio 4 Hidden Markov Models

Para elegir el etiquetado de una sentencia se utilizan dos valores:
* La probabilidad de que ocurra un tag dado una cierta cantidad (n) de tags previos anteriores
* La probabilidad de que ocurra que cierta palabra x este asociada a un tag y

Estas probabilidades se obtienen de diccionarios que son introducidos por parametros

trans: cada n-1 tags, tienen asociado distintos tag que los suceden con su respectiva probabilidad
out: cada tag tiene asociado palabras con las que se relaciona y su probabilidad de ocurrencia

###### Algoritmo de Viterbi

Se implementa el algoritmo de viterbi para poder el etiquetado de cada sentencia. Para ello se utilizan
las probabilidades antes mencionadas y una tabla "pi" la cual va guardando las probabilidades maximas
para una secuencia de cierto largo que termine con determinados tags

## Ejercicio 5

Se estiman las estructuras trans y out utilizando sentencias de entrenamiento, cada una de las cuales
viene etiquetada. Se utilizan los estimadores de maximum-likelihood definidos por Collins.

| n |   Total   |    Known    |    Unknown   |      Tiempo     |
|---|---------- |-------------|--------------|-----------------|
| 1 |   85.84%  |    95.28%   |     0.45%    |    20 seg       |
| 2 |   91.34%  |    97.63%   |     34.33%   |    42 seg       |
| 3 |   91.86%  |    97.65%   |     39.49%   |	  3 min 54seg  |
| 4 |   91.61%  |    97.31%   |     40.03%   |    29 min 7seg  |

MLHMM N = 1

|            |   sp000 |  nc0s000|    da0000|    aq0000|        fc|   nc0p000|        rg |  np00000  |      fp  |      cc|  
|------------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
|      sp000 |  14.328 |   0.003 |   0.000 |   0.000 |   0.000 |   0.000 |   0.005 |   0.000 |   0.000 |   0.000 | 
|    nc0s000 |   1.793 |  10.408 |   0.000 |   0.261 |   0.000 |   0.001 |   0.033 |   0.001 |   0.000 |   0.001 | 
|     da0000 |   0.151 |   0.000 |   9.542 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 | 
|     aq0000 |   1.818 |   0.225 |   0.000 |   4.827 |   0.000 |   0.135 |   0.003 |   0.000 |   0.000 |   0.000 | 
|         fc |   0.000 |   0.000 |   0.000 |   0.000 |   5.850 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 | 
|    nc0p000 |   1.236 |   0.001 |   0.000 |   0.179 |   0.000 |   4.102 |   0.000 |   0.000 |   0.000 |   0.000 | 
|         rg |   0.316 |   0.017 |   0.000 |   0.031 |   0.000 |   0.000 |   3.283 |   0.000 |   0.000 |   0.022 | 
|    np00000 |   2.036 |   0.006 |   0.000 |   0.001 |   0.000 |   0.003 |   0.000 |   1.523 |   0.000 |   0.001 | 
|         fp |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   3.550 |   0.000 | 
|         cc |   0.014 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.049 |   0.001 |   0.000 |   3.342 | 


MLHMM N = 2


|            |   sp000 |  nc0s000|    da0000|    aq0000|        fc|   nc0p000|        rg |  np00000  |      fp  |      cc|  
|------------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
|      sp000 |  14.282 |   0.002 |   0.013 |   0.001 |   0.001 |   0.000 |   0.023 |   0.002 |   0.000 |   0.004 | 
|    nc0s000 |   0.030 |  11.783 |   0.071 |   0.215 |   0.019 |   0.007 |   0.030 |   0.301 |   0.000 |   0.002 | 
|     da0000 |   0.004 |   0.072 |   9.519 |   0.001 |   0.000 |   0.000 |   0.000 |   0.058 |   0.000 |   0.000 | 
|     aq0000 |   0.110 |   0.369 |   0.110 |   5.839 |   0.136 |   0.100 |   0.064 |   0.170 |   0.001 |   0.002 | 
|         fc |   0.000 |   0.000 |   0.000 |   0.000 |   5.850 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 | 
|    nc0p000 |   0.024 |   0.683 |   0.104 |   0.133 |   0.026 |   4.219 |   0.020 |   0.198 |   0.000 |   0.000 | 
|         rg |   0.061 |   0.030 |   0.028 |   0.056 |   0.003 |   0.007 |   3.353 |   0.074 |   0.000 |   0.024 | 
|    np00000 |   0.031 |   0.424 |   0.038 |   0.152 |   0.052 |   0.008 |   0.046 |   2.505 |   0.001 |   0.001 | 
|         fp |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   3.549 |   0.000 | 
|         cc |   0.001 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.055 |   0.011 |   0.000 |   3.338 | 


MLHMM N = 3

|            |   sp000 |  nc0s000|    da0000|    aq0000|        fc|   nc0p000|        rg |  np00000  |      fp  |      cc|  
|------------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
|      sp000 |  14.281 |   0.003 |   0.014 |   0.002 |   0.002 |   0.000 |   0.018 |   0.003 |   0.000 |   0.002 | 
|    nc0s000 |   0.012 |  11.853 |   0.064 |   0.209 |   0.017 |   0.034 |   0.023 |   0.252 |   0.001 |   0.004 | 
|     da0000 |   0.000 |   0.068 |   9.513 |   0.008 |   0.000 |   0.000 |   0.000 |   0.050 |   0.000 |   0.000 | 
|     aq0000 |   0.087 |   0.324 |   0.075 |   6.091 |   0.091 |   0.096 |   0.066 |   0.109 |   0.002 |   0.013 | 
|         fc |   0.000 |   0.000 |   0.000 |   0.000 |   5.850 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 | 
|    nc0p000 |   0.018 |   0.657 |   0.091 |   0.140 |   0.014 |   4.331 |   0.026 |   0.155 |   0.001 |   0.004 | 
|         rg |   0.058 |   0.025 |   0.025 |   0.059 |   0.009 |   0.009 |   3.393 |   0.031 |   0.000 |   0.025 | 
|    np00000 |   0.024 |   0.396 |   0.037 |   0.149 |   0.033 |   0.024 |   0.069 |   2.553 |   0.001 |   0.007 | 
|         fp |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   3.548 |   0.000 | 
|         cc |   0.001 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.063 |   0.009 |   0.000 |   3.331 | 

MLHMM = 4

|            |   sp000 |  nc0s000|    da0000|    aq0000|        fc|   nc0p000|        rg |  np00000  |      fp  |      cc|  
|------------|---------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
|      sp000 |  14.290 |   0.002 |   0.012 |   0.001 |   0.002 |   0.000 |   0.018 |   0.003 |   0.000 |   0.004 | 
|    nc0s000 |   0.021 |  11.850 |   0.069 |   0.217 |   0.014 |   0.075 |   0.030 |   0.207 |   0.000 |   0.002 | 
|     da0000 |   0.002 |   0.066 |   9.513 |   0.005 |   0.001 |   0.000 |   0.002 |   0.049 |   0.000 |   0.000 | 
|     aq0000 |   0.095 |   0.328 |   0.069 |   6.056 |   0.108 |   0.110 |   0.083 |   0.103 |   0.002 |   0.012 | 
|         fc |   0.000 |   0.000 |   0.000 |   0.000 |   5.850 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 | 
|    nc0p000 |   0.020 |   0.647 |   0.088 |   0.139 |   0.017 |   4.381 |   0.024 |   0.131 |   0.000 |   0.004 | 
|         rg |   0.061 |   0.033 |   0.028 |   0.062 |   0.004 |   0.014 |   3.380 |   0.032 |   0.000 |   0.031 | 
|    np00000 |   0.032 |   0.426 |   0.053 |   0.133 |   0.033 |   0.026 |   0.043 |   2.577 |   0.001 |   0.007 | 
|         fp |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   0.000 |   3.550 |   0.000 | 
|         cc |   0.001 |   0.000 |   0.000 |   0.003 |   0.000 |   0.000 |   0.060 |   0.006 |   0.000 |   3.334 | 



## Ejercicio 6: Features para Etiquetado de Secuencias

Se implementaron los siguientes features básicos

*word_lower: la palabra actual en minúsculas.
*word_istitle: la palabra actual empieza en mayúsculas.
*word_isupper: la palabra actual está en mayúsculas.
*word_isdigit: la palabra actual es un número.

También implementar los siguientes features paramétricos:

*NPrevTags(n): la tupla de los últimos n tags.
*PrevWord(f): Dado un feature f, aplicarlo sobre la palabra anterior en lugar de la actual.

## Ejercicio 7: MEMM

### Clasificador: LogisticRegression

| n |   Total   |    Known    |    Unknown   |      Tiempo     |
|---|---------- |-------------|--------------|-----------------|
| 1 |   91.10%  |    94.55%   |     59.84%   |    31 seg       |
| 2 |   90.68%  |    94.14%   |     59.31%   |    1 min 2seg   |
| 3 |   90.87%  |    94.24%   |     60.41%   |    1 min        |
| 4 |   90.86%  |    94.22%   |     60.37%   |    1 min  |


### Clasificador: MultinomialNB

Se evaluaron las 4 de manera simultanea

| n |   Total   |    Known    |    Unknown   |      Tiempo     |
|---|---------- |-------------|--------------|-----------------|
| 1 |   77.02% | 81.47% | 36.72%   |   1 hora  15 min     |
| 2 |   61.48% | 65.10% | 28.73% | 1 hora 15 min  |

| 3 | 61.76% | 65.19% | 30.66% | 1 hora 15 min  |

| 4 |60.27% | 63.35% | 32.41% | 1 hora 15 min  |


### Clasificador: LinearSVC


| n |   Total   |    Known    |    Unknown   |      Tiempo     |
|---|---------- |-------------|--------------|-----------------|
| 1 |   93.59%  |    97.11%   |     61.74%   |    1 min 2 seg       |
| 2 |   93.56%  |    97.04%|61.98%|57 seg|
| 3 | 93.68% | 97.10%| 62.73% | 1 min 15 seg
| 4 |93.69%| 97.13% | 62.54% | 2 min 5 seg |




