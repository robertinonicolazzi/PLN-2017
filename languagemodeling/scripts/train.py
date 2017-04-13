"""
Train an n-gram model.

Usage:
  train.py -n <n> [-m <model>] -o <file>
  train.py -h | --help

Options:
  -n <n>        Order of the model.
  -m <model>    Model to use [default: ngram]:
                  ngram: Unsmoothed n-grams.
                  addone: N-grams with add-one smoothing.
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

import nltk.data
from nltk.corpus import PlaintextCorpusReader
from languagemodeling.ngram import NGram, AddOneNGram
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
    | \.\.           # ellipsis
    | \.\.\.\.          # ellipsis
    | [][.,;"'¿?():-_`]
    '''
    tokenizer = RegexpTokenizer(pattern)
    sent_tokenizer = nltk.data.load('tokenizers/punkt/spanish.pickle')
    corpus = PlaintextCorpusReader(r'languagemodeling/Corpus',
                                   'corpusTrain.txt',
                                   sent_tokenizer=sent_tokenizer,
                                   word_tokenizer=tokenizer)
    sents = corpus.sents()
    # train the model
    n = int(opts['-n'])
    m = str(opts['-m'])

    if m == "ngram":
        print("Modelo NGram")
        model = NGram(n, sents)
    elif m == "addone":
        print("Modelo AddOne NGram")
        model = AddOneNGram(n, sents)
    else:
        print("Tipo de modelo inexistente")
        exit()

    # save it
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
