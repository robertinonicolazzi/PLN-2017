# -*- coding: utf-8 -*-
#!/usr/bin/python
import unicodedata
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def removeStopWords(keys):
	keys_list = keys.split()
	important_words = [word for word in keys_list if word not in set(stopwords.words('spanish'))]

	return " ".join(important_words)


def lenEntity(entity):
	entity = entity.replace('_',' ')
	entity = entity.split()

	return len(entity)

def prepareGroup(group):
	group = group.strip()
	group = group.replace(' ','_')
	group = str(group[0].upper() + group[1:])
	return group

def resolveQuery(sparql, query):
	answers = []
	sparql.setQuery(query)
	results = sparql.query().convert()
	for result in results["results"]["bindings"]:
		answers.append(result["result"]["value"])
		
	return answers

def delete_tildes(content):
	new_list = []
	for c in unicodedata.normalize('NFD', content):
		if unicodedata.category(c) != 'Mn':
			new_list += [c]

	return "".join(new_list)

def cleanQuestion(question):

	question = question.replace('¿','')
	question = question.replace('?','')
	question = question.strip()
	question = str(question[0].lower() + question[1:])

	return question

def cleanKeywords(st_keywords):
	st_keywords = st_keywords.replace(',','')
	return st_keywords

def parseQuery(st_query):

	st_query = st_query[st_query.find("{")+1:st_query.find("}")]
	st_query = st_query.replace('.','')
	st_query = st_query.split()
	dbo = ""
	if len(st_query) == 3:
		try:
			dbo = st_query[1]
			if dbo[0] =="<":
				dbo = (dbo.split("/")[-1])[:-1]
			else:
				dbo = dbo.split(":")[1]
		except:
			dbo = ""
			print (st_query, "Exception")

	return dbo

def getEntity(st_query):

	st_query = st_query[st_query.find("{")+1:st_query.find("}")]
	st_query = st_query.replace('.','')
	st_query = st_query.split()
	ent = ""
	if len(st_query) == 3:
		ent = st_query[0]
		if ent[0] =="?":
			ent = st_query[2]

		if ent[0] =="<":
			ent = (ent.split("/")[-1])[:-1]
		elif ent[0] == "r" or ent[0] == "d":
			ent = ent.split(":")[1]
		else:
			return ""

	return ent

def getFirstTag(listTuple):

	# par (word, tag)
	return listTuple[0][1]

def getSecondTag(listTuple):

	# par (word, tag)
	return listTuple[1][1]


