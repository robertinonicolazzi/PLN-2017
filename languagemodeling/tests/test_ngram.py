# https://docs.python.org/3/library/unittest.html
from unittest import TestCase
from math import log

from languagemodeling.ngram import NGram


class TestNGram(TestCase):

    def setUp(self):
        self.sents = [
            'el gato come pescado .'.split(),
            'la gata come salmón .'.split(),
        ]

    def test_count_1gram(self):
        ngram = NGram(1, self.sents)

        counts = {
            (): 12,
            ('el',): 1,
            ('gato',): 1,
            ('come',): 2,
            ('pescado',): 1,
            ('.',): 2,
            ('</s>',): 2,
            ('la',): 1,
            ('gata',): 1,
            ('salmón',): 1,
        }
        for gram, c in counts.items():
            self.assertEqual(ngram.count(gram), c)

    def test_count_2gram(self):
        ngram = NGram(2, self.sents)

        counts = {
            ('<s>',): 2,
            ('el',): 1,
            ('gato',): 1,
            ('come',): 2,
            ('pescado',): 1,
            ('.',): 2,
            ('la',): 1,
            ('gata',): 1,
            ('salmón',): 1,
            ('<s>', 'el'): 1,
            ('el', 'gato'): 1,
            ('gato', 'come'): 1,
            ('come', 'pescado'): 1,
            ('pescado', '.'): 1,
            ('.', '</s>'): 2,
            ('<s>', 'la'): 1,
            ('la', 'gata'): 1,
            ('gata', 'come'): 1,
            ('come', 'salmón'): 1,
            ('salmón', '.'): 1,
        }
        for gram, c in counts.items():
            self.assertEqual(ngram.count(gram), c)

    def test_count_3gram(self):
        ngram = NGram(3, self.sents)

        counts = {
            ('<s>', 'el'): 1,
            ('el', 'gato'): 1,
            ('gato', 'come'): 1,
            ('come', 'pescado'): 1,
            ('pescado', '.'): 1,
            ('<s>', 'la'): 1,
            ('<s>', '<s>'): 2,
            ('la', 'gata'): 1,
            ('gata', 'come'): 1,
            ('come', 'salmón'): 1,
            ('salmón', '.'): 1,
            ('<s>','<s>', 'la'): 1,
            ('<s>','<s>', 'el'): 1,
            ('<s>', 'el','gato'): 1,
            ('el','gato','come'): 1,
            ('gato','come','pescado'): 1,
            ('come','pescado','.'): 1,
            ('pescado','.','</s>'): 1,
            ('<s>', 'la','gata'): 1,
            ('la','gata','come'): 1,
            ('gata','come','salmón'): 1,
            ('come','salmón','.'): 1,
            ('salmón','.','</s>'): 1,

        }
        for gram, c in counts.items():
            self.assertEqual(ngram.count(gram), c)

    def test_cond_prob_1gram(self):
        ngram = NGram(1, self.sents)

        probs = {
            'pescado': 1 / 12.0,
            'come': 2 / 12.0,
            'salame': 0.0,
        }
        for token, p in probs.items():
            self.assertEqual(ngram.cond_prob(token), p)

    def test_cond_prob_3gram(self):
        ngram = NGram(3, self.sents)
        probs = {
            ('pescado', ('gato', 'come')): 1/1.0,
            ('salmón', ('gato', 'come')): 0.0,
            ('salame', ('gato', 'come')): 0.0,
            ('salmón', ('gata', 'come')): 1/1.0,
            ('gata', ('<s>', 'la')): 1/1.0,
            ('come', ('la','gata')): 1/1.0,
            ('salmón', ('gata','come')): 1/1.0,
        }
        for (token, prev), p in probs.items():
            print (prev)
            self.assertEqual(ngram.cond_prob(token, list(prev)), p)

    def test_sent_prob_3gram(self):
        ngram = NGram(3, self.sents)
        print (ngram.counts)
        sents = {
            # after '<s><s>': 'el' and 'la' have prob 0.5.
            # el resto de las ocurrencias aparece
            'el gato come pescado .': 0.5*1.0,
            'la gata come salmón .': 0.5*1.0,
            'el gato come salmón .': 0.5*0.0,
            'la gata come pescado .': 0.5*0.0,
            'el gato come salame .': 0.5*0.0,  # 'salame' unseen
            'la la la': 0.0,  # 'la' after 'la' unseen
        }
        
        for sent, prob in sents.items():
            self.assertAlmostEqual(ngram.sent_prob(sent.split()), prob, msg=sent)

    def test_cond_prob_2gram(self):
        ngram = NGram(2, self.sents)

        probs = {
            ('pescado', 'come'): 0.5,
            ('salmón', 'come'): 0.5,
            ('salame', 'come'): 0.0,
        }
        for (token, prev), p in probs.items():
            self.assertEqual(ngram.cond_prob(token, [prev]), p)

    def test_sent_prob_1gram(self):
        ngram = NGram(1, self.sents)

        sents = {
            # 'come', '.' and '</s>' have prob 1/6, the rest have 1/12.
            'el gato come pescado .': (1 / 6.0)**3 * (1 / 12.0)**3,
            'la gata come salmón .': (1 / 6.0)**3 * (1 / 12.0)**3,
            'el gato come salame .': 0.0,  # 'salame' unseen
            'la la la': (1 / 6.0)**1 * (1 / 12.0)**3,
        }
        for sent, prob in sents.items():
            self.assertAlmostEqual(ngram.sent_prob(sent.split()), prob, msg=sent)

    def test_sent_prob_2gram(self):
        ngram = NGram(2, self.sents)

        sents = {
            # after '<s>': 'el' and 'la' have prob 0.5.
            # after 'come': 'pescado' and 'salmón' have prob 0.5.
            'el gato come pescado .': 0.5 * 0.5,
            'la gata come salmón .': 0.5 * 0.5,
            'el gato come salmón .': 0.5 * 0.5,
            'la gata come pescado .': 0.5 * 0.5,
            'el gato come salame .': 0.0,  # 'salame' unseen
            'la la la': 0.0,  # 'la' after 'la' unseen
        }
        for sent, prob in sents.items():
            self.assertAlmostEqual(ngram.sent_prob(sent.split()), prob, msg=sent)



    def test_sent_log_prob_1gram(self):
        ngram = NGram(1, self.sents)

        log2 = lambda x: log(x, 2)
        sents = {
            # 'come', '.' and '</s>' have prob 1/6, the rest have 1/12.
            'el gato come pescado .': 3 * log2(1 / 6.0) + 3 * log2(1 / 12.0),
            'la gata come salmón .': 3 * log2(1 / 6.0) + 3 * log2(1 / 12.0),
            'el gato come salame .': float('-inf'),  # 'salame' unseen
            'la la la': log2(1 / 6.0) + 3 * log2(1 / 12.0),
        }
        for sent, prob in sents.items():
            self.assertAlmostEqual(ngram.sent_log_prob(sent.split()), prob, msg=sent)

    def test_sent_log_prob_2gram(self):
        ngram = NGram(2, self.sents)

        log2 = lambda x: log(x, 2)
        sents = {
            # after '<s>': 'el' and 'la' have prob 0.5.
            # after 'come': 'pescado' and 'salmón' have prob 0.5.
            'el gato come pescado .': 2 * log2(0.5),
            'la gata come salmón .': 2 * log2(0.5),
            'el gato come salmón .': 2 * log2(0.5),
            'la gata come pescado .': 2 * log2(0.5),
            'el gato come salame .': float('-inf'),  # 'salame' unseen
            'la la la': float('-inf'),  # 'la' after 'la' unseen
        }
        for sent, prob in sents.items():
            self.assertAlmostEqual(ngram.sent_log_prob(sent.split()), prob, msg=sent)
