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
import json
import spacy
from sklearn.svm import LinearSVC
import sys
from questionanswering.funaux import *
from sklearn.tree import DecisionTreeClassifier
correctas = []
#correctas= ['0', '2', '3', '4', '5', '7', '12', '13', '17', '18', '19', '21', '22', '25', '28', '29', '32', '33', '38', '39', '42', '48', '49', '54', '70', '71', '74', '80', '11', '35', '36', '40', '41', '61', '63', '68', '72', '79', '93', '98', '104', '108', '114', '115', '118', '119', '121', '125', '126', '127', '134', '136', '153', '154']
#correctas = ['3000', '3001', '3002', '3004', '3005', '3006', '3007', '3008', '3009', '3010', '3011', '3012', '3013']
#13/17
correctas = ['20', '31', '37', '55', '59', '64', '81', '85', '109', '139', '144', '180', '185', '212']


from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB


from sklearn.linear_model import LogisticRegressionCV
from sklearn.linear_model import LogisticRegression

from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer

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
	'''
	x = load_obj('train_x')
	y = load_obj('train_y') 
	print(x[0])
	print('Train class...')
	clasi = LogisticRegression(class_weight={1:8})
	model.pExtractor.train(x,y,classi= clasi)
	print('OK - Class Loaded...')
	'''

	print('Loading corpus...')
	with open(r'/media/robertnn/DatosLinux/PLN-2017/questionanswering/Corpus/SimpleData.json', 'r') as data_file:
	  data = json.load(data_file)




	questionsSample = data["questions"]

	print('Parsing...')
	hits = len(correctas)
	total = len(correctas)
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
		if 	quest["id"] in correctas:
			continue;

		if  not quest["answertype"] == "boolean":
			continue

		st_quest, st_keys = getQuestAnKey(quest)
		print(st_quest)
		answers_gold = getAnswer(quest,quest["answertype"])
		answers_model = model.answer_question(st_quest,st_keys)

		if  quest["answertype"] == "boolean":
			if answers_model == answers_gold:
				hits +=1
				print ("CORRECTO")
				correctas.append(quest["id"])
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
				correctas.append(quest["id"])
				hits +=1
			else:
				if 	quest["aggregation"]:
					out = open('Log/aggregation.log','a')
				else:
					st_dbo = parseQuery(quest["query"]["sparql"])
					if st_dbo == "":
						out = open('Log/complex.log','a')
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
		#print (correctas)
		print ("HITS:", hits)
		print ("TOTAL:", total)
		print(correctas)
	print ("HITS:", hits)
	print ("TOTAL:", total)
	print ("Accurancy:", hits/total)

	