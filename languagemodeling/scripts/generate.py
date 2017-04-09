"""
Generate natural language sentences using a language model.

Usage:
  generate.py -i <file> -n <n>
  generate.py -h | --help

Options:
  -i <file>     Language model file.
  -n <n>        Number of sentences to generate.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle

from nltk.corpus import PlaintextCorpusReader
from languagemodeling.ngram import NGramGenerator


if __name__ == '__main__':
    opts = docopt(__doc__)

    # load the data


    corpus = PlaintextCorpusReader(r'languagemodeling/', 'harrypotter.txt')
    sents =  corpus.sents()
    # train the model
    n = int(opts['-n'])

    filepath = str(opts['-i'])
    fileload = open(filepath,'rb')

    model = pickle.load(fileload)
    generator = NGramGenerator(model)

    for _ in range(0,n):
    	print (generator.generate_sent())