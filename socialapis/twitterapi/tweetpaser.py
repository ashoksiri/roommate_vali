# -*- coding: utf-8 -*-
from dateutil.parser import parse
import json
from socialapis.utils.social_utils import force_text

def parse_tweet(tweet):

    temp_tweet = {}

    def parseuser(user):
        temp_user = {}
        temp_user['id'] = user.get('id')
        temp_user['id_str'] = user.get('id_str')
        temp_user['profile_background_image_url_https'] = user.get('profile_background_image_url_https')
        temp_user['profile_image_url_https'] = user.get('profile_image_url_https')
        temp_user['followers_count'] = user.get('followers_count')
        temp_user['listed_count'] = user.get('id')
        temp_user['is_translation_enabled'] = user.get('is_translation_enabled')
        temp_user['utc_offset'] = user.get('utc_offset')
        temp_user['statuses_count'] = user.get('statuses_count')
        temp_user['description'] = user.get('description')
        temp_user['friends_count'] = user.get('friends_count')
        temp_user['location'] = user.get('location')
        temp_user['profile_image_url'] = user.get('profile_image_url')
        temp_user['following'] = user.get('following')
        temp_user['geo_enabled'] = user.get('geo_enabled')
        temp_user['screen_name'] = user.get('screen_name')
        temp_user['lang'] = user.get('lang')
        temp_user['favourites_count'] = user.get('favourites_count')
        temp_user['name'] = user.get('name')
        temp_user['notifications'] = user.get('notifications')
        temp_user['url'] = user.get('url')
        temp_user['created_at'] = parse(user.get('created_at'),ignoretz=True)
        temp_user['time_zone'] = user.get('time_zone')
        temp_user['protected'] = user.get('protected')
        temp_user['is_translator'] = user.get('is_translator')

    def parseplace(place):
        temp_place = {}
        temp_place['id'] = place['id']
        temp_place['full_name'] = place['full_name']
        temp_place['url'] = place['url']
        temp_place['place_type'] = place['place_type']
        temp_place['bounding_box'] = place['bounding_box']
        temp_place['name'] = place['name']
        temp_place['country'] = place['country']
        temp_place['city'] = place['city']

    temp_tweet['text'] = tweet['text']
    temp_tweet['text_parsed'] = tweet['text']
    temp_tweet['id_str'] = tweet['id_str']
    temp_tweet['created_at'] = parse(tweet['created_at'],ignoretz=True)
    temp_tweet['truncated'] = tweet['truncated']
    temp_tweet['is_quote_status'] = tweet['is_quote_status']
    temp_tweet['in_reply_to_status_id_str'] = tweet['in_reply_to_status_id_str']
    temp_tweet['favorite_count'] = tweet['favorite_count']
    temp_tweet['retweeted'] = tweet['retweeted']
    temp_tweet['source'] = tweet['source']
    temp_tweet['in_reply_to_screen_name'] = tweet['in_reply_to_screen_name']
    temp_tweet['quoted_status_id_str'] = tweet.get('quoted_status_id_str')
    temp_tweet['retweet_count'] = tweet['retweet_count']
    temp_tweet['reply_count'] = tweet.get('reply_count') if tweet.get('reply_count') else 0
    temp_tweet['favorited'] = tweet['favorited']
    temp_tweet['in_reply_to_user_id_str'] = tweet['in_reply_to_user_id_str']
    temp_tweet['lang'] = tweet['lang']
    temp_tweet['place'] = parseplace(tweet['place']) if tweet.get("place") else {}
    temp_tweet['entities'] = tweet['entities']
    temp_tweet['user'] = parseuser(tweet['user']) if "user" in tweet else {}
    temp_tweet['polarity'] = tweet.get('polarity')

    return temp_tweet









if __name__ == "__main__":
    with open("tweets.json",'r',encoding='utf-8') as file:
        tweet = json.loads(file.read())
        print(parse_tweet(tweet))