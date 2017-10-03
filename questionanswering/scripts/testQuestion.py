"""Evaulate a parser.

Usage:
  testQuestion.py -i <file> -q <question> -k <keys>
  testQuestion.py -h | --help

Options:
  -i <file>     Parsing model file.
  -q <question> question
  -k <keys>
  -h --help     Show this screen.
"""
from docopt import docopt
import dill as pickle
import json
import sys
from questionanswering.funaux import *

def getQuestAnKey(quest):
    idiomas = quest["question"]
    st_keywords = ""
    st_question = ""
    for idiom in idiomas:
        if idiom["language"] == "es":
            st_question = idiom["string"]
            st_keywords = idiom["keywords"]
            break
    return st_question,st_keywords


def getAnswer(quest,ans_type):
    answers = []
    a = "result"

    if ans_type == "date":
        a = "date"
    elif ans_type == "resource":
        a="uri"
    elif ans_type == "number":
        a = "c"
    elif ans_type == "string":
        a = "string"

    for bind in quest["answers"][0]["results"]["bindings"]:
        answers.append(bind[a]["value"])

    return set(answers)

def progress(msg, width=None):
    """Ouput the progress of something on the same line."""
    if not width:
        width = len(msg)
    print('\b' * width + msg, end='')
    sys.stdout.flush()



if __name__ == '__main__':
    
    opts = docopt(__doc__)

    print('Loading model...')
    filename = opts['-i']
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()

    st_quest = str(opts['-q'])
    st_keys = str(opts['-k'])


    
    print (model.get_answer_type(st_quest))
    print (model.answer_question(st_quest,st_keys))


            
