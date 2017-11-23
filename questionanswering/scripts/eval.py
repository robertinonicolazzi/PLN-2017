"""Evaulate a parser.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Parsing model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import dill as pickle
import json, spacy, sys
from questionanswering.funaux import *


from sklearn.linear_model import LogisticRegression

from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

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
	print('OK - Model Loaded...')

	print('Loading Spacy...')
	nlp = spacy.load('es_default', parser=False)
	print('OK - Spacy Loaded...')
	model.nlp_api = nlp
	model.pExtractor.nlp_api = nlp
	model.eExtractor.nlp_api = nlp

	print('Loading corpus...')
	with open(r'Corpus/SimpleDataCustom.json', 'r') as data_file:
	  data = json.load(data_file)




	questionsSample = data["questions"]

	print('Parsing...')
	hits = 0
	total = 0
	total_gold, total_model = 0, 0
	n = len(questionsSample)
	#format_str = '{:3.1f}% ({}/{}) (P={:2.2f}%, R={:2.2f}%, F1={:2.2f}%)'

	out = open('Log/aggregation.log','w').close()
	out = open('Log/bool.log','w').close()
	out = open('Log/simple.log','w').close()
	out = open('Log/complex.log','w').close()
	#progress(format_str.format(0.0, 0, n, 0.0, 0.0, 0.0))
	agg = 10
	for i, quest in enumerate(questionsSample):
		st_quest, st_keys = getQuestAnKey(quest)
		answers_gold = getAnswer(quest,quest["answertype"])
		answers_model = model.answer_question(st_quest,st_keys)

		if  quest["answertype"] == "boolean":
			if answers_model == answers_gold:
				hits +=1
				print ("CORRECTO")
			else:
				out = open('Log/bool.log','a')
				out.write(str(st_quest) + "\n")
				out.write(str(st_keys) + "\n")
				out.write(quest["query"]["sparql"])
				out.write('---------------------------------------\n')
				out.close()

			total +=1
		else:
	
			if type(answers_model) is bool:
				total +=1
				continue		

			if answers_model == set(answers_gold):
				print ("CORRECTO")
				hits +=1
			else:
				if 	quest["aggregation"]:
					out = open('Log/aggregation.log','a')
				else:
					out = open('Log/simple.log','a')
					
				out.write(str(st_quest) + "\n")
				out.write(str(st_keys) + "\n")
				out.write(quest["query"]["sparql"])
				out.write('RESPUESTAS \n')
				for seta in answers_model:
					out.write((seta)+"----Model: \n")
				out.write('---------------------------------------\n')
				out.close()
			total +=1
		print ("HITS:", hits)
		print ("TOTAL:", total)
	print ("HITS:", hits)
	print ("TOTAL:", total)
	print ("Accurancy:", hits/total)

	