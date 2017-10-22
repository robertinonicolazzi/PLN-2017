# -*- coding: utf-8 -*-
#!/usr/bin/python

from SPARQLWrapper import SPARQLWrapper, JSON
from questionanswering.funaux import *
from questionanswering.booleanHelper import BooleanHelper
from questionanswering.aggregationHelper import AggregationHelper
from questionanswering.entityExtractor import EntityExtractor
from questionanswering.propertyExtractor import PropertyExtractor

import sys, json, re, nltk,nltk.classify.util,numpy as np


def progress(msg, width=None):
	"""Ouput the progress of something on the same line."""
	if not width:
		width = len(msg)
	print('\b' * width + msg, end='')
	sys.stdout.flush()
	
class ClassAnswerType:

	def __init__(self, questions, nlp,propCorpus=[[],[]]):

		self.nlp_api = nlp
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)
		self.propertyExtractor = PropertyExtractor(nlp)
		train_prop_x = []
		train_prop_y = []
		self.all_words = set()

		train_answer_type = []
		keys = []
		dbo = []
		format_str = 'Answ Type ({}/{}) (Preg={}, Total={}), Prop {}'

		progress(format_str.format(0,len(questions), 0, len(questions),0))

		i=0
		j=0
		for quest in questions:
			i +=1
			idiomas = quest["question"]
			st_keywords = ""
			st_question = ""
			for idiom in idiomas:
				if idiom["language"] == "es":
					st_question = idiom["string"]
					st_keywords = idiom["keywords"]
					break
			if st_question == "":
				continue

			# Generamos features para tipo de respuesta
			feat_question = self.features_answer_type(st_question)
			st_answer_type = quest["answertype"]
			train_answer_type.append((feat_question,st_answer_type))

			# Intento de mapeo de propiedades

			temp_train_x,temp_train_y = self.propertyExtractor.generate_train_by_entity(quest["query"]["sparql"],st_keywords)
			if not len(temp_train_x) == 0:
				j += 1
			progress(format_str.format(i,len(questions), i, len(questions),j))
			train_prop_x += temp_train_x
			train_prop_y += temp_train_y

		self.clas_tipo = nltk.NaiveBayesClassifier.train(train_answer_type)

		self.propertyExtractor.train(train_prop_x,train_prop_y,propCorpus,self.nlp_api.word_tokenize)
		self.entityExtractor = EntityExtractor(self.nlp_api)






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
					<http://dbpedia.org/resource/{}> dbo:{} ?result
				}}
				'''.format(entity,properti)

		answers = resolveQuery(sparql,query)

		if len(answers) == 0:
			query = '''
				select distinct ?result 
				where {{
					<http://dbpedia.org/resource/{}> dbp:{} ?result
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
		

		self.entityExtractor.parseQuestion(q)


		answers = []
		answer_type = self.get_answer_type(q)
		
		print('{:18} {}'.format('QUESTION: ',q))		
		print('{:18} {}'.format('ANSWER TYPE: ',answer_type))

		entities,keys_restantes = self.entityExtractor.get_entities(q_keys,answer_type)

		print("Entitdades: ", entities)
		print("Keys Restastes: ",keys_restantes)
		if len(entities) > 1 and not answer_type == "boolean":
			print ("System not allow complex questios")
			return []

		if len(entities) == 0:
			print ("Entities not Found")
			return []

		if answer_type == "boolean":
			return self.boolean_answerer(q,q_keys,entities)

		#Resto de los tipos
		h_aggregation = AggregationHelper()
		keyAggregation = h_aggregation.check_aggregation(answer_type,q)
		es_entity = entities[0][0]
		en_entity = entities[0][1]

		st_property = self.propertyExtractor.get_question_property(en_entity,keys_restantes)

		print("Entidad Espanol:",es_entity)
		print("Entidad Ingles :",en_entity)
		print("Propiedad      :",st_property)

		answers = self.get_english_ans(en_entity, st_property)
		print("Respuesta:",answers)

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