# -*- coding: utf-8 -*-
#!/usr/bin/python
import unicodedata
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pickle

def save_obj(obj, name ):
	with open('obj/'+ name + '.pkl', 'wb+') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def ft_translate(st_keywords,st_dbo_clean,n=0):
    temp_prop_x = []
    ls_dbo = re.split(r'([A-Z][a-z]*)', st_dbo_clean)

    if len(ls_dbo) == 1 and len(st_keywords.split()) == 1:
        ls_es_en = es_to_en(st_keywords)
        ls_en_es = en_to_es(st_dbo_clean)
        

        

        if len(ls_en_es) == 0 or len(ls_es_en) == 0:
            return [], []
        if not n==0:
            ls_en_es = ls_en_es[:n]
            ls_es_en = ls_es_en[:n]
        ls_comb = list(itertools.product(ls_es_en, ls_en_es))
        for en, es in ls_comb:
            es = delete_tildes(es)
            x = {'estoen':en, 'entoes':es, 'en=estoen':(st_dbo_clean == en), 'es=entoes':(st_keywords == es)}
            x.update({en: True,es: True})
            temp_prop_x.append(x)

    else:
        print("complex", st_dbo_clean, st_keywords)
        return [], []

    return temp_prop_x

def load_obj(name):
	with open('obj/' + name + '.pkl', 'rb') as f:
		return pickle.load(f)

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


