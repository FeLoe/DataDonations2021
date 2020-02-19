#At the moment prints all the data relevant (for researchers or for respondents) in a dict
#Looks at Tweets, Likes, Follower/Following, Personalization and Ad Impressions
import json
import os
import pandas as pd
from pandas.io.json import json_normalize
import logging
from collections import defaultdict
import glob
import argparse
import datetime
import re

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
log = logging.getLogger(__name__)


def main(file_path, max_exported_messages):
    global MAX_EXPORTED_MESSAGES
    MAX_EXPORTED_MESSAGES = max_exported_messages
    log.info('Parsing Twitter data...')
    data = parse_data(file_path)
    log.info('{:,} tweets parsed.'.format(len(data['tweets'])))
    if len(data) < 1:
        log.info('Nothing to save.')
        exit(0)
    print(data)


def parse_data(file_path):
    data, tweets_data, likes_data, follower_data, following_data, ad_impression_data, interests, age, gender, advertisers, shows = ([] for i in range(11))
    for root, dirs, files in os.walk(file_path):
        for filename in files:
            if not filename.endswith('.js'):
                continue
            documents_of_interest = ['tweet.js', 'personalization.js', 'like.js', 'following.js', 'follower.js', 'ad-impressions.js']
            if filename not in documents_of_interest:
                continue
            conversation_id = root.split('/')[-1]
            conversation_with_name = None
            document = os.path.join(root, filename)
            with open(document, "r") as f:
                raw_data = ' '.join(f.read().split('\n'))
                info = re.search(r'window.YTD.(.*).part0 = (\[ \{.*?\} \} \])', raw_data)
                json_data = json.loads(info.group(2))
                type_of_data = info.group(1)
            #Tweets sent by respondent (timestamp, text, but also infos on URLs, Hashtags, people mentioned etc)
            if type_of_data == 'tweet':
                try:
                    tweets_data = json_normalize(json_data)
                    tweets_data.columns = tweets_data.columns.str.replace('^tweet.', '')
                    tweets_data.columns = tweets_data.columns.str.replace('^entities.|^extended_entities', '')
                    tweets_data['created_at'] = pd.to_datetime(tweets_data['created_at'])
                    tweets_data = tweets_data.drop(['source', 'symbols', 'truncated', 'in_reply_to_status_id_str', 'in_reply_to_user_id_str', 'in_reply_to_screen_name', 'id_str'], axis = 1)
                except:
                    tweets_data = []
            #Personalization: What does Twitter think who you are? Mostly interesting for respondents to look at
            elif type_of_data == 'personalization':
                try:
                    personalization_data = json_normalize(json_data)
                    interests = json_normalize(personalization_data['p13nData.interests.interests'][0])
                    age = personalization_data['p13nData.inferredAgeInfo.age'][0][0]
                    gender = personalization_data['p13nData.demographics.genderInfo.gender'][0]
                    advertisers = personalization_data['p13nData.interests.audienceAndAdvertisers.advertisers'][0]
                    shows = personalization_data['p13nData.interests.shows'][0]
                except:
                    log.warning(f"Could not parse {type_of_data}.js correctly.")
            #All the likes of one person (includes text of liked tweet and ID of liked Tweet)
            #Todo: Extract all the URLs from the liked Tweets
            elif type_of_data == 'like':
                try:
                    likes_data = json_normalize(json_data)
                    likes_data.columns = likes_data.columns.str.replace('^like.', '')
                except:
                    log.warning(f"Could not parse {type_of_data}.js correctly.")
            #IDs of all the people the respondent follows
            elif type_of_data == 'following':
                try:
                    following_data = json_normalize(json_data)
                except:
                    log.warning(f"Could not parse {type_of_data}.js correctly.")
            #IDs of all the people that follow the respondent
            elif type_of_data == 'follower':
                try:
                    follower_data = json_normalize(json_data)
                except:
                    log.warning(f"Could not parse {type_of_data}.js correctly.")
            #All of the ad impressions (includes info on advertiser, including Tweet text and URLs)
            elif type_of_data == 'ad_impressions':
                try:
                    ad_impression_data = pd.concat((json_normalize(item['ad']['adsUserData']['adImpressions']['impressions']) for item in json_data), sort = True)
                except:
                    log.warning(f"Could not parse {type_of_data}.js correctly.")
            else:
                log.info(f"Ignored file {type_of_data}.js")
                continue
            data = {
            "tweets":tweets_data,
            "likes":likes_data,
            "followers":follower_data,
            "following":following_data,
            "ad_impressions":ad_impression_data,
            "interests":interests,
            "age":age,
            "gender":gender,
            "advertisers":advertisers,
            "shows":shows
            }
    return data



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='The folder with the Twitter data')
    args = parser.parse_args()


    o = main(args.file, 100000)
