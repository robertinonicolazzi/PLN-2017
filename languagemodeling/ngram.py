
from random import random
from math import log
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
        return self.counts[tokens]

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
        self.word_types = nPalabras = 0
        for sent in testSents:
            nPalabras += len(sent)
        self.word_types = nPalabras

    def log_probability(self):
        log_probability = 0
        for sent in self.sents:
            log_probability += self.model.sent_log_prob(sent)

        return log_probability

    def cross_entropy(self):
        return self.log_probability() / float(self.word_types)

    def perplexity(self):
        return pow(2, -self.cross_entropy())
