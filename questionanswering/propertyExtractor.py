from SPARQLWrapper import SPARQLWrapper, JSON
from questionanswering.funaux import *
from nltk.corpus import stopwords
from sklearn.linear_model import LogisticRegressionCV
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

	def train(self,train_prop_x,train_prop_y,propCorpus,tokenizer):
		self.pipeline = self.init_pipeline(train_prop_x,train_prop_y,propCorpus,tokenizer)

	def generate_train_by_entity(self, query,st_keywords):

		temp_prop_x = []
		temp_prop_y = []
		st_dbo = parseQuery(query)
		if st_dbo == "":
			return [],[]

		st_ent = getEntity(query)
		if st_ent == "":
			return [],[]
		

		st_keywords = delete_tildes(st_keywords)
		keys= [x.strip() for x in st_keywords.split(',')]
		keys_result= [x.strip() for x in st_keywords.split(',')]
		for k in keys:
			tag_word = self.nlp_api.pos_tag(k)
			for w,t in tag_word:
				if t == "np00000":
					keys_result.remove(k)
					break

		st_keywords = " ".join(keys_result)
		x = {'eng':st_dbo, 'esp':st_keywords}
		y = 1

		print(x)
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
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				if not prop == st_dbo: 
					x = {'eng':prop, 'esp':st_keywords}
					y = 0
					temp_prop_x.append(x)
					temp_prop_y.append(y)


		return temp_prop_x, temp_prop_y

	def init_pipeline(self,x,y,extraCorpus,tokenizer):
		esp_stopwords = stopwords.words('spanish')
		vectorizer = DictVectorizer()


		classifier = tree.DecisionTreeClassifier()
		pipeline = Pipeline([("vec", vectorizer), ("clas", classifier)])

		pipeline.fit(x,y)
		print("Features")

		return pipeline

	def removeStopWords(self,keys):
		keys_list = keys.split()
		important_words = filter(lambda x: x not in set(stopwords.words('spanish')), keys_list)
		return " ".join(important_words)



	def get_question_property(self,entity,keys):
		st_keys = " ".join(keys)
		st_keys = delete_tildes(st_keys)
		st_keys = self.removeStopWords(st_keys)
		sparql = self.sparqlEn
		query = '''
		SELECT distinct ?p WHERE {{
			<http://dbpedia.org/resource/{}> dbo:WikiPageDisambiguate* ?uri.
			?uri ?p ?v.
		}}
		'''.format(entity)
		properti = ""
		sparql.setQuery(query)
		results = sparql.query().convert()
		for result in results["results"]["bindings"]:
			value = result["p"]["value"]
			if "ontology" in value or "property" in value:
				prop = value.split('/')[4]
				
				temp = self.pipeline.predict([{'eng':prop, 'esp':st_keys}])
				if temp[0] == 1:
					print({'eng':prop, 'esp':st_keys})
					print (self.pipeline.predict_proba([{'eng':prop, 'esp':st_keys}]))					
					properti = prop
					print(properti)
				

		

		return properti