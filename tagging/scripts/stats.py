# -*- coding: utf-8 -*-
"""Print corpus statistics.

Usage:
  stats.py
  stats.py -h | --help

Options:
  -h --help     Show this screen.
"""
from docopt import docopt

from corpus.ancora import SimpleAncoraCorpusReader
from collections import defaultdict

def redWhite(s):
    return '\x1b[1;37;41m' + s + '\x1b[0m'

if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    corpus = SimpleAncoraCorpusReader('/home/robertnn/Facultad/ancora-3.0.1es/')
    sents = list(corpus.tagged_sents())

    total_tokens = 0
    vocabulary = set({})
    tags = set({})
    dict_tags = defaultdict(int)
    dict_words = defaultdict(lambda : defaultdict(int))

    for sent in sents:
        total_tokens += len(sent)
        for tuple_word in sent:
            vocabulary.add(tuple_word[0])
            tags.add(tuple_word[1])
            dict_tags[tuple_word[1]] += 1
            dict_words[tuple_word[1]][tuple_word[0]] += 1

    total_vocabulary = len(vocabulary)
    total_tags = len(tags)
    # compute the statistics

    tags_ordenados = sorted(dict_tags.items(), key = lambda x: x[1], reverse = True)

    print (redWhite('Estadísticas Básicas'))
    print ('{:26} {}'.format(' Cantidad de Oraciones:', len(sents)))
    print ('{:26} {}'.format(' Cantidad de Tokens:',total_tokens))
    print ('{:26} {}'.format(' Cantidad de Palabras:',total_vocabulary))
    print ('{:26} {}'.format(' Cantidad de Etiquetas:',total_tags))

    print (redWhite('Etiquetas Mas Frecuentes'))
    import pdb;pdb.set_trace() 
    total_values_tag = sum(dict_tags.values())
    print (dict_words)
    print ('{:^10}  {:^15}  {:^16}  {:^20}'.format('TAG', '#Apariciones' ,'Frecuencia', '5 Palabras Mas Frecuentes'))
    for i in range(0,10):
        print ('{:^10}  {:^15}  {:^16}  {:^20}'.format(tags_ordenados[i][0], tags_ordenados[i][1] ,round(tags_ordenados[i][1]/float(total_values_tag),3), dict_words[tags_ordenados[i][0]]))
