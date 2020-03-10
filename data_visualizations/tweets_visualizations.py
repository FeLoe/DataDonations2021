#%%
import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly.offline import iplot, init_notebook_mode
import cufflinks
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
cufflinks.go_offline(connected=True)
init_notebook_mode(connected=True)

#%%
#Reading datasets, converting column datatypes or creating new ones
Tweets = pd.read_csv('data/Tweets.csv')
Tweets['created_at'] = pd.to_datetime(Tweets['created_at'])
Tweets['length'] = Tweets['full_text'].str.len()
Likes = pd.read_csv('data/Likes.csv')

#%%
#First viz: Weekly tweets
weekly_tweets = Tweets[['created_at','favorite_count']].\
         set_index('created_at').\
         resample('W-MON').sum()
weekly_tweets.iplot(kind='bar', xTitle='Date', yTitle='Sum',
    title='Weekly Tweets')
#%%
#Second viz: Weekly likes
weekly_likes = Tweets[['created_at','favorite_count']].\
         set_index('created_at').\
         resample('W-MON').agg({'Sum weekly likes': 'sum', 'Average weekly likes':'mean'})
weekly_likes.columns = weekly_likes.columns.droplevel(1)
weekly_likes.iplot(kind='bar', xTitle='Date', yTitle='N',
    title='Weekly Likes')
#%%
#Third viz: Weekly retweets
weekly_retweets = Tweets[['created_at','retweet_count']].\
         set_index('created_at').\
         resample('W-MON').agg({'Sum weekly retweets': 'sum', 'Average weekly retweets':'mean'})
weekly_retweets.columns = weekly_retweets.columns.droplevel(1)
weekly_retweets.iplot(kind='bar', xTitle='Date', yTitle='N',
    title='Weekly Retweets')

# %%
#Fourth viz: Wordcloud of Tweet content
tweet_content = " ".join(Tweets['full_text'].tolist())
tweet_content = re.sub('@[^\s]+|RT|https|co|amp','',tweet_content)

icon = svg2rlg("icons/twitter.svg")
renderPM.drawToFile(icon, "icons/twitter.png", fmt="PNG")

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return tuple(Greens_9.colors[random.randint(2,8)])

icon = Image.open("icons/twitter.png").convert("RGBA")
mask = Image.new("RGB", icon.size, (255,255,255))
mask.paste(icon,icon)
mask = np.array(mask)

wc = WordCloud(font_path='fonts/CabinSketch-Bold.ttf', background_color="white", max_words=2000, mask=mask,
               max_font_size=300, random_state=42)
               
# generate word cloud
wc.generate(tweet_content)
wc.recolor(color_func=color_func, random_state=3)
wc.to_file("output/tweets.png")

# %%
#Fifth viz: Likes of Tweets 
likes_content = " ".join(Likes['fullText'].tolist())
likes_content = re.sub('@[^\s]+|RT|https|co|amp','',likes_content)

icon = svg2rlg("icons/thumbs-up.svg")
renderPM.drawToFile(icon, "icons/thumbs-up.png", fmt="PNG")

def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return tuple(Greens_9.colors[random.randint(2,8)])

icon = Image.open("icons/thumbs-up.png").convert("RGBA")
mask = Image.new("RGB", icon.size, (255,255,255))
mask.paste(icon,icon)
mask = np.array(mask)

wc = WordCloud(font_path='fonts/CabinSketch-Bold.ttf', background_color="white", max_words=2000, mask=mask,
               max_font_size=300, random_state=42)
               
# generate word cloud
wc.generate(likes_content)
wc.recolor(color_func=color_func, random_state=3)
wc.to_file("output/likes_twitter.png")


# %%
