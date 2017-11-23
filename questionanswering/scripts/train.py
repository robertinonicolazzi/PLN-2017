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
import dill, json, spacy
from questionanswering.main import ClassAnswerType


if __name__ == '__main__':
    opts = docopt(__doc__)

    print('Loading corpus...')

    pathTrainData = r'/media/robertnn/DatosLinux/PLN-2017/questionanswering/Corpus/TrainData.json'


    with open(pathTrainData, 'r') as data_file:
      data = json.load(data_file)
    questionsSample = data["questions"]
    n = int(opts['-n'])

    if not n == 0:
      questionsSample = questionsSample[:n]
    print('Loading Property Mapping extra corpus')

    nlp = spacy.load('es_default', parser=False)

    """print('Loading StanfordCoreNLP...')

    pathStandford = r'/media/robertnn/DatosLinux/Standford/stanford-corenlp-full-2017-06-09/'
    nlp = StanfordCoreNLP(pathStandford, lang='es',memory='2g')
    """
    
    print('Training model...')
    model = ClassAnswerType(questions=questionsSample,nlp=nlp)

    print('Saving...')
    filename = opts['-o']
    f = open(filename, 'wb')
    model.nlp_api = None
    model.eExtractor.nlp_api = None
    model.pExtractor.nlp_api = None
    dill.dump(model, f)
    f.close()
    