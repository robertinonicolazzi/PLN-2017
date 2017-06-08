"""Train a parser.

Usage:
  train.py [-m <model>] -o <file>
  train.py -m upcfg [--hM <n> ] -o <file>
  train.py -h | --help

Options:
  -m <model>    Model to use [default: flat]:
                  flat: Flat trees
                  rbranch: Right branching trees
                  lbranch: Left branching trees
                  upcfg: Unlexicalized PCFG
  --hM <n>       horzMarkov order n
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from corpus.ancora import SimpleAncoraCorpusReader

from parsing.baselines import Flat, RBranch
from parsing.upcfg import UPCFG

models = {
    'flat': Flat,
    'rbranch': RBranch,
    'upcfg': UPCFG
}


if __name__ == '__main__':
    opts = docopt(__doc__)

    print('Loading corpus...')
    files = 'CESS-CAST-(A|AA|P)/.*\.tbf\.xml'
    corpus = SimpleAncoraCorpusReader('/media/robertnn/DatosLinux/ancora-3.0.1es/', files)

    print('Training model...')
    if opts['--hM'] is None:
      model = models[opts['-m']](corpus.parsed_sents())
    else:
      model = models[opts['-m']](corpus.parsed_sents(),horzMarkov=int(opts['--hM']))


    print('Saving...')
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
