# -*- coding: utf-8 -*-
"""
Translator module that uses the Google Translate API.

Adapted from Terry Yin's google-translate-python.
Language detection added by Steven Loria.
"""


import codecs
import ctypes
import json
import datetime
import re
from decimal import Decimal

from queue import Queue
from threading import Thread
import time
import requests

from dateutil.parser import parse
from socialapis import get_sentiment
from socialapis.utils import getGeoLocation

import six

_PROTECTED_TYPES = six.integer_types + (
    type(None), float, Decimal, datetime.datetime, datetime.date, datetime.time
)

from pymongo import MongoClient

db = MongoClient('mongodb://10.1.4.64:27017')['geodb']['geocoder']

import sys

import logging


logger = logging.getLogger(__name__)

PY2 = int(sys.version[0]) == 2

if PY2:

    import urllib2 as request
    from urllib.parse import quote as urlquote
    from urllib.parse import urlencode

    text_type = str
    binary_type = str
    string_types = (str, str)
    str = str
    str = str
    imap = imap
    izip = izip


    def implements_to_string(cls):
        """Class decorator that renames __str__ to __unicode__ and
        modifies __str__ that returns utf-8.
        """
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls
else:  # PY3
    from urllib import request
    from urllib.parse import quote as urlquote
    from urllib.parse import urlencode

    text_type = str
    binary_type = bytes
    string_types = (str,)
    str = str
    str = (str, bytes)
    imap = map
    izip = zip
    import csv

    implements_to_string = lambda x: x


# From six
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""

    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):  # noqa

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, 'temporary_class', (), {})


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_text(strings_only=True).
    """
    return isinstance(obj, _PROTECTED_TYPES)

concurrent = 200


class Request(dict):
    """
    A simple model that wraps mongodb document
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__



class Translator(object):

    """A language translator and detector.

    Usage:
    ::
        >>> from textblob.translate import Translator
        >>> t = Translator()
        >>> t.translate('hello', from_lang='en', to_lang='fr')
        u'bonjour'
        >>> t.detect("hola")
        u'es'
    """

    url = "http://translate.google.com/translate_a/t?client=webapp&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=at&ie=UTF-8&oe=UTF-8&otf=2&ssel=0&tsel=0&kc=1"

    headers = {
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
            'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19')
    }

    def __init__(self):
        self.q = Queue(concurrent * 2)
        self.session = requests.Session()

    def get_translate_url(self, source, from_lang='auto', to_lang='en'):

        if PY2:
            source = source.encode('utf-8')
        data = {"q": source}
        url = '{url}&sl={from_lang}&tl={to_lang}&hl={to_lang}&tk={tk}'.format(
            url=self.url,
            from_lang=from_lang,
            to_lang=to_lang,
            tk=_calculate_tk(source),
        )
        encoded_data = urlencode(data).encode('utf-8')
        return url, self.headers, encoded_data

    def get_url(self, source, from_lang='auto', to_lang='en'):

        if PY2:
            source = source.encode('utf-8')
        data = {"q": source}
        url = '{url}&sl={from_lang}&tl={to_lang}&hl={to_lang}&tk={tk}'.format(
            url=self.url,
            from_lang=from_lang,
            to_lang=to_lang,
            tk=_calculate_tk(source),
        )
        encoded_data = urlencode(data).encode('utf-8')
        return url, encoded_data

    def translate(self, source, from_lang='auto', to_lang='en', host=None, type_=None):
        """Translate the source text from one language to another."""
        if PY2:
            source = source.encode('utf-8')
        data = {"q": source}
        url = '{url}&sl={from_lang}&tl={to_lang}&hl={to_lang}&tk={tk}'.format(
            url=self.url,
            from_lang=from_lang,
            to_lang=to_lang,
            tk=_calculate_tk(source),
        )
        response = self._request(url, host=host, type_=type_, data=data)
        result = json.loads(response)
        if isinstance(result, list):
            try:
                result = result[0]  # ignore detected language
            except IndexError:
                pass
        self._validate_translation(source, result)
        return result

    def detect(self, source, host=None, type_=None):
        """Detect the source text's language."""
        if PY2:
            source = source.encode('utf-8')
        if len(source) < 3:
            raise ValueError('Must provide a string with at least 3 characters.')
        data = {"q": source}
        url = '{url}&sl=auto&tk={tk}'.format(url=self.url, tk=_calculate_tk(source))
        response = self._request(url, host=host, type_=type_, data=data)
        result, language = json.loads(response)
        return language

    def _validate_translation(self, source, result):
        """Validate API returned expected schema, and that the translated text
        is different than the original string.
        """
        if not result:
            raise ValueError('Translation API returned and empty response.')
        if PY2:
            result = result.encode('utf-8')
        if result.strip() == source.strip():
            raise ValueError('Translation API returned the input string unchanged.')

    def _request(self, url, host=None, type_=None, data=None):
        encoded_data = urlencode(data).encode('utf-8')
        req = request.Request(url=url, headers=self.headers, data=encoded_data)
        if host or type_:
            req.set_proxy(host=host, type=type_)
        resp = request.urlopen(req)
        content = resp.read()
        return content.decode('utf-8')

    def doWork(self):
        while True:
            request = self.q.get()
            response = request.session.post(url=request.url, headers=request.headers, data=request.body)
            self.doSomethingWithResult(response, datatype=request.datatype)
            self.q.task_done()


    def get_cordinates(self,loc):
        #logger.info("Getting Location for location {}".format(loc))
        if loc:
            try:
                locs = [x.strip() for x in loc.split(',')]
                if len(locs) > 0:
                    if len(locs) > 1:
                        # city = locs[0]
                        # country = myconts.get(locs[1].lower()) or "" if len(locs[1]) > 2 else locs[1] or ""
                        geo_obj = getGeoLocation(locs[0], locs[1].lower())
                        if geo_obj:
                            print("trying to add location cordinates for user tweet")
                            d = {}
                            d['geo_lat'] = geo_obj.get('lat', '')
                            d['geo_lon'] = geo_obj.get('lon', '')
                            d['c_code'] = geo_obj.get('c_code', '')
                            return {"lat": d['geo_lat'], "lon": d['geo_lon'], "c_code": d['c_code']}
                        else:
                            print("location is empty")
            except Exception as e:
                print("there is some encoding error")
                print("error is: {0}".format(e))

    def doSomethingWithResult(self, resp, datatype):
        if resp.status_code == 200:
            data = json.loads(resp.content.decode('utf-8'))

            if datatype == 'tweet':
                temp_tweet_id = resp.request.headers.get('tweet_id')
                temp_tweet = self.temp_tweets[temp_tweet_id]
                temp_tweet['text_parsed'] = data[0]
                temp_tweet['polarity'] = get_sentiment(data[0]).__polarity__()
                temp_tweet['created_at'] = parse(temp_tweet['created_at'].__str__(), ignoretz=True)

                # geocoding test starts here
                location = temp_tweet['user']
                if 'location' in location and location.get('location'):
                    location = location['location'].encode('utf-8').strip()
                    location = location.decode("utf-8")
                    geo_cordinates = self.get_cordinates(location)
                    if geo_cordinates:
                        temp_tweet['loc'] = {}
                        temp_tweet['loc']['type'] = 'Point'
                        temp_tweet['loc']['coordinates'] = [geo_cordinates.get('lon', ''),geo_cordinates.get('lat', '')]
                        temp_tweet['c_code'] = geo_cordinates.get('c_code', '')
                # geocoding test ends here

                self.temp_tweets[temp_tweet_id] = temp_tweet

            if datatype == 'post':
                temp_post_id = resp.request.headers.get('post_id')
                temp_post = self.temp_posts[temp_post_id]
                temp_post['message_parsed'] = data[0]
                temp_post['polarity'] = get_sentiment(data[0]).__polarity__()
                temp_post['lang'] = data[1]
                self.temp_posts[temp_post_id] = temp_post

            if datatype == 'comment':
                temp_comment_id = resp.request.headers.get('comment_id')
                temp_comment = self.temp_comments[temp_comment_id]
                temp_comment['message_parsed'] = data[0]
                temp_comment['polarity'] = get_sentiment(data[0]).__polarity__()
                temp_comment['lang'] = data[1]
                self.temp_comments[temp_comment_id] = temp_comment

            if datatype == 'video':
                temp_video_id = resp.request.headers.get('video_id')
                temp_video = self.temp_videos[temp_video_id]
                temp_video['snippet']['descriptionParsed'] = data[0]
                temp_video['polarity'] = get_sentiment(data[0]).__polarity__()
                temp_video['lang'] = data[1]
                comments = temp_video.get('comments',[])
                temp_video['comments'] = Translator().process_video_comments(comments)
                temp_video['snippet']['publishedAt'] = parse(temp_video['snippet']['publishedAt'].__str__(),ignoretz=True)
                self.temp_videos[temp_video_id] = temp_video

            if datatype == 'video_comment':
                temp_video_comment_id = resp.request.headers.get('video_comment_id')
                temp_comment = self.temp_video_comments[temp_video_comment_id]
                temp_comment['snippet']['topLevelComment']['snippet']['textOriginalParsed'] = data[0]
                temp_comment['polarity'] = get_sentiment(data[0]).__polarity__()
                temp_comment['lang'] = data[1]
                self.temp_video_comments[temp_video_comment_id] = temp_comment


    def index_tweets(self, tweets):
        self.temp_tweets = {}
        for tweet in tweets:
            self.temp_tweets[tweet['id_str']] = tweet

    def index_comments(self, comments):
        self.temp_comments = {}
        for comment in comments:
            self.temp_comments[comment['id']] = comment

    def index_posts(self, posts):
        self.temp_posts = {}
        for post in posts:
            self.temp_posts[post.get('id')] = post

    def index_videos(self, videos):
        self.temp_videos = {}
        for video in videos:
            self.temp_videos[video.get('videoId')] = video

    def index_video_comments(self,comments):
        self.temp_video_comments = {}
        for comment in comments:
            self.temp_video_comments[comment['id']] = comment



    def process_tweets(self, data):

        self.index_tweets(data)
        for i in range(len(data)):
            t = Thread(target=self.doWork)
            t.daemon = True
            t.start()
        try:
            for tweet in data:

                url, body = self.get_url(tweet['text'])
                headers = {
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                    'User-Agent': (
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
                        'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'),
                    'tweet_id': tweet.get('id_str')
                }

                request = Request(url=url, headers=headers, body=body, session=self.session, datatype='tweet')
                self.q.put(request)
            self.q.join()

        except KeyboardInterrupt:
            sys.exit(1)

        return list(self.temp_tweets.values())

    def process_video_comments(self,data):

        self.index_video_comments(data)

        for i in range(len(data)):
            t = Thread(target=self.doWork)
            t.daemon = True
            t.start()
        try:
            for comment in data:
                url, body = self.get_url(comment.get('snippet').get('topLevelComment').get('snippet').get('textOriginal'))

                headers = {
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                    'User-Agent': (
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
                        'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'),
                    'video_comment_id': comment.get('id')
                }

                request = Request(url=url, headers=headers, body=body, session=self.session, datatype='video_comment')
                self.q.put(request)
            self.q.join()

        except KeyboardInterrupt:
            sys.exit(1)

        return list(self.temp_video_comments.values())

    def process_videos(self, data):

        self.index_videos(data)

        for i in range(len(data)):
            t = Thread(target=self.doWork)
            t.daemon = True
            t.start()
        try:
            for video in data:
                url, body = self.get_url(video.get('snippet').get('description'))
                headers = {
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                    'User-Agent': (
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
                        'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'),
                    'video_id': video.get('videoId')
                }

                request = Request(url=url, headers=headers, body=body, session=self.session, datatype='video')
                self.q.put(request)
            self.q.join()

        except KeyboardInterrupt:
            sys.exit(1)

        return list(self.temp_videos.values())


    def process_posts(self, data):

        self.index_posts(data)

        for i in range(len(data)):
            t = Thread(target=self.doWork)
            t.daemon = True
            t.start()
        try:
            for post in data:
                if post.get('message') and post.get('message') != '':
                    url, encoded_data = self.get_url(post.get('message'))
                    post_id = post.get('id') if 'id' in post else post.get('postid')
                    headers = {
                        'Accept': '*/*',
                        'Connection': 'keep-alive',
                        'User-Agent': (
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
                            'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'),
                        'post_id': post_id
                    }
                    request = Request(url=url, headers=headers, session=self.session, body=encoded_data,
                                      datatype='post')
                    self.q.put(request)
                else:

                    temp_post_id = post.get('id') if 'id' in post else post.get('postid')
                    temp_post = self.temp_posts[temp_post_id]
                    temp_post['message_parsed'] = post.get('message')
                    # temp_post['polarity'] = get_sentiment('').__polarity__()
                    temp_post['lang'] = None
                    self.temp_posts[temp_post_id] = temp_post
            self.q.join()
        except KeyboardInterrupt:
            sys.exit(1)

        self.q.empty()
        self.session.close()
        return self.temp_posts.values()


    def process_comments(self, data):

        self.index_comments(data)

        for i in range(len(data)):
            t = Thread(target=self.doWork)
            t.daemon = True
            t.start()
        try:
            for comment in data:

                comment_id = comment.get('id') if 'id' in comment else comment.get('commentid')

                if comment.get('message') and comment.get('message') != '':
                    url, encoded_data = self.get_url(comment.get('message'))

                    headers = {
                        'Accept': '*/*',
                        'Connection': 'keep-alive',
                        'User-Agent': (
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
                            'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'),
                        'comment_id': comment_id
                    }
                    request = Request(url=url, headers=headers, body=encoded_data, session=self.session,
                                      datatype='comment')
                    self.q.put(request)

                else:
                    temp_comment_id = comment_id
                    temp_comment = self.temp_comments[temp_comment_id]
                    temp_comment['message_parsed'] = comment.get('message')
                    # temp_comment['polarity'] = get_sentiment('').__polarity__()
                    temp_comment['lang'] = None
                    self.temp_comments[temp_comment_id] = temp_comment

            self.q.join()
        except KeyboardInterrupt:
            sys.exit(1)
        self.q.empty()
        self.session.close()
        return self.temp_comments.values()


def _unescape(text):
    """Unescape unicode character codes within a string.
    """
    pattern = r'\\{1,2}u[0-9a-fA-F]{4}'
    return re.sub(pattern, lambda x: codecs.getdecoder('unicode_escape')(x.group())[0], text)


def _calculate_tk(source):
    """Reverse engineered cross-site request protection."""
    # Source: https://github.com/soimort/translate-shell/issues/94#issuecomment-165433715
    # Source: http://www.liuxiatool.com/t.php

    tkk = [406398, 561666268 + 1526272306]
    b = tkk[0]

    if PY2:
        d = list(map(ord, source))
    else:
        d = source.encode('utf-8')

    def RL(a, b):
        for c in range(0, len(b) - 2, 3):
            d = b[c + 2]
            d = ord(d) - 87 if d >= 'a' else int(d)
            xa = ctypes.c_uint32(a).value
            d = xa >> d if b[c + 1] == '+' else xa << d
            a = a + d & 4294967295 if b[c] == '+' else a ^ d
        return ctypes.c_int32(a).value

    a = b

    for di in d:
        a = RL(a + di, "+-a^+6")

    a = RL(a, "+-3^+b+-f")
    a ^= tkk[1]
    a = a if a >= 0 else ((a & 2147483647) + 2147483648)
    a %= pow(10, 6)

    tk = '{0:d}.{1:d}'.format(a, a ^ b)
    return tk

