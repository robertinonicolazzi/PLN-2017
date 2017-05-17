from collections import defaultdict
from math import log2


class HMM:
 
    def __init__(self, n, tagset, trans, out):
        """
        n -- n-gram size.
        tagset -- set of tags.
        trans -- transition probabilities dictionary.
        out -- output probabilities dictionary.
        """
        self.tag_set = set(tagset)
        self.n = n

        #funcion q
        self.trans = trans

        #funcion e
        self.out = dict(out)
 
    def tagset(self):
        """Returns the set of tags.
        """
        return self.tag_set
 
    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.
 
        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        return self.trans.get(tuple(prev_tags),{}).get(tag,0.0)
 
    def out_prob(self, word, tag):
        """Probability of a word given a tag.
 
        word -- the word.
        tag -- the tag.
        """
        return self.out.get(tag).get(word,0)
 
    def tag_prob(self, y):
        """
        Probability of a tagging.
        Warning: subject to underflow problems.
 
        y -- tagging.

        """
        #Generar el producto de los q
        prob = 1.0
        temp_y = ['<s>']*(self.n-1)+ list(y) + ['</s>']
        n = self.n
        for i in range(n-1,len(temp_y)):
            tag = temp_y[i]
            prev_tags = temp_y[i-n+1:i]
            trans_p = self.trans_prob(tag,prev_tags)
            prob *= trans_p

        return prob
 
    def prob(self, x, y):
        """
        Joint probability of a sentence and its tagging.
        Warning: subject to underflow problems.
 
        x -- sentence.
        y -- tagging.
        """

        #en tag prob ya tenemos calculado q, falta calcular los productos de e
        e = 1.0
        tag_p = self.tag_prob(y)
        for w,t in zip(x,y):
            e *= self.out_prob(w,t)

        return tag_p * e
 
    def tag_log_prob(self, y):
        """
        Log-probability of a tagging.
 
        y -- tagging.
        """
        #Generar el producto de los q
        prob = 0.0
        temp_y = ['<s>']*(self.n-1)+ list(y) + ['</s>']
        n = self.n
        for i in range(n-1,len(temp_y)):
            tag = temp_y[i]
            prev_tags = temp_y[i-n+1:i]
            trans_p = self.trans_prob(tag,prev_tags)
            if trans_p == 0:
                prob = float('-inf')
                break

            prob += log2(trans_p)

        return prob

    def log_prob(self, x, y):
        """
        Joint log-probability of a sentence and its tagging.
 
        x -- sentence.
        y -- tagging.
        """

        e = 0.0
        tag_p = self.tag_log_prob(y)
        prob_e = 0.0
        for w,t in zip(x,y):
            e = self.out_prob(w,t)
            if e == 0:
                prob_e = float('-inf')
                break
            prob_e += log2(e)


        return tag_p + prob_e
 
    def tag(self, sent):
        """Returns the most probable tagging for a sentence.
 
        sent -- the sentence.
        """
        V = ViterbiTagger(self)
        return V.tag(sent)
 
 
class ViterbiTagger:
 
    def __init__(self, hmm):
        """
        hmm -- the HMM.
        """
        self.hmm = hmm
        self._pi = pi = defaultdict(dict)
        self.trans = self.hmm.trans
        self.trans_prob = self.hmm.trans_prob
        self.out_prob = self.hmm.out_prob
        self.tag_set = self.hmm.tag_set
        self.n = self.hmm.n

        pi[0][tuple(['<s>']*(self.hmm.n-1))] = (0,[])

 
    def tag(self, sent):
        """Returns the most probable tagging for a sentence.
 
        sent -- the sentence.
        """
        m = len(sent)
        pi = self._pi
        for k in range(1,m+1):
        	for tag in self.tag_set:
        		for prev_tags, (prob, tags) in pi[k-1].items():
        			q = self.hmm.trans_prob(tag,prev_tags)
        			e = self.hmm.out_prob(sent[k-1],tag)

        			if not e:
        				continue
        			prob+=log2(e)+log2(q)
        			prev_tags = (prev_tags + (tag,))[1:]
        			if prev_tags not in pi[k] or prob > pi[k][prev_tags][0]:
        				pi[k][prev_tags] = (prob, tags + [tag])

        max_prob = float('-inf')
        resul_tag = []
        for prev_tags, (prob, tags) in pi[m].items():
        	q = self.hmm.trans_prob('</s>', prev_tags)
        	if q > 0.0:
        		prob += log2(q)
        		if max_prob < prob:
        			max_prob = prob
        			result_tag = tags
        return result_tag