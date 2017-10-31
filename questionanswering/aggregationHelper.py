from SPARQLWrapper import SPARQLWrapper, JSON
import re
from questionanswering.funaux import *
import csv

typesPATH = r'/media/robertnn/DatosLinux/PLN-2017/questionanswering/Data/types'



class AggregationHelper:

	# -------------------------------------------------------------
	# -- AGGREGATION ----------------------------------------------
	# -------------------------------------------------------------


	def __init__(self):
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)
		self.default_comparatives = ['areaTotal','birthDate','height']


	def proc_desc_rules(self,st_question):
		desc_rules = ['mas mayor','mas grande','mayor','grande','ultima','mas alto','mas alta']

		for rule in desc_rules:
			if rule in st_question:
				return True,rule

		return False,""

	def proc_asc_rules(self,st_question):
		desc_rules = ['mas menor','mas joven','menor','chico','mas chico']

		for rule in desc_rules:
			if rule in st_question:
				return True,rule

		return False,""

	def check_aggregation(self,answer_type,st_question,st_keys):
		st_question = delete_tildes(st_question)
		st_question = cleanQuestion(st_question)

		countBool = bool(re.search('cuant(o|a)s', st_question))
		desc_rule = self.proc_desc_rules(st_question)
		asc_rule = self.proc_asc_rules(st_question)


		if countBool and answer_type == "number":
			result = "count"
		elif desc_rule[0]:
			result = "desc"+"_"+desc_rule[1]
		elif asc_rule[0]:
			result = "asc"+"_"+asc_rule[1]
		else:
			result = "none"

		return result

	def clean_key_rule(self,key,q_keys):
		key_split = key.split('_')
		rule = key_split[1]

		q_keys = q_keys.replace(rule,' ')
		q_keys = q_keys.split()

		q_keys = " ".join(q_keys)
		return q_keys

	def get_type(self,q_keys):

		for st_type in q_keys.split(','):
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
						return selected_uri
						break
		return ""

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