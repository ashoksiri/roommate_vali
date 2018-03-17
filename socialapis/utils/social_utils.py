# -*- coding: utf-8 -*-
import datetime
import re
from decimal import Decimal

import six
from textblob import TextBlob

from socialapis import Sentiment
from socialapis.config import client
from google.cloud.language import enums, types

from pymongo import MongoClient
mangodb = MongoClient('mongodb://10.1.4.64:27017')['geodatabase']
import _mysql


import time


_PROTECTED_TYPES = six.integer_types + (
    type(None), float, Decimal, datetime.datetime, datetime.date, datetime.time
)


import sys

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


def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if issubclass(type(s), six.text_type):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not issubclass(type(s), six.string_types):
            if six.PY3:
                if isinstance(s, bytes):
                    s = six.text_type(s, encoding, errors)
                else:
                    s = six.text_type(s)
            elif hasattr(s, '__unicode__'):
                s = six.text_type(s)
            else:
                s = six.text_type(bytes(s), encoding, errors)
        else:
            # Note: We use .decode() here, instead of six.text_type(s, encoding,
            # errors), so that if s is a SafeBytes, it ends up being a
            # SafeText at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise ValueError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = ' '.join(force_text(arg, encoding, strings_only, errors)
                         for arg in s)
    return s


def removeUrl(text):
    return re.sub(r'http\S+', '', text)


def clean(text):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    text = text.replace('\n',' ')
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w +:\/\/\S +)", " ", text).split())


def get_sentiment(engword):

    if engword is not None and len(engword) > 2:
        without_hyperlink = removeUrl(engword)
        cleaned = clean(without_hyperlink)

        try:
            document = types.Document(
                content=cleaned,
                type=enums.Document.Type.PLAIN_TEXT)

            sentiment = client.analyze_sentiment(document=document).document_sentiment

            if 0.25 < sentiment.score < 1.0:
                return Sentiment(cleaned, sentiment.score, 'positive')
            elif -1.0 < sentiment.score < -0.25:
                return Sentiment(cleaned, sentiment.score, 'negative')
            elif -0.25 < sentiment.score < 0.25:
                return Sentiment(cleaned, sentiment.score, 'neutral')
        except Exception as e:
            return Sentiment('', 0.0, 'neutral')
    else:
        return Sentiment('', 0.0, 'neutral')



# connecting to local mysql database for fetching the data


# try:
#     dbs.query("SELECT * FROM `IN` WHERE `COL3` LIKE '%hyderabad%' LIMIT 1")
# except:
#     dbs.query("SELECT * FROM `IN` WHERE `COL 3` LIKE '%hyderabad%' LIMIT 1")
#
# rea = dbs.store_result()
# try:
#     jformat = rea.fetch_row()
#     jformat = jformat[0]
#     lat = jformat[4]
#     lng = jformat[5]
#     print(lat,lng)
# except:
#     print("there is n record for the given location")


def getGeoLocation(locname,country):
    if country:
        # dbs = _mysql.connect(host="10.1.4.57", port=3306, user="root", passwd="Cosmos12#", db="geodatabase")
        try:
            collection = mangodb[country]
            # get_myobj = collection.find({'$and':[{"country_name":country},{"name":locname}]}).count()
            # myquery = '$and:[{"country_name": "' + country + '"},{"name": "' + locname + '"}]'
            # gexer = '$regex : /'+locname+'/i'

            get_myobj = collection.find({"$and":[{"country_name": country}, { "name" :  {'$regex' : locname, '$options' : 'i'}}]}).limit(1)
            for i in get_myobj:
                lat = i["latitude"]
                lng = i["longitude"]
                c_code = i["country_code"]
                return {"lat": lat, "lon": lng, "c_code": c_code}
            # lat = jformat[2]
            # lng = jformat[3]
            # print(lat, lng)
            # return{"lat": lat, "lon": lng}
        except Exception as e:
            print(e)
            # print("there is no record for the given location")
            # dbs.close()
            # return{}
            # pdb.set_trace()
    else:
        return{}

# getGeoLocation("bangalore","india")
def validate_config(dict):
    pass

# getGeoLocation("bangalore","IN")