# -*- coding: utf-8 -*-
#!/usr/bin/python
import unicodedata
from nltk.tokenize import word_tokenize

def cleanQuestion(question):

	# Eliminamos acentos
	question = unicodedata.normalize('NFKD', question).encode('ASCII', 'ignore')

	# Eliminamos signos de pregunta
	if question.startswith('¿'):
		question = question[1:]
	if question[len(question) - 1] == '?':
		question = question[:-1]

	# Volvemos a minusculas
	listaPalabras = word_tokenize(question)
	question = [word.lower() for word in listaPalabras]

	return ' '.join(question)

def cleanKeywords(st_keywords):
	st_keywords = unicodedata.normalize('NFKD', st_keywords).encode('ASCII', 'ignore')
	st_keywords = st_keywords.replace(',','')

def parseQuery(st_query):

	st_query = st_query[s.find("{")+1:s.find("}")]
	st_query = st_query.replace('.','')
	st_query = st_query.split()

	if len(st_query) == 3:
		dbo = st_query[1]
		if dbo[0] =="<":
			dbo = (dbo.split("/")[-1])[:-1]
		else:
			dbo = dbo.split(":")[1]

	return dbo


