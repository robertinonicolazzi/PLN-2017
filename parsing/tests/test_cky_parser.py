# https://docs.python.org/3/library/unittest.html
from unittest import TestCase
from math import log2

from nltk.tree import Tree
from nltk.grammar import PCFG

from parsing.cky_parser import CKYParser


class TestCKYParser(TestCase):

    def test_ambi(self):
        grammar = PCFG.fromstring(
            """
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
            """)
        from nose.tools import set_trace; set_trace()

        parser = CKYParser(grammar)

        lp, t = parser.parse('Alice called Bob from Cardiff'.split())
         
        lp2 = log2(1.0 * 0.25 * 0.6 * 0.4*1.0*0.25*1.0**1.0*0.25)
        self.assertAlmostEqual(lp, lp2)
        pi = {
            (1, 2): {},
            (1, 3): {'S': -5.321928094887362},
            (5, 5): {'NP': -2.0},
            (4, 5): {'PP': -2.0},
            (4, 4): {'P': 0.0},
            (1, 4): {},
            (1, 1): {'NP': -2.0},
            (1, 5): {'S': -8.05889368905357},
            (2, 3): {'VP': -3.321928094887362},
            (2, 2): {'V': 0.0}, 
            (2, 5): {'VP': -6.058893689053568},
            (3, 5): {'NP': -6.0},
            (3, 4): {},
            (2, 4): {},
            (3, 3): {'NP': -2.0}
        }
        self.assertEqualPi(parser._pi, pi)
        bp = {
            (1, 2): {},
            (1, 3): {'S': Tree('S', [Tree('NP', ['Alice']), Tree('VP', [Tree('V', ['called']), Tree('NP', ['Bob'])])])},
            (5, 5): {'NP': Tree('NP', ['Cardiff'])},
            (4, 5): {'PP': Tree('PP', [Tree('P', ['from']), Tree('NP', ['Cardiff'])])},
            (4, 4): {'P': Tree('P', ['from'])},
            (1, 4): {},
            (1, 1): {'NP': Tree('NP', ['Alice'])},
            (1, 5): {'S': Tree('S', [
            Tree('NP', ['Alice']), 
            Tree('VP', [
                Tree('VP', [
                    Tree('V', ['called']),
                    Tree('NP', ['Bob'])
                    ]), 
                Tree('PP', [
                    Tree('P', ['from']),
                    Tree('NP', ['Cardiff'])
                    ])
                ])
            ])
            },
            (2, 3): {'VP': Tree('VP', [Tree('V', ['called']), Tree('NP', ['Bob'])])},
            (2, 2): {'V': Tree('V', ['called'])},
            (2, 5): {'VP': Tree('VP', [Tree('VP', [Tree('V', ['called']), Tree('NP', ['Bob'])]), Tree('PP', [Tree('P', ['from']), Tree('NP', ['Cardiff'])])])},
            (3, 5): {'NP': Tree('NP', [Tree('NP', ['Bob']), Tree('PP', [Tree('P', ['from']), Tree('NP', ['Cardiff'])])])},
            (3, 4): {},
            (2, 4): {},
            (3, 3): {'NP': Tree('NP', ['Bob'])}
        }
        self.assertEqual(parser._bp, bp)


            
        # check log probability




    def test_parse(self):
        grammar = PCFG.fromstring(
            """
                S -> NP VP              [1.0]
                NP -> Det Noun          [0.6]
                NP -> Noun Adj          [0.4]
                VP -> Verb NP           [1.0]
                Det -> 'el'             [1.0]
                Noun -> 'gato'          [0.9]
                Noun -> 'pescado'       [0.1]
                Verb -> 'come'          [1.0]
                Adj -> 'crudo'          [1.0]
            """)

        parser = CKYParser(grammar)

        lp, t = parser.parse('el gato come pescado crudo'.split())

        # check chart
        pi = {
            (1, 1): {'Det': log2(1.0)},
            (2, 2): {'Noun': log2(0.9)},
            (3, 3): {'Verb': log2(1.0)},
            (4, 4): {'Noun': log2(0.1)},
            (5, 5): {'Adj': log2(1.0)},

            (1, 2): {'NP': log2(0.6 * 1.0 * 0.9)},
            (2, 3): {},
            (3, 4): {},
            (4, 5): {'NP': log2(0.4 * 0.1 * 1.0)},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {'VP': log2(1.0) + log2(1.0) + log2(0.4 * 0.1 * 1.0)},

            (1, 4): {},
            (2, 5): {},

            (1, 5): {'S':
                     log2(1.0) +  # rule S -> NP VP
                     log2(0.6 * 1.0 * 0.9) +  # left part
                     log2(1.0) + log2(1.0) + log2(0.4 * 0.1 * 1.0)},  # right part
        }
        self.assertEqualPi(parser._pi, pi)

        # check partial results
        bp = {
            (1, 1): {'Det': Tree.fromstring("(Det el)")},
            (2, 2): {'Noun': Tree.fromstring("(Noun gato)")},
            (3, 3): {'Verb': Tree.fromstring("(Verb come)")},
            (4, 4): {'Noun': Tree.fromstring("(Noun pescado)")},
            (5, 5): {'Adj': Tree.fromstring("(Adj crudo)")},

            (1, 2): {'NP': Tree.fromstring("(NP (Det el) (Noun gato))")},
            (2, 3): {},
            (3, 4): {},
            (4, 5): {'NP': Tree.fromstring("(NP (Noun pescado) (Adj crudo))")},

            (1, 3): {},
            (2, 4): {},
            (3, 5): {'VP': Tree.fromstring(
                "(VP (Verb come) (NP (Noun pescado) (Adj crudo)))")},

            (1, 4): {},
            (2, 5): {},

            (1, 5): {'S': Tree.fromstring(
                """(S
                    (NP (Det el) (Noun gato))
                    (VP (Verb come) (NP (Noun pescado) (Adj crudo)))
                   )
                """)},
        }
        self.assertEqual(parser._bp, bp)

        # check tree
        t2 = Tree.fromstring(
            """
                (S
                    (NP (Det el) (Noun gato))
                    (VP (Verb come) (NP (Noun pescado) (Adj crudo)))
                )
            """)
        self.assertEqual(t, t2)

        # check log probability
        lp2 = log2(1.0 * 0.6 * 1.0 * 0.9 * 1.0 * 1.0 * 0.4 * 0.1 * 1.0)
        self.assertAlmostEqual(lp, lp2)

    def assertEqualPi(self, pi1, pi2):
        self.assertEqual(set(pi1.keys()), set(pi2.keys()))

        for k in pi1.keys():
            d1, d2 = pi1[k], pi2[k]
            self.assertEqual(d1.keys(), d2.keys(), k)
            for k2 in d1.keys():
                prob1 = d1[k2]
                prob2 = d2[k2]
                self.assertAlmostEqual(prob1, prob2)
