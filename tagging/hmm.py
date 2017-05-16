class HMM:
 
    def __init__(self, n, tagset, trans, out):
        """
        n -- n-gram size.
        tagset -- set of tags.
        trans -- transition probabilities dictionary.
        out -- output probabilities dictionary.
        """
        self.tag_set = tagset
        self.n = n
        self.trans = trans
        self.out = out
 
    def tagset(self):
        """Returns the set of tags.
        """
        return self.tag_set
 
    def trans_prob(self, tag, prev_tags):
        """Probability of a tag.
 
        tag -- the tag.
        prev_tags -- tuple with the previous n-1 tags (optional only if n = 1).
        """
        return self.trans.get(prev_tags).get(word,0)
 
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
 
    def prob(self, x, y):
        """
        Joint probability of a sentence and its tagging.
        Warning: subject to underflow problems.
 
        x -- sentence.
        y -- tagging.
        """
 
    def tag_log_prob(self, y):
        """
        Log-probability of a tagging.
 
        y -- tagging.
        """
 
    def log_prob(self, x, y):
        """
        Joint log-probability of a sentence and its tagging.
 
        x -- sentence.
        y -- tagging.
        """
 
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
        self.tagset = self.hmm.tagset
        self.n = self.hmm.n

        pi[0][tuple(['<s>']*(self.hmm.n-1))] = (0,[])

 
    def tag(self, sent):
        """Returns the most probable tagging for a sentence.
 
        sent -- the sentence.
        """
        m = len(sent)
        pi = self._pi
        for k in range(1,m+1):
        	for tag in self.tagset:
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
        	if q > 0.0
        		prob += log2(q)
        		if max_prob < prob:
        			max_prob = prob
        			result_tag = tags
        return result_tag