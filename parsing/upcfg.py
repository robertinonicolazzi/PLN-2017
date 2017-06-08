from parsing.util import unlexicalize, lexicalize
from parsing.cky_parser import CKYParser
from nltk.tree import Tree
from nltk.grammar import Nonterminal, induce_pcfg


def printDifc(dicta):

    for a in dicta.items():
        print(a)


class UPCFG:
    """Unlexicalized PCFG.
    """

    def __init__(self, parsed_sents, start='sentence', horzMarkov=None):
        """
        parsed_sents -- list of training trees.
        """

        """
        en las reglas, reemplazar todas las entradas léxicas por su POS tag.
        Luego, el parser también debe ignorar las entradas léxicas y usar la
        oración de POS tags para parsear.
        """
        productions = []
        for tree in parsed_sents:
            tree_temp = tree.copy(deep=True)
            unlexicalize(tree_temp)
            tree_temp.chomsky_normal_form(horzMarkov=horzMarkov)
            tree_temp.collapse_unary(collapsePOS=True, collapseRoot=True)
            productions += tree_temp.productions()

        # Generamos una PCFG a partir de las producciones

        pcfg = induce_pcfg(start=Nonterminal(start), productions=productions)
        self._productions = pcfg.productions()
        self._model = CKYParser(pcfg)
        self._start_symbol = pcfg.start().symbol()

    def productions(self):
        """Returns the list of UPCFG probabilistic productions.
        """
        return self._productions

    def parse(self, tagged_sent):
        """Parse a tagged sentence.

        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        words = [w for (w, _) in tagged_sent]
        tags = [t for (_, t) in tagged_sent]

        prob, tree = self._model.parse(tags)

        # Si no encuentra un arbol de parseo devolver flat

        if prob == float('-inf') or tree is None:
            # Flat tree
            leaves = [Tree(t, [w]) for (w, t) in tagged_sent]
            tree = Tree(self._start_symbol, leaves)

        else:
            tree.un_chomsky_normal_form()
            tree = lexicalize(tree, words)

        return tree
