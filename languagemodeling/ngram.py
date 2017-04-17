
from random import random
from math import log, ceil
from collections import defaultdict

INICIO = '<s>'
FINAL = '</s>'


class NGram:

    def __init__(self, n, sents):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        """
        assert (n > 0)
        self.n = n
        self.counts = counts = defaultdict(int)

        for sent in sents:
            sent = self.rellenarSent(sent)
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i:i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1

    def rellenarSent(self, sent):
        return [INICIO for _ in range(self.n - 1)] + sent + [FINAL]

    def count(self, tokens):
        """Count for an n-gram or (n-1)-gram.

        tokens -- the n-gram or (n-1)-gram tuple.
        """
        return self.counts[tuple(tokens)]

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        if not prev_tokens:
            prev_tokens = []
        assert(len(prev_tokens) == self.n - 1)
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
        sent = self.rellenarSent(sent)
        result = 1
        for i in range(self.n - 1, len(sent)):
            word = sent[i]
            prev_tokens = sent[i - self.n + 1:i]
            result *= self.cond_prob(word, prev_tokens)

        return result

    def sent_log_prob(self, sent):
        """Log-probability of a sentence.

        sent -- the sentence as a list of tokens.
        """
        sent = self.rellenarSent(sent)
        result = 0

        for i in range(self.n - 1, len(sent)):
            word = sent[i]
            prev_tokens = sent[i - self.n + 1:i]
            temp = self.cond_prob(word, prev_tokens)

            if temp == 0:
                result += float('-inf')
                break
            else:
                result += log(temp, 2)

        return result


class NGramGenerator:

    def __init__(self, model):
        """
        model -- n-gram model.
        """
        self.model = model
        self.n = n = model.n

        self.probs = probs = dict()
        self.sorted_probs = sorted_probs = dict()
        # Agarramos el ultimo token de cada gram y a partir de los previos
        # calculamos su probabilidad condicional

        for ngram in model.counts:
            if len(ngram) == n:
                token = ngram[n - 1]
                prev_tokens = ngram[:n - 1]
                if prev_tokens not in probs:
                    probs[prev_tokens] = dict()
                probs[prev_tokens][token] = model.cond_prob(token,
                                                            list(prev_tokens))

        for prev_tokens, probabilidades in probs.items():
            temp_sorted_probs = sorted(
                probabilidades.items(), key=lambda x: (-x[1], x[0]))
            sorted_probs[prev_tokens] = temp_sorted_probs

    def generate_sent(self):
        """Randomly generate a sentence."""

        # Determinamos la primer palabra luego de los
        # delimitadores de inicio de sentencia
        prev_tokens = [INICIO for _ in range(self.n - 1)]
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

        assert(len(prev_tokens) == self.n - 1)

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

    """
       Todos los métodos de NGram.
    """

    def __init__(self, n, sents):
        assert (n > 0)

        self.n = n
        self.counts = counts = defaultdict(int)
        word_types = set({FINAL})
        for sent in sents:
            word_types.update(set(sent))  # Mantenemos unicidad
            sent = self.rellenarSent(sent)
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i:i + n])
                counts[ngram] += 1
                counts[ngram[:-1]] += 1
        self.v = len(word_types)

    def V(self):
        """Size of the vocabulary.
        """
        return self.v

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        if not prev_tokens:
            prev_tokens = []

        assert (len(prev_tokens) == self.n - 1)

        tokens = prev_tokens + [token]
        a = self.counts[tuple(tokens)]
        b = self.counts[tuple(prev_tokens)]

        res = (a + 1) / float(float(b) + self.v)

        return res


class Evaluacion:
    def __init__(self, model, testSents):
        self.model = model
        self.sents = testSents
        self.cantidad_palabras = nPalabras = 0
        for sent in testSents:
            nPalabras += len(sent)
        self.cantidad_palabras = nPalabras

    def log_probability(self):
        log_probability = 0
        for sent in self.sents:
            log_probability += self.model.sent_log_prob(sent)

        return log_probability

    def cross_entropy(self):
        return self.log_probability() / float(self.cantidad_palabras)

    def perplexity(self):
        return pow(2, -self.cross_entropy())

class InterpolatedNGram(NGram):
 
    def __init__(self, n, sents, gamma=None, addone=True):
        """
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        gamma -- interpolation hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """
        assert (n > 0)
        self.n = n
        self.counts = counts = defaultdict(int)

        self.gamma = gamma
        self.addone = addone
        if gamma == None:
            train_sents = sents[0:int(ceil(len(sents)*0.1))]
            held_out = sents[int(ceil(len(sents)*0.1)):]
            word_types = set({FINAL})
            for sent in train_sents:
                word_types.update(set(sent))  # Mantenemos unicidad
                sent = self.rellenarSent(sent)
                for i in range(len(sent) - n + 1):
                    ngram = tuple(sent[i:i + n])
                    counts[ngram] += 1
                    for k in range(n):
                        counts[ngram[:k]] += 1 
            #hay que sumar las ocurrencias de n,n-1,n-2... y la cantidad de palabras
            counts[(FINAL,)]= len(train_sents)
            self.lambdas = []
            self.v = 0
            if addone:
                self.v = len(word_types)

            gammas_posibles = [10.0, 100.0, 200.0]

            gamma_elegido = 0
            min_perplexity = float('inf')
            for g in gammas_posibles:
                p = Evaluacion(self, held_out).perplexity()
                if p < min_perplexity:
                    gamma_elegido = g
                    min_perplexity = p

            self.gamma = gamma_elegido


        else:
            word_types = set({FINAL})
            for sent in sents:
                word_types.update(set(sent))  # Mantenemos unicidad
                sent = self.rellenarSent(sent)
                for i in range(len(sent) - n + 1):
                    ngram = tuple(sent[i:i + n])
                    counts[ngram] += 1
                    for k in range(n):
                        counts[ngram[:k]] += 1 
            #hay que sumar las ocurrencias de n,n-1,n-2... y la cantidad de palabras
            counts[(FINAL,)]= len(sents)
            self.lambdas = []
            self.v = 0
            if addone:
                self.v = len(word_types)

    def rellenarSent(self, sent):
        return [INICIO for _ in range(self.n - 1)] + sent + [FINAL]

    def lamb(self,tokens=None):
        self.lambdas = []
        for k in range(self.n):
            cantidad = self.counts[tuple(tokens[k:])]
            b = 1
            if k != self.n-1:
                b = cantidad / float(cantidad + self.gamma)

            a = 1 - sum(self.lambdas)

            result = a*b
            self.lambdas.append(result)


    def qML(self, token, prev_tokens):
        if not prev_tokens:
            prev_tokens = []
        tokens = prev_tokens + [token]
        a = self.counts[tuple(tokens)]
        b = self.counts[tuple(prev_tokens)]

        res = 0

        if self.addone:
            res = (a+1)/float(b+self.v)
        elif b != 0:
            res = a / float(b)

        return res

    def cond_prob(self, token, prev_tokens=None):
        """Conditional probability of a token.

        token -- the token.
        prev_tokens -- the previous n-1 tokens (optional only if n = 1).
        """
        if not prev_tokens:
            prev_tokens = []
        assert(len(prev_tokens) == self.n - 1)

        result = 0
        self.lamb(prev_tokens)
        for i in range(self.n):
            result += self.lambdas[i]*self.qML(token, prev_tokens[i:])

        return result

class BackOffNGram(NGram):
 
    def __init__(self, n, sents, beta=None, addone=True):
        """
        Back-off NGram model with discounting as described by Michael Collins.
 
        n -- order of the model.
        sents -- list of sentences, each one being a list of tokens.
        beta -- discounting hyper-parameter (if not given, estimate using
            held-out data).
        addone -- whether to use addone smoothing (default: True).
        """
        self.n = n
        self.counts = counts = defaultdict(int)
        self.Aset = Aset = defaultdict(set)
        self.beta = beta
        self.addone = addone
        word_types = set({FINAL})
        
        for sent in sents:
            word_types.update(set(sent))  # Mantenemos unicidad
            sent = self.rellenarSent(sent)
            for i in range(len(sent) - n + 1):
                ngram = tuple(sent[i:i + n])
                Aset[tuple(sent[i:i + n-1])].update({sent[i + n-1]})
                counts[ngram] += 1
                for k in range(n):
                    counts[ngram[:k]] += 1 
        #hay que sumar las ocurrencias de n,n-1,n-2... y la cantidad de palabras
        counts[(FINAL,)]= len(sents)
        self.lambdas = []
        self.v = len(word_types)

    def cond_prob(self, token, prev_tokens=None):

        if prev_tokens == None:
            prev_tokens = []
        res = 0
        if len(prev_tokens) != 0:
            if token in self.A(prev_tokens):
                a = self.counts[tuple(prev_tokens+ [token])]- self.beta
                b = self.counts[tuple(prev_tokens)]
                if b != 0:
                    res = a/float(b)
            else:
                a = self.alpha(prev_tokens)*self.cond_prob(token,prev_tokens[1:])
                b = self.denom(prev_tokens)
                if b != 0:
                    res = a/float(b)
            
        else:
            if self.addone == False:
                res = (self.counts[(token,)])/float(self.counts[tuple()])
            else:
                res = (self.counts[(token,)] + 1.0)/float(self.counts[tuple()] +self.v)

        return res      


    def A(self, tokens):
        """Set of words with counts > 0 for a k-gram with 0 < k < n.
 
        tokens -- the k-gram tuple.
        """

        return self.Aset[tuple(tokens)]

 
    def alpha(self, tokens):
        """Missing probability mass for a k-gram with 0 < k < n.
 
        tokens -- the k-gram tuple.
        """
        result = 1
        denom = self.counts[tuple(tokens)]
        Aset = self.A(tokens)
        if len(Aset) != 0 and denom != 0:
            result = (self.beta * len(Aset))/float(denom)

        return result
 
    def denom(self, tokens):
        """Normalization factor for a k-gram with 0 < k < n.
 
        tokens -- the k-gram tuple.
        """
        tokens = list(tokens)

        suma = sum(self.cond_prob(i,tokens[1:]) for i in self.Aset[tuple(tokens)])
        return 1 - suma