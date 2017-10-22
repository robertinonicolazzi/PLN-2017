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

	def ExtractPhrases(self, myTree, phrase):
	    """ 
	    Extract phrases from a parsed (chunked) tree
	    Phrase = tag for the string phrase (sub-tree) to extract
	    Returns: List of deep copies;  Recursive
	    """
	    myPhrases = []
	    if (myTree.label() == phrase):
	        myPhrases.append( myTree.copy(True) )
	    for child in myTree:
	        if (type(child) is nltk.Tree):
	            list_of_phrases = self.ExtractPhrases(child, phrase)
	            if (len(list_of_phrases) > 0):
	                myPhrases.extend(list_of_phrases)
	    return myPhrases


	def parseQuestion(self,q):

		st = self.nlp_api.parse(q)
		tree = Tree.fromstring(st)
		tree.draw()

	def getNounGroups(self,key):
		st = self.nlp_api.parse(key)
		tree = Tree.fromstring(st)
		tree.draw()
		phases = self.ExtractPhrases(tree,"grup.nom")

		nouns = []
		for p in phases:
			nouns.append(" ".join(p.leaves()))

		return nouns

	def get_entities(self, keywords,answer_type):

		found_entities = []
		keys= [x.strip() for x in keywords.split(',')]
		keys_restantes= [x.strip() for x in keywords.split(',')]
		keyid = -1
		for key in keys:
			keyid += 1
			noum_group = self.getNounGroups(key)
			
			for group in noum_group:
				tag_word = self.nlp_api.pos_tag(group)
				dbpedia_group = prepareGroup(group)

				hasProp = False
				for w,t in tag_word:
					if t == "np00000":
						hasProp = True
						break


				if not hasProp and lenEntity(dbpedia_group) == 1:
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
			for enti in found_entities:
				if enti[4]:
					result_entities.append((enti[0],enti[1]))
					break;

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