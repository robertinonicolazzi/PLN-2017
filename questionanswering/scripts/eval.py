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
correctas= ['0', '2', '4', '5', '7', '11', '13', '17', '22', '25', '28', '32', '35', '36', '38', '40', '41', '48', '49', '61', '66', '68', '70', '71', '72', '74', '79', '80', '93', '97', '98', '104', '108', '114', '118', '119', '121', '125', '126', '127', '134', '136', '145', '146', '152', '153', '154', '159', '162', '167', '169', '171', '174', '175', '176', '189', '191', '192', '207', '213', '18', '19', '21', '29', '30', '42', '113', '160', '164', '204']
correctas_bool = []

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
	model.propertyExtractor.nlp_api = nlp
	model.entityExtractor.nlp_api = nlp 
	print('Loading corpus...')
	with open(r'/media/robertnn/DatosLinux/PLN-2017/questionanswering/SimpleData.json', 'r') as data_file:
	  data = json.load(data_file)

	
	questionsSample = data["questions"]

	print('Parsing...')
	hits, total_gold, total_model = 0, 0, 0
	total = 0
	n = len(questionsSample)
	#format_str = '{:3.1f}% ({}/{}) (P={:2.2f}%, R={:2.2f}%, F1={:2.2f}%)'

	#progress(format_str.format(0.0, 0, n, 0.0, 0.0, 0.0))
	for i, quest in enumerate(questionsSample):
		if 	quest["id"] in correctas:
			continue;

		if  quest["answertype"] == "list":
			continue;
		

		if  quest["answertype"] == "boolean":
			continue
			st_quest, st_keys = getQuestAnKey(quest)
			answer_golden = getAnswer(quest,quest["answertype"])
			answers_model = model.answer_question(st_quest,st_keys)

			if answers_model == answer_golden:
				hits +=1
				print ("CORRECTO")
				correctas_bool.append(quest["id"])
			else:
				out = open('myfile','a')
				out.write(str(st_quest) + "\n")
				out.write('----------------------------\n')
				out.close()

			total +=1
			print ("Accurancy:", hits/total)
			print(correctas_bool)
		else:
			if not quest["aggregation"]:
				continue
			#st_dbo = parseQuery(quest["query"]["sparql"])
			#if st_dbo == "":
			#	continue

			out = open('myfile','a')

			st_quest, st_keys = getQuestAnKey(quest)
			answers_gold = getAnswer(quest,quest["answertype"])
			answers_model = model.answer_question(st_quest,st_keys)

			out.write(str(st_quest) + "\n")

			rank = 1
			if type(answers_model) is bool:
				total +=1
				continue
				


			
			correcta = False;
			

			if answers_model == set(answers_gold):
				out.write("RESPUETA CORRECTA\n")
				correctas.append(quest["id"])
				correcta = True
				hits +=1
			total +=1

			if not correcta:
				for a in answers_gold:
					out.write(str(a)+"--- Gold\n")
				for seta in answers_model:
					out.write((seta)+"----Model Rank: \n")
				out.write(quest["query"]["sparql"])
			out.write('----------------------------\n')
			out.close()
			
			print ("HITS:", hits)
			print ("TOTAL:", total)

	print ("HITS:", hits)
	print ("TOTAL:", total)
	print ("Accurancy:", hits/total)
	print (correctas)
	