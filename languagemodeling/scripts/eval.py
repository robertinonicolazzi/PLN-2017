"""
Evaulate a language model using the test set.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Language model file.
  -h --help     Show this screen.
"""

from docopt import docopt
import pickle
import nltk.data
from nltk.corpus import PlaintextCorpusReader
from languagemodeling.ngram import Evaluacion
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
                                   'corpusEvalTest.txt',
                                   word_tokenizer=tokenizer,
                                   sent_tokenizer=sent_tokenizer)
    test_sents = corpus.sents()

    filepath = str(opts['-i'])
    fileload = open(filepath, 'rb')

    model = pickle.load(fileload)

    evaluacion = Evaluacion(model, test_sents)
    print("Archivo cargado: %s" % filepath)
    print("-------------------------------------------")
    print("Perplexity: %f\n" % evaluacion.perplexity())
