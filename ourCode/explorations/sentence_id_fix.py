#!/usr/bin/python
from gensim.models.doc2vec import Doc2Vec, LabeledLineSentence, LabeledSentence
from itertools import izip, islice
from random import shuffle
import timeit
import sys
from inspection import preprocess, inspect_words, inspect_sentences

class BitextDoubleSentence(object):
    def __init__(self, filename, size, repeat=1):
        self.filename = filename
        self.size = size
        self.repeat = repeat
 
    def __iter__(self):
        f = self.filename
        with open(f + 'en') as ens, open(f + 'de') as des: 
            for i, (en, de) in enumerate(islice(izip(ens, des), self.size)):
                pen = preprocess(en)
                en = ['%s_en'%w for w in pen.split()]
                de = ['%s_de'%w for w in preprocess(de).split()]
                langs = [en, de]
                shuffle(langs)
                for l in langs:
                    yield LabeledSentence(words=l, labels=[pen]*self.repeat)

print 'Simply training German and English words with the bitext sentence id as label'
start = timeit.default_timer()

f = sys.argv[1]+'/europarl-v7.de-en.'
n = 50000
sentences = BitextDoubleSentence(f, n)
print '%s sentences' % n

model = Doc2Vec(alpha=0.025, min_alpha=0.025, size=256, workers=8)
model.build_vocab(sentences)
print '%s words in vocab' % (len(model.vocab) - n)

print 'epochs'
for epoch in range(10):
    model.train(sentences)
    print epoch
    model.alpha -= 0.002  # decrease the learning rate

inspect_sentences(model)
model.train_lbls = False # stop training sentences
model.alpha = 0.025 # reset learning rate
# scale sentence vectors by repeating
sentences = BitextDoubleSentence(f, n, repeat=5)

print 'epochs'
for epoch in range(10):
    model.train(sentences)
    print epoch
    model.alpha -= 0.002  # decrease the learning rate

stop = timeit.default_timer()
print 'Running time %ss' % (stop - start)

inspect_words(model)
