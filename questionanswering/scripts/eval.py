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
		if  quest["answertype"] == "list":
			continue;

		if  quest["answertype"] == "boolean":
			
			st_quest, st_keys = getQuestAnKey(quest)

			answer_golden = getAnswer(quest,quest["answertype"])
			answers_model = model.answer_question(st_quest,st_keys)
			print(st_quest)
			print(answers_model)
			if answers_model == answer_golden:
				hits +=1
				print ("CORRECTO")

			total +=1
		else:
			

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
			
			for seta in answers_model:
				if len(seta) == 0:
					continue
				if seta == set(answers_gold):
					out.write("RESPUETA CORRECTA\n")
					correcta = True
					hits +=1
			total +=1

			if not correcta:
				for a in answers_gold:
					out.write(str(a)+"--- Gold\n")
				for seta in answers_model:
					for a in seta:
						out.write((a)+"----Model Rank: "+str(rank)+"\n")
					rank += 1
				out.write(quest["query"]["sparql"])
			out.write('----------------------------\n')
			out.close()
			
			print ("HITS:", hits)
			print ("TOTAL:", total)

	print ("HITS:", hits)
	print ("TOTAL:", total)
	print ("Accurancy:", hits/total)
	


'''
		total_gold += len(gold_spans)
		total_model += len(model_spans)

		# compute labeled partial results
		prec = float(hits) / total_model * 100
		rec = float(hits) / total_gold * 100
		f1 = 2 * prec * rec / (prec + rec)

		progress(format_str.format(float(i+1) * 100 / n, i+1, n, prec, rec, f1))

	print('')
	print('Parsed {} sentences'.format(n))
	print('Labeled')
	print('  Precision: {:2.2f}% '.format(prec))
	print('  Recall: {:2.2f}% '.format(rec))
	print('  F1: {:2.2f}% '.format(f1))
'''