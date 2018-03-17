# -*- coding: utf-8 -*-
"""
    This Utils package is responsible for getting the tweets from twitter
    api matched with searchkey and convert the response as database structure

"""

import json
import logging

import oauth2
from urllib.parse import urlencode
from socialapis.config.tokens import (
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET
)
from dateutil.parser import parse
from django.utils.encoding import smart_text


def parsedata(q,tweet):
    pass


logger = logging.getLogger(__file__)

SEARCH_URL = 'https://api.twitter.com/1.1/search/tweets.json'


def oauth_req(url, http_method="GET", post_body=b"", http_headers=None):
    consumer = oauth2.Consumer(key=TWITTER_CONSUMER_KEY, secret=TWITTER_CONSUMER_SECRET)
    token = oauth2.Token(key=TWITTER_ACCESS_TOKEN, secret=TWITTER_ACCESS_TOKEN_SECRET)
    client = oauth2.Client(consumer, token)
    resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
    content = content.decode('utf-8')
    return content


def buildUrl(url, **kwargs):
    url = url + '?' + urlencode(kwargs)
    return url


def dict_clean(items):
    result = {}
    for key, value in items:
        if value is None:
            if key in ['url']:
                value = ''
        if isinstance(value, str) or isinstance(value, bytes):
            value = value.encode('utf-8')
        result[key] = value
    return result


def process_tweet(q, tweet):
    del tweet['id']
    tweet['created_at'] = parse(tweet['created_at'], ignoretz=True)
    tweet['user']['created_at'] = parse(tweet['user']['created_at'], ignoretz=True)
    tweet['text_parsed'] = tweet['text']
    tweet['searchKey'] = q
    # processed.append(tweet)
    # if tweet.get('retweeted_status') :
    #     process_tweet(q,tweet.get('retweeted_status'),processed)
    return tweet


def getTweets(q, limit=100, **kwargs):
    logger.info("q param {}".format(q))
    flag = True
    tweets = []
    count = 0
    max_id = None
    kwargs['q'] = q
    kwargs['count'] = 100

    while (flag):
        current_tweet_ids = []
        if max_id:
            kwargs['max_id'] = max_id
            url = buildUrl(SEARCH_URL, **kwargs)
            data = json.loads(oauth_req(url), object_pairs_hook=dict_clean)
        else:
            url = buildUrl(SEARCH_URL, **kwargs)
            data = json.loads(oauth_req(url), object_pairs_hook=dict_clean)

        length = len(data['statuses'])

        count = count + length

        processed_tweets = []

        if length == 0:
            flag = False
        else:
            for tweet in data['statuses']:
                current_tweet_ids.append(tweet.get('id'))
                processed_tweets.append(tweet)
                # pytho#     })
            max_id = min(current_tweet_ids)

        tweets = tweets + processed_tweets

        if count > limit:
            return tweets[:limit]

    if count < limit:
        logger.warning("Requested {} Tweets but got {} tweets from Api ".format(limit, len(tweets)))
    return tweets


if __name__ == '__main__':
    for tweet in getTweets('lokesh babu'):
        print(json.dumps(tweet))