	def features_answer_type(self,st_question):
		feat = {}
		st_question = cleanQuestion(st_question)
		tag_word = self.nlp_api.pos_tag(st_question)

		
		feat["ask_cuanto"] = bool(re.search('cu(a|á)nt(o|a)(s|) ', st_question))
		feat["init_dame"] = (st_question.split(" ")[0] == 'dame')
		feat["ask_cuando"] = bool(re.search('cu(a|á)ndo ', st_question))
		feat["init_verb"]  = getFirstTag(tag_word).startswith('v')
		feat["init_verb2"]  = getFirstTag(tag_word).startswith('v')
		feat["art_sust"]   = (getFirstTag(tag_word) == 'da0000') and (getSecondTag(tag_word).startswith('n'))
		feat["art_sust2"]   = (getFirstTag(tag_word) == 'da0000') and (getSecondTag(tag_word).startswith('n'))
		return feat


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

