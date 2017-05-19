"""Evaulate a tagger.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Tagging model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle
import sys

from collections import Counter
from corpus.ancora import SimpleAncoraCorpusReader
from sklearn.metrics import confusion_matrix


def progress(msg, width=None):
    """Ouput the progress of something on the same line."""
    if not width:
        width = len(msg)
    print('\b' * width + msg, end='')
    sys.stdout.flush()


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the model
    filename = opts['-i']
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()

    # load the data
    files = '3LB-CAST/.*\.tbf\.xml'

    ancora = '/media/robertnn/DatosLinux/ancora-3.0.1es/'
    corpus = SimpleAncoraCorpusReader(ancora, files)
    sents = list(corpus.tagged_sents())

    # tag
    hits, total, total_u, total_k, hits_k, hits_u = 0, 0, 0, 0, 0, 0
    n = len(sents)

    # listas para la matrix de confusion

    matrix_tags_model = []
    matrix_tags_gold = []
    for i, sent in enumerate(sents):
        word_sent, gold_tag_sent = zip(*sent)

        model_tag_sent = model.tag(word_sent)
        assert len(model_tag_sent) == len(gold_tag_sent), i

        matrix_tags_gold += list(gold_tag_sent)
        matrix_tags_model += model_tag_sent
        # global score
        hits_sent = [m == g for m, g in zip(model_tag_sent, gold_tag_sent)]
        hits += sum(hits_sent)
        total += len(sent)
        acc = float(hits) / total

        # Verificar palabras conocidas y no conocidas
        # comparar el tag de ancora, gold_tag_sent con el generado por el model
        for t in range(len(gold_tag_sent)):
            if model.unknown(word_sent[t]):
                total_u += 1
                if gold_tag_sent[t] == model_tag_sent[t]:
                    hits_u += 1
            else:
                total_k += 1
                if gold_tag_sent[t] == model_tag_sent[t]:
                    hits_k += 1
        acc_k = float(hits_k) / total_k
        acc_u = float(hits_u) / total_u

        progress('{:3.1f}% (Total:{:2.2f}%, \
            Known:{:2.2f}%, Unknown:{:2.2f}%)'.format(
            float(i) * 100 / n, acc * 100, acc_k * 100, acc_u * 100))

    acc = float(hits) / total
    acc_k = float(hits_k) / total_k
    acc_u = float(hits_u) / total_u

    print('')
    print('Total: {:2.2f}%, Known: {:2.2f}%, Unknown: {:2.2f}%'.format(
        acc * 100, acc_k * 100, acc_u * 100))

    most_frequent_taq = [tag for (tag, _) in Counter(
        matrix_tags_gold).most_common(10)]
    matrix_confusion = confusion_matrix(
        matrix_tags_gold, matrix_tags_model, most_frequent_taq)

    # para obtener la frecuencia hacemos
    matrix_confusion = (matrix_confusion / float(total)) * 100

    columnwidth = max([len(x)
                       for x in most_frequent_taq] + [7])  # 5 is value length
    empty_cell = " " * columnwidth

    print("    " + empty_cell, end=" ")
    for label in most_frequent_taq:
        print(" %{0}s ".format(columnwidth) % label, end=" ")
    print()

    for i, label1 in enumerate(most_frequent_taq):
        print("    %{0}s |".format(columnwidth) % label1, end=" ")
        for j in range(len(most_frequent_taq)):
            cell = "%{0}.3f |".format(columnwidth) % matrix_confusion[i, j]
            print(cell, end=" ")
        print()
