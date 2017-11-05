from SPARQLWrapper import SPARQLWrapper, JSON
from questionanswering.funaux import *

from sklearn.linear_model import LogisticRegressionCV

from sklearn.naive_bayes import BernoulliNB

from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline
from sklearn import tree
import numpy as np
np.set_printoptions(threshold=np.inf)

class PropertyExtractor:
	# -------------------------------------------------------------
	# --GET PROPERTY ----------------------------------------------
	# -------------------------------------------------------------

	def __init__(self,nlp):
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)
		self.nlp_api = nlp

	def train(self,train_prop_x,train_prop_y,propCorpus):
		self.pipeline = self.init_pipeline(train_prop_x,train_prop_y,propCorpus)

	def only_noun_verb(self,st_keys):
		st_result = st_keys
		tag_word = self.nlp_api(st_keys)
		tag_word = [(word.text,word.tag_) for word in tag_word]
		for w,t in tag_word:
			if "VERB" in t:
				continue
			if "NOUN" in t:
				continue
			if "ADJ" in t:
				continue
			st_result = st_result.replace(w,' ')

		st_result = st_result.split()
		return " ".join(st_result)


	def generate_train_by_entity(self, query,st_keywords):

		temp_prop_x = []
		temp_prop_y = []
		st_dbo = parseQuery(query)
		if st_dbo == "":
			return [],[]

		st_ent = getEntity(query)
		if st_ent == "":
			return [],[]
		
		st_keywords = removeStopWords(st_keywords)
		st_keywords = delete_tildes(st_keywords)

		keys= [x.strip() for x in st_keywords.split(',')]
		keys_result= [x.strip() for x in st_keywords.split(',')]
		for k in keys:
			tag_word = self.nlp_api(k)
			tag_word = [(word.text,word.tag_) for word in tag_word]
			for w,t in tag_word:
				if "PROPN" in t:
					keys_result.remove(k)
					break

		st_keywords = " ".join(keys_result)
		st_keywords = self.only_noun_verb(st_keywords)
		#x = {'eng':st_dbo, 'esp':st_keywords}
		key_st = st_dbo+","+st_keywords
		x = {key_st:True}
		y = 1

		temp_prop_x.append(x)
		temp_prop_y.append(y)

		sparql = self.sparqlEn
		query = '''
		SELECT distinct ?p WHERE {{
			<http://dbpedia.org/resource/{}> ?p ?v.

		}}
		'''.format(st_ent)

		sparql.setQuery(query)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			value = result["p"]["value"]

			if "wiki" in value or "abstract" in value or "thumbnail" in value:
				continue
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				if not prop == st_dbo: 
					#x = {'eng':prop, 'esp':st_keywords}
					key_st = prop+","+st_keywords
					x = {key_st:True}
					y = 0
					temp_prop_x.append(x)
					temp_prop_y.append(y)


		return temp_prop_x, temp_prop_y

	def init_pipeline(self,x,y,extraCorpus):
		esp_stopwords = stopwords.words('spanish')
		vectorizer = DictVectorizer()


		classifier = tree.DecisionTreeClassifier()
		pipeline = Pipeline([("vec", vectorizer), ("clas", classifier)])
		x = x + extraCorpus[0]
		y = y + extraCorpus[1]
		pipeline.fit(x,y)
		print("Features")

		return pipeline

	def get_question_property_type(self,st_type,keys):
		st_keys = " ".join(keys)
		
		st_keys = removeStopWords(st_keys)
		st_keys = delete_tildes(st_keys)
		st_keys = self.only_noun_verb(st_keys)
		sparql = self.sparqlEn
		query = '''
		SELECT distinct ?p WHERE {{
			?instance a <http://dbpedia.org/ontology/{}> . 
         	?instance ?p ?obj .
		}}
		'''.format(st_type)
		properti = ""
		sparql.setQuery(query)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			value = result["p"]["value"]

			if "wiki" in value or "abstract" in value or "thumbnail" in value:
				continue
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				test = {}
				for k in st_keys.split():
					test[prop+","+k] = True
				test[prop+","+st_keys] = True

				temp = self.pipeline.predict([test])
				if temp[0] == 1:
					print(test)	
					properti = prop		

		return properti

	def get_question_property_type_fast(self,st_type,keys):
		st_keys = " ".join(keys)
		
		st_keys = removeStopWords(st_keys)
		st_keys = delete_tildes(st_keys)
		st_keys = self.only_noun_verb(st_keys)
		sparql = self.sparqlEn
		query = '''
		SELECT distinct ?p WHERE {{
			?p rdfs:domain ?class . 
  			dbo:{} rdfs:subClassOf+ ?class.
		}}
		'''.format(st_type)
		properti = ""
		sparql.setQuery(query)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			value = result["p"]["value"]

			if "wiki" in value or "abstract" in value or "thumbnail" in value:
				continue
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				test = {}
				for k in st_keys.split():
					test[prop+","+k] = True
				test[prop+","+st_keys] = True

				temp = self.pipeline.predict([test])
				if temp[0] == 1:
					print(test)	
					properti = prop		

		return properti

	def get_question_property(self,entity,keys):
		st_keys = " ".join(keys)
		
		st_keys = removeStopWords(st_keys)
		st_keys = self.only_noun_verb(st_keys)
		st_keys = delete_tildes(st_keys)
		print(st_keys)
		sparql = self.sparqlEn
		query = '''
		SELECT distinct ?p WHERE {{
			<http://dbpedia.org/resource/{}> dbo:wikiPageDisambiguates* ?uri.
			?uri ?p ?v.
		}}
		'''.format(entity)
		properti = ""
		sparql.setQuery(query)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			value = result["p"]["value"]

			if "wiki" in value or "abstract" in value or "thumbnail" in value:
				continue
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				key_st = prop+","+st_keys

				test = {key_st:True}
				temp = self.pipeline.predict([test])
				if temp[0] == 1:
					print(test)	
					properti = prop		

		return properti

	def get_question_property_rev(self,entity,keys):
		st_keys = " ".join(keys)
		
		st_keys = removeStopWords(st_keys)
		st_keys = delete_tildes(st_keys)
		st_keys = self.only_noun_verb(st_keys)
		sparql = self.sparqlEn
		query = '''
		SELECT distinct ?p WHERE {{
			?uri ?p <http://dbpedia.org/resource/{}>.
		}}
		'''.format(entity)
		properti = ""
		sparql.setQuery(query)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			value = result["p"]["value"]

			if "wiki" in value or "abstract" in value or "thumbnail" in value:
				continue
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				key_st = prop+","+st_keys

				test = {key_st:True}
				temp = self.pipeline.predict([test])

				if temp[0] == 1:
					print(test)
					properti = prop
		

		return properti