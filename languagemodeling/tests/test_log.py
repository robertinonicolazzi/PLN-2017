# https://docs.python.org/3/library/unittest.html
from unittest import TestCase
from math import log

from languagemodeling.ngram import Evaluacion, NGram


def log2(x):
    """
    Calcula el logaritmo en base 2 de x.
    """
    return log(x, 2)


class TestNGram(TestCase):

    def setUp(self):
        self.sents = [
            'el gato come pescado .'.split(),
            'la gata come salmón .'.split(),
        ]

    def test_log_probability_1gram(self):
        # 3*log2(1/6.0) + 3*log2(1/12.0) + 3*log2(1/6.0) + 3*log2(1/12.0)
        # =
        # 3*(log2(1/6.0) + log2(1/12.0) + log2(1/6.0) + log2(1/12.0))
        # =
        # 3*(2*log2(1/6.0) + 2*log2(1/12.0))
        # =
        # 3*(2*(log2(1/6.0) + log2(1/12.0)))
        # =
        # 6*(log2(1/6.0) + log2(1/12.0))
        # =
        # 6*log2(1/6.0 * 1/12.0)
        # =
        # 6*log2(1/72.0)
        ngram = NGram(1, self.sents)
        evala = Evaluacion(ngram, self.sents)
        log_prob = 6 * log2(1 / 72.0)

        self.assertAlmostEqual(evala.log_probability, log_prob)

    def test_log_probability_2gram(self):
        # 2*log2(0.5) + 2*log2(0.5)
        # =
        # 2*(log2(0.5) + log2(0.5))
        # =
        # 2*log2(0.5 * 0.5)
        # =
        # 2*log2(0.25)
        ngram = NGram(2, self.sents)
        evala = Evaluacion(ngram, self.sents)
        log_prob = 2 * log2(0.25)

        self.assertAlmostEqual(evala.log_probability, log_prob)

    def test_cross_entropy_1gram(self):
        ngram = NGram(1, self.sents)
        evala = Evaluacion(ngram, self.sents)
        cross = (6 * log2(1 / 72.0)) / 10.0

        self.assertAlmostEqual(evala.cross_entropy, cross)

    def test_cross_entropy_2gram(self):
        ngram = NGram(2, self.sents)
        evala = Evaluacion(ngram, self.sents)
        cross = (2 * log2(0.25)) / 10.0

        self.assertAlmostEqual(evala.cross_entropy, cross)

    def test_perplexity_1gram(self):
        ngram = NGram(1, self.sents)
        evala = Evaluacion(ngram, self.sents)
        perple = pow(2, -((6 * log2(1 / 72.0)) / 10.0))

        self.assertAlmostEqual(evala.perplexity, perple)

    def test_perplexity_2gram(self):
        ngram = NGram(1, self.sents)
        evala = Evaluacion(ngram, self.sents)
        perple = pow(2, -((2 * log2(0.25)) / 10.0))

        self.assertAlmostEqual(evala.perplexity, perple)
