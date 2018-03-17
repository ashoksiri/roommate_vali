
"""
    This Utils package is responsible for getting the tweets from twitter
    api matched with searchkey and convert the response as database structure

"""

import json
import logging



import oauth2
from urllib.parse import urlencode

from socialapis import translate
from socialapis.config import (TWITTER_ACCESS_TOKEN,
                                        TWITTER_ACCESS_TOKEN_SECRET,
                                        TWITTER_CONSUMER_KEY,
                                        TWITTER_CONSUMER_SECRET)

# import tweepy
# consumer_key=TWITTER_CONSUMER_KEY
# consumer_secret=TWITTER_CONSUMER_SECRET
#
# # The access tokens can be found on your applications's Details
# # page located at https://dev.twitter.com/apps (located
# # under "Your access token")
# access_token=TWITTER_ACCESS_TOKEN
# access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
#
# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
#
# api = tweepy.API(auth)
#
# statuses = api.search(q='nara lokesh')
#
# for status in statuses:
#     print(status)
#
#
#
from datetime import datetime

class ApsmaEncoder(json.JSONEncoder):

    def default(self, o):

        if isinstance(o,datetime):
            return o.__str__()
        return str(o)

logger = logging.getLogger(__file__)

SEARCH_URL = 'https://api.twitter.com/1.1/search/tweets.json'
USER_TIME_LINE  = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'
RETWEET_URL = 'https://api.twitter.com/1.1/statuses/retweet/{}.json'

class Twitter(object):

    def __init__(self,access_token,access_token_secret,consumer_key,consumer_secret):
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def oauth_req(self,url,http_method="GET", post_body=b"", http_headers=None):
        consumer = oauth2.Consumer(key=self.consumer_key, secret=self.consumer_secret)
        token = oauth2.Token(key=self.access_token, secret=self.access_token_secret)
        client = oauth2.Client(consumer, token)
        resp, content = client.request( url, method=http_method, body=post_body, headers=http_headers)
        content = content.decode('utf-8')
        return content,resp


    def buildUrl(self,url,**kwargs):
        url =  url+'?'+urlencode(kwargs)
        return url


    def get_user_tweets(self,q,ids,limit=50,**kwargs):

        tweets_final = []
        logger.info("userid param {}".format(ids))

        for id in ids:

            logger.info("userid param {}".format(id))
            print("userid param {}".format(id))
            flag = True
            tweets = []
            count = 0
            max_id = None
            kwargs['user_id'] = id
            kwargs['count'] = 50

            while (flag):
                current_tweet_ids = []
                if max_id:
                    kwargs['max_id'] = max_id
                    url = self.buildUrl(USER_TIME_LINE, **kwargs)
                    data, resp = self.oauth_req(url)

                else:
                    url = self.buildUrl(USER_TIME_LINE, **kwargs)
                    data, resp = self.oauth_req(url)
                data = json.loads(data)
                print("the count of total tweets are **************************",count)

                length = len(data)

                if length == 0:
                    flag = False
                else:
                    for tweet in data:
                        current_tweet_ids.append(tweet.get('id'))
                    max_id = min(current_tweet_ids)

                    data = list(filter(lambda x:json.dumps(x).rfind(q)!=-1,data))
                    length = len(data)


                    count = count + length

                    if length == 0:
                        flag = False
                    else:
                        for tweet in data:
                            current_tweet_ids.append(tweet.get('id'))
                        max_id = min(current_tweet_ids)

                    tweets = tweets + translate().process_tweets(data)

                    if count > limit:
                        flag = False

            if count < limit:
                logger.warning("Requested {} Tweets but got {} tweets from Api ".format(limit, len(tweets)))

            tweets_final += tweets

        return tweets_final

    def getTweets(self,q,limit=100,**kwargs):

        logger.info("q param {}".format(q))
        flag = True
        tweets = []
        count = 0
        max_id = None
        kwargs['q'] = q
        kwargs['count'] = 100

        while(flag):
            current_tweet_ids = []
            if  max_id:
                kwargs['max_id'] = max_id
                url = self.buildUrl(SEARCH_URL, **kwargs)
                data , resp = self.oauth_req(url)
            else:
                url = self.buildUrl(SEARCH_URL, **kwargs)
                data ,resp = self.oauth_req(url)

            data  = json.loads(data)

            length = len(data['statuses'])

            count = count + length

            if length == 0:
                flag = False
            else:
                for tweet in data['statuses']:
                    current_tweet_ids.append(tweet.get('id'))
                max_id = min(current_tweet_ids)

            tweets = tweets +  translate().process_tweets(data['statuses'])


            if count > limit:
                return tweets[:limit]

        if count < limit:
            logger.warning("Requested {} Tweets but got {} tweets from Api ".format(limit,len(tweets)))
        return tweets


    def retweet(self,tweet_id):

        url = RETWEET_URL.format(tweet_id)
        content,resp = self.oauth_req(url, http_method='POST')
        return content,resp

    def reply(self,tweet_id,message):

        url = TWEET_URL
        params = {'status' : message,'in_reply_to_status_id' : tweet_id}
        url = self.buildUrl(url,**params)
        content, resp = self.oauth_req(url,http_method='POST')

        return content, resp

if __name__ == '__main__':
    twitter = Twitter(consumer_key=TWITTER_CONSUMER_KEY,consumer_secret=TWITTER_CONSUMER_SECRET,
                      access_token=TWITTER_ACCESS_TOKEN,access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)
    #print(json.dumps(twitter.getTweets(q='narendramodi'),cls=ApsmaEncoder))
    print(json.dumps(twitter.getTweets(q='@msdhoni'), cls=ApsmaEncoder))