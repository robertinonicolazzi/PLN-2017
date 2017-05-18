from featureforge.vectorizer import Vectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from tagging.features import History,word_lower,word_istitle,word_isupper,word_isdigit,NPrevTags,PrevWord

class MEMM:
 
    def __init__(self, n, tagged_sents):
        """
        n -- order of the model.
        tagged_sents -- list of sentences, each one being a list of pairs.
        """
        #Agregar features anteriores al vector
        self.vocabulary= set()
        self.tag_set = set()
        self.n = n
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
                     ('clf', LogisticRegression()),
        ])

        #Para entrenar necesitamos las historias y los tags

        self.text_clf = self.text_clf.fit(self.sents_histories(tagged_sents),self.sents_tags(tagged_sents))


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
        histories = []
        n = self.n
        sent =  [word for (word,_) in tagged_sent]
        tags =  [tag for (_,tag) in tagged_sent]
        tags = ['<s>']*(n-1) + tags

        for i in range(len(sent)):
            histories.append(History(sent,tags[i:i+n-1],i))

        return histories


 
    def sents_tags(self, tagged_sents):
        """
        Iterator over the tags of a corpus.
 
        tagged_sents -- the corpus (a list of sentences)
        """
        tags = []
        for sent in tagged_sents:
            tags += self.sent_tags(sent)

        return tags


 
    def sent_tags(self, tagged_sent):
        """
        Iterator over the tags of a tagged sentence.
 
        tagged_sent -- the tagged sentence (a list of pairs (word, tag)).
        """
        return [tag for (_,tag) in tagged_sent]
 
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
        return w not in self.vocabulary