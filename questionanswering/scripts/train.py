"""Train Question Answering 0.1

Usage:
  train.py -o <file> -t <path> -n <n>
  train.py -h | --help

Options:
  -o <file>     Output model file.
  -n <n>        senteces.
  -h --help     Show this screen.
"""
from docopt import docopt
import dill as pickle
import json

from questionanswering.main import ClassAnswerType
from stanfordcorenlp import StanfordCoreNLP
text = ["alcalde Cordoba", "gobernado Buenos Aires"] 
dbo = ["mayor"]

if __name__ == '__main__':
    opts = docopt(__doc__)

    print('Loading corpus...')

    pathTrainData = r'/media/robertnn/DatosLinux/PLN-2017/questionanswering/TrainData.json'


    with open(pathTrainData, 'r') as data_file:
      data = json.load(data_file)
    questionsSample = data["questions"]
    n = int(opts['-n'])

    if not n == 0:
      questionsSample = questionsSample[:n]
    print('Loading Property Mapping extra corpus')

    propertyCorpus = [[],[]]

    print('Loading StanfordCoreNLP...')

    pathStandford = r'/media/robertnn/DatosLinux/Standford/stanford-corenlp-full-2017-06-09/'
    nlp = StanfordCoreNLP(pathStandford, lang='es',memory='2g')

    
    print('Training model...')
    model = ClassAnswerType(questions=questionsSample,nlp=nlp,propCorpus=propertyCorpus)

    print('Saving...')
    filename = opts['-o']
    f = open(filename, 'wb')
    pickle.dump(model, f)
    f.close()
    