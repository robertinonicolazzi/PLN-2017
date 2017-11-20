

from SPARQLWrapper import SPARQLWrapper, JSON
import sys

import csv


def generate(st_id,st_type,agg,q,q_keys,st_query):
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	sparql.setReturnFormat(JSON)
	q_id = st_id
	anwer_type = st_type
	aggregation = agg
	question = "¿"+q+"?"
	keywords = q_keys

	query = st_query

	template = '''{{
		"id": "{}",
		"answertype": "{}",
		"aggregation": {},
		"onlydbo": true,
		"hybrid": false,
		"question": [
			{{
				"language": "es",
				"string": "{}",
				"keywords": "{}"
			}}
		],
		"query": {{
			"sparql": "{}"
		}},
		'''.format(q_id,anwer_type,aggregation,question,keywords,query)
	sparql.setQuery(query)

	st_ans = str(sparql.query().convert()).replace("\'","\"")
	st_ans = st_ans.replace("True","true")
	st_ans = st_ans.replace("False","false")
	template_ans = '''
		"answers": [{}]
	}},'''.format(st_ans)

	final = template + template_ans

	out = open('Corpus/SimpleDataCustom.json','a')
	out.write(final)
	out.close()

id_n = 3000
out = open('Corpus/SimpleDataCustom.json',"w")
out.write('''{
	"dataset": {
		"id": "qald-7-train-multilingual"
	},
	"questions": [''')
out.close()

with open(r'/media/robertnn/DatosLinux/PLN-2017/questionanswering/scripts/testMap.csv', 'r') as f:
	reader = csv.reader(f)
	tipos = map(tuple, reader)
	for (st_type,agg,q,q_keys,st_query) in tipos:
		generate(str(id_n),st_type,agg,q,q_keys,st_query)
		id_n += 1
out = open('Corpus/SimpleDataCustom.json','a')
out.write(']}')
out.close()