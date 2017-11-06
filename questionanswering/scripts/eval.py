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
import sys
from questionanswering.funaux import *

#correctas = []
correctas= ['0', '2', '3', '4', '5', '7', '11', '13', '17', '18', '19', '20', '21', '22', '28', '29', '30', '31', '32', '33', '35', '36', '37', '38', '39', '40', '41', '42', '43', '48', '49', '55', '59', '61', '68', '70', '71', '72', '74', '79', '80', '81', '87', '93', '96', '97', '98', '101', '104', '108', '109', '111', '113', '114', '115', '118', '119', '121', '125', '126', '127', '128', '134', '136', '139', '144', '145', '146', '152', '153', '154', '155', '159', '160', '162', '164', '167', '169', '171', '174', '175', '176', '180', '185', '189', '191', '192', '201', '204', '207', '212', '213', '12', '25', '54', '63', '203', '208', '24', '99', '112', '149', '182', '200', '85', '105', '107', '135', '151', '197', '166']


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

	nlp = spacy.load('es_default', parser=False)
	model.nlp_api = nlp
	model.pExtractor.nlp_api = nlp
	model.eExtractor.nlp_api = nlp 
	print('Loading corpus...')
	with open(r'/media/robertnn/DatosLinux/PLN-2017/questionanswering/SimpleData.json', 'r') as data_file:
	  data = json.load(data_file)

	vistos = ['0', '2', '3', '4', '5', '6', '7', '9', '10', '11', '12', '13', '17', '18', '19', '20', '21', '22', '23', '24', '25', '28', '29', '30', '31', '32', '33', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '48', '49', '50', '52', '54', '55', '58', '59', '60', '61', '63', '64', '65']


	questionsSample = data["questions"][:50]

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
		#if 	quest["id"] in correctas:
		#	continue;

		'''if quest["aggregation"]:
			agg = agg - 1
			vistos.append(quest["id"])
			if agg == 0:
				break
		else:
			continue
		'''
		st_quest, st_keys = getQuestAnKey(quest)
		answers_gold = getAnswer(quest,quest["answertype"])
		answers_model = model.answer_question(st_quest,st_keys)

		if  quest["answertype"] == "boolean":
			continue
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
	print (vistos)
	print ("HITS:", hits)
	print ("TOTAL:", total)
	print ("Accurancy:", hits/total)
	print (correctas)
	