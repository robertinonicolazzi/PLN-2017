from collections import defaultdict
from nltk.tree import Tree

def printDifc(dicta):

    for a in dicta.items():
        print (a)

class CKYParser:
    
    def __init__(self, grammar):
        """
        grammar -- a binarised NLTK PCFG.
        """

        self.grammar = grammar

        #Extraemos las probabilidades de q(X->YZ) y de q(X->xi)
        self._probs_dict = _probs_dict = defaultdict(dict)
        for p in grammar.productions():
            lhs = p.lhs().symbol()
            rhs = p.rhs()
            if len(rhs) == 2:
                rhs = rhs[0].symbol(),rhs[1].symbol()

            _probs_dict[rhs][lhs] = p.logprob()


    def parse(self, sent):
        """Parse a sequence of terminals.
 
        sent -- the sequence of terminals.
        """
        n = len(sent)
        self._pi = pi = defaultdict(dict)
        self._bp = bp = defaultdict(dict)
        probs_dict = self._probs_dict
        #Inicializamos los q(X->xi)

        for i, word in enumerate(sent, start=1):
            #Buscamos los X tal que X->word

            for X, log_prob in probs_dict[(word,)].items():
                pi[(i,i)][X] = log_prob
                bp[(i,i)][X] = Tree(X,[word])

        for l in range(1,n):
            for i in range(1,n+1-l):
                j = l + i
                pi[(i,j)] = {}
                bp[(i,j)] = {}
                #Agarramos los YZ tal que X->YZ para cada s E {i...(j-1)}
                for s in range(i,j):
                    #Generamos posibles YZ
                    #from nose.tools import set_trace; set_trace()

                    for Y in pi[(i,s)].keys():
                        for Z in pi[(s+1,j)].keys():

                            #Obtenemos los X
                            for X, logprob in probs_dict.get((Y,Z),{}).items():
                                pi_y = pi[(i,s)][Y]
                                pi_z = pi[(s+1,j)][Z]
                                log_prob = logprob + pi_z + pi_y

                                if log_prob > pi[(i,j)].get(X,float('-inf')):
                                    pi[(i,j)][X] = log_prob
                                    bp[(i,j)][X] = Tree(X,[bp[(i,s)][Y],bp[(s+1,j)][Z] ])

        # Obtener el mejor arbol y la mejor probabilidad

        result_prob = pi[(1,n)].get(self.grammar.start().symbol(), float('-inf'))
        result_tree = bp[(1,n)].get(self.grammar.start().symbol(),None)

        printDifc(bp)
        return (result_prob, result_tree)