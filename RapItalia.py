import pandas as pd 
import re
import matplotlib.pyplot as plt
import numpy as np
import codecs
from nltk.corpus import stopwords
import nltk.tokenize
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

#%%
# Read in information about albums and tracks
album_tracks = pd.read_csv('albuminfo.txt','\t',names=['album','year','song'])
album_tracks = album_tracks.drop_duplicates()

#%%
# Find the first tracks
grouped = album_tracks.groupby(by='album')
first_song_info = grouped['album','year','song'].first()
first_song_info.index = range(len(first_song_info))

#%%
# Extract and process the text 
for i,songtitle in enumerate(first_song_info.song):
    filename = 'lyrics/' + songtitle + '.txt'
    try:
        with codecs.open(filename,'r','utf-8') as f:
            songtext = f.read()
            f.close()
    except IOError:
        print filename
        continue
    
    
    songtext = songtext.strip()
    re.sub('\r\n(\r\n)+','\r\n',songtext)
    
    words = songtext.split()
    first_song_info.loc[i,'word_count'] = len(words)
    first_song_info.loc[i,'num_lines']= songtext.count('\n')+1
    first_song_info.loc[i,'avg_word_length']= np.nanmean([len(x) for x in words])
    try:
        first_song_info.loc[i,'language'] = whichLanguage(scoreFunction(songtext))    
    except UnicodeDecodeError:
        first_song_info.loc[i,'language'] =np.nan
        
#%%
# Strip out songs without enough lyrics 
song_valid = np.all([np.invert(first_song_info.word_count.isnull()),first_song_info.word_count > 25],0)
first_song_info = first_song_info.loc[song_valid,:]

##%%
## Explore possible features for classifying rap songs 
#words_per_line = first_song_info.loc[:,'word_count']/first_song_info.loc[:,'num_lines']
#plt.figure()
#plt.hist(words_per_line,bins=np.arange(2,10,0.2))
#
#plt.figure()
#plt.hist(first_song_info.word_count,bins=np.arange(0,800,20))
#
#plt.figure()
#plt.plot(first_song_info.word_count,words_per_line,'.')
#
#plt.figure()
#plt.hist(first_song_info.avg_word_length,50)

#%%
# Compute rap content by cutoff and print detected song titles to check

rapCutoff = 500

first_song_info.loc[:,'is_rap'] = first_song_info.loc[:,'word_count'] > rapCutoff
print "These songs were identified as rap: "
print first_song_info.loc[first_song_info.is_rap,['song','word_count']].sort_values(by='word_count')

#%%
# Rap albums: absolute

byyear = first_song_info.groupby(by=['year'])
totalalbums = byyear['song'].count()
totalrap = byyear['is_rap'].sum()
nonrap = totalalbums-totalrap
ind = totalalbums.index    # the x locations for the groups
width = 0.45 
plt.figure(figsize=[10,6])
rapcolours = [[0.5, 0.5, 1],[0, 0, 0]]
p1 = plt.bar(ind-width, nonrap, width, color=rapcolours[0],linewidth=0)
p2 = plt.bar(ind, totalrap, width, color=rapcolours[1],linewidth=0)
plt.xlim([1965,2017])
plt.xticks(range(1965,2020,5))
format = 'png'
plt.ylabel('Albums')
plt.xlabel('Release year')
ax = plt.gca()
ax.get_yaxis().set_tick_params(direction='in')
ax.get_xaxis().set_tick_params(direction='in')
plt.draw()
plt.legend(['Non-rap','Rap'],loc='upper left')
plt.title('Rap Content of Albums in an Italian Lyrics Database')


plt.savefig('RapItalia_plot_1.png', dpi=100,format=format,bbox_inches="tight")

#%%
# Rap albums: proportions

totalalbums = totalrap + nonrap
rapprops = np.array([totalrap/totalalbums,nonrap/totalalbums])

width = 0.7
plt.figure(figsize=[10,6])
lefts = ind-(0.5*width)
p1 = plt.bar(lefts, rapprops[0,:], width, color=rapcolours[0],linewidth=0)
p2 = plt.bar(lefts, rapprops[1,:], width, color=rapcolours[1], bottom=rapprops[0,:], linewidth=0)
plt.ylabel('Proportion of albums')
plt.xlabel('Release year')
plt.legend(['Rap','Non Rap'],loc='upper left')
plt.title('Rap Content of Albums in an Italian Lyrics Database (by Proportion)')

plt.xticks(range(1965,2020,5))
plt.xlim([1965,2017])

plt.savefig('RapItalia_plot_1a.png', dpi=100,format=format,bbox_inches="tight")

#%%
# Languages: absolute numbers

langcolours = np.array([[0.65,0.38,0.72],[0.3, 0.9, 0.27],[0.9,0.20,0.20]])

byyearlang = first_song_info.groupby(by=['year','language'])
languagereport = byyearlang['album'].count().unstack()
languagereport.loc[:,'other'] = np.nansum(languagereport.loc[:,['french','german','portuguese','spanish']],1)
years = languagereport.index
totalitalian = np.nan_to_num(languagereport.loc[:,'italian'])
totalenglish = np.nan_to_num(languagereport.loc[:,'english'])
totalother = np.nan_to_num(languagereport.loc[:,'other'])
width =0.3

plt.figure(figsize=[10,6])
p1 = plt.bar(years-(width+0.5*width), totalitalian, width, color=langcolours[0,:],linewidth=0)
p2 = plt.bar(years-(0.5*width), totalenglish, width, color=langcolours[1,:],linewidth=0)
p3 = plt.bar(years+(width-0.5*width), totalother, width, color=langcolours[2,:],linewidth=0)
plt.ylabel('Albums')
plt.xlabel('Release year')

plt.xlim([1965,2017])
plt.xticks(range(1965,2020,5))
plt.legend(['Italian','English','Other'],title='Album language',loc='upper left')
plt.title('Language Content of Albums in an Italian Lyrics Database')
ax = plt.gca()
ax.get_yaxis().set_tick_params(direction='in')
ax.get_xaxis().set_tick_params(direction='in')
plt.draw()

plt.savefig('RapItalia_plot_2.png', dpi=100,format=format,bbox_inches="tight")
#%%
# Languages: proportions
totalalbums = totalitalian + totalenglish + totalother
langprops = np.array([totalitalian/totalalbums,totalenglish/totalalbums,totalother/totalalbums])

width =0.7
plt.figure(figsize=[10,6])
lefts = years-(0.5*width)
p1 = plt.bar(lefts, langprops[0,:], width, color=langcolours[0,:],linewidth=0)
p2 = plt.bar(lefts, langprops[1,:], width, color=langcolours[1,:], bottom=langprops[0,:], linewidth=0)
p3 = plt.bar(lefts, langprops[2,:], width, color=langcolours[2,:], bottom=(langprops[1,:]+langprops[0,:]),linewidth=0)
plt.ylabel('Proportion of albums')
plt.xlabel('Release year')
plt.legend(['Italian','English','Other'],title='Album language',loc='lower left')
plt.title('Language Content of Albums in an Italian Lyrics Database (by Proportion)')

plt.xlim([1965,2017])
plt.xticks(range(1965,2020,5))

plt.savefig('RapItalia_plot_2a.png', dpi=100,format=format,bbox_inches="tight")
