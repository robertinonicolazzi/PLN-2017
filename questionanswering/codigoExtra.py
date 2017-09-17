def getPassage(self,question, question_keywords, answertype):

		string_question = question.replace('?',' ?')
		string_question = question.replace('¿','¿ ')
		string_list = word_tokenize(string_question)
		tagged_sent = self.model_POS.tag(string_list)
		print (tagged_sent)

		tagged = self.model_POS.tag([ word.strip() for word in question_keywords.split(',')])
		tagged_keywords = list(zip([ word.strip() for word in question_keywords.split(',')],tagged))

		print (tagged_keywords)

		sustPropios = []
		sustComunes = []
		verbos = []

		propiedad = []
		subPropiedad = []
		for w,t in tagged_keywords:
			w = w.strip()
			w.replace(' ','_')
			if t == "np00000":
				sustPropios.append(w)
			if t.startswith("n") and not t == "np00000":
				sustComunes.append(w)
			if t.startswith("v"):
				verbos.append(w)

		import pdb; pdb.set_trace()
		# Veamos si empieza con preposición, el primer sustantivo es la subpropiedad
		# del verbo que determina la propiedad padre
		empiezaConPreposicion = (tagged_sent[1] == "sp000")
		if empiezaConPreposicion:
			subPropiedad.append(sustComunes[0])
			sustComunes.pop(0)

		if answertype == "date":

			for key in mapeoDate.keys():
				bind = mapeoDate.get(key)
				for verb in verbos:
					if verb in bind:
						propiedad.append(key)

			if not len(sustPropios) == 0:
				resource = sustPropios[0]
			else:
				resource = sustComunes[0]

			if not len(acciones) == 0:
				pregunta = propiedad[0]
			else:
				pregunta = "fecha"


		
		return answertype, ','.join(sustPropios) + ','+ ','.join(sustCo



	def generarQuery(self,answertype, entidades, propiedades):
		dbo = "PREFIX dbo: <http://dbpedia.org/ontology/>\n"
		res = "PREFIX res: <http://dbpedia.org/resource/>\n"

		resEs = "PREFIX res: <http://es.dbpedia.org/resource/>\n"
		propEs = "PREFIX dpo: <http://es.dbpedia.org/property/>\n"

		resElegido = ""
		dboElegido = ""

		resElegido = resEs
		dboElegido = propEs
		query = dboElegido + resElegido + select + where


		
		sparql = SPARQLWrapper("http://dbpedia.org/sparql")
		sparql.setQuery(query)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()
		where = "WHERE {\n        res:"+entPropias[0]+" dbo:"+pregunta+" ?result .\n}"
		respuesta = ""
		for result in results["results"]["bindings"]:
			print("RESPUESTA: ",result["result"]["value"])
			print()
			respuesta = result["result"]["value"]
			break


	def extract_posibly_property(self, keywords):
		keywords = keywords.split()

		result = []
		for k in keywords:
			k = k.split()
			if len(k) == 1:
				tag = self.model_POS.tag(k)
				if tag.startswith('v') or tag.startswith('n'):
					result.append(k)

		return result