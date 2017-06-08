




Flat:

Parsed 1444 sentences
Labeled
  Precision: 99.93% 
  Recall: 14.58% 
  F1: 25.44% 

UnLabeled
  Precision: 100.00% 
  Recall: 14.59% 
  F1: 25.46% 

Tiempo Evaluación 0m9.276s


RBranch

Parsed 1444 sentences
Labeled
  Precision: 8.81% 
  Recall: 14.58% 
  F1: 10.98% 
UnLabeled
  Precision: 8.88% 
  Recall: 14.69% 
  F1: 11.07% 

real  0m9.907s



CKY
S -> NP VP      [1.0]
NP -> NP PP     [0.25] 
VP -> V NP      [0.40] 
VP -> VP PP     [0.60]
PP -> P NP      [1.0]
NP -> 'Alice'   [0.25] 
NP -> 'Bob'     [0.25] 
NP -> 'Cardiff' [0.25] 
V -> 'called'   [1.0]
P -> 'from'     [1.0]

![](arbol1.png)
![](arbol2.png)



UPCFG

Parsed 1444 sentences
Labeled
  Precision: 72.59% 
  Recall: 72.44% 
  F1: 72.51% 
UnLabeled
  Precision: 74.76% 
  Recall: 74.61% 
  F1: 74.69% 

real  7m50.845s
user  7m49.288s
sys 0m0.468s


Markov

n = 0

Labeled
  Precision: 69.71% 
  Recall: 69.78% 
  F1: 69.75% 
UnLabeled
  Precision: 71.61% 
  Recall: 71.68% 
  F1: 71.65% 

real  2m26.770s
user  2m26.460s
sys 0m0.316s


n = 1


Labeled
  Precision: 74.20% 
  Recall: 74.21% 
  F1: 74.21% 
UnLabeled
  Precision: 76.26% 
  Recall: 76.27% 
  F1: 76.27% 

real  3m9.357s
user  3m9.088s
sys 0m0.288s


n = 2

Labeled
  Precision: 74.58% 
  Recall: 74.13% 
  F1: 74.35% 
UnLabeled
  Precision: 76.59% 
  Recall: 76.13% 
  F1: 76.36% 

real  5m32.338s
user  5m31.800s
sys 0m0.344s


n = 3

Labeled
  Precision: 73.74% 
  Recall: 73.11% 
  F1: 73.42% 
UnLabeled
  Precision: 75.88% 
  Recall: 75.23% 
  F1: 75.55% 

real  6m31.420s
user  6m30.916s
sys 0m0.348s

