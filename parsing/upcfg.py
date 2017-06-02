from parsing.util import unlexicalize,lexicalize
from parsing.cky_parser import CKYParser
from nltk.tree import Tree
from nltk.grammar import Nonterminal, induce_pcfg
def printDifc(dicta):

    for a in dicta.items():
        print (a)

class UPCFG:
    """Unlexicalized PCFG.
    """
 
    def __init__(self, parsed_sents, start='sentence'):
        """
        parsed_sents -- list of training trees.
        """

        """
        en las reglas, reemplazar todas las entradas léxicas por su POS tag.
        Luego, el parser también debe ignorar las entradas léxicas y usar la
        oración de POS tags para parsear.
        """
        print(parsed_sents)
        productions = []
        for tree in parsed_sents:
            tree_temp = tree.copy(deep=True)
            print(tree_temp)
            unlexicalize(tree_temp)
            print(tree_temp)
            tree_temp.chomsky_normal_form()
            print(tree_temp)
            tree_temp.collapse_unary(collapsePOS=True)
            print(tree_temp)
            productions += tree_temp.productions()

        #Generamos una PCFG a partir de las producciones

        pcfg = induce_pcfg(start=Nonterminal(start), productions = productions)
        self._productions = pcfg.productions()
        print(self._productions)
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
        words = [w for (w,_) in tagged_sent]
        tags = [t for (_,t) in tagged_sent]

        prob, tree = self._model.parse(tags)

        #Si no encuentra un arbol de parseo devolver flat

        if tree is None and prob == float('-inf'):
            #Flat tree
            leaves = [Tree(t,[w]) for w,t in tagged_sent]
            tree = Tree(self._start_symbol,leaves)

        else:
            tree = lexicalize(tree, words)
            tree.un_chomsky_normal_form()

        return tree
