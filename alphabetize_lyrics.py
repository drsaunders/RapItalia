# -*- coding: utf-8 -*-
"""
Created on Wed May 18 14:20:13 2016

@author: dsaunder
"""

import codecs
import re
import pandas as pd 

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
    filename = 'full_lyrics/' + songtitle + '.txt'
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
    words.sort()
    newtext = ''
    for w in words:
        newtext = newtext + w + " "
        
#    print newtext + "\n\n"

    filename = 'lyrics/' + songtitle + '.txt'
    try:
        with codecs.open(filename,'w','utf-8') as f:
            f.write(newtext)
        
    except IOError:
        print filename
        continue

    