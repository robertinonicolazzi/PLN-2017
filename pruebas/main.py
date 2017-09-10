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
from funaux import *


#set([u'resource', u'string', u'list', u'number', u'boolean', u'date'])



f = open(r'/media/robertnn/DatosLinux/PLN-2017/pruebas/Tagger.tag', 'rb')
taggerSample = pickle.load(f)
f.close()

f = open(r'/media/robertnn/DatosLinux/PLN-2017/pruebas/parser', 'rb')
parserSample = pickle.load(f)
f.close()
with open('TrainData.json', 'r') as data_file:
	data = json.load(data_file)

questionsSample = data["questions"]

mapeoDate = { 'birthDate': ["nació","nacio"]}

class ClassAnswerType:

	def __init__(self, questions, tagger, parser):

		self.model_POS = tagger
		self.all_words = set()
		train_set_property = []
		train_set_answer_type = []
		ls_keys_dbo = []

		for quest in questions:
			idiomas = quest["question"]
			st_keywords = ""
			st_question = ""
			for idiom in idiomas:
				if idiom["language"] == "es":
					st_question = cleanQuestion(idiom["string"])
					st_keywords = cleanKeywords(idiom["keywords"])
					break
			if st_question == "":
				continue
			
			# Generamos features para tipo de respuesta
			feat_question = self.features_answer_type(st_question)
			st_answer_type = quest["answertype"]
			train_set_answer_type.append((feat_question,st_answer_type))

			# Intento de mapeo de propiedades
		st_dbo = parseQuery(quest["query"]["sparql"])
		ls_keys_dbo.append(st_keywords, st_dbo)

		self.clas_tipo = nltk.NaiveBayesClassifier.train(train_set_answer_type)



	# --GET PROPERTY ----------------------------------------------

	def get_question_property(self,question):

		question_features_test = self.features_bag_of_words(question)
		prop_question = self.clas_propiedades.prob_classify(question_features_test)

		return prop_question

	def features_bag_of_words(self,question):
		features = {}
		for word in self.all_words:
			features['contains({})'.format(word)] = (word in word_tokenize(question))
		return features


		return feat

	# --GET ANSWER TYPE--------------------------------------------


	def get_answer_type(self,st_question):

		question_features_test = self.features_answer_type(st_question)
		type_question = self.clas_tipo.classify(question_features_test)

		return type_question

	def features_answer_type(self,st_question):
		feat = {}
		tagged_sent = self.model_POS.tag(st_question.split())

		feat["ask_cuanto"] = bool(re.search('cuant(o|a)(s|) ', st_question))
		feat["ask_cuando"] = bool(re.search('cuando ', st_question))
		feat["init_verb"]  = tagged_sent[0].startswith('v')
		feat["art_sust"]   = (tagged_sent[0] == 'da0000') and (tagged_sent[1]== 'nc0s000')

		return feat


	# --GET ENTITY-------------------------------------------------

	def get_entity(self,question, question_keywords, answertype):

		split_keys= question_keywords.split(',')

		entidades = []

		for keys_set in split_keys:
			tagged = self.model_POS.tag(word_tokenize(keys_set))
			tagged_keywords = list(zip(word_tokenize(keys_set),tagged))

			for w,t in tagged_keywords:
				if t == "np00000":
					#Construimos el nombre completo
					entity = w
					index = tagged.index(w)
					sustPropios.append(w)

	
		return ','.join(entidades)

	def answer_question(self, q, q_keys):
		# 1 - Obtenemos el tipo de la pregunta
		answer_type = self.get_answer_type(q)

		# 2 - Obtenemos la Entidad Principal

		# 3 - Obtenemos las posibles propiedades
		question = q_keys
		question_features_test = self.features_bag_of_words(question)
		self.clas_propiedades.show_most_informative_features(5)
		return self.clas_propiedades.classify(question_features_test)
		#print (sorted(prop_question._prob_dict.items(), key=lambda x: x[1]))



test_question = "¿ Es Michelle Obama la mujer de Barack Obama ?"

tagged_sent = taggerSample.tag(test_question)
tagged_keywords = list(zip(word_tokenize(test_question),tagged_sent))
print (parserSample.parse(tagged_keywords))


"""
keywords_test ="anfitrión, BBC Wildlife"
answerTypeClass = ClassAnswerType(questionsSample,tagger=taggerSample)
resp = answerTypeClass.answer_question(test_question,keywords_test)
print(resp)
"""


"""
top = Tk()
top.grid_columnconfigure(2, weight=1)
top.resizable(width=False, height=False)
top.title('Question Answering')

L1 = Label(top, text="Pregunta")
E1 = Entry(top, bd =2,width=50)
L2 = Label(top, text="keywords")
E2 = Entry(top, bd =2,width=50)


L1.grid(row=1,column=1,padx=10,pady=5)
L2.grid(row=2,column=1,padx=10,pady=5)
E1.grid(row=1,column=2)
E2.grid(row=2,column=2)

labelframe = LabelFrame(top, text="Respueta")
labelframe.grid(row=6,column=1,columnspan=2,sticky='w',padx=5)

def helloCallBack():
	quest = E1.get()
	keys = E2.get()
	resp = answerTypeClass.answer_question(quest,keys)

	 
	left = Label(labelframe, text= "Tipo:       " + resp)
	
	padright = 500-10-len(resp)-14-95
	left.grid(row=7,column=1,sticky='w',padx=(0, padright))
	'''
	left2 = Label(labelframe, text="Entidad:  " + resp[1])
	left2.grid(row=8,column=1,sticky='w')

	left3 = Label(labelframe, text="Respuesta: " + resp[2])
	left3.grid(row=11,column=1,sticky='w',pady=5)

	left4 = Label(labelframe, text="Query: \n\n" + resp[3],justify=LEFT)
	left4.grid(row=10,column=1,sticky='w',pady=10)
	'''

B = Button(top, text ="Respuesta", command = helloCallBack)
B.grid(row=3,column=2,sticky='e',padx=10)

top.minsize(width=500, height=200)
top.mainloop()
"""