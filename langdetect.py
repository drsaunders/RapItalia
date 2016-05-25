# -*- coding: utf-8 -*-
"""
Created on Wed May 25 13:56:15 2016

@author: dsaunder
"""
from nltk.corpus import stopwords
import nltk.tokenize
import numpy as np

#%%
###############
# The following code is copied from 
# http://www.mostlymaths.net/2012/06/language-detection-in-python-with-nltk.html
# And is written by Ruben Berenguel


def scoreFunction(wholetext):
    """Get text, find most common words and compare with known
    stopwords. Return dictionary of values"""
    # C makes me program like this: create always empty stuff just in case
    dictiolist={}
    scorelist={}
    # These are the available languages with stopwords from NLTK
    NLTKlanguages=["dutch","finnish","german","italian",

"portuguese","spanish","turkish","danish","english",

"french","hungarian","norwegian","russian","swedish"]
    # Just in case I add stopword lists

    languages=NLTKlanguages #+FREElanguages
    # Fill the dictionary of languages, to avoid  unnecessary function calls
    for lang in NLTKlanguages:
        dictiolist[lang]=stopwords.words(lang)
    # Split all the text in tokens and convert to lowercase. In a
    # decent version of this, I'd also clean the unicode
    tokens=nltk.tokenize.word_tokenize(wholetext.encode('utf-8'))
    tokens=[t.lower() for t in tokens]
    # Determine the frequency distribution of words, looking for the
    # most common words
    freq_dist=nltk.FreqDist(tokens)
    # This is the only interesting piece, and not by much. Pick a
    # language, and check if each of the 20 most common words is in
    # the language stopwords. If it's there, add 1 to this language
    # for each word matched. So the maximal score is 20. Why 20? No
    # specific reason, looks like a good number of words.
    for lang in languages:
        scorelist[lang]=0
        for word in freq_dist.keys()[0:20]:
            if word in dictiolist[lang]:
                scorelist[lang]+=1
    return scorelist

def whichLanguage(scorelist):
    """This function just returns the language name, from a given
    "scorelist" dictionary as defined above."""
    maximum=0
    lang = np.nan
    for item in scorelist:
        value=scorelist[item]
        if maximum<value:
            maximum=value
            lang=item
    return lang
###########
