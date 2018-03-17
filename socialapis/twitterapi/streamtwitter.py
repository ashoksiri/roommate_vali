import json
from itertools import groupby

from django.db.models import Q
from django.forms import model_to_dict

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import StreamListener

from socialanalytics.utils import inserttweets

from fuzzywuzzy import fuzz
from socialapis import translate

from usermanage.models import ChannelConfig, Tracking, AlertMonitoring
from usermanage.models import ClientKeyword
from usermanage.serializers import TrackingSerializer, AlertMonitoringSerializer

from socialanalytics import db
import logging

log = logging.getLogger(__name__)

class Controller(object):

    def __init__(self,keywords:list,stream:Stream,config:ChannelConfig,track:Tracking):
        self.keywords = keywords
        self.stream = stream
        self.config = config
        self.track = track


    def check_keyword_change(self):
        log.info("Checking alert keyword changes in the database.....{}".format(self.config.client.id))
        keywords = ClientKeyword.objects.filter(client=self.config.client, is_keyword_alert=1,status=1)
        keywords = [keyword.keyword.keyword for keyword in keywords if keyword.keyword.status != 0]
        flag = False
        if set(keywords) != set(self.keywords):
            self.keywords = keywords
            flag = True
        log.info("Status is {} and keywords fron db = {} keyword from listener = {} ".format(flag,keywords,self.keywords))
        return flag


    def change_alert_record(self,key,min_id,max_id,count):

        log.info('min_id {}'.format(min_id))
        log.info('max_id {}'.format(max_id))
        log.info('new Records {}'.format(count))


        keywords = ClientKeyword.objects.filter(client=self.track.client,is_keyword_alert=1)

        for keyword in keywords:
            if keyword.keyword.keyword == key:
                doc = AlertMonitoring.objects.filter(Q(client=self.track.client) &
                                            Q(keyword=keyword) &
                                            Q(source_type='twitter') ).order_by('-id')[:1]
                doc = list(doc)
                if len(doc)>0:

                    doc = doc[0]
                    initial_count = doc.initial_count

                    if doc.actual_count:
                        initial_count = doc.actual_count


                    data = {
                        'user': doc.user.id,
                        'client': doc.client.id,
                        'keyword': doc.keyword.id,
                        'initial_count': initial_count,
                        'actual_count':initial_count + count,
                        'max_id': max_id.__str__(),
                        'min_id':min_id.__str__(),
                        'source_type': doc.source_type,
                        'status': 1,
                        'read_flag': 0,
                    }

                    serializer = AlertMonitoringSerializer(data=data)
                    if serializer.is_valid(raise_exception=False):
                        serializer.save()
                        log.info(serializer.data)
                    else:
                        log.info(serializer.errors)
                    if doc.status  == 2:
                        self.stream.disconnect()

    def insert_tweet_data(self,data):
        tweets = translate().process_tweets(data)
        grouped_tweets = groupby(tweets, lambda x: x.get('searchKey'))
        for key, value in grouped_tweets:
            inserted_ids = inserttweets(db=db, data=list(value))
            if len(inserted_ids) > 0:
                min_id = inserted_ids[0]
                max_id = inserted_ids[len(inserted_ids)-1]
                log.info("{} No of Documents with {} inserted Successfully ... ".format(len(inserted_ids),key))
                self.change_alert_record(key, min_id, max_id, len(list(inserted_ids)))



class MyListener(StreamListener,Controller):
    tweets = []
    counter = 0
    stream_counter = 0
    keyword_changed = False

    def on_data(self, raw_data):

        self.stream_counter += 1
        try:
            for keyword in self.keywords:
                if fuzz.partial_token_set_ratio(json.dumps(raw_data),keyword) == 100:
                    tweet = json.loads(raw_data)
                    tweet.update({'searchKey':keyword})


                    if self.stream_counter % 10 == 0:
                        log.info("Tweets got {}".format(self.stream_counter))
                        self.keyword_changed = self.check_keyword_change()

                    if self.keyword_changed:
                        log.info("Before Disconnecting ......")
                        self.stream.disconnect()
                        update_tracking_status(self.track, status=2)
                        self.insert_tweet_data(self.tweets)
                        if len(self.keywords)>0:
                            start_track(self.config,self.keywords,self.track,recalled=True)
                        self.counter = 0
                        self.tweets = []

                    self.tweets.append(tweet)
                    self.counter = self.counter + 1
                    if self.counter == 100 :
                        self.insert_tweet_data(self.tweets)
                        self.tweets = []
                        self.counter = 0
        except Exception as e :
            log.error(e)
            self.stream.disconnect()
            update_tracking_status(self.track, status=2)
            self.insert_tweet_data(self.tweets)
            start_track(self.config, self.keywords, self.track, recalled=True)
            self.counter = 0
            self.tweets = []



    def on_limit(self, track):
        log.info(track)
    def on_error(self, status_code):
        log.error("Error occured with status {}".format(status_code))
        update_tracking_status(self.track, status=2)
        self.stream.disconnect()

    def on_disconnect(self, notice):
        log.error("session disconnected with notice {}".format(notice))
        update_tracking_status(self.track, status=2)
        self.insert_tweet_data(self.tweets)
        if len(self.keywords) > 0:
            start_track(self.config, self.keywords, self.track, recalled=True)
        self.counter = 0
        self.tweets = []



def update_tracking_status(instance,status=2):


    data = model_to_dict(instance)
    data.update({'status':status})
    serializer = TrackingSerializer(data=data,instance=instance)
    if serializer.is_valid(raise_exception=False):
        log.info("Track Status Updated to {}".format(status))
        serializer.save()
    else:
        log.info(serializer.errors)



def start_track(config:ChannelConfig,keywords:list,track:Tracking,recalled=False):

    keywords = json.loads(track.keywords)

    if len(keywords) == 0:
        log.info("Stream Not Started...")
    else:
        log.info("new Stream started successfully.....")

        if not recalled:
            config = config.get_decoded(email=config.user.email)

        auth = OAuthHandler(consumer_key=config.twitter_consumer_key, consumer_secret=config.twitter_consumer_secret)
        auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)

        keywords =keywords
        listener = MyListener()
        listener.keywords = keywords
        listener.config = config
        listener.track = track
        listener.keyword_changed = False
        listener.check_keyword_change()

        log.info("Listner instantiation {}".format(config.user))

        update_tracking_status(track,status=1)

        s = Stream(auth=auth, listener=listener)
        listener.stream = s

        s.filter(track=keywords)
        log.info("Stream disconnected successfully.....")
        update_tracking_status(track)