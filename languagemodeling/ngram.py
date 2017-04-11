# https://docs.python.org/3/library/collections.html
from collections import defaultdict
from math import log 

from random import random

INICIO = '<s>'
FINAL = '</s>'
class NGram(object):

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        self.counts = counts = defaultdict(int)

        for sent in sents:
            sent = [INICIO for i in range(n-1)] + sent + [FINAL]
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i: i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
 
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        if not prev_tokens:
            prev_tokens = []

        assert len(prev_tokens) == self.n - 1

        tokens = prev_tokens + [token]
        a = self.counts[tuple(tokens)]
        b = self.counts[tuple(prev_tokens)]

        res = 0
        if b != 0:
            res = a / float(b)

        return res


    def sent_prob(self, sent):
        """Probability of a sentence. Warning: subject to underflow problems.
 
        sent -- the sentence as a list of tokens.
        """
        n = self.n
        ant = [INICIO for i in range(n-1)]
        sent = ant + sent + [FINAL]
        result = 1
        for i in range(n-1,len(sent)):  #Rango inicia en n-1 para tomar la primer palabra distinta de <s>
            word = sent[i]
            prev_tokens = sent[i-n+1:i]
            result *= self.cond_prob(word, prev_tokens)

        return result 

 
    def sent_log_prob(self, sent):
        """Log-probability of a sentence.
 
        sent -- the sentence as a list of tokens.
        """
        n = self.n
        ant = [INICIO for i in range(n-1)]
        sent = ant + sent + [FINAL]
        result = 0
        for i in range(n-1,len(sent)):  #Rango inicia en n-1 para tomar la primer palabra distinta de <s>
            word = sent[i]
            prev_tokens = sent[i-n+1:i]
            temp = self.cond_prob(word, prev_tokens)

            if temp == 0:
                result += float('-inf')
            else:
                result += log(temp,2)

        return result 

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.
 
        tokens -- the n-gram or (n-1)-gram tuple.
        """

        return self.counts[tokens]

    def prob(self, token, prev_tokens=None):
        n = self.n
        if not prev_tokens:
            prev_tokens = []
        assert len(prev_tokens) == n - 1

        tokens = prev_tokens + [token]
        return float(self.counts[tuple(tokens)]) / self.counts[tuple(prev_tokens)]

class NGramGenerator:
 
    def __init__(self, model):
        """
        model -- n-gram model.
        """
        self.model = model
        self.n = model.n
        n = self.n
        self.probs = probs = dict()
        self.sorted_probs = sorted_probs = dict()

        #probs debe ser de la forma (n-1 tokes anteriores): {next1: prob, next2: prob}
        for ngram in model.counts:
            if len(ngram) == n:
                token = ngram[n-1] #tomamos el ultimo para determinar su probabilidad a partir de los anteriores
                prev_tokens = ngram[:n-1] #tupla de tokens previos
                if prev_tokens not in probs:
                    probs.update({prev_tokens: dict()}) #agregamos un elemento al diccionado probs de los n-1 tokens anteriores
                probs[prev_tokens].update({token: model.cond_prob(token, list(prev_tokens))})

        for prev_tokens, probabilidades in probs.items():
            temp_sorted_probs = sorted(probabilidades.items(),
                                        key= lambda x : (-x[1],x[0]))
            sorted_probs.update({prev_tokens: temp_sorted_probs})

 
    def generate_sent(self):
        """Randomly generate a sentence."""

        #Para evitar errores de underflow agregamos al inicio
        prev_tokens = [INICIO for i in range(self.n-1)] 
        sentence = []

        result = self.generate_token(prev_tokens)

        while result != FINAL:
            sentence.append(result)
            prev_tokens = prev_tokens + [result]
            prev_tokens.pop(0)
            result = self.generate_token(prev_tokens)

        return sentence

 
    def generate_token(self, prev_tokens=None):
        """Randomly generate a token, given prev_tokens.
 
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """

        if not prev_tokens:
            prev_tokens = []

        assert(len(prev_tokens) == self.n-1)

        """
        ya que la 'variable aleatoria' toma cantidades finitas de valores
        vamos a usar el siguiente algoritmo de variables continuas aleatoria
        rias 
        """
        tokens_posibles = self.sorted_probs[tuple(prev_tokens)]

        u = random()

        acumulada = 0
        tokenElegido = ''

        for token, prob in tokens_posibles:
            acumulada += prob
            if u <= acumulada:
                tokenElegido = token
                break

        assert(tokenElegido != '')

        return tokenElegido


class AddOneNGram(NGram):
    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert n > 0
        self.n = n
        self.counts = counts = defaultdict(int)
        vocabulary  = set({FINAL})
        for sent in sents:
            vocabulary.update(set(sent))
            sent = [INICIO for i in range(n-1)] + sent + [FINAL]
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i: i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1

        self.v = len(vocabulary)

    def V(self):
        return self.v

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.
 
        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        if not prev_tokens:
            prev_tokens = []

        assert len(prev_tokens) == self.n - 1

        tokens = prev_tokens + [token]
        a = self.counts[tuple(tokens)]
        b = self.counts[tuple(prev_tokens)]

        res = 0
        if b != 0:
            res = (a+1) / float(float(b)+ self.v)

        return res

class Evaluacion(object):
    def __init__(self, model, testSents):
        """
        Recordemos que podemos escribir la probabilidad de una cadena de palabras
        utilizando la regla de la cadena
        """
        nPalabras = 0
        log_probability = 0

        for sent in testSents:
            nPalabras += len(sent) #sumamos las palabras de cada sentencia
            log_probability += model.sent_log_prob(sent)

        crossEntropy = log_probability / float(nPalabras)
        perplex = pow(2,-crossEntropy)

        self.log_probability = log_probability
        self.perplexity = perplex
        self.cross_entropy = crossEntropy

