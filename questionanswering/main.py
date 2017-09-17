# -*- coding: utf-8 -*-
#!/usr/bin/python

from tkinter import *
import json
import re
from nltk.classify import apply_features
import nltk.classify.util

from nltk.tokenize import RegexpTokenizer
from SPARQLWrapper import SPARQLWrapper, JSON
from funaux import *
import nltk
from nltk.corpus import stopwords
from nltk import Tree
from stanfordcorenlp import StanfordCoreNLP
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

class ClassAnswerType:

	def __init__(self, questions, nlp):

		self.nlp_api = nlp
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.all_words = set()
		self.pipeline = None
		train_answer_type = []
		keys = []
		dbo = []

		for quest in questions:
			idiomas = quest["question"]
			st_keywords = ""
			st_question = ""
			for idiom in idiomas:
				if idiom["language"] == "es":
					st_question = idiom["string"]
					st_keywords = cleanKeywords(idiom["keywords"])
					break
			if st_question == "":
				continue
			
			# Generamos features para tipo de respuesta
			feat_question = self.features_answer_type(st_question)
			st_answer_type = quest["answertype"]
			train_answer_type.append((feat_question,st_answer_type))

			# Intento de mapeo de propiedades
			st_dbo = parseQuery(quest["query"]["sparql"])
			if st_dbo != "":
				keys.append(delete_tildes(st_keywords))
				dbo.append(st_dbo)
		self.clas_tipo = nltk.NaiveBayesClassifier.train(train_answer_type)
		self.pipeline = self.init_pipeline(keys,dbo)
		

	def init_pipeline(self,x,y):
		esp_stopwords = stopwords.words('spanish')
		vectorizer = CountVectorizer(analyzer='word',
										 tokenizer=self.nlp_api.word_tokenize,
										 lowercase=True,
										 stop_words=esp_stopwords)

		classifier = LogisticRegression()
		pipeline = Pipeline([("vec", vectorizer), ("clas", classifier)])
		pipeline.fit(x,y)

		return pipeline

	# --GET ANSWER TYPE--------------------------------------------

	def get_answer_type(self,st_question):

		question_features_test = self.features_answer_type(st_question)
		type_question = self.clas_tipo.classify(question_features_test)
		return type_question

	def features_answer_type(self,st_question):
		feat = {}
		st_question = cleanQuestion(st_question)
		tag_word = self.nlp_api.pos_tag(st_question)

		
		feat["ask_cuanto"] = bool(re.search('cu(a|á)nt(o|a)(s|) ', st_question))
		feat["ask_cuando"] = bool(re.search('cu(a|á)ndo ', st_question))
		feat["init_verb"]  = getFirstTag(tag_word).startswith('v')
		feat["art_sust"]   = (getFirstTag(tag_word) == 'da0000') and (getSecondTag(tag_word)== 'nc0s000')

		return feat

	# --GET PROPERTY ----------------------------------------------

	def get_english_ans(self, entity, properti):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setReturnFormat(JSON)

		query = '''
				select distinct ?result 
				where {{
					dbr:{} dbo:{} ?result
				}}
				'''.format(entity,properti)

		sparql.setQuery(query)			
		results = sparql.query().convert()
		print (query)
		for result in results["results"]["bindings"]:
			print("TYPE: ",result["result"]["type"])
			print("RESPUESTA: ",result["result"]["value"])
			print()

	def get_english_dbpedia(self, entity):

		query ='''
		PREFIX esdbr: <http://es.dbpedia.org/resource/> 
		SELECT ?same WHERE {{ 
		esdbr:{}   owl:sameAs   ?same .
		}}
		'''.format(entity)

		sparql = self.sparql
		sparql.setQuery(query)			
		results = sparql.query().convert()

		bindings = results["results"]["bindings"]

		for result in bindings:
			same = result["same"]["value"]
			if "http://dbpedia.org/" in same:
				return same.split('/')[4]

	def get_question_property(self,keys):
		st_keys = "".join(keys)
		st_keys = delete_tildes(st_keys)
		return self.pipeline.predict([st_keys])

	def check_entity_prop(self,entity, properti):

		# Veamos si hay relacion directa con la propiedad
		# sino nos fijamos en un futuro mapping
		en_entity = self.get_english_dbpedia(entity)

		self.get_english_ans(en_entity, properti)


	# --GET ENTITY-------------------------------------------------

	def get_entity(self,st_keys):

		keys= st_keys.split(',')
		keys_restantes = st_keys.split(',')
		entities = []

		for k in keys:
			tag = self.nlp_api.pos_tag(k)
			
			if "np00000" in [t for w,t in tag]:
				entities.append((k.strip(),self.nlp_api.dependency_parse(k)))
				keys_restantes.remove(k)

		return entities,keys_restantes

	def check_entitiesEsp(self,ls_entities):
		sparql = self.sparql
		
		# Lista de (entidad, texto desambiguante)
		entities = []
		amb_entities = []

		temp_entities = []
		for e,dep_p in ls_entities:
			e = e.replace(' ','_')
			query = '''PREFIX esdbp: <http://es.dbpedia.org/property/>
					PREFIX esdbr: <http://es.dbpedia.org/resource/>
					ASK {{ esdbr:{}   ?p    ?o .}}'''.format(e)

			sparql.setQuery(query)			
			results = sparql.query().convert()
			if results["boolean"] is False:
				#second chance
				names = [ (x,y) for tag,x,y in dep_p if tag =='name']
				for x,y in names:
					name = e.split('_')
					name = name[x-1] + "_" +name[y-1]
					query = '''PREFIX esdbp: <http://es.dbpedia.org/property/>
					PREFIX esdbr: <http://es.dbpedia.org/resource/>
					ASK {{ esdbr:{}   ?p    ?o .}}'''.format(name)
					sparql.setQuery(query)			
					results = sparql.query().convert()
					if results["boolean"] is True:
						amb_entities.append(name)
			else:
				entities.append(e)

		return entities,amb_entities



	# ------------------------------------------------------------------------
	# ---------------------- RESPONDER PREGUNTAS -----------------------------
	# ------------------------------------------------------------------------

	def answer_question(self, q, q_keys):
		print('\x1b[6;30;42m{:18}\x1b[0m {}'.format('QUESTION: ',q))
		print('\x1b[6;30;42m{:18}\x1b[0m {}'.format('KEYWORDS: ',q_keys))
		
		answer_type = self.get_answer_type(q)
		print('\x1b[6;30;42m{:18}\x1b[0m {}'.format('ANS_TYPE: ',answer_type))


		temp_entities, keys_restantes = self.get_entity(q_keys)
		print('\x1b[6;30;42m{:18}\x1b[0m {}'.format('INIT ENTITIES: ',''.join([x for x,y in temp_entities])))
		print('\x1b[6;30;42m{:18}\x1b[0m {}'.format('KEYS RESTANTES: ',''.join([x for x in keys_restantes])))

		entities, amb_entities = self.check_entitiesEsp(temp_entities)



		if len(temp_entities) != len(entities) + len(amb_entities):
			# Se descartaron entidades
			return ("Entidades descartadas")

		if len(entities) == 0 and len(amb_entities) == 0:
			return ("Entities not found on DBPedia")

		if len(entities) == 1 and len(amb_entities) == 0:
			#Una entidad encontrada
			st_property = self.get_question_property("".join(keys_restantes))
			self.check_entity_prop(entities[0],st_property[0])