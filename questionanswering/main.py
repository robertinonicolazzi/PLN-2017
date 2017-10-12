# -*- coding: utf-8 -*-
#!/usr/bin/python


import json
import re

import nltk.classify.util

from nltk.tokenize import RegexpTokenizer
from SPARQLWrapper import SPARQLWrapper, JSON
from questionanswering.funaux import *
import nltk
from nltk.corpus import stopwords
from nltk import Tree

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

import numpy as np

from heapq import nlargest

class ClassAnswerType:

	def __init__(self, questions, nlp,propCorpus=[[],[]]):

		self.nlp_api = nlp
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)

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

		self.pipeline = self.init_pipeline(keys,dbo,propCorpus)
		

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

	def get_question_property(self,keys):
		st_keys = " ".join(keys)
		st_keys = delete_tildes(st_keys)
		temp = self.pipeline.predict_proba([st_keys])
		temp = temp.tolist()
		nmax = nlargest(2, enumerate(temp[0]), key=lambda x:x[1])
		properties = []
		for i,v in nmax:
			properties.append(self.pipeline.steps[-1][-1].classes_[i])
		return properties


	# -------------------------------------------------------------
	# --ENTITY WORKFLOW -------------------------------------------
	# -------------------------------------------------------------
	def get_english_dbpedia(self, entity):

		query ='''
		PREFIX esdbr: <http://es.dbpedia.org/resource/> 
		SELECT ?same WHERE {{ 
		<http://es.dbpedia.org/resource/{}>    dbpedia-owl:wikiPageRedirects* ?resource .  ?resource owl:sameAs ?same.
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


	def get_named_entities(self,st_keys):

		keys= [x.strip() for x in st_keys.split(',')]
		keys_restantes = [x.strip() for x in st_keys.split(',')]
		entities = []

		for k in keys:
			tag = self.nlp_api.pos_tag(k)
			
			if "np00000" in [t for w,t in tag]:
				entities.append((k,self.nlp_api.dependency_parse(k)))
				keys_restantes.remove(k)

		if len(entities) == 0:
			for k in keys:
				words = k.split()			
				for w in words:
					if w[0] == w[0].upper():
						entities.append((w,self.nlp_api.dependency_parse(w)))
						keys_restantes.remove(w)
					
		return entities,keys_restantes

	def get_entities_

	def check_entities_espanol(self,ls_entities):
		sparql = self.sparql
		
		# Lista de (entidad, texto desambiguante)
		entities = []
		amb_entities = []
		boolDirectEnglish = False
		temp_entities = []
		for e,dep_p in ls_entities:
			get_name = False
			tagged_sent = self.nlp_api.pos_tag(e)
			e = e.strip()
			e = e.replace(' ','_')
			e = str(e[0].upper() + e[1:])

			query = '''PREFIX esdbp: <http://es.dbpedia.org/property/>
					PREFIX esdbr: <http://es.dbpedia.org/resource/>
					ASK {{ <http://es.dbpedia.org/resource/{}>    ?p    ?o .}}'''.format(e)

			sparql.setQuery(query)			
			results = sparql.query().convert()
			if results["boolean"] is False:
				#second chance
				hayNames = False
				names = [ (x,y) for tag,x,y in dep_p if tag =='name']
				for x,y in names:
					hayNames = True
					name = e.split('_')
					name = name[x-1] + "_" +name[y-1]
					query = '''PREFIX esdbp: <http://es.dbpedia.org/property/>
					PREFIX esdbr: <http://es.dbpedia.org/resource/>
					ASK {{ <http://es.dbpedia.org/resource/{}>    ?p    ?o .}}'''.format(name)
					sparql.setQuery(query)			
					results = sparql.query().convert()
					if results["boolean"] is True:
						amb_text = e.replace(name,'')
						amb_text = amb_text.replace('_',' ')
						amb_entities.append((name,amb_text))
						continue
						get_name = True
	
				english = self.try_english(e)
				if not english == "":
					entities.append(english)
					boolDirectEnglish = True
					continue

				if not get_name:
					for w,t in tagged_sent:
						if t == "np00000":
							name = w
							query = '''PREFIX esdbp: <http://es.dbpedia.org/property/>
							PREFIX esdbr: <http://es.dbpedia.org/resource/>
							ASK {{ <http://es.dbpedia.org/resource/{}>    ?p    ?o .}}'''.format(name)
							sparql.setQuery(query)			
							results = sparql.query().convert()
							if results["boolean"] is True:
								amb_text = e.replace(name,'')
								amb_text = amb_text.replace('_',' ')
								amb_entities.append((name,amb_text))
								break

			else:
				entities.append(e)

		return entities,amb_entities,boolDirectEnglish


	def try_english(self,e):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setReturnFormat(JSON)
		
		# Lista de (entidad, texto desambiguante)
		entities = ""

		e = e.strip()
		e = e.replace(' ','_')
		e = str(e[0].upper() + e[1:])

		query = '''	ASK {{ dbr:{}   ?p    ?o .}}'''.format(e)

		sparql.setQuery(query)	
		results = sparql.query().convert()
		if results["boolean"] is True:
			entities = e

		return entities

	def try_english_name(self,ls_entities):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setReturnFormat(JSON)
		
		# Lista de (entidad, texto desambiguante)
		entities = []
		for e,dep_p in ls_entities:
			e = e.strip()
			e = e.replace(' ','_')
			e = str(e[0].upper() + e[1:])

			query = '''	ASK {{ dbr:{}   ?p    ?o .}}'''.format(e)

			sparql.setQuery(query)	
			results = sparql.query().convert()
			if results["boolean"] is True:
				entities.append(e)

		return entities

	# -------------------------------------------------------------
	# --GET SIMPLE ANSWERS WORKFLOW -------------------------------
	# -------------------------------------------------------------
	def default_ans(self, entity,answertype):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setReturnFormat(JSON)
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

		sparql.setQuery(query)			
		results = sparql.query().convert()
		for result in results["results"]["bindings"]:
			answers.append(result["result"]["value"])

		if len(answers) == 0:
			query = '''
				select distinct ?result 
				where {{
					dbr:{} dbp:{} ?result
				}}
				'''.format(entity,properti)

			sparql.setQuery(query)
			results = sparql.query().convert()
			for result in results["results"]["bindings"]:
				answers.append(result["result"]["value"])	

		return set(answers)

	def get_english_ans_reverse(self, entity, properti):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setReturnFormat(JSON)
		answers = []
		query = '''
				select distinct ?result, ?resource
				where {{

				<http://dbpedia.org/resource/{}> dbo:wikiPageDisambiguates* ?resource.					
				?result {}:{} ?resource

				}}
				'''.format(entity,"dbo",properti)

		sparql.setQuery(query)			
		results = sparql.query().convert()
		for result in results["results"]["bindings"]:
			answers.append(result["result"]["value"])

		return set(answers)

	def get_english_ans(self, entity, properti, dism=""):
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setReturnFormat(JSON)
		answers = []

		if not dism == "":
			query = '''
			select distinct ?result ?abstract
			where {{

			<http://dbpedia.org/resource/{}> dbo:wikiPageDisambiguates* ?resource.
			?resource dbo:wikiPageRedirects* ?redirect.					
			?redirect dbo:{} ?result.
			?redirect dbo:abstract ?abstract.
			FILTER langMatches(lang(?abstract),'es')

			}}'''.format(entity,properti)
		else:
			if "disambiguation" in entity:
				query = '''
						SELECT ?result WHERE {{
						<http://dbpedia.org/resource/{}> dbo:wikiPageDisambiguates ?resource.
						?resource dbo:{} ?result
						}}'''.format(entity,properti)
			else:
				query = '''
						select distinct ?result 
						where {{
							<http://dbpedia.org/resource/{}> dbo:wikiPageDisambiguates* ?resource.
							?resource dbo:{} ?result
						}}
						'''.format(entity,properti)

		sparql.setQuery(query)			
		results = sparql.query().convert()
		for result in results["results"]["bindings"]:
			answers.append(result["result"]["value"])

		return set(answers)



	# -----------------------------------------------------------------------
	# ---------------------- PREGUNTAS BOOLEAN ------------------------------
	# -----------------------------------------------------------------------

	def answerBoolean(self,q,q_keys):

		
		pr_entity_es = ""
		sn_entity_es = ""
		answers = False
		q = cleanQuestion(q)

		#Named entity (entity,dep_parse)
		named_entities,keys_restantes = self.get_named_entities(q_keys)
		entities, amb_entities, english_get = self.check_entities_espanol(named_entities)

		entities_total = entities+amb_entities
		if len(entities_total) == 1:
			pr_entity_es = entities_total[0]
			if english_get:
				pr_entity_en = pr_entity_es
			else:
				pr_entity_en = self.get_english_dbpedia(pr_entity_es)

			# si hay una sola entidad tenemos 3 tipos posibles
			# - Entity tiene propiedad
			# - Entity tiene tipos
			# - Existe entity De tal Forma

			bool_key, properti = self.boolean_key_one_entity(q)

			if bool_key == "type":
				answers = self.get_type_answer(pr_entity_es, properti)
			elif bool_key == "exist":
				answers = self.get_exist_answer(pr_entity_es, properti)
			else:
				properti = self.get_question_property(keys_restantes)
				answers = self.get_properti_answer(pr_entity_en,properti[0])
				print(properti[0])


		elif len(entities_total) == 2:

			print('{:18} {}'.format('INIT ENTITIES: ','|'.join([x for (x,y) in named_entities])))
			print('{:18} {}'.format('Found ENTITIES: ','|'.join([x for x in entities])))
			print('{:18} {}'.format('Found AMB ENTITIES: ','|'.join([x+","+y for (x,y) in amb_entities])))



			props, st_filter = self.two_entities_prop_filter(q,keys_restantes)
			if type(entities_total[0]) is tuple:
				pr_entity_es = entities_total[0][0]
			else:
				pr_entity_es = entities_total[0]

			if type(entities_total[1]) is tuple:
				sn_entity_es = entities_total[1][0]
			else:
				sn_entity_es = entities_total[1]

			pr_entity_en = self.get_english_dbpedia(pr_entity_es)
			sn_entity_en = self.get_english_dbpedia(sn_entity_es)
			if sn_entity_en is None:
				sn_entity_en = entities_total[1]
			answers = self.two_entities_answer(pr_entity_en,sn_entity_en,props[0],st_filter)
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

	def two_entities_answer(self,pr_entity,sn_entity,properti,st_filter):

		if st_filter == "same":
			query ='''
				ASK 
				WHERE {{
				<http://dbpedia.org/resource/{}> dbo:{} ?result .
				<http://dbpedia.org/resource/{}> dbo:{} ?result .
				}}
				'''.format(pr_entity,properti,sn_entity,properti)
		elif not st_filter == "":
			query ='''
				ASK 
				WHERE {{
				<http://dbpedia.org/resource/{}> dbo:{} ?x .
				<http://dbpedia.org/resource/{}> dbo:{} ?y . {}
				}}
				'''.format(pr_entity,properti,sn_entity,properti,st_filter)
		else:
			bind = '''ASK 
				WHERE {{
				<http://dbpedia.org/resource/{}> dbo:{} ?result. FILTER (BOUND(?result))
				}}'''.format(pr_entity,properti)
			sparql = self.sparqlEn
			sparql.setQuery(bind)			
			results = sparql.query().convert()

			if results["boolean"]:
				query ='''
					ASK 
					WHERE {{
					<http://dbpedia.org/resource/{}> dbo:{} <http://dbpedia.org/resource/{}> .
					}}
					'''.format(pr_entity,properti,sn_entity)
			else:
				query ='''
					ASK 
					WHERE {{
					<http://dbpedia.org/resource/{}> dbo:{} <http://dbpedia.org/resource/{}> .
					}}
					'''.format(sn_entity,properti,pr_entity)

		print (query)
		sparql = self.sparqlEn
		sparql.setQuery(query)			
		results = sparql.query().convert()

		return results["boolean"]
	# ------------------------------------------------------------------------
	# ---------------------- RESPONDER PREGUNTAS -----------------------------
	# ------------------------------------------------------------------------

	def answer_question(self, q, q_keys):

		print ('---------------------------------------------------------------')
		
		st_property = "not found"
		en_entity = "not found"
		entidad_elegida = ""
		answers = []
		answer_type = self.get_answer_type(q)
		
		print('{:18} {}'.format('QUESTION: ',q))		
		print('{:18} {}'.format('ANSWER TYPE: ',answer_type))
		
		if answer_type == "boolean":
			return self.answerBoolean(q,q_keys)

		temp_entities, keys_restantes = self.get_named_entities(q_keys)
		if len(temp_entities) > 1 and not answer_type == "boolean":
			print ("System not allow complex questios")
			return []


		entities, amb_entities,boolDirectEnglish = self.check_entities_espanol(temp_entities)		

		print('{:18} {}'.format('INIT ENTITIES: ','|'.join([x for (x,y) in temp_entities])))
		print('{:18} {}'.format('Found ENTITIES: ','|'.join([x for x in entities])))
		print('{:18} {}'.format('Found AMB ENTITIES: ','|'.join([x+","+y for (x,y) in amb_entities])))

		# Elegimos la entidad

		#import pdb; pdb.set_trace()
		dis_text = ""
		if len(entities+amb_entities) == 0:
				return []
		else:
			if len(entities) == 1:
				entidad_elegida = entities[0]
			else:
				entidad_elegida = amb_entities[0][0]
				dis_text = amb_entities[0][1]

		if boolDirectEnglish is True:
			en_entity = entidad_elegida
		else:
			en_entity = self.get_english_dbpedia(entidad_elegida)


		# -----------------------------------------
			
		keyAggregation = self.check_aggregation(answer_type,cleanQuestion(q))


		print('Entity choose:' , entidad_elegida)
		print('English entity :' , en_entity)

		list_properties = self.get_question_property(keys_restantes)
		for st_property in list_properties:
			print('Question property:' , st_property)

			if keyAggregation == "count":
				ans_temp = self.get_aggregation_count(en_entity,st_property)
				if not len(ans_temp) == 0:
					answers.append(ans_temp)
			if keyAggregation == "max":
				print ()
			


			ans_temp = self.get_english_ans(en_entity, st_property,dis_text)
			if not len(ans_temp) == 0:
				answers.append(ans_temp)



		if len(answers) == 0 and answer_type == "date":
			ans_temp = self.default_ans(en_entity,answer_type)
			if not len(ans_temp) == 0:
				answers.append(ans_temp)
		if len(answers) == 0 and answer_type == "resource":
			ans_temp = self.get_english_ans_reverse(en_entity,list_properties[0])
			if not len(ans_temp) == 0:
				answers.append(ans_temp)

		print('---------------------------------------------------------------')
		return answers