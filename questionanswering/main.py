# -*- coding: utf-8 -*-
#!/usr/bin/python

from SPARQLWrapper import SPARQLWrapper, JSON
from questionanswering.funaux import *
from questionanswering.templates import *
from questionanswering.booleanHelper import BooleanHelper
from questionanswering.aggregationHelper import AggregationHelper
from questionanswering.entityExtractor import EntityExtractor
from questionanswering.propertyExtractor import PropertyExtractor
import sys,json,re,nltk, nltk.classify.util, spacy
import numpy as np


def progress(msg, width=None):
    """Ouput the progress of something on the same line."""
    if not width:
        width = len(msg)
    print('\b' * width + msg, end='')
    sys.stdout.flush()


class ClassAnswerType:

    def __init__(self, questions, nlp=None):

        self.nlp_api = nlp
        self.sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
        self.sparql.setReturnFormat(JSON)
        self.sparqlEn = SPARQLWrapper("http://dbpedia.org/sparql")
        self.sparqlEn.setReturnFormat(JSON)
        self.pExtractor = PropertyExtractor(self.nlp_api)
        train_prop_x = []
        train_prop_y = []
        self.all_words = set()

        train_answer_type = []
        keys = []
        dbo = []
        format_str = 'Answ Type ({}/{}) (Preg={}, Total={}), Prop {} '

        progress(format_str.format(0, len(questions), 0, len(questions), 0))

        i = 0
        j = 0
        for quest in questions:
            i += 1
            idiomas = quest["question"]
            st_keywords = ""
            st_question = ""
            for idiom in idiomas:
                if idiom["language"] == "es":
                    st_question = idiom["string"]
                    st_keywords = idiom["keywords"]
                    break
            if st_question == "":
                continue

            # Generamos features para tipo de respuesta
            feat_question = self.features_answer_type(st_question)
            st_answer_type = quest["answertype"]

            train_answer_type.append((feat_question, st_answer_type))

            # Intento de mapeo de propiedades

            temp_train_x, temp_train_y = self.pExtractor.generate_train_by_entity(
                quest["query"]["sparql"], st_keywords)
            if not len(temp_train_x) == 0:
                j += 1
            progress(
                format_str.format(
                    i,
                    len(questions),
                    i,
                    len(questions),
                    j))
            train_prop_x += temp_train_x
            train_prop_y += temp_train_y

        self.clas_tipo = nltk.NaiveBayesClassifier.train(train_answer_type)

        self.pExtractor.train(train_prop_x, train_prop_y)
        self.eExtractor = EntityExtractor(self.nlp_api)
        self.train_prop_x = train_prop_x
        self.train_prop_y = train_prop_y

    # -------------------------------------------------------------
    # --GET ANSWER TYPE--------------------------------------------
    # -------------------------------------------------------------

    def get_answer_type(self, st_question):
        question_features_test = self.features_answer_type(st_question)
        type_question = self.clas_tipo.classify(question_features_test)
        return type_question

    def features_answer_type(self, st_question):
        feat = {}
        st_question = cleanQuestion(st_question)
        tag_word = self.nlp_api(st_question)
        tag_word = [(word.text, word.tag_) for word in tag_word]

        feat["init_dame"] = bool(re.search('(D|d)ame ',st_question))
        feat["ask_cuanto"] = bool(re.search('cu(a|á)nt(o|a)(s|) ',st_question))
        feat["init_dame"] = (st_question.split(" ")[0] == 'dame')
        feat["ask_cuando"] = bool(re.search('cu(a|á)ndo ', st_question))
        feat["init_verb"] = 'VERB' in getFirstTag(tag_word) or 'AUX' in getFirstTag(tag_word)
        feat["init_verb2"] = 'VERB' in getFirstTag(tag_word) or 'AUX' in getFirstTag(tag_word)

        second_tag = getSecondTag(tag_word)
        articulo = 'PronType=Art' in getFirstTag(tag_word) and 'DET' in getFirstTag(tag_word)

        feat["art_sust2"] = articulo and (('NOUN' in second_tag) or ('PROPN' in second_tag))
        feat["art_sust"] = articulo and (('NOUN' in second_tag) or ('PROPN' in second_tag))

        return feat

    # -------------------------------------------------------------
    # --GET SIMPLE ANSWERS WORKFLOW -------------------------------
    # -------------------------------------------------------------
    def default_ans(self, entity, answertype):
        sparql = self.sparqlEn
        answers = []
        properti = ""
        if answertype == "date":
            properti = "date"

        query = '''
				select distinct ?result
				where {{
					<http://dbpedia.org/resource/{}> dbp:{} ?result
				}}
				'''.format(entity, properti)

        answers = resolveQuery(sparql, query)

        return set(answers)

    def get_english_ans_reverse(self, entity, properti):
        sparql = self.sparqlEn
        query = templates.get('simple_rev',"")
        query = query.format(res=entity, prop=properti)
        answers = resolveQuery(sparql, query)
        return set(answers)

    def get_english_ans(self, entity, properti):
        sparql = self.sparqlEn
        query = templates.get('simple',"")
        query = query.format(res=entity, prop=properti)
        answers = resolveQuery(sparql, query)

        if len(answers) == 0:
            query = templates.get('simple_amb',"")
            query = query.format(res=entity, prop=properti)
            answers = resolveQuery(sparql, query)
        return set(answers)

    # -----------------------------------------------------------------------
    # ---------------------- PREGUNTAS BOOLEAN ------------------------------
    # -----------------------------------------------------------------------

    def boolean_answerer(self, q, q_keys):

        pr_entity_es = ""
        sn_entity_es = ""
        answers = False
        q = cleanQuestion(q)
        h_boolean = BooleanHelper()

        entities, k_rest = self.eExtractor.get_entities(
            q_keys, 'boolean')
        if len(entities) == 0:
            print("Entities not Found")
            return []
        print("Entidades     : ", entities)
        print("Keys Restantes: ", k_rest)

        if len(entities) == 1:
            pr_entity_es = entities[0][0]
            pr_entity_en = entities[0][1]

            bool_key, properti = h_boolean.boolean_key_one_entity(q)
            print("Bool_key:", bool_key)
            print("PropertiTemp:", properti)
            if bool_key == "type":
                answers = h_boolean.get_type_answer(pr_entity_es, properti)
            elif bool_key == "exist":
                answers = h_boolean.get_exist_answer(pr_entity_es, properti)
            else:
                properti = self.pExtractor.get_question_property(
                    pr_entity_en, k_rest)
                answers = h_boolean.get_properti_answer(pr_entity_en, properti)

        elif len(entities) == 2:

            pr_entity_en = entities[0][1]
            sn_entity_en = entities[1][1]
            props, st_filter = self.two_entities_prop_filter(
                q, pr_entity_en, sn_entity_en, k_rest)

            if props == "":
                return []

            answers = h_boolean.two_entities_answer(
                pr_entity_en, sn_entity_en, props, st_filter)
        else:
            answers = []

        return answers

    def two_entities_prop_filter(
            self, question, entity, sn_entity, k_rest):
        prop = ""
        st_filter = ""
        if "antes" in question:
            st_filter = "FILTER (?x < ?y)"
            prop = "date"
        elif "despues" in question:
            st_filter = "FILTER (?x > ?y)"
            prop = "date"
        elif "menor" in question:
            st_filter = "FILTER (?x < ?y)"
            prop = self.pExtractor.get_question_property(entity, k_rest)
            if prop == "":
                prop = self.pExtractor.get_question_property(sn_entity, k_rest)
        elif "mayor" in question or "grande" in question:
            st_filter = "FILTER (?x > ?y)"
            prop = self.pExtractor.get_question_property(entity, k_rest)
            if prop == "":
                prop = self.pExtractor.get_question_property(sn_entity, k_rest)
        elif "misma" in question or "igual" in question or "mismos" in question:
            st_filter = "same"
            prop = self.pExtractor.get_question_property(entity, k_rest)
            if prop == "":
                prop = self.pExtractor.get_question_property(sn_entity, k_rest)
        else:
            prop = self.pExtractor.get_question_property(entity, k_rest)
            if prop == "":
                prop = self.pExtractor.get_question_property(sn_entity, k_rest)
            # la igualdad es viendo si pertenece
            st_filter = ""

        return prop, st_filter

    # ------------------------------------------------------------------------
    # ---------------------- RESPONDER PREGUNTAS -----------------------------
    # ------------------------------------------------------------------------

    def answer_question(self, q, q_keys,log=False):

        log_dict = {}

        print('---------------------------------------------------------------')

        answers = []
        answer_type = self.get_answer_type(q)

        print('{:15} | {}'.format('QUESTION: ', q))
        print('{:15} | {}'.format('ANSWER TYPE: ', answer_type))

        if answer_type == "boolean":
            return self.boolean_answerer(q, q_keys)

        h_agg = AggregationHelper(nlp=self.nlp_api)
        agg_key = h_agg.check_aggregation(answer_type, q, q_keys)

        if not agg_key == "none":
            return self.agg_answerer(h_agg, q, q_keys, agg_key, answer_type)

        entities, k_rest = self.eExtractor.get_entities(
            q_keys, answer_type)

        if len(entities) == 0:
            print("Entities not Found")
            return []

        print("Entidades     : ", entities)
        print('{:15} | {:10}'.format("1 Keys", "|".join(k_rest)))

        es_entity = entities[0][0]
        en_entity = entities[0][1]

        st_property = self.pExtractor.get_question_property(
            en_entity, k_rest)

        print("Entidad Ingles :", en_entity)
        print("Propiedad      :", st_property)

        answers = self.get_english_ans(en_entity, st_property)
        print("Respuesta:", answers)

        if len(answers) == 0 and answer_type == "date":
            answers = self.default_ans(en_entity, answer_type)

        if len(answers) == 0 and answer_type == "resource":
            print("Reverse")
            st_property = self.pExtractor.get_question_property_rev(
                en_entity, k_rest)
            answers = self.get_english_ans_reverse(en_entity, st_property)

        print('---------------------------------------------------------------')

        log_dict["answer_type"] = answer_type
        log_dict["entity"] = "ES: "+es_entity + " | EN: " + en_entity
        log_dict["property"] = st_property
        log_dict["answers"] = "\n".join([a for a in answers])

        if log:
            return log_dict

        return answers

    def agg_answerer(self, h_agg, q,
                             q_keys, key, answer_type):
        q_keys = delete_tildes(q_keys)
        answers = []
        if key == "count":
            entities, k_rest = self.eExtractor.get_entities(
                q_keys,
                answer_type
            )
            if len(entities) == 0:
                print("Entities not Found")
                return []
            print("Entidades     : ", entities)
            print("Keys Restantes: ", k_rest)

            es_entity = entities[0][0]
            en_entity = entities[0][1]

            st_property = self.pExtractor.get_question_property(
                en_entity, k_rest)
            answers = self.get_english_ans(en_entity, st_property)
            if key == "count" and not len(answers) == 0:
                if 'resource' in list(answers)[0]:
                    answers = h_agg.get_aggregation_count(
                        en_entity, st_property)

        if "asc" in key or "desc" in key:
            entities, k_rest = self.eExtractor.get_entities(
                q_keys, answer_type)

            #import pdb; pdb.set_trace()
            st_place = ""
            if len(entities) == 1:
                st_place, k_rest = h_agg.check_entity(
                    entities[0], q_keys, k_rest)
                if not st_place == "":
                    print('{:15} | {:10}'.format("Lugar", st_place))
                    entities = []
            if len(entities) == 0:
                st_property = ""
                k_rest, st_subproperty = h_agg.get_sub_property(
                    key, k_rest)               
                print('{:15} | {:10}'.format("SubPropiedad", st_subproperty))
                print('{:15} | {:10}'.format("1 Keys", ",".join(k_rest)))

                st_type, k_rest = h_agg.get_type(k_rest)
                print('{:15} | {:10}'.format('Tipo Entidad', st_type))
                print('{:15} | {:10}'.format("2 Keys", ",".join(k_rest)))

                if not len(k_rest) == 0:
                    st_property = self.pExtractor.get_question_property_type(
                        st_type, k_rest)

                if st_property == "":
                    if len(answers) == 0:
                        for st_property in h_agg.get_default(
                                st_subproperty):
                            answers = h_agg.get_aggregation_order_type(
                                st_type, st_property, key)
                            if not len(answers) == 0:
                                break
                else:
                    if not st_place == "":
                        answers = h_agg.get_aggregation_order_type_place(
                            st_type, st_property, key, st_place)
                    else:
                        answers = h_agg.get_aggregation_order_type(
                            st_type, st_property, key)


            else:
                # Tenemos la Entidad
                es_entity = entities[0][0]
                en_entity = entities[0][1]

                # Obtenemos la subpropiedad para comparar los resultados
                # child--BirthDate
                k_rest, st_subproperty = h_agg.get_sub_property(
                    key, k_rest)                

                # Vemos que se quiere saber de la entidad (propiedad) Ej:
                # Hijos--child
                st_property = self.pExtractor.get_question_property(
                    en_entity, k_rest)

                print('{:15} | {:10}'.format('Entidad', en_entity))
                print('{:15} | {:10}'.format("SubPropiedad", st_subproperty))
                print('{:15} | {:10}'.format("Keys Restantes", "|".join(k_rest)))
                print('{:15} | {:10}'.format("Propiedad", st_property))

                answers = h_agg.get_subprop_answer(
                    en_entity, st_property, st_subproperty, key)
                if len(answers) == 0:
                    for st_sub in h_agg.get_default(st_subproperty):
                        answers = h_agg.get_subprop_answer(
                            en_entity, st_property, st_sub, key)
                        if not len(answers) == 0:
                            break
        print("Respuesta:", answers)
        return set(answers)
