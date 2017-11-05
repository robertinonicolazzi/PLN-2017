

from SPARQLWrapper import SPARQLWrapper, JSON
import sys

def generate(st_id,st_type,agg,q,q_keys,st_query)
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	sparql.setReturnFormat(JSON)
	q_id = st_id
	anwer_type = st_type
	aggregation = agg
	question = q
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

	out = open('customTrain.json','a')
	out.write(final)
	out.close()