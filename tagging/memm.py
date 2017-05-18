from featureforge.vectorizer import Vectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline

from tagging.features import History,word_lower,word_istitle,word_isupper,word_isdigit,NPrevTags,PrevWord

class MEMM:
 
    def __init__(self, n, tagged_sents):
        """
        n -- order of the model.
        tagged_sents -- list of sentences, each one being a list of pairs.
        """
 
 		#Agregar features anteriores al vectorezer
 		self.vocabulary= set()
 		self.tag_set = set()

 		temp_features = [word_lower, word_istitle,word_isdigit,word_isupper]
 		features=[word_lower, word_istitle,word_isdigit,word_isupper]
 		#agregamos los features no basicos
 		for i in range(self.n):
 			features.append(NPrevTags(i))

 		for feature in temp_features:
 			features.append(PrevWord(feature))

 		#Obtener conjunto de palabras conocidas y de tags
        for sent in tagged_sents:
            tags = tuple(tag for (_,tag) in sent)
            words = tuple(word for (word,_) in sent)
            self.vocabulary = self.vocabulary.union(words)
            self.tag_set = self.tag_set.union(tags)


 		self.text_clf = Pipeline([('vect', Vectorizer(features)),
                     ('clf', MultinomialNB()),
		])

		#Para entrenar necesitamos las historias y los tags


    def sents_histories(self, tagged_sents):
        """
        Iterator over the histories of a corpus.
 
        tagged_sents -- the corpus (a list of sentences)
        """
        histories = []
        for sent in tagged_sents:
            histories += self.sent_histories(sent)

		return histories
		 		
    def sent_histories(self, tagged_sent):
        """
        Iterator over the histories of a tagged sentence.
 
        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
 
    def sents_tags(self, tagged_sents):
        """
        Iterator over the tags of a corpus.
 
        tagged_sents -- the corpus (a list of sentences)
        """
 
    def sent_tags(self, tagged_sent):
        """
        Iterator over the tags of a tagged sentence.
 
        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
 
    def tag(self, sent):
        """Tag a sentence.
 
        sent -- the sentence.
        """
 
    def tag_history(self, h):
        """Tag a history.
 
        h -- the history.
        """
 
    def unknown(self, w):
        """Check if a word is unknown for the model.
 
        w -- the word.
        """