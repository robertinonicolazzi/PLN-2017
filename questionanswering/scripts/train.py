"""Train Question Answering 0.1

Usage:
  train.py -o <file>
  train.py -h | --help

Options:
  -o <file>     Output model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle
import json

from questionanswering.main import ClassAnswerType



if __name__ == '__main__':
    opts = docopt(__doc__)

    print('Loading corpus...')

    with open('TrainData.json', 'r') as data_file:
      data = json.load(data_file)
    questionsSample = data["questions"]

    print('Loading Property Mapping extra corpus')

    print('Loading StanfordCoreNLP...')

    nlp = StanfordCoreNLP(r'/media/robertnn/DatosLinux/Standford/stanford-corenlp-full-2017-06-09/', lang='es')


    print('Training model...')
    model = ClassAnswerType(questions=questionsSample,nlp=nlp)

    print('Saving...')
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
