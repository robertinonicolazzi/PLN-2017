# -*- coding: utf-8 -*-
#!/usr/bin/python

from SPARQLWrapper import SPARQLWrapper, JSON

from questionanswering.funaux import *
from questionanswering.booleanHelper import BooleanHelper
from questionanswering.aggregationHelper import AggregationHelper

import json, re, nltk,nltk.classify.util,numpy as np

from nltk.corpus import stopwords
from nltk import Tree

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

from heapq import nlargest


class ClassAnswerType:

	def __init__(self, questions, nlp,propCorpus=[[],[]]):

		self.nlp_api = nlp
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)

		train_prop_x = []
		train_prop_y = []
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

			temp_train_x,temp_train_y = self.generate_train_by_entity(quest["query"]["sparql"])
			train_prop_x += temp_train_x
			train_prop_y += temp_train_y

		self.clas_tipo = nltk.NaiveBayesClassifier.train(train_answer_type)

		self.pipeline = self.init_pipeline(train_prop_x,train_prop_y,propCorpus)
		

	# -------------------------------------------------------------
	# --GET ANSWER TYPE--------------------------------------------
	# -------------------------------------------------------------

	def get_answer_type(self,st_question):

		question_features_test = self.features_answer_type(st_question)

		type_question = self.clas_tipo.classify(question_features_test)
		return type_question

	def features_answer_type(self,st_question):
		feat = {}
		st_question = cleanQuestion(st_question)
		tag_word = self.nlp_api.pos_tag(st_question)

		
		feat["ask_cuanto"] = bool(re.search('cu(a|á)nt(o|a)(s|) ', st_question))
		feat["init_dame"] = (st_question.split(" ")[0] == 'dame')
		feat["ask_cuando"] = bool(re.search('cu(a|á)ndo ', st_question))
		feat["init_verb"]  = getFirstTag(tag_word).startswith('v')
		feat["init_verb2"]  = getFirstTag(tag_word).startswith('v')
		feat["art_sust"]   = (getFirstTag(tag_word) == 'da0000') and (getSecondTag(tag_word).startswith('n'))
		feat["art_sust2"]   = (getFirstTag(tag_word) == 'da0000') and (getSecondTag(tag_word).startswith('n'))
		return feat

	# -------------------------------------------------------------
	# --GET PROPERTY ----------------------------------------------
	# -------------------------------------------------------------
	def generate_train_by_entity(self, query):

		temp_prop_x = []
		temp_prop_y = []
		st_dbo = parseQuery(query)
		if st_dbo == "":
			return [],[]

		st_ent = getEntity(query)
		if st_ent == "":
			return [],[]
		

		st_keywords = delete_tildes(st_keywords)
		
		x = (st_keywords,st_dbo)
		y = 1
		temp_prop_x.append(x)
		temp_prop_y.append(y)

		sparql = self.sparqlEn
		query = '''
		SELECT distinct ?p WHERE {{
			<http://dbpedia.org/resource/{}> ?p ?v.

		}}
		'''.format(entity)

		sparql.setQuery(query)
		results = sparql.query().convert()
		for result in results["results"]["bindings"]:
			value = result["p"]["value"]
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				if not prop == st_dbo 
					x = (st_keywords,prop)
					y = 0
					temp_prop_x.append(x)
					temp_prop_y.append(y)

		return temp_prop_x, temp_prop_y

	def init_pipeline(self,x,y,extraCorpus):
		esp_stopwords = stopwords.words('spanish')
		vectorizer = CountVectorizer(analyzer='word',
										 tokenizer=self.nlp_api.word_tokenize,
										 lowercase=True,
										 stop_words=esp_stopwords)

		classifier = LogisticRegression()
		pipeline = Pipeline([("vec", vectorizer), ("clas", classifier)])

		x = x + extraCorpus[0]
		y = y + extraCorpus[1]
		pipeline.fit(x,y)
		return pipeline

	def get_question_property(self,entity,keys):
		st_keys = " ".join(keys)
		st_keys = delete_tildes(st_keys)

		sparql = self.sparqlEn
		query = '''
		SELECT distinct ?p WHERE {{
			<http://dbpedia.org/resource/{}> ?p ?v.

		}}
		'''.format(entity)
		properti = ""
		sparql.setQuery(query)
		results = sparql.query().convert()
		for result in results["results"]["bindings"]:
			value = result["p"]["value"]
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				temp = self.pipeline.predict_proba([(st_keys,prop)])
				if temp == 1:
					properti = prop
					break

		

		return properti


	# -------------------------------------------------------------
	# --ENTITY WORKFLOW -------------------------------------------
	# -------------------------------------------------------------
	def get_english_dbpedia(self, entity):

		query ='''
		SELECT ?same WHERE {{ 
			<http://es.dbpedia.org/resource/{}>
			dbpedia-owl:wikiPageRedirects* 
			?resource . 
			?resource 
			owl:sameAs 
			?same.
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

		return entity

	def get_entities(self, keywords):

		found_entities = []
		keys= [x.strip() for x in st_keys.split(',')]

		for key in keys:
			noum_group = getNounGroups(key)
			for group in noum_group:
				group = prepareGroup(group)

				if self.check_ent_dbES(group):
					es_ent = group
					en_ent = self.get_english_dbpedia(group)
					found_entities.append((es_ent,en_ent,lenEntity(es_ent)))
				else:
					if self.check_ent_dbEN(group):
						es_ent = group
						en_ent = group
						found_entities.append((es_ent,en_ent,lenEntity(es_ent)))

		found_entities = sorted(found_entities, key=itemgetter(2),reverse=True)

		return found_entities


	def check_ent_dbES(self,entity):
		sparql = self.sparql
		query ='''
				ASK {{
					<http://es.dbpedia.org/resource/{}> ?p ?v
				}}'''.format(entity)

		sparql.setQuery(query)			
		result = sparql.query().convert()

		return result["boolean"]

	def check_ent_dbEN(self,entity):
		sparql = self.sparqlEn
		query ='''
				ASK {{
					<http://dbpedia.org/resource/{}> ?p ?v
				}}'''.format(entity)

		sparql.setQuery(query)			
		result = sparql.query().convert()

		return result["boolean"]

	# -------------------------------------------------------------
	# --GET SIMPLE ANSWERS WORKFLOW -------------------------------
	# -------------------------------------------------------------
	def default_ans(self, entity,answertype):
		sparql = self.sparqlEn
		answers = []
		properti = ""
		if answertype == "date":
			properti = "date"

		query = '''
				select distinct ?result 
				where {{
					dbr:{} dbo:{} ?result
				}}
				'''.format(entity,properti)

		answers = resolveQuery(sparql,query)

		if len(answers) == 0:
			query = '''
				select distinct ?result 
				where {{
					dbr:{} dbp:{} ?result
				}}
				'''.format(entity,properti)

			answers = resolveQuery(sparql,query)

		return set(answers)

	def get_english_ans_reverse(self, entity, properti):
		sparql = self.sparqlEn
		answers = []
		query = '''
				select distinct ?result, ?resource
				where {{

				<http://dbpedia.org/resource/{}> dbo:wikiPageDisambiguates* ?resource.					
				?result {}:{} ?resource

				}}
				'''.format(entity,"dbo",properti)

		answers = resolveQuery(sparql,query)

		return set(answers)

	def get_english_ans(self, entity, properti):
		sparql = self.sparqlEn
		answers = []

		query = '''
				select distinct ?result 
				where {{
						<http://dbpedia.org/resource/{}> dbo:{} ?result
						
				}}
				'''.format(entity,properti)
		answers = resolveQuery(sparql,query)

		if len(answers) == 0:
			query = '''
					select distinct ?result 
					where {{
							<http://dbpedia.org/resource/{}> dbo:wikiPageDisambiguates ?resource.
							?resource dbo:{} ?result
					}}
					'''.format(entity,properti)

			answers = resolveQuery(sparql,query)


		return set(answers)



	# -----------------------------------------------------------------------
	# ---------------------- PREGUNTAS BOOLEAN ------------------------------
	# -----------------------------------------------------------------------

	def boolean_answerer(self,q,q_keys,entities):

		
		pr_entity_es = ""
		sn_entity_es = ""
		answers = False
		q = cleanQuestion(q)
		h_boolean = BooleanHelper()

		if len(entities) == 1:
			pr_entity_es = entities[0][0]
			pr_entity_en = entities[0][1]
			bool_key, properti = h_boolean.boolean_key_one_entity(q)

			if bool_key == "type":
				answers = h_boolean.get_type_answer(pr_entity_es, properti)
			elif bool_key == "exist":
				answers = h_boolean.get_exist_answer(pr_entity_es, properti)
			else:
				properti = self.get_question_property(keys_restantes)
				answers = h_boolean.get_properti_answer(pr_entity_en,properti[0])

		elif len(entities) == 2:

			props, st_filter = self.two_entities_prop_filter(q,keys_restantes)

			pr_entity_es = entities[0][0]
			pr_entity_en = entities[0][1]

			sn_entity_es = entities[1][0]
			sn_entity_en = entities[1][1]
			
			answers = h_boolean.two_entities_answer(pr_entity_en,sn_entity_en,props[0],st_filter)
		else:
			answers = []


		return answers

	def two_entities_prop_filter(self,question,keys_restantes):
		prop = []
		st_filter = ""
		if "antes" in question:
			st_filter = "FILTER (?x < ?y)"
			prop.append("date")
		elif "despues" in question:
			st_filter = "FILTER (?x > ?y)"
			prop.append("date")
		elif "menor" in question:
			st_filter = "FILTER (?x < ?y)"
			prop = self.get_question_property(keys_restantes)
		elif "mayor" in question or "grande" in question:
			st_filter = "FILTER (?x > ?y)"
			prop = self.get_question_property(keys_restantes)
		elif "misma" in question or "igual" in question or "mismos" in question:
			st_filter = "same"
			prop = self.get_question_property(keys_restantes)
		else:
			prop = self.get_question_property(keys_restantes)
			#la igualdad es viendo si pertenece
			st_filter = ""

		return prop, st_filter


	# ------------------------------------------------------------------------
	# ---------------------- RESPONDER PREGUNTAS -----------------------------
	# ------------------------------------------------------------------------

	def answer_question(self, q, q_keys):

		print ('---------------------------------------------------------------')
		
		st_property = ""
		en_entity = ""
		entidad_elegida = ""
		answers = []
		answer_type = self.get_answer_type(q)
		
		print('{:18} {}'.format('QUESTION: ',q))		
		print('{:18} {}'.format('ANSWER TYPE: ',answer_type))
		

		entities = self.get_entities(q_keys)
		keys_restantes = self.resolve_context
		print(entities)

		return
		if len(entities) > 1 and not answer_type == "boolean":
			print ("System not allow complex questios")
			return []

		if answer_type == "boolean":
			return self.boolean_answerer(q,q_keys,entities)

		#Resto de los tipos
		h_aggregation = AggregationHelper()
		keyAggregation = h_aggregation.check_aggregation(answer_type,q)
		es_entity = entities[0][0]
		en_entity = entities[0][1]

		st_property = self.get_question_property(keys_restantes)

		print("Entidad Espanol:",es_entity)
		print("Entidad Ingles :",en_entity)
		print("Propiedad      :",st_property)

		answers = self.get_english_ans(en_entity, st_property)

		if answer_type == "number" and keyAggregation == "count" and not len(answers) == 0:
			try:
				val = float(answers[0])
			except ValueError:
				answers = h_aggregation.answer_aggregation("count",en_entity,st_property)

		if len(answers) == 0 and answer_type == "date":
			answers = self.default_ans(en_entity,answer_type)

		if len(answers) == 0 and answer_type == "resource":
			answers = self.get_english_ans_reverse(en_entity,st_property)

		print('---------------------------------------------------------------')
		return answers