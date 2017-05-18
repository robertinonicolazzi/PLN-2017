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

from corpus.ancora import SimpleAncoraCorpusReader


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
    hits, total,total_u,total_k,hits_k,hits_u = 0, 0,0,0,0,0
    n = len(sents)
    for i, sent in enumerate(sents):
        word_sent, gold_tag_sent = zip(*sent)

        model_tag_sent = model.tag(word_sent)
        assert len(model_tag_sent) == len(gold_tag_sent), i

        # global score
        hits_sent = [m == g for m, g in zip(model_tag_sent, gold_tag_sent)]
        hits += sum(hits_sent)
        total += len(sent)
        acc = float(hits) / total



        #Verificar palabras conocidas y no conocidas
        #comparar el tag de ancora, gold_tag_sent con el generado por el model
        for t in range(len(gold_tag_sent)):
            if model.unknown(word_sent[t]):
                total_u +=1
                if gold_tag_sent[t]==model_tag_sent[t]:
                    hits_u +=1
            else:
                total_k +=1
                if gold_tag_sent[t]==model_tag_sent[t]:
                    hits_k +=1
        acc_k = float(hits_k)/total_k
        acc_u = float(hits_u)/total_u


        progress('{:3.1f}% (Total:{:2.2f}%, Known:{:2.2f}%, Unknown:{:2.2f}%)'.format(float(i) * 100 / n, acc * 100,acc_k*100,acc_u*100))

    acc = float(hits) / total
    acc_k =float(hits_k)/total_k
    acc_u= float(hits_u)/total_u

    print('')
    print('Total: {:2.2f}%, Known: {:2.2f}%, Unknown: {:2.2f}%'.format(acc * 100,acc_k*100,acc_u*100))