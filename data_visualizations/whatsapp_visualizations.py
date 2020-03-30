#%%
import pandas as pd
import plotly
import plotly.graph_objs as go
import logging
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from imageio import imread
import numpy as np
import csv
import random
from PIL import Image
from palettable.colorbrewer.sequential import Greens_9
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
import os
from nltk.corpus import stopwords
from string import punctuation

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
log = logging.getLogger(__name__)
os.makedirs('../data_visualizations/output', exist_ok = True)

#%%
#Reading datasets, converting column datatypes or creating new ones
Apps = pd.read_csv('data/WhatsApp.csv')
datetime = Apps['date'].str.split(' ', n = 1, expand = True)
Apps['Date'] = datetime[0]
Apps['Time'] = datetime[1]
Apps['Letter_Count'] = Apps['message'].apply(lambda s : len(s))
Apps['Word_Count'] = Apps['message'].apply(lambda s : len(s.split(' ')))

#%%
#First viz: creating barchart with top 10 message posters
author_value_counts = Apps['author'].value_counts() # Number of messages per author
top_10_author_value_counts = author_value_counts.head(10) # Number of messages per author for the top 10 most active authors
top_10_author_value_counts.plot.barh() # Plot a bar chart using pandas built-in plotting apis

#%%
#Second viz: creating barchart with top 10 media message posters
media_messages_Apps = Apps[Apps['message'] == '<Media omitted>']
author_media_messages_value_counts = media_messages_Apps['author'].value_counts()
top_10_author_media_messages_value_counts = author_media_messages_value_counts.head(10)
top_10_author_media_messages_value_counts.plot.barh()

#%%
#Third viz: creating barchart with top 10 word posters
total_word_count_grouped_by_author = Apps[['author', 'Word_Count']].groupby('author').sum()
sorted_total_word_count_grouped_by_author = total_word_count_grouped_by_author.sort_values('Word_Count', ascending=False)
top_10_sorted_total_word_count_grouped_by_author = sorted_total_word_count_grouped_by_author.head(10)
top_10_sorted_total_word_count_grouped_by_author.plot.barh()
plt.xlabel('Number of Words')
plt.ylabel('Authors')

#%%
#Fourth viz: creating barchart with top 10 words per message
author_word_counts = pd.Series(total_word_count_grouped_by_author['Word_Count'])
df = { 'Word_Count': author_word_counts, 'Message_Count': author_value_counts }
df = total_word_count_grouped_by_author.merge(author_value_counts.to_frame(), left_index=True, right_index=True)
df.columns = ['word_count', 'message_count']
df['avg_word_count'] = df['word_count']/df['message_count']
avgwordcount = df.drop(columns = ['word_count', 'message_count'])
avgwordcount_sorted = avgwordcount.sort_values('avg_word_count', ascending=False)
top_10_avgwordcount = avgwordcount_sorted.head(10)
top_10_avgwordcount.plot.barh()
plt.xlabel('Average number of words per message')
plt.ylabel('Authors')

#%%
#Fifth viz: creating barchart with top 10 most active dates
Apps['Date'].value_counts().head(10).plot.barh() # Top 10 Dates on which the most number of messages were sent
plt.xlabel('Number of Messages')
plt.ylabel('Date')

# %%
#Sixth viz: Wordcloud of WhatsApp chat content
Apps['message']=[message.lower() for message in Apps['message']]  # convert to lower case
Apps['message']=["".join([l for l in message if l not in punctuation]) for message in Apps['message']]  #remove punctuation
Apps['message']=[message.replace('<p>',' ').replace('</p>',' ').replace('media omitted', ' ') for message in Apps['message']]   #remove HTML tags
Apps['message']=[" ".join(message.split()) for message in Apps['message']]   # remove double spaces by splitting the strings into words and joining these words again
mystopwords = set(stopwords.words('dutch')) # use default NLTK stopword list; alternatively:
Apps['message'] = [" ".join([w for w in message.split() if w not in mystopwords]) for message in Apps['message']]
Apps['message'] = [" ".join([w for w in message.split() if w != 'wel']) for message in Apps['message']]

Apps_content = " ".join(Apps['message'].tolist())
Apps_content = re.sub('@[^\s]+|RT|https|co|amp','',Apps_content)

icon = svg2rlg("icons/comment.svg")
renderPM.drawToFile(icon, "icons/comment.png", fmt="PNG")

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
     return tuple(Greens_9.colors[random.randint(2,8)])

icon = Image.open("icons/comment.png").convert("RGBA")
mask = Image.new("RGB", icon.size, (255,255,255))
mask.paste(icon,icon)
mask = np.array(mask)

wc = WordCloud(font_path='fonts/CabinSketch-Bold.ttf', background_color="white", max_words=2000, mask=mask,
                max_font_size=300, random_state=42)

# generate word cloud
wc.generate(Apps_content)
wc.recolor(color_func=color_func, random_state=3)
wc.to_file("output/apps.png")

