"""Evaulate a parser.

Usage:
  eval.py -i <file> -e <ent> -k <key>
  eval.py -h | --help

Options:
  -i <file>     Parsing model file.

  -e <file>     Parsing model file.
  -k <file>     Parsing model file.
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
	else:
		return quest["answers"][0]["boolean"]

	for bind in quest["answers"][0]["results"]["bindings"]:
		answers.append(bind[a]["value"])

	return set(answers)




if __name__ == '__main__':
	
	opts = docopt(__doc__)

	print('Loading model...')
	filename = opts['-i']
	f = open(filename, 'rb')
	model = pickle.load(f)
	f.close()

	print('Loading corpus...')
	with open(r'/media/robertnn/DatosLinux/PLN-2017/questionanswering/SimpleData.json', 'r') as data_file:
	  data = json.load(data_file)

	ent = opts['-e']
	k = opts['-k']
	k_list = [k]

	print(model.propertyExtractor.get_question_property(ent,k_list))
