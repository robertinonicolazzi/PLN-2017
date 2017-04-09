"""Train an n-gram model.

Usage:
  train.py -n <n> -o <file>
  train.py -h | --help

Options:
  -n <n>        Order of the model.
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from nltk.corpus import PlaintextCorpusReader
from languagemodeling.ngram import NGram
from nltk.tokenize import RegexpTokenizer

if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data

    pattern = r'''(?ix)    # set flag to allow verbose regexps
      (?:sr\.|sra\.)
    | (?:[A-Z]\.)+        # abbreviations, e.g. U.S.A.
    | \w+(?:-\w+)*        # words with optional internal hyphens
    | \$?\d+(?:\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
    | \.\.\.            # ellipsis
    | [][.,;"'?():-_`]  
    '''
    tokenizer = RegexpTokenizer(pattern)
    corpus = PlaintextCorpusReader(r'languagemodeling/', 'harrypotter.txt',word_tokenizer=tokenizer)
    sents =  corpus.sents()
    # train the model
    n = int(opts['-n'])
    model = NGram(n, sents)

    # save it
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
