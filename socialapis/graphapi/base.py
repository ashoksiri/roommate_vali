import datetime
import json
import logging
import time
import urllib.request, urllib.parse, urllib.error


import requests as request
from socialapis.utils.social_utils import force_text
from socialapis import BasicPage, Page, Post
from socialapis import translate

logger = logging.getLogger(__file__)

API_URL = 'https://graph.facebook.com/v'

VERSION = ['2.8','2.9','2.10']

MAX_PAGE_SIZE = 1000

DEFAULT_PAGE_SIZE = 50

PAGE_FIELDS =[ 'id','about','fan_count','bio','category',
               'company_overview','contact_address','picture',
               'current_location','description','description_html',
               'general_info','likes','link','location','new_like_count',
               'name','phone','rating_count','talking_about_count',
               'website','were_here_count']

COMMENT_FIELDS = ['id','from','message','created_time']

POST_FIELDS = ['id','from','created_time','message','icon',
               'link','permalink_url','place','type','to',
               'updated_time','full_picture','picture','shares'
               'reactions.type(LIKE).limit(20).summary(total_count).as(like)',
               'reactions.type(LOVE).limit(20).summary(total_count).as(love)',
               'reactions.type(WOW).limit(20).summary(total_count).as(wow)',
               'reactions.type(HAHA).limit(20).summary(total_count).as(haha)',
               'reactions.type(SAD).limit(20).summary(total_count).as(sad)',
               'reactions.type(ANGRY).limit(20).summary(total_count).as(angry)',
               'comments.limit(50).summary(total_count)']

class Graph(object):

    def __init__(self,access_token,version):
        self.access_token = access_token
        self.version = version
        #self.translator = FBFeedTranslate()



        if self.version not in VERSION:
            raise ValueError("Version Not Found")

    def _request_until_succeed(self,url):

        self.response = None
        request_warns = 0

        while True:
            try:

                self.response = request.get(url)
                if self.response.status_code == 200:

                    break
                else:
                    logger.warn(self.response)
                    request_warns += 1
                    if request_warns >= 5:
                        break


            except Exception as e:
                # Other errors are possible, such as IOError.
                print(("Error: " + str(e)))
                pass

        data = force_text(self.response.text)
        return json.loads(data)

    def _get_api_url(self):
        return API_URL+self.version

    def _prepare_url(self,url):
        return url+'&access_token={}'.format(self.access_token)

    def get_sccess_token(self):
        return self.access_token

    def getPages(self,keyword,**kwargs):
        limit = kwargs['limit'] if 'limit' in kwargs else DEFAULT_PAGE_SIZE
        fields = 'id,name,fan_count'
        if limit > MAX_PAGE_SIZE:
            raise ValueError('Max Allowed Size is 1000')

        if 'fields' in kwargs:
            fields = kwargs['fields']

        url       = self._get_api_url()
        keyword   = urllib.parse.quote_plus(keyword)
        url       = url + '/search?type=page&limit={}&q={}'.format(limit,keyword)
        final_url = self._prepare_url(url + '&fields='+fields)
        response  = self._request_until_succeed(final_url)

        if 'data' in response:
            return [BasicPage(page['id'],page['fan_count'],page['name']) for page in \
                    sorted(response['data'],key=lambda x:x['fan_count'],reverse=True)][:limit]
        else:
            return  []

    def getPage(self,pageid):
        url = self._get_api_url()
        url = self._prepare_url(url+'/'+pageid+'?fields={}'.format(','.join(PAGE_FIELDS)))
        response = self._request_until_succeed(url)
        if response:
            return Page(data=response)
        else:
            return None

    def getComments(self,postid,limit=100,**kwargs):

        if type(postid) != str:
            postid = str(postid)

        if limit > 7500:
            limit = 7500

        url = self._get_api_url()+'/{}/comments'.format(postid)
        url = self._prepare_url(url+'?fields={}&limit={}'.format(','.join(COMMENT_FIELDS),limit))
        has_next_page = True
        num_processed = 0
        after = ''
        comments = []

        while has_next_page:
            after = '' if after is '' else "&after={}".format(after)
            base_url = url + after
            response = self._request_until_succeed(base_url)

            trans_comments = translate().process_comments(response['data'])
            comments = comments + trans_comments
            num_processed = num_processed + len(trans_comments)


            if 'paging' in response:
                after = response['paging']['cursors']['after']
            else:
                has_next_page = False

            if num_processed >= limit:
                return comments

        return comments



    def getPosts(self,pageid,limit=100,commentLimit=50,**kwargs):


        if type(pageid) != str:
            pageid = str(pageid)

        page = self.getPage(pageid=pageid)
        url  = self._get_api_url()+'/{}/posts'.format(pageid)

        if limit < 100:
            url  = self._prepare_url(url+'?fields={}&limit={}'.format(','.join(POST_FIELDS),limit))
        else:
            url = self._prepare_url(url + '?fields={}&limit={}'.format(','.join(POST_FIELDS), 100))

        has_next_page = True
        num_processed = 0

        after = ''

        if 'since' in kwargs:
            since = "&since={}".format(kwargs['since'])
        else:
            since = "&since={}".format('')

        if 'until' in kwargs:
            until = "&until={}".format(kwargs['until'])
        else:
            until = "&until={}".format('')

        logger.info("Scraping Facebook Page:{} ".format(pageid))

        posts = []
        posts_indexed = {}

        def indexposts(posts):
            for post in posts:
                posts_indexed[post.get('id')] = post


        while has_next_page:
            after = '' if after is '' else "&after={}".format(after)
            base_url = url + after + since + until

            response = self._request_until_succeed(base_url)
            if response:
                statuses = translate().process_posts(data=response['data'])

            else:
                statuses = []

            indexposts(statuses)
            # if commentLimit > 50 :
            #     post_ids = [status.get('id') for status in statuses]
            #     comments = self.getCommentsPosts(post_ids,limit=commentLimit)
            #     for key,value in comments.items():
            #         post = posts_indexed[key]
            #         post['comments']['data'] = value
            #         posts_indexed[key] = post

            if commentLimit > 50:
                logger.info("user asked comments above default size")
            else:
                logger.info("Going with default comment limit")


            for status in list(posts_indexed.values()):
                comments = translate().process_comments(status['comments']['data'])
                status['comments']['data'] = comments
                status['page'] = page
                posts.append(Post(data=status))
                num_processed += 1
                if num_processed % 100 == 0:
                    print(("{} Statuses Processed: {}".format
                          (num_processed, datetime.datetime.now())))

            # if there is no next page, we're done.
            if 'paging' in response:
                after = response['paging']['cursors']['after']
            else:
                has_next_page = False

            posts_indexed = {}

            if num_processed >= limit:
                return posts[:limit]

        if num_processed < limit:
            logger.warn('Required {} but got {} from page {}'.format(limit,num_processed,pageid))

        return posts

    def getPost(self,postid,**kwargs):
        pass

    def getComment(self,commentid,**kwargs):
        pass

    def getReactions(self,id,**kwargs):
        pass

    def commentUrl(self,postid,limit=100):
        url = self._get_api_url() + '/{}/comments'.format(postid)
        url = self._prepare_url(url + '?fields={}&limit={}'.format(','.join(COMMENT_FIELDS), limit))
        return url

    def getCommentsPosts(self,posts=None,limit=100):

        if not posts:
            return  {}

        def indexComments(posts):
            temp_posts = {}
            for post in posts:
                temp_posts[post] = []
            return temp_posts

        indexed_comments = indexComments(posts)
        reqs = []
        for post in posts:
            url =  self.commentUrl(postid=post,limit=limit)
            headers = {'post_id':post}
            reqs.append(grequests.get(url,headers=headers))

        for resp in grequests.map(reqs):
            post_id = resp.request.headers.get('Post_id')
            indexed_comments[post_id] = json.loads(resp.content)['data']

        return indexed_comments


    def feed_post(self,message):
        text = message


    def post_comment(self,message,postid):
        url = self._get_api_url() + '/{}/comments'.format(postid)
        access_token =  "EAAR3Q7sFWtYBAHKfTuDgRTLLO4DY8SZAjhlpSBRK6tiUXYbm062QsmpXX1gNa4iHoKIa89m5vSJDewC1fdASPnvqEyZA9zslZAYeHBGfl3ROgh2VkmGB6YxEWi09TXASDM4yxkseVb6visaQqtFz7cyura1wg5Pu1f7pC5RwwZDZD"
        url = url+'?access_token='+access_token
        url = url+'&message='+message
        response = request.post(url)
        return response

if __name__  == '__main__':
    access_token = '1257032691047126|mP2cUAf8cIH-ZA0WntiqScJT8HI'
    version = '2.10'
    # graph = Graph(access_token,version)
    # starttime = time.time()
    # posts = graph.getPosts(pageid='965525870130270',limit=2)
    #
    # for post in posts:
    #     print(post)
    a = 'ashok patwari'
    b = b'ashok patwari'
    print(type(a),type(b))
    keyword = urllib.parse.quote_plus(b'ashok patwari')
    print(keyword)
    # comments = graph.getComments(postid='177526890164_10159755990745165',limit=100)
    # with open('posts.json','w') as file:
    #     #file.write('\n'.join([json.dumps(c,cls=ComplexEncoder) for c in comments]))
    #     file.write(json.dumps(posts, cls=ComplexEncoder))
    # print time.time() - starttime
    # for c in comments:
    #     print json.dumps(c,cls=ComplexEncoder)


