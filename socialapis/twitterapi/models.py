from django.db import models

from datetime import datetime
import json


# Create your models here.

class Address(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)



class Place(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    full_name = models.CharField(max_length=50, null=True)
    url = models.CharField(max_length=200, null=True)
    place_type = models.CharField(max_length=50, null=True)
    bounding_box = models.TextField(default="", null=True)
    name = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)



class TUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    id_str = models.CharField(max_length=50)
    profile_background_image_url_https = models.TextField(default="", null=True)
    profile_image_url_https = models.CharField(max_length=200, null=True)
    followers_count = models.IntegerField()
    listed_count = models.IntegerField()
    is_translation_enabled = models.BooleanField(default=False)
    utc_offset = models.IntegerField(null=True)
    statuses_count = models.IntegerField(null=True)
    description = models.TextField(default="", null=True)
    friends_count = models.IntegerField()
    location = models.TextField(default="", null=True)
    profile_image_url = models.CharField(max_length=200, null=True)
    following = models.BooleanField(default=False)
    geo_enabled = models.BooleanField(default=False)
    screen_name = models.CharField(max_length=100)
    lang = models.CharField(max_length=20)
    favourites_count = models.IntegerField()
    name = models.CharField(max_length=100)
    notifications = models.BooleanField(default=False)
    url = models.CharField(max_length=200)
    created_at = models.DateTimeField(null=True)
    time_zone = models.CharField(max_length=25, null=True)
    protected = models.BooleanField(default=False)
    is_translator = models.BooleanField(default=False)



class Polarity(models.Model):
    key = models.CharField(max_length=20, null=True)
    value = models.FloatField(null=True)



class Tweet(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(default="", null=True)
    id_str = models.CharField(max_length=50, null=True, unique=True)
    created_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    truncated = models.BooleanField(default=False)

    text_parsed = models.TextField(default="", null=True)
    is_quote_status = models.BooleanField(default=False)
    in_reply_to_status_id_str = models.CharField(null=True, max_length=50)

    favorite_count = models.IntegerField(default=0)
    retweeted = models.BooleanField(default=False)

    # coordinates = models.EmbeddedDocumentField(Coordinates, null=True)
    source = models.TextField(default="", null=True)
    in_reply_to_screen_name = models.CharField(null=True, max_length=50)
    quoted_status_id_str = models.CharField(null=True, max_length=50)

    retweet_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    favorited = models.BooleanField(default=False)

    in_reply_to_user_id_str = models.CharField(null=True, max_length=50)
    lang = models.CharField(max_length=10, null=True)
    place = models.ForeignKey(Place, null=True)
    entities = models.TextField(default="", null=True)
    user = models.ForeignKey(TUser, null=True)
    polarity = models.ForeignKey(Polarity, null=True)
    searchKey = models.CharField(max_length=50, null=True)
    sourceType = models.CharField(default='twitter', max_length=10)

    def set_entities(self, x):
        self.entities = json.dumps(x)

    # def get_entities(self):
    #     return json.loads(self.entities)