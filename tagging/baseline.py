from collections import defaultdict, Counter

class BaselineTagger:

    def __init__(self, tagged_sents):
        """
        tagged_sents -- training sentences, each one being a list of pairs.
        """
        self.dict_word_tags = dict_word_tags = defaultdict(Counter)
        self.dict_word_freq_tag = dict_word_freq_tag = defaultdict(str)
        self.vocabulary = vocabulary = set({})
        for sent in tagged_sents:
            for word, tag in sent:
                self.vocabulary.add(word)
                dict_word_tags[word][tag] += 1

        for wordd, tag_dict in dict_word_tags.items():
            dict_word_freq_tag[wordd] = tag_dict.most_common(1)[0][0]
        print (dict_word_tags)
        self.vocabulary = vocabulary

    def tag(self, sent):
        """Tag a sentence.

        sent -- the sentence.
        """
        return [self.tag_word(w) for w in sent]

    def tag_word(self, w):
        """Tag a word.

        w -- the word.
        """
        if self.unknown(w):
            return 'nc0s000'
        else:
            return self.dict_word_freq_tag[w]

    def unknown(self, w):
        """Check if a word is unknown for the model.

        w -- the word.
        """
        return (w not in self.vocabulary)
