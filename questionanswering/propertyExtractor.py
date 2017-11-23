from SPARQLWrapper import SPARQLWrapper, JSON
from questionanswering.funaux import *
from questionanswering.templates import *

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer

import numpy as np
import itertools, operator
from questionanswering.WordReferenceWrapper import *
from googletrans import Translator

class PropertyExtractor:
    # -------------------------------------------------------------
    # --GET PROPERTY ----------------------------------------------
    # -------------------------------------------------------------

    def __init__(self, nlp):
        self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
        self.sparql.setReturnFormat(JSON)
        self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
        self.sparqlEn.setReturnFormat(JSON)
        self.nlp_api = nlp
        self.igProp = ["wiki","abstract","thumbail","gdp","hdi","PopulatedPlace","wordnet_type"]

        self.translator = Translator()
        self.pipeline = None
        self.dbo_trans = {}
        self.lang_trans = {}
        self.esp_sins = {}

    def train(self, x, y, classi=None):
        vectorizer = DictVectorizer()

        if classi == None:
            classifier = LogisticRegression(class_weight={1:8})
        else:
            classifier = classi
        self.pipeline = Pipeline([("vec", vectorizer), ("clas", classifier)])
        x = x
        y = y

        self.pipeline.fit(x, y)
    

    # --------- LIMPIEZA KEYS ----------------------
    def only_noun_verb(self, st_keys):
        st_result = st_keys
        tag_word = self.nlp_api(st_keys)
        tag_word = [(word.text, word.tag_) for word in tag_word]
        for w, t in tag_word:
            if "VERB" in t:
                continue
            if "NOUN" in t:
                continue
            if "ADJ" in t:
                continue
            st_result = st_result.replace(w, ' ')

        st_result = st_result.split()
        return " ".join(st_result)

    def remove_keys_with_PROPN(self, st_keywords):
        keys = [x.strip() for x in st_keywords.split(',')]
        keys_result = [x.strip() for x in st_keywords.split(',')]
        for k in keys:
            tag_word = self.nlp_api(k)
            tag_word = [(word.text, word.tag_) for word in tag_word]
            for w, t in tag_word:
                if "PROPN" in t:
                    keys_result.remove(k)
                    break
        return " ".join(keys_result)

    def clean_dbo(self,st_dbo):
        ls_dbo = re.split(r'([A-Z][a-z]*)', st_dbo)

        return (" ".join([a.lower() for a in ls_dbo])).strip()

    def clean_keys_prop(self,st_keywords):
        st_keywords = removeStopWords(st_keywords)      
        st_keywords = self.remove_keys_with_PROPN(st_keywords)
        st_keywords = self.only_noun_verb(st_keywords)
        st_keywords = delete_tildes(st_keywords)

        return st_keywords
    #----------FINAL LIMPIEZA KEYS -----------------


    def trans_es_to_en(self,text):
        knows=[]
        text = list(text)
        text_copy = list(text)
        for i in range(len(text_copy)):
            k = self.lang_trans.get(text_copy[i],"")
            if not k == "":
                knows.append((i,k))
                text.remove(text_copy[i])

        result =self.translator.translate(text, dest="en", src="es")
        result = [delete_tildes(a.text).strip() for a in result]
        for i,k in knows:
            result.insert(i,k)

            
        return result

    def trans_en_to_es(self,text):
        knows=[]
        
        text = list(text)
        text_copy = list(text)
        for i in range(len(text_copy)):
            k = self.dbo_trans.get(text_copy[i],"")
            if not k == "":
                knows.append((i,k))
                text.remove(text_copy[i])
                
        result = self.translator.translate(text, dest="es", src="en")
        result = [delete_tildes(a.text).strip() for a in result]
        for i,k in knows:
            result.insert(i,k)

        return result

    def get_sinonimos(self,word):

        sinonimos = self.esp_sins.get(word,[])
        if sinonimos == []:
            sinonimos = get_synoms(word)
            self.esp_sins[word] = sinonimos
            print("cached sins", word)
        return sinonimos



    def generate_train_by_entity(self, query, st_keywords):

        temp_prop_x = []
        temp_prop_y = []

        st_dbo = parseQuery(query)
        if st_dbo == "":
            return [], []
        st_ent = getEntity(query)
        if st_ent == "":
            return [], []
        if st_keywords == "" or st_keywords == None:
            return [], []

        # Limpiamos y tokenizamos Keywords y DBO
        st_keywords = self.clean_keys_prop(st_keywords)
        st_dbo_clean = self.clean_dbo(st_dbo)

        # Obtenemos los Features

        sinonimos = [st_keywords]
        sinonimos_trans = []
        dbo_props = [st_dbo_clean]
        dbo_props_trans = []

        # Obtenemos sinonimos si podemos
        print("keys: ",st_keywords)
        for k in st_keywords.split():
            sinonimos += self.get_sinonimos(k)

        
        # Traducimos todos los sinonimos
        sinonimos_trans = self.trans_es_to_en(sinonimos)

        # Obtenemos las propiedades
        query = templates.get('props_ent',"").format(ent=st_ent)
        self.sparqlEn.setQuery(query)
        results = self.sparqlEn.query().convert()
        for result in results["results"]["bindings"]:
            value = result["p"]["value"]
            if any(s in value for s in self.igProp):
                continue

            if "ontology" in value or "property" in value:
                prop = value.split('/')[4]
                if len(prop) <= 3:
                    continue
                if not prop == st_dbo:
                    dbo_props.append(self.clean_dbo(prop))

        dbo_props_trans = self.trans_en_to_es(dbo_props)

        assert(len(dbo_props_trans) == len(dbo_props))
        assert(len(sinonimos) >= 0)
        assert(len(sinonimos_trans) >= 0)

        #Generamos los positivos
        for i in range(len(sinonimos)):
            # Guardamos traducciones de propiedades conocidas
            self.lang_trans[sinonimos[i]] = sinonimos_trans[i]

            x = self.get_all_features(sinonimos[i],dbo_props[0],es_to_en=sinonimos_trans[i],en_to_es=dbo_props_trans[0],sins=sinonimos)
            y = 1
            temp_prop_x.append(x)
            temp_prop_y.append(y)



        #Generamos los negativos
        for i in range(len(dbo_props)):
            # Guardamos traducciones de propiedades conocidas
            self.dbo_trans[dbo_props[i]] = dbo_props_trans[i]
            for j in range(len(sinonimos)):
                x = self.get_all_features(sinonimos[j],dbo_props[i],es_to_en=sinonimos_trans[j],en_to_es=dbo_props_trans[i],sins=sinonimos)
                y = 0
                temp_prop_x.append(x)
                temp_prop_y.append(y)


        return temp_prop_x, temp_prop_y

    def get_all_features(self, st_keywords, st_dbo,es_to_en="",en_to_es="",sins = []):
        """
        Keywords  preprocesados
        Dbo:      birthDate -> birth | Date
        """

        x = {}
        x = {x:True for x in (st_keywords+" "+st_dbo).split()}
        x[st_keywords+"-"+st_dbo] = True
        x["es"] = st_keywords
        x["en"] = st_dbo
        x["estoen"] = es_to_en
        x["entoes"] = en_to_es
        x["es=entoes"] = (st_keywords in en_to_es)
        x["en=estoen"] = (st_dbo in es_to_en)



        for s in sins:
            x[s+"=entoes"] = (s in en_to_es)
            x[s] = True



        return x


    def get_properti(self,temp,entity,keys):
        properti = ""
        choose = []
        ls_dbo = []
        ls_dbo_clean = []
        ls_dbo_trans = []

        st_keys = " ".join(keys)


        # Limpiamos los keys
        st_keys = self.clean_keys_prop(st_keys)        
        print("Keys analizados: ",st_keys)

        # Obtenemos las propiedades
        sparql = self.sparqlEn
        query = templates.get(temp,"").format(ent=entity)
        sparql.setQuery(query)
        results = sparql.query().convert()


        for result in results["results"]["bindings"]:
            value = result["p"]["value"]
            if any(s in value for s in self.igProp):
                continue
            if "ontology" in value or "property" in value:
                prop = value.split('/')[4]
                if len(prop) <= 3:
                    continue
            if "ontology" in value or "property" in value:
                prop = value.split('/')[4]
                ls_dbo_clean.append(self.clean_dbo(prop))
                ls_dbo.append(prop)


        # Traducimos las propiedades
        ls_dbo_clean = ls_dbo_clean

        print("Traduciendo propiedades...", len(ls_dbo_clean))
        if len(ls_dbo_clean) >= 100:
            ls_dbo_clean = ls_dbo_clean[:100]
            ls_dbo = ls_dbo[:100]
            
        ls_dbo_trans = self.trans_en_to_es(ls_dbo_clean)
        print("OK - Propiedades traducidas")
        sinonimos = [st_keys]
        for k in st_keys.split():
            sinonimos += self.get_sinonimos(k)

        es_to_en = self.trans_es_to_en([st_keys])[0]
        for i in range(len(ls_dbo_clean)):
            test = self.get_all_features(st_keys,ls_dbo_clean[i],es_to_en=es_to_en,en_to_es=ls_dbo_trans[i],sins = sinonimos)
            temp = self.pipeline.predict([test])
            prob = self.pipeline.predict_proba([test])[0][1]

            choose.append((ls_dbo[i],prob))
            if ls_dbo_clean[i] == "spouse":
                print (test)

        choose = sorted(choose, key=operator.itemgetter(1),reverse=True)
        if not len(choose) == 0:
            properti = ""
            if choose[0][1] > 0.20:
                properti = choose[0][0]

        return properti

    def get_question_property_type(self, st_type, keys):
        properti = self.get_properti('props_type',st_type,keys)
        return properti

    def get_question_property(self, entity, keys):
        properti = self.get_properti('props_ent_amb',entity,keys)
        return properti

    def get_question_property_rev(self, entity, keys):
        properti = self.get_properti('props_ent_rev',entity,keys)
        return properti