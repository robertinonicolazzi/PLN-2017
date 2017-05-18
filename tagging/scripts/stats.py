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
    corpus = SimpleAncoraCorpusReader('/media/robertnn/DatosLinux/ancora-3.0.1es/')
    sents = list(corpus.tagged_sents())

    total_tokens = 0
    vocabulary = set({})
    tags = set({})
    dict_tags = defaultdict(int)
    dict_tag_words = defaultdict(lambda : defaultdict(int))
    dict_words_tag = defaultdict(lambda : defaultdict(int))

    for sent in sents:
        total_tokens += len(sent)
        for tuple_word in sent:
            vocabulary.add(tuple_word[0])
            tags.add(tuple_word[1])
            dict_tags[tuple_word[1]] += 1
            dict_tag_words[tuple_word[1]][tuple_word[0]] += 1
            dict_words_tag[tuple_word[0]][tuple_word[1]] += 1

    total_vocabulary = len(vocabulary)
    total_tags = len(tags)
    # compute the statistics

    tags_ordenados = sorted(dict_tags.items(), key = lambda x: x[1], reverse = True)

    print (redWhite('Estadísticas Básicas'))
    print ('{:26} {}'.format(' Cantidad de Oraciones:', len(sents)))
    print ('{:26} {}'.format(' Cantidad de Tokens:',total_tokens))
    print ('{:26} {}'.format(' Cantidad de Palabras:',total_vocabulary))
    print ('{:26} {}'.format(' Cantidad de Etiquetas:',total_tags))

    print ('\n',redWhite('Etiquetas Mas Frecuentes'),'\n')

    total_values_tag = sum(dict_tags.values())

    print ('{:^23}  | {:^28}  |  {:^29} | {:^40}'.format(redWhite('TAG'), redWhite('#Apariciones') ,redWhite('Frecuencia'),redWhite('5 Palabras Mas Frecuentes')))
    for i in range(0,10):
        temp_list = sorted(dict_tag_words[tags_ordenados[i][0]].items(), key = lambda x : -x[1])[:5]
        words ="" 
        for a in temp_list:
            words += a[0] + " | "

        print ('{:^10} | {:^15} | {:^16} | {:<40}'.format(tags_ordenados[i][0], tags_ordenados[i][1] ,round(100*tags_ordenados[i][1]/float(total_values_tag),3), words))

    print ('\n')
    print ('\n')
    print ('{:^23}  | {:^28}  |  {:^29} | {:^40}'.format(redWhite('Ambiguedad'), redWhite('#Apariciones') ,redWhite('Frecuencia'),redWhite('5 Palabras Mas Frecuentes')))

    grados_ambiguedad = defaultdict(int)
    grado_palabra_count = defaultdict(lambda : defaultdict(int))
    for key in dict_words_tag.keys():
        grados_ambiguedad[len(dict_words_tag[key])] += 1
        grado_palabra_count[len(dict_words_tag[key])][key] += sum(dict_words_tag[key].values())

    for i in range(1,10):
        temp_list = sorted(grado_palabra_count[i].items(), key = lambda x : -x[1])[:5]
        words ="" 
        for a in temp_list:
            words += a[0] + " \ "
        print ('{:^10} | {:^15} | {:^16} | {:<40}'.format(i,grados_ambiguedad[i], round(100*grados_ambiguedad[i]/float(total_vocabulary),3), words))
