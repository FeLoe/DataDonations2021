#%%
import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly.offline import iplot, init_notebook_mode
import cufflinks
import re
from wordcloud import WordCloud, STOPWORDS
cufflinks.go_offline(connected=True)
init_notebook_mode(connected=True)

#%%
#Reading dataset, converting column datatypes or creating new ones
Tweets = pd.read_csv('Tweets.csv')
Tweets['created_at'] = pd.to_datetime(Tweets['created_at'])
Tweets['length'] = Tweets['full_text'].str.len()

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
wc = WordCloud(background_color="white", max_words=2000)

wc.generate(tweet_content)

wc.to_file("twitter_wordcloud.png")

plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()

# %%
