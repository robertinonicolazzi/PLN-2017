
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
 
    def _generar_counts(self,sents):
        self.counts = counts = defaultdict(int)
        n = self.n
        word_types = set({FINAL})
        for sent in sents:
            counts[()] += len(sent) + 1
            word_types.update(set(sent))  # Mantenemos unicidad
            sent = self.rellenarSent(sent)
            n= self.n

            while n != 0:
                for i in range(len(sent) - n + 1):
                    ngram = tuple(sent[i:i + n])
                    counts[ngram] += 1
                n = n-1
        #hay que sumar las ocurrencias de n,n-1,n-2... y la cantidad de palabras
        counts[(FINAL,)]= len(sents)
        if self.addone:
            self.v = len(word_types)

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
            percent = int(ceil(len(sents)*0.9))
            if percent == len(sents):
                percent -= 1
            train_sents = sents[:percent]
            held_out = sents[percent:]
            import time;
            start_time = time.time()
            self._generar_counts(train_sents)
            print("--- %s seconds COUNT---" % (time.time() - start_time))

            gammas_posibles = [350.0,500.0,750.0,1000.0,1250.0,1500.0]

            min_perplexity = float('inf')
            for g in gammas_posibles:
                self.gamma = g
                p = Evaluacion(self, held_out).perplexity()
                if p < min_perplexity:
                    gamma_elegido = g
                    min_perplexity = p
            print ("gamma_elegido",gamma_elegido)
            self.gamma = gamma_elegido


        else:
            import time;
            start_time = time.time()
            self._generar_counts(sents)
            print("--- %s seconds COUNT---" % (time.time() - start_time))

    def rellenarSent(self, sent):
        return [INICIO for _ in range(self.n - 1)] + sent + [FINAL]

    def lamb(self,tokens=None):
        self.lambdas = []
        for k in range(self.n-1):

            cantidad = self.counts[tuple(tokens[k:])]
            if cantidad == 0:
                print ("no puede ser cero", tuple(tokens[k:]))
            b = cantidad / float(cantidad + self.gamma)
            a = 1 - sum(self.lambdas)
            result = a*b
            self.lambdas.append(result)

        result = (1- sum(self.lambdas))
        self.lambdas.append(result)


    def qML(self, token, prev_tokens):
        if not prev_tokens:
            prev_tokens = []
        tokens = prev_tokens + [token]
        a = self.counts[tuple(tokens)]
        b = self.counts[tuple(prev_tokens)]

        res = 0

        if len(prev_tokens)==0 and self.addone:
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

        result = 0
        #from nose.tools import set_trace; set_trace()
        self.lamb(prev_tokens)
        """
        Recordemos, lamda[0] corresponde a n-gram
        lambda[1] corresponde n-1-gram 
        lambda[self.n-1] corresponde a n-1-gram
        """
        for i in range(self.n):
            result += self.lambdas[i]*self.qML(token, prev_tokens[i:])

        return result

class BackOffNGram(NGram):
 
    def _generar_counts_Aset(self, sents):
        self.counts = counts = defaultdict(int)
        self.Aset = Aset = defaultdict(set)
        n = self.n
        word_types = set({FINAL})
        for sent in sents:
            counts[()] += len(sent) + 1
            word_types.update(set(sent))  # Mantenemos unicidad
            sent = self.rellenarSent(sent)
            n= self.n

            while n != 0:
                for i in range(len(sent) - n + 1):
                    ngram = tuple(sent[i:i + n])
                    Aset[ngram[:-1]].update(ngram[-1:])
                    counts[ngram] += 1
                n = n-1
        #hay que sumar las ocurrencias de n,n-1,n-2... y la cantidad de palabras
        counts[(FINAL,)]= len(sents)
        if self.addone:
            self.v = len(word_types)

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
        self.dict_alphas = defaultdict(float)
        self.beta = beta
        self.addone = addone
        self.v = None

        if beta == None:
            percent = int(ceil(len(sents)*0.9))
            if percent == len(sents):
                percent -= 1
            train_sents = sents[:percent]
            held_out = sents[percent:]
            import time;
            start_time = time.time()
            self._generar_counts_Aset(train_sents)
            print("--- %s seconds COUNT---" % (time.time() - start_time))
            gammas_posibles = [0.1,0.3,0.5,0.7,0.8,0.9]

            gamma_elegido = 0.0
            min_perplexity = float('inf')
            for g in gammas_posibles:
                self.beta = g
                self.generar_alphas()
                p = Evaluacion(self, held_out).perplexity()
                if p < min_perplexity:
                    gamma_elegido = g
                    min_perplexity = p
            print("beta elegido",gamma_elegido)
            self.beta = gamma_elegido
        else:
            import time
            start_time = time.time()
            self._generar_counts_Aset(sents)
            print("--- %s seconds COUNT---" % (time.time() - start_time))
            self.generar_alphas()
        print("Termino con grado",self.n)

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

    def generar_alphas(self):

        for tokens in self.counts.keys():
            denom = self.counts[tuple(tokens)]
            Aset = self.A(tokens)
            if len(Aset) != 0 and denom != 0:
                result = (self.beta * len(Aset))/float(denom)
                self.dict_alphas[tuple(tokens)] = result

    def alpha(self, tokens):
        """Missing probability mass for a k-gram with 0 < k < n.
 
        tokens -- the k-gram tuple.
        """

        return self.dict_alphas.get(tuple(tokens),1)
 
    def denom(self, tokens):
        """Normalization factor for a k-gram with 0 < k < n.
 
        tokens -- the k-gram tuple.
        """
        denom = self.counts[tuple(tokens[1:])]
        suma = sum(self.counts[tuple(tokens[1:])+(i,)] for i in self.Aset[tuple(tokens)])
        if len(tokens) == 1:
            #hay que diferenciar unigramas, ver si aplica addone o no
            if self.addone:
                num = suma + len(self.Aset[tuple(tokens)])
                denom = denom + self.v
            else:
                num = suma

        else:
            num = suma - self.beta* len(self.Aset[tuple(tokens)])

        if denom == 0: 
            return 1
        else:
            return 1 - (num/float(denom))
