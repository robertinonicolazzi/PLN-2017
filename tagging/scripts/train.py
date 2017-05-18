"""Train a sequence tagger.

Usage:
  train.py [-m <model>] [-n <n>] -o <file>
  train.py -h | --help

Options:
  -m <model>    Model to use [default: base]:
                  base: Baseline
                  mlhmm: Mximun LikeLiHood HMM
  -o <file>     Output model file.
  -n <n>        Order of the model
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from corpus.ancora import SimpleAncoraCorpusReader
from tagging.baseline import BaselineTagger
from tagging.hmm import MLHMM


models = {
    'base': BaselineTagger,
    'mlhmm': MLHMM
}


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data
    files = 'CESS-CAST-(A|AA|P)/.*\.tbf\.xml'
    ancora = '/media/robertnn/DatosLinux/ancora-3.0.1es/'

    model_temp = models[opts['-m']]
    n = opts['-n']
    corpus = SimpleAncoraCorpusReader(ancora, files)
    if model_temp is None:
        print("Modelo inexistente")
        exit()

    if n is None:
        if opts['-m']=='mlhmm':
          print("Debe ingresar un n>=1 para MLHMM")
          exit()
        else:
          sents = list(corpus.tagged_sents())
          model = model_temp(sents)
    else:
        sents = list(corpus.tagged_sents())
        if opts['-m']=='base':
          model = model_temp(sents)
        else:
          model = model_temp(int(n),sents)



    # train the model


    # save it
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
