import SPARQLWrapper
import questionanswering.funaux
import csv
import json


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


	def check_aggregation(self,answer_type,st_question):
		cuantoBool = bool(re.search('cu(a|á)nt(o|a)s', st_question))
		boolNumber = (answer_type == "number")
		result = "none"
		if cuantoBool and boolNumber:
			result = "count"

		return result

	def get_aggregation_count(self, entity, properti):
		sparql = self.sparqlEn
		answers = []
		query = '''
				SELECT (COUNT(DISTINCT ?uri) as ?result)  
				where {{
					dbr:{} dbo:{} ?uri
				}}
				'''.format(entity,properti)

		sparql.setQuery(query)			
		results = sparql.query().convert()
		for result in results["results"]["bindings"]:
			answers.append(result["result"]["value"])
		return set(answers)

class BooleanHelper:
	
	def __init__(self):
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)


	def boolean_key_one_entity(self,q_clean):

		q_clean = delete_tildes(q_clean)

		b_tipo = bool(re.search('es una ', q_clean))
		if "tipo" in q_clean:
			q_list = q_clean.split(" ")
			indextipo = q_list.index("tipo")

			return "type", q_list[indextipo+2]

		if "es una" in q_clean:
			q_list = q_clean.split(" ")
			indextipo = q_list.index("una")
			return "type", q_list[indextipo+1]
		
		if "existe" in q_clean or "hay algun" in q_clean or "hay" in q_clean:
			q_list = q_clean.split(" ")
			indextipo = q_list.index("algun")
			return "exist",q_list[indextipo+1]

		return "properti", "none"

	def get_exist_answer(self,entity, st_type):

		st_type = st_type.strip()
		st_type = str(st_type[0].lower() + st_type[1:])
		st_type = delete_tildes(st_type)
		selected_uri = ""
		entity = entity.replace("_"," ")
		with open(typesPATH, 'r') as f:
			reader = csv.reader(f)
			tipos = map(tuple, reader)
			for (uri,tipo) in tipos:
				if st_type in tipo:
					selected_uri = uri.split('/')[4]
					break		
		query ='''
		ASK 
		WHERE {{
		?uri rdf:type dbo:{} .
		?uri rdfs:label '{}'@es .
		}}
		'''.format(selected_uri,entity)

		sparql = self.sparqlEn
		sparql.setQuery(query)			
		results = sparql.query().convert()

		return results["boolean"]		

	def get_properti_answer(self,entity,properti):
		query ='''
		ASK 
		WHERE {{
		dbr:{} dbo:{} ?result .

		}}
		'''.format(entity,properti)

		sparql = self.sparqlEn
		sparql.setQuery(query)			
		results = sparql.query().convert()

		return results["boolean"]

	def get_type_answer(self,entity, st_type):

		query ='''
		PREFIX esdbr: <http://es.dbpedia.org/resource/> 
		SELECT ?abstract WHERE {{
		<http://es.dbpedia.org/resource/{}>    dbpedia-owl:wikiPageRedirects* ?resource .
				?resource dbpedia-owl:abstract ?abstract.
		FILTER langMatches(lang(?abstract),'es')

		}}
		'''.format(entity)

		sparql = self.sparql
		sparql.setQuery(query)			
		results = sparql.query().convert()

		bindings = results["results"]["bindings"]

		for result in bindings:
			abstract = result["abstract"]["value"]
			if st_type in abstract:
				return True

		return False