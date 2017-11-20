from SPARQLWrapper import SPARQLWrapper, JSON
from questionanswering.funaux import *
from nltk import Tree
import nltk
import operator

class EntityExtractor:
	# -------------------------------------------------------------
	# --ENTITY WORKFLOW -------------------------------------------
	# -------------------------------------------------------------

	def __init__(self,nlp):
		self.nlp_api = nlp
		self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
		self.sparql.setReturnFormat(JSON)
		self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
		self.sparqlEn.setReturnFormat(JSON)

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


	def getNounGroups(self,key):
		conectores = [
			'ADP__AdpType=Prep',
			'DET__Definite=Def|Gender=Masc|Number=Sing|PronType=Art',
			'ADP__AdpType=Preppron|Gender=Masc|Number=Sing',
			'CCONJ___',
			'DET__Definite=Def|Gender=Fem|Number=Sing|PronType=Art',
			'DET__Definite=Def|Gender=Masc|Number=Plur|PronType=Art',
			'DET__Definite=Def|Gender=Fem|Number=Plur|PronType=Art'
			]
		if len(key) == 0:
			return []

		tag_word = self.nlp_api(key)
		tag_word = [(word.text,word.tag_) for word in tag_word]
		
		nouns = []
		g = []
		hasProp = False

		

		for w,t in tag_word:

			if "NOUN" in t:
				g.append(w)
			elif "PROPN" in t:
				g.append(w)
				hasProp = True
			elif t in conectores:
				g.append(w)
			else:
				if not len(g) == 0:

					nouns.append((" ".join(g),hasProp))
					hasProp = False
					g = []
		if not len(g)== 0:
			nouns.append((" ".join(g),hasProp))

		st_ket_f = key.split()[1:]
		if not len(st_ket_f) == 0:
			nouns += self.getNounGroups(" ".join(st_ket_f))
		st_ket_f = key.split()[:-1]
		if not len(st_ket_f) == 0:
			nouns += self.getNounGroups(" ".join(st_ket_f))

		nouns = list(set(nouns))
		return nouns

	def get_entities(self, keywords,answer_type):

		found_entities = []
		keys= [x.strip() for x in keywords.split(',')]
		keys_restantes= [x.strip() for x in keywords.split(',')]
		keyid = -1
		for key in keys:

			keyid += 1
			noum_group = self.getNounGroups(key)
			
			for group,hasProp in noum_group:
				dbpedia_group = prepareGroup(group)
				if hasProp == False and lenEntity(dbpedia_group) == 1:
					continue
				if self.check_ent_dbES(dbpedia_group):
					es_ent = dbpedia_group
					en_ent = self.get_english_dbpedia(dbpedia_group)
					context = key.replace(group,' ')
					found_entities.append((es_ent,en_ent,context,lenEntity(es_ent),hasProp,keyid))
				else:
					if self.check_ent_dbEN(dbpedia_group):
						es_ent = dbpedia_group
						en_ent = dbpedia_group
						context = key.replace(group,' ')
						found_entities.append((es_ent,en_ent,context,lenEntity(es_ent),hasProp,keyid))

		found_entities = sorted(found_entities, key=operator.itemgetter(3),reverse=True)
		result_entities = []

		if len(found_entities) == 0:
			return [],keys_restantes

		if not answer_type == "boolean":
			for enti in found_entities:
				if enti[4]:
					result_entities.append((enti[0],enti[1],enti[2]))
					keys_restantes.pop(enti[5])
					break;
			if len(result_entities) == 0:
				result_entities.append((found_entities[0][0],found_entities[0][1],found_entities[0][2]))
				keys_restantes.pop(found_entities[0][5])
		else:
			bool_ent = []
			chose = 0
			first_entity = ""
			keys_restantes_copy = list(keys_restantes)
			for enti in found_entities:
				if chose == 2:
					break

				if enti[4] and not enti[0] in first_entity or first_entity == "":
					chose += 1

					result_entities.append((enti[0],enti[1],enti[2]))
					first_entity = enti[0]
					elem = keys_restantes_copy[enti[5]]
					keys_restantes.remove(elem)
			if len(result_entities) == 0:
				result_entities.append((found_entities[0][0],found_entities[0][1],found_entities[0][2]))
				keys_restantes.pop(found_entities[0][5])

		return result_entities, keys_restantes


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