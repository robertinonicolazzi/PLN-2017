from SPARQLWrapper import SPARQLWrapper, JSON
import re

class AggregationHelper:

	# -------------------------------------------------------------
	# -- AGGREGATION ----------------------------------------------
	# -------------------------------------------------------------

	def __init__(self):
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)


	def check_aggregation(self,answer_type,st_question):
		cuantoBool = bool(re.search('cu(a|á)nt(o|a)s', st_question))
		boolNumber = (answer_type == "number")
		result = "none"
		if cuantoBool and boolNumber:
			result = "count"

		return result

	def answer_aggregation(self,key,en_entity,st_property):
		answers = []
		if keyAggregation == "count":
			ans_temp = self.get_aggregation_count(en_entity,st_property)
			if not len(ans_temp) == 0:
				answers.append(ans_temp)
		if keyAggregation == "max":
			print ()

		return answers

	def get_aggregation_count(self, entity, properti):
		sparql = self.sparqlEn
		answers = []
		query = '''
				SELECT (COUNT(DISTINCT ?uri) as ?result)  
				where {{
					dbr:{} dbo:{} ?uri
				}}
				'''.format(entity,properti)

		resolveQuery(sparql,query)
		return set(answers)