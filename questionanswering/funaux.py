# -*- coding: utf-8 -*-
#!/usr/bin/python
import unicodedata
from nltk.tokenize import word_tokenize

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
		dbo = st_query[1]
		if dbo[0] =="<":
			dbo = (dbo.split("/")[-1])[:-1]
		else:
			dbo = dbo.split(":")[1]

	return dbo

def getFirstTag(listTuple):

	# par (word, tag)
	return listTuple[0][1]

def getSecondTag(listTuple):

	# par (word, tag)
	return listTuple[1][1]


