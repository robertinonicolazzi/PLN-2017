# -*- coding: utf-8 -*-
#!/usr/bin/python

from tkinter import *

import json
import re
from nltk.classify import apply_features
import nltk.classify.util
from nltk.tokenize import word_tokenize
import pickle
from nltk.tokenize import RegexpTokenizer
from SPARQLWrapper import SPARQLWrapper, JSON
import httplib2
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("spanish")

#set([u'resource', u'string', u'list', u'number', u'boolean', u'date'])



f = open(r'/media/robertnn/DatosLinux/PLN-2017/pruebas/Tagger.tag', 'rb')
taggerSample = pickle.load(f)
f.close()


with open('TrainData.json', 'r') as data_file:
	data = json.load(data_file)

questionsSample = data["questions"]

mapeoDate = { 'birthDate': ["nació","nacio"]}

class ClassAnswerType:

	def __init__(self, questions, tagger):

		self.model_POS = tagger
		train_set = []
		question_type= []
		for quest in questions:
			idiomas = quest["question"]
			string_question = None
			for idiom in idiomas:
				if idiom["language"] == "es":
					string_question = idiom["string"]
					string_question = string_question.replace('?',' ?')
					string_question = string_question.replace('¿','¿ ')
					
					break
			if string_question is None:
				continue

			question_type.append((string_question,quest["answertype"]))

			q_features = self.question_features(string_question)
			train_set.append( (q_features,quest["answertype"]) )

		self.all_words = set(word.lower() for passage in question_type for word in word_tokenize(passage[0]))
		self.classifier = nltk.NaiveBayesClassifier.train(train_set[:160])

	#train_set = apply_features(question_features, question_type[400:])
	#test_set = apply_features(question_features, question_type[:100])



	def classify(self,question):
		question = question.replace('?','')
		question = question.replace('¿','')
		question_features_test = self.question_features(question)
		type_question = self.classifier.classify(question_features_test)
		question = question.split()
		#tagged_sentence = list(zip(question,tag_sentence))
		return type_question


	def question_features(self,question):
		feat = {}
		#feat = {word: (word in tokenizer.tokenize(question[0])) for word in all_words}
		feat["ask_cuanto"] = bool(re.search('(c|C)u(a|á)nt(o|a)(s|) ', question))
		feat["ask_cuando"] = bool(re.search('(c|C)u(a|á)ndo ', question))

		#POS Feature
		tagged_sent = self.model_POS.tag(question.split())
		feat["init_verb"] = tagged_sent[0].startswith('v')
		feat["art_sust"] = (tagged_sent[0] == 'da0000') and (tagged_sent[1]== 'nc0s000')

		return feat

	def getPassage(self,question, question_keywords, answertype):

		string_question = question.replace('?',' ?')
		string_question = question.replace('¿','¿ ')
		string_list = word_tokenize(string_question)
		tagged_sent = self.model_POS.tag(string_list)
		print (tagged_sent)

		tagged = self.model_POS.tag([ word.strip() for word in question_keywords.split(',')])
		tagged_keywords = list(zip([ word.strip() for word in question_keywords.split(',')],tagged))

		print (tagged_keywords)

		sustPropios = []
		sustComunes = []
		verbos = []

		propiedad = []
		subPropiedad = []
		for w,t in tagged_keywords:
			w = w.strip()
			w.replace(' ','_')
			if t == "np00000":
				sustPropios.append(w)
			if t.startswith("n") and not t == "np00000":
				sustComunes.append(w)
			if t.startswith("v"):
				verbos.append(w)

		import pdb; pdb.set_trace()
		# Veamos si empieza con preposición, el primer sustantivo es la subpropiedad
		# del verbo que determina la propiedad padre
		empiezaConPreposicion = (tagged_sent[1] == "sp000")
		if empiezaConPreposicion:
			subPropiedad.append(sustComunes[0])
			sustComunes.pop(0)

		if answertype == "date":

			for key in mapeoDate.keys():
				bind = mapeoDate.get(key)
				for verb in verbos:
					if verb in bind:
						propiedad.append(key)

			if not len(sustPropios) == 0:
				resource = sustPropios[0]
			else:
				resource = sustComunes[0]

			if not len(acciones) == 0:
				pregunta = propiedad[0]
			else:
				pregunta = "fecha"


		
		return answertype, ','.join(sustPropios) + ','+ ','.join(sustComunes) , ','.join(propiedad) + ','.join(subPropiedad), "query"

	def generarQuery(self,answertype, entidades, propiedades):
		dbo = "PREFIX dbo: <http://dbpedia.org/ontology/>\n"
		res = "PREFIX res: <http://dbpedia.org/resource/>\n"

		resEs = "PREFIX res: <http://es.dbpedia.org/resource/>\n"
		propEs = "PREFIX dpo: <http://es.dbpedia.org/property/>\n"

		resElegido = ""
		dboElegido = ""

		resElegido = resEs
		dboElegido = propEs
		query = dboElegido + resElegido + select + where


		
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setQuery(query)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()
		where = "WHERE {\n        res:"+entPropias[0]+" dbo:"+pregunta+" ?result .\n}"
		respuesta = ""
		for result in results["results"]["bindings"]:
			print("RESPUESTA: ",result["result"]["value"])
			print()
			respuesta = result["result"]["value"]
			break

	def answerQuest(self, question,question_keywords):
		answer_type = self.classify(question)
		return self.getPassage(question,question_keywords,answer_type)


test_question = "¿Cuándo nació Barack Obama?"
keywords_test ="Barack Obama, nació"
answerTypeClass = ClassAnswerType(questionsSample,tagger=taggerSample)




top = Tk()
top.grid_columnconfigure(2, weight=1)


top.resizable(width=False, height=False)
top.title('Question Answering')
L1 = Label(top, text="Pregunta")
L1.grid(row=1,column=1,padx=10,pady=5)
E1 = Entry(top, bd =2,width=50)
E1.grid(row=1,column=2)

L2 = Label(top, text="keywords")
L2.grid(row=2,column=1,padx=10,pady=5)
E2 = Entry(top, bd =2,width=50)
E2.grid(row=2,column=2)

labelframe = LabelFrame(top, text="Respueta")

labelframe.grid(row=6,column=1,columnspan=2,sticky='w',padx=5)


def helloCallBack():
	quest = E1.get()
	keys = E2.get()
	resp = answerTypeClass.answerQuest(quest,keys)

	 
	left = Label(labelframe, text= "Tipo:       " + resp[0])
	padright = 500-10-len(resp[0])-14-95
	left.grid(row=7,column=1,sticky='w',padx=(0, padright))
	left2 = Label(labelframe, text="Entidad:  " + resp[1])
	left2.grid(row=8,column=1,sticky='w')

	left3 = Label(labelframe, text="Respuesta: " + resp[2])
	left3.grid(row=11,column=1,sticky='w',pady=5)

	left4 = Label(labelframe, text="Query: \n\n" + resp[3],justify=LEFT)
	left4.grid(row=10,column=1,sticky='w',pady=10)



B = Button(top, text ="Respuesta", command = helloCallBack)

B.grid(row=3,column=2,sticky='e',padx=10)
top.minsize(width=500, height=200)

#Zona de respuesta

top.mainloop()
"""
class answerQuest:
	__init__(self,question)


verbos = tuple_result[1][2]
entidad = tuple_result[1][0]

propertyList = []
for key in mapeoDate.keys():
	bind = mapeoDate.get(key)
	for verb in verbos:
		if verb in bind:
			propertyList.append(key)
print (propertyList)
#print (nltk.classify.accuracy(classifier, train_set[:55]))

"""




"""


class Consultas(self):
	self.instance = SPARQLWrapper("http://dbpedia.org/sparql")

	fun getResult(query,answerType):
sparql = self.instance
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
	print(result["uri"]["value"])

\{[^\"]*"language": ".[^s]"[^\}]*\},

"""