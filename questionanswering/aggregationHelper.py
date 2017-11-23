from SPARQLWrapper import SPARQLWrapper, JSON
import re, csv
from questionanswering.funaux import *

typesPATH = r'Data/types'



class AggregationHelper:

	# -------------------------------------------------------------
	# -- AGGREGATION ----------------------------------------------
	# -------------------------------------------------------------


	def __init__(self,nlp):
		self.nlp_api = nlp
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)
		self.default_comparatives = {
		'grande': ['capacity','areaTotal'],
		'chico': ['capacity','areaTotal'],
		'mayor':['birthDate'],
		'menor':['birthDate'],
		'joven': ['birthDate'],
		'alto':['height']
		}

	def get_default(self,sub_prop):

		return self.default_comparatives.get(sub_prop,[])

	def order_rules(self,st_question):
		#Agarra lo mas grande
		complex_cont = ["NOUN","ADJ"]
		tag_word = self.nlp_api(st_question)
		tag_word = [(word.text,word.tag_) for word in tag_word]

		for i,(w,t) in enumerate(tag_word):
			if w == "mayor":
				for a in complex_cont:
					if a in tag_word[i+1][1]:
						return True, "desc_mayor"
						break
				return True,"asc_mayor"
			if w == "menor":
				for a in complex_cont:
					if a in tag_word[i+1][1]:
						return True, "asc_menor"
						break
				return True,"desc_menor"



		desc_rules = ['mas joven','mas menor','mas grande','grande','ultima','mas alto','mas alta']
		for rule in desc_rules:
			if rule in st_question:
				return True,"desc_"+rule

		asc_rules = ['chico','mas chico']
		for rule in asc_rules:
			if rule in st_question:
				return True,"asc_"+rule


		return False,""





	def check_aggregation(self,answer_type,st_question,st_keys):
		st_question = delete_tildes(st_question)
		st_question = cleanQuestion(st_question)

		countBool = bool(re.search('cuant(o|a)s', st_question))
		order_rule = self.order_rules(st_question)



		if countBool and answer_type == "number":
			result = "count"
		elif order_rule[0]:
			result = order_rule[1]
		else:
			result = "none"

		return result

	def get_sub_property(self,key,q_keys):
		prop = ""

		q_keys= ",".join(q_keys)

		key_split = key.split('_')
		rule = key_split[1]

		q_keys = q_keys.replace(rule,' ')
		q_keys = q_keys.strip()
		q_keys = re.sub(r'\s+',' ',q_keys); 
		

		

		if q_keys[-1] == ',':
			q_keys = q_keys[:-1]
		if q_keys[0] == ',':
			q_keys = q_keys[1:]
		q_keys = q_keys.split(',')

		for i in range(0,len(q_keys)):
			q_keys[i] = q_keys[i].strip()

		
		if rule.split()[0] == "mas":
			prop = rule.split()[1]
		else:
			prop = rule

		return q_keys,prop

	def get_type(self,q_keys):
		r_selected_uri = ""
		r_selected_type= ""

		for st_type in q_keys:
			st_type = st_type.strip()
			st_type = str(st_type[0].lower() + st_type[1:])
			st_type = delete_tildes(st_type)
			st_type = removeStopWords(st_type)
			selected_uri = ""

			with open(typesPATH, 'r') as f:
				reader = csv.reader(f)
				tipos = map(tuple, reader)
				for (uri,tipo) in tipos:
					if st_type in tipo:
						selected_uri = uri.split('/')[4]
						r_selected_uri = selected_uri
						r_selected_type = st_type
						break
		if not r_selected_type == "":
			q_keys.remove(r_selected_type)
		return r_selected_uri,q_keys



	def get_subprop_answer(self, entity, properti,subproperti,order):
		sparql = self.sparqlEn
		answers = []



		if "desc" in order:
			st_order = "ORDER BY DESC(?n) OFFSET 0 LIMIT 1"
		else:
			st_order = "ORDER BY ASC(?n) OFFSET 0 LIMIT 1"

		query = '''
				SELECT DISTINCT ?result
				where {{
					<http://dbpedia.org/resource/{}>  dbo:{} ?result.
					?result dbo:{} ?n
				}} {}
				'''.format(entity,properti,subproperti,st_order)
		print(query)
		answers = resolveQuery(sparql,query)
		return set(answers)

	def get_aggregation_order_type_place(self, st_type, properti,order,place):
		sparql = self.sparqlEn
		answers = []



		if "desc" in order:
			st_order = "ORDER BY DESC(?n) OFFSET 0 LIMIT 1"
		else:
			st_order = "ORDER BY ASC(?n) OFFSET 0 LIMIT 1"

		query = '''
				SELECT DISTINCT ?result 
				WHERE {{
				?result a <http://dbpedia.org/ontology/{}> . 
				?result <http://dbpedia.org/ontology/location> <http://dbpedia.org/resource/{}> . 
				?result <http://dbpedia.org/ontology/{}> ?n . 
				}} {}

				'''.format(st_type,place,properti,st_order)
		print(query)
		answers = resolveQuery(sparql,query)
		if len(answers) == 0:
			query = '''
					SELECT DISTINCT ?result 
					WHERE {{ 
					?result a <http://dbpedia.org/ontology/{}> . 
					?result <http://dbpedia.org/ontology/country> <http://dbpedia.org/resource/{}> . 
					?result <http://dbpedia.org/ontology/{}> ?n . 
					}} {}

					'''.format(st_type,place,properti,st_order)
			print(query)
			answers = resolveQuery(sparql,query)
		return set(answers)

	def get_aggregation_order_type(self, st_type, properti,order):
		sparql = self.sparqlEn
		answers = []



		if "desc" in order:
			st_order = "ORDER BY DESC(?n) OFFSET 0 LIMIT 1"
		else:
			st_order = "ORDER BY ASC(?n) OFFSET 0 LIMIT 1"

		query = '''
				SELECT DISTINCT ?result
				where {{
					?result a dbo:{}.
					?result dbo:{} ?n
				}} {}
				'''.format(st_type,properti,st_order)
		print(query)
		answers = resolveQuery(sparql,query)
		return set(answers)

	def check_entity(self, entity, keys, keys_restantes):
		doc = self.nlp_api(entity[0].replace('_',' '))
		rs_entity = ""
		rs_keys = keys_restantes
		for ent in doc.ents:
			if ent.label_ == "GPE" or ent.label_ == "LOC":
				rs_entity = entity[1]
				keys = keys.replace(entity[0].replace('_',' '), ' ')
				keys = keys.strip()
				keys = re.sub(r'\s+',' ',keys); 
				rs_keys = keys.split(',')
		return rs_entity, rs_keys

	def get_aggregation_count(self, entity, properti):
		sparql = self.sparqlEn
		answers = []
		query = '''
				SELECT (COUNT(DISTINCT ?uri) as ?result)  
				where {{
					dbr:{} dbo:{} ?uri
				}}
				'''.format(entity,properti)
		answers = resolveQuery(sparql,query)
		return set(answers)