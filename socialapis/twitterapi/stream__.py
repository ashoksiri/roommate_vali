#
#
# from tweepy import OAuthHandler, StreamListener, Stream
#
# TWITTER_CONSUMER_KEY="RF4wlvvvyKucIi9H1pke46Lhk"
# TWITTER_CONSUMER_SECRET="Jut4hf7m6tIn1Z4ftYPGSsACENpSFVziANEk9eQNgaE0KP3L5M"
# TWITTER_ACCESS_TOKEN="848949254290788352-i8KrkbyV31L6GzvqwxcpC4TBU0FkuPd"
# TWITTER_ACCESS_TOKEN_SECRET="lo2EV31yxeLJAQ2PIw9iN1CiwYDaOYGwTZwWX4jh37eRy"
#
# auth = OAuthHandler(consumer_key=TWITTER_CONSUMER_KEY, consumer_secret=TWITTER_CONSUMER_SECRET)
# auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
#
#
# class Listener(StreamListener):
#
#     def on_data(self, raw_data):
#         print(raw_data)
#
#
# s = Stream(auth=auth,listener=Listener())
# s.filter(track=['crime'])

from pymongo import MongoClient
import pymongo

db = MongoClient('mongodb://10.1.4.64:27017')['geodb']['geocoder']

fields =[("name", pymongo.DESCENDING),("country_name", pymongo.ASCENDING),("country_code", pymongo.ASCENDING)]

db.create_index(keys=fields,unique=True)

print("done")