import json
from dateutil.parser import parse
import datetime

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.__str__()
        if hasattr(obj,'__dict__'):
            return obj.__dict__()
        else:
            return json.JSONEncoder.default(self, obj)

class BasicPage(object):

    def __init__(self,id,fan_count,name):
        self.id = id
        self.fan_count = fan_count
        self.name = name

    def __iter__(self):
        yield 'id',self.id
        yield 'fan_count',self.fan_count
        yield 'name',self.name

    def __dict__(self):
        return dict(self)

    def __json__(self):
        return json.dumps(self.__dict__())


class Adress(object):

    def __init__(self,**kwargs):
        kwargs = kwargs['data'] if 'data' in kwargs else {}
        self.id = kwargs['id'] if 'id' in kwargs else None
        self.city = kwargs['city'] if 'city' in kwargs else None
        self.city_page = kwargs['city_page'] if 'city_page' in kwargs else None
        self.country = kwargs['country'] if 'country' in kwargs else None
        self.postal_code = kwargs['postal_code'] if 'postal_code' in kwargs else None
        self.region = kwargs['region'] if 'region' in kwargs else None
        self.street1 = kwargs['street1'] if 'street1' in kwargs else None
        self.street2 = kwargs['street2'] if 'street2' in kwargs else None

    def __iter__(self):
        yield 'id',self.id
        yield 'city',self.city
        yield 'city_page',self.city_page
        yield 'country',self.country
        yield 'postal_code',self.postal_code
        yield 'region',self.region
        yield 'street1',self.street1
        yield 'street2',self.street2

    def __dict__(self):
        return dict(self)

    def __json__(self):
        return json.dumps(self.__dict__())

class Location(object):

    def __init__(self,**kwargs):
        kwargs = kwargs['data'] if 'data' in kwargs else {}
        self.city_id = kwargs['city_id'] if 'city_id' in kwargs else None
        self.city = kwargs['city'] if 'city' in kwargs else None
        self.state = kwargs['state'] if 'state' in kwargs else None
        self.country = kwargs['country'] if 'country' in kwargs else None
        self.street = kwargs['street'] if 'street' in kwargs else None
        self.zip = kwargs['zip'] if 'zip' in kwargs else None
        self.latitude = kwargs['latitude'] if 'latitude' in kwargs else None
        self.longitude = kwargs['longitude'] if 'longitude' in kwargs else None

    def __iter__(self):
        yield 'city_id',self.city_id
        yield 'city',self.city
        yield 'state',self.state
        yield 'country',self.country
        yield 'street',self.street
        yield 'zip',self.zip
        yield 'latitude',self.latitude
        yield 'longitude',self.longitude

    def __dict__(self):
        return dict(self)

    def __json__(self):
        return json.dumps(self.__dict__())

def parseLocation(location):
        """
        This will return dictionary of the location having below fields.
        if values presented in the given location the fields will be sent if not None values will be sent
        :param location: dictionary
        :return: dictionary
        """


        place = {'city'          : location.get('city',None),
                'city_id'       : location.get('city_id',None),
                'country'       : location.get('country', None),
                'country_code'  : location.get('country_code', None),
                'latitude'      : location.get('latitude', None),
                'located_in'    : location.get('located_in', None),
                'longitude'     : location.get('longitude', None),
                'name'          : location.get('name', None),
                'region'        : location.get('region', None),
                'region_id'     : location.get('region_id', None),
                'state'         : location.get('state', None),
                'street'        : location.get('street', None),
                'zip'           : location.get('zip', None),
        }

        return place

class Page(object):

    def __init__(self,**kwargs):
        kwargs = kwargs['data'] if 'data' in kwargs else {}
        self.id = kwargs['id'] if 'id' in kwargs else None
        self.about = kwargs['about'] if 'about' in kwargs else None
        self.fan_count = kwargs['fan_count'] if 'fan_count' in kwargs else None
        self.bio = kwargs['bio'] if 'bio' in kwargs else None
        self.category = kwargs['category'] if 'category' in kwargs else None
        self.company_overview = kwargs['company_overview'] if 'company_overview' in kwargs else None
        self.contact_address = Adress(data=kwargs['contact_address']) if 'contact_address' in kwargs else None
        self.picture = kwargs['picture']['data']['url'] if 'picture' in kwargs else None
        self.current_location = kwargs['current_location'] if 'current_location' in kwargs else None
        self.description = kwargs['description'] if 'description' in kwargs else None
        self.description_html = kwargs['description_html'] if 'description_html' in kwargs else None
        self.general_info = kwargs['general_info'] if 'general_info' in kwargs else None
        self.link = kwargs['link'] if 'link' in kwargs else None
        location = parseLocation(kwargs.get('location')) if 'location' in kwargs else None
        self.location = location
        self.new_like_count = kwargs['new_like_count'] if 'new_like_count' in kwargs else None
        self.name = kwargs['name'] if 'name' in kwargs else None
        self.phone = kwargs['phone'] if 'phone' in kwargs else None
        self.rating_count = kwargs['rating_count'] if 'rating_count' in kwargs else None
        self.talking_about_count = kwargs['talking_about_count'] if 'talking_about_count' in kwargs else None
        self.website = kwargs['website'] if 'website' in kwargs else None
        self.were_here_count = kwargs['were_here_count'] if 'were_here_count' in kwargs else None

    def __str__(self):
        return super(Page, self).__str__()

    def __iter__(self):
        yield 'pageid',self.id
        yield 'about',self.about
        yield 'fan_count',self.fan_count
        yield 'bio',self.bio
        yield 'category',self.category
        yield 'company_overview' ,self.company_overview
        yield 'contact_address',self.contact_address
        yield 'picture',self.picture
        yield 'current_location',self.current_location
        yield 'description',self.description
        yield 'description_htmls',self.description_html
        yield 'general_info',self.general_info
        yield 'link',self.link
        yield 'location',self.location
        yield 'new_like_count',self.new_like_count
        yield 'name',self.name
        yield 'phone',self.phone
        yield 'rating_count' , self.rating_count
        yield 'talking_about_count',self.talking_about_count
        yield 'website',self.website
        yield 'were_here_count',self.were_here_count

    def __dict__(self):
        return dict(self)

    def __json__(self):
        return json.dumps(self.__dict__(),cls=ComplexEncoder)

class From(object):

    def __init__(self,**kwargs):
        if 'data' in kwargs:
            kwargs = kwargs['data']
        self.id = kwargs.get('id') if 'id' in kwargs else None
        self.name = kwargs.get('name') if 'name' in kwargs else None

    def __iter__(self):
        yield 'id',self.id
        yield 'name',self.name

    def __dict__(self):
        return dict(self)

    def __json__(self):
        return json.dumps(self.__dict__(),cls=ComplexEncoder)

class Comment(object):

    def __init__(self,**kwargs):


        if 'data' in kwargs:
            kwargs = kwargs['data']


        self.id = kwargs.get('id') if 'id' in kwargs else None
        self.created_time = parse(kwargs.get('created_time'),ignoretz=True) if 'created_time' in kwargs else None
        self._from = From(data=kwargs.get('from')) if 'from' in kwargs else {}
        self.message = kwargs.get('message') if 'message' in kwargs else None
        self.message_parsed = kwargs.get('message_parsed') if 'message_parsed' in kwargs else None
        self.polarity = kwargs.get('polarity') if 'polarity' in kwargs else None
        self.lang = kwargs.get('lang') if 'lang' in kwargs else None

    def __iter__(self):
        yield 'commentid',self.id
        yield 'from_id',self._from.id if self._from else None
        yield 'from_user', self._from.name if self._from else None

        yield 'created_time',self.created_time
        yield 'message',self.message
        yield 'message_parsed' , self.message_parsed
        yield 'polarity',self.polarity
        yield 'lang', self.lang

    def __dict__(self):
        return dict(self)

    def __json__(self):
        return json.dumps(self.__dict__(),cls=ComplexEncoder)

    def __str__(self):
        return json.dumps(self.__dict__(),cls=ComplexEncoder)

class Post(object):


    def __iter__(self):
        yield 'id', self.id
        yield 'postid',self.id
        yield 'from_user', self._from.name
        yield 'from_user_id',self._from.id
        yield 'created_time', self.created_time
        yield 'message', self.message
        yield 'permalink_url', self.permalink_url
        yield 'link', self.link
        yield 'type', self.type
        yield 'updated_time', self.updated_time
        yield 'picture',self.picture
        yield 'full_picture', self.full_picture
        yield 'likes', [like.__dict__() for like in self.likes]
        yield 'loves', [like.__dict__() for like in self.loves]
        yield 'wows', [like.__dict__() for like in self.wows]
        yield 'angrys', [like.__dict__() for like in self.angries]
        yield 'sads', [like.__dict__() for like in self.sads]
        yield 'place',self.place
        yield 'hahas', [like.__dict__() for like in self.hahas]
        yield 'lang' , self.lang
        yield 'comments', [comment.__dict__() for comment in self.comments if comment.id]
        yield 'shares', self.shares
        yield 'pageinfo', self.page.__dict__()
        yield 'likes_count', self.likeCount
        yield 'loves_count', self.loveCount
        yield 'wows_count', self.wowCount
        yield 'sads_count', self.sadCount
        yield 'angrys_count', self.angryCount
        yield 'hahas_count', self.hahaCount
        yield 'comment_count', self.commentCount
        yield 'message_parsed' , self.message_parsed
        yield 'polarity',self.polarity
        yield 'lang',self.lang

    def __dict__(self):
        return dict(self)

    def __json__(self):
        return json.dumps(self.__dict__(),cls=ComplexEncoder)



    def __init__(self,**kwargs):
        if 'data' in kwargs:
            kwargs = kwargs['data']
        self.id = kwargs.get('id') if 'id' in kwargs else None
        self._from = From(data=kwargs.get('from')) if 'from' in kwargs else None
        self.created_time = parse(kwargs.get('created_time'),ignoretz=True) if 'created_time' in kwargs else None
        self.message  = kwargs.get('message') if 'message' in kwargs else None
        self.message_parsed = kwargs.get('message_parsed') if 'message_parsed' in kwargs else None
        self.permalink_url = kwargs.get('permalink_url') if 'permalink_url' in kwargs else None
        self.link = kwargs.get('link') if 'link' in kwargs else None
        self.type = kwargs.get('type') if kwargs.get('type') else None
        place = parseLocation(kwargs.get('place').get('location')) if kwargs.get('place') else {}
        self.place = place
        self.lang  = kwargs.get('lang') if kwargs.get('lang') else None
        self.updated_time = parse(kwargs.get('updated_time'),ignoretz=True) if 'updated_time' in kwargs else None
        self.likes = [From(data=like) for like in kwargs.get('like').get('data')] if 'like' in kwargs else []
        self.loves = [From(data=love) for love in kwargs.get('love').get('data')] if 'love' in kwargs else []
        self.wows  = [From(data=wow) for wow in kwargs.get('wow').get('data')] if 'wow' in kwargs else []
        self.hahas = [From(data=haha) for haha in kwargs.get('haha').get('data')] if 'haha' in kwargs else []
        self.sads  = [From(data=sad) for sad in kwargs.get('sad').get('data')] if 'sad' in kwargs else []
        self.angries = [From(data=angry) for angry in kwargs.get('angry').get('data')] if 'angry' in kwargs else []
        self.comments = [Comment(data=comment) for comment in
                         kwargs.get('comments').get('data')] \
            if 'comments' in kwargs and kwargs.get('comments').get('data') else []

        self.shares = kwargs.get('shares').get('count') if 'shares' in kwargs else 0
        self.page   = kwargs.get('page') if 'page' in kwargs else Page()
        self.likeCount = kwargs.get('like').get('summary').get('total_count') if 'like' in kwargs else 0
        self.wowCount = kwargs.get('wow').get('summary').get('total_count') if 'wow' in kwargs else 0
        self.angryCount = kwargs.get('angry').get('summary').get('total_count') if 'angry' in kwargs else 0
        self.hahaCount = kwargs.get('haha').get('summary').get('total_count') if 'haha' in kwargs else 0
        self.sadCount = kwargs.get('sad').get('summary').get('total_count') if 'sad' in kwargs else 0
        self.loveCount = kwargs.get('love').get('summary').get('total_count') if 'live' in kwargs else 0
        self.commentCount = kwargs.get('comments').get('summary').get('total_count') if 'comments' in kwargs else 0
        self.picture = kwargs.get('picture') if 'picture' in kwargs else None
        self.full_picture = kwargs.get('full_picture') if 'full_picture' in kwargs else None
        self.polarity = kwargs.get('polarity') if 'polarity' in kwargs else {}

class Sentiment(object):
    def __init__(self, text, sentimentValue, sentimentType):
        self.text = text
        self.sentimentValue = sentimentValue
        self.sentimentType = sentimentType

    def __iter__(self):
        yield 'text', self.text
        yield 'sentimentValue', self.sentimentValue
        yield 'sentimentType', self.sentimentType

    def __str__(self):
        return self.text

    def __polarity__(self):
        return {'key': self.sentimentType, 'value': self.sentimentValue}

