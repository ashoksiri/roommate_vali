
from dateutil.parser import parse
from django.utils.encoding import smart_text
import re,requests,time,hashlib,json
from bs4 import BeautifulSoup

from urllib.parse import quote_plus
from socialapis.utils import get_sentiment
from socialapis.translate import Request


from queue import Queue
from threading import Thread

urls = [
        {'url':'http://english.sakshi.com/andhrapradesh','regional':True,'news_source':'sakshi','lang':'english'},
        {'url':'http://english.sakshi.com/telangana','regional':True,'news_source':'sakshi','lang':'english'},
        {'url':'http://english.sakshi.com/national','regional':False,'news_source':'sakshi','lang':'english'},
        {'url':'http://www.apherald.com/rss/eng','regional':False,'news_source':'ApHerald','lang':'english'},
        {'url':'http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms','regional':False,'news_source':'Times Of India','lang':'english'},
        {'url':'http://timesofindia.indiatimes.com/rssfeeds/1898055.cms','regional':False,'news_source':'Times Of India','lang':'english'},
        {'url':'http://timesofindia.indiatimes.com/rssfeeds/-2128816011.cms','regional':True,'news_source':'Times Of India','lang':'english'},
        {'url':'http://www.eenaduindia.com/states/south/andhra-pradesh','regional':True,'news_source':'Eenadu','lang':'english'},
        {'url':'http://www.eenaduindia.com/news/national-news','regional':False,'news_source':'Eanadu','lang':'english'},
        {'url':'http://www.eenaduindia.com/states/south/telangana','regional':True,'news_source':'Eenadu','lang':'english'},
        {'url':'http://zeenews.india.com/rss/business.xml','regional':False,'news_source':'ZeeNews','lang':'english'},
        {'url':'http://zeenews.india.com/rss/india-news.xml','regional':False,'news_source':'ZeeNews','lang':'english'},
        {'url':'http://zeenews.india.com/rss/india-national-news.xml','regional':False,'news_source':'ZeeNews','lang':'english'},
        {'url':'http://www.thehindu.com/news/national/?service=rss','regional':False,'news_source':'Hindu','lang':'english'},
        {'url':'http://www.thehindu.com/news/national/andhra-pradesh/?service=rss','regional':True,'news_source':'Hindu','lang':'english'},
        {'url':'http://www.thehindu.com/news/national/telangana/?service=rss','regional':True,'news_source':'Hindu','lang':'english'},
        {'url':'http://indianexpress.com/section/india/','regional':False,'news_source':'indianExpress','lang':'english'},
        {'url':'http://www.oneindia.com/rss/news-india-fb.xml','regional':False, 'news_source':'one india','lang':'english'},
        {'url':'https://news.google.com/news?hl=en&tab=nn&edchanged=1&authuser=0&ned=en_in&output=rss&q=','regional':False,'news_source':'google','lang':'english'}
]



def unicode_decode(text):
    if text:
        return smart_text(text, encoding='utf-8', strings_only=False, errors='strict')
    else:
        return None

def checkKeyword(keyword,content):
    for word in content.lower().split():
        if word.rfind('\'') > 0:
            word = word.split('\'', 1)[0]
        if word.rfind('\"') > 0:
            word = word.split('\"', 1)[0]
        if word.strip() == keyword.lower():
            return True
    else:
        return False


class NewsApi(object):

    def __init__(self):
        self.q = Queue(len(urls) * 2)
        self.session = requests.Session()



    def doWork(self):
        while True:
            request = self.q.get()
            try:
                response = self.session.get(url=request.url)
                self.doSomethingWithResult(response,request)
            except Exception as e:
                print(e)
                pass
            self.q.task_done()

    def doSomethingWithResult(self,response,request:Request):


        if response:

            content = BeautifulSoup(response.text, 'html.parser')

            if request.news_source == 'sakshi':
                url = 'http://english.sakshi.com'
                image_host = 'http://thumbor.assettype.com'
                for div in content.find(class_='left-container').find_all(class_="section-list__article"):
                    try:
                        title = div.find(class_='section-list__content').find(
                            class_='section-list__headline').get_text().strip().lower()
                        content = div.find(class_='section-list__content').find(
                            class_='section-list__summary').get_text().strip().lower()

                        if checkKeyword(self.keyword,title) or checkKeyword(self.keyword,content):
                            articleUrl = url + div.find('a')['href'].strip()
                            imageUrl = image_host + '/' + div.find(class_='section-list__image-container').find('img')[
                                'data-image-key'].strip()
                            section = div.find(class_='section-list__section-name').get_text().strip()

                            timestamp = div.find(class_='section-list__content').find(
                                class_='section-list__timestamp').get_text().strip().lower()
                            timestamp = parse(timestamp,fuzzy=True)
                            polarity  = get_sentiment(title).__polarity__()
                            self.news.append(
                                {
                                    'newsid': hashlib.md5(title.encode('utf-8')).hexdigest(),
                                    'link': articleUrl,
                                    'image': imageUrl,
                                    'section': section.lower(),
                                    'title': title,
                                    'titleParsed':title,
                                    'description': content,
                                    'descriptionParsed':content,
                                    'polarity':polarity,
                                    'created_at': timestamp,
                                    'regional': True,
                                    'source': request.news_source,
                                    'searchKey' : self.keyword
                                }
                            )
                    except Exception as e:
                        print('Sakshi English Method', e)
                        pass
            if request.news_source == 'ApHerald':
                try:
                    for item in content.find_all('item'):
                        title       = item.find('title').get_text().strip()
                        description = item.find('description')
                        description = item.find('summarytag') if description is None else description
                        description = BeautifulSoup(re.sub('[\[CDATA\]]', '', description.get_text().strip())[2:-1],
                                                    'html.parser').get_text().strip()

                        if checkKeyword(self.keyword, title) or checkKeyword(self.keyword, description):
                            image = item.find('image').get_text()
                            link = item.find('guid')
                            link = item.find('weblink') if link is None or link.get_text().rfind('http') == -1 else link
                            link = link.get_text().strip()
                            timestamp = item.find('pubdate')
                            timestamp = item.find('publishdate') if item.find('pubdate') is None else timestamp
                            timestamp = parse(timestamp.get_text().strip())
                            section = image[image.rfind('ImageStore/images/') + 18:]
                            section = section[0:section.find('/')]
                            polarity = get_sentiment(title)
                            self.news.append(
                                {
                                    'newsid': hashlib.md5(title.lower().encode('utf-8')).hexdigest(),
                                    'link': link,
                                    'image': image,
                                    'section': section.lower(),
                                    'title': title,
                                    'titleParsed': title,
                                    'description': description,
                                    'descriptionParsed': description,
                                    'polarity': polarity.__polarity__(),
                                    'created_at': timestamp,
                                    'regional': True,
                                    'source': request.news_source,
                                    'searchKey': self.keyword
                                }
                            )
                except Exception as e:
                    print ('AP Herald',e)
                    pass
            if request.news_source == 'Times Of India':
                try:
                    for item in content.find_all('item'):
                        title = item.find('title').get_text()
                        description = BeautifulSoup(item.find('description').get_text(), 'html.parser').get_text()
                        if description == '':
                            continue
                        if checkKeyword(self.keyword, title) or checkKeyword(self.keyword, description):
                            timestamp = parse(item.find('pubdate').get_text())
                            link = item.find('guid').get_text()
                            section = link[link.rfind('indiatimes.com/') + 15:]
                            section = section[0:section.find('/')]
                            polarity = get_sentiment(title).__polarity__()
                            self.news.append(
                                {
                                    'newsid': hashlib.md5(title.lower().encode('utf-8')).hexdigest(),
                                    'link': link,
                                    'image': None,
                                    'section': section.lower(),
                                    'title': title,
                                    'titleParsed': title,
                                    'description': description,
                                    'descriptionParsed': description,
                                    'polarity': polarity,
                                    'created_at': timestamp,
                                    'regional': False,
                                    'source': request.news_source,
                                    'searchKey': self.keyword
                                }
                            )
                except Exception as e:
                    print ('Time of India Method', e)
                    pass
            if request.news_source == 'one india':
                try:
                    for item in content.find_all('item'):
                        title = item.find('title').get_text().strip()
                        description = item.find('description').get_text().strip()
                        if checkKeyword(self.keyword, title) or checkKeyword(self.keyword, description):
                            timestamp = item.find('pubdate').get_text().strip()
                            timestamp = parse(timestamp)
                            image = item.find('enclosure')['url']
                            link = item.find('guid').get_text().strip()
                            section = link[link.rfind('https://www.oneindia.com/') + 25:]
                            section = section[0:section.find('/')]
                            polarity = get_sentiment(title).__polarity__()
                            self.news.append(
                                {
                                    'newsid': hashlib.md5(title.lower().encode('utf-8')).hexdigest(),
                                    'link': link,
                                    'image': image,
                                    'section': section.lower(),
                                    'title': title,
                                    'titleParsed': title,
                                    'description': description,
                                    'descriptionParsed': description,
                                    'polarity': polarity,
                                    'created_at': timestamp,
                                    'regional': False,
                                    'source': request.news_source,
                                    'searchKey': self.keyword

                                })
                except Exception as e:
                    print ('One India Method', e)
                    pass
            if request.news_source == 'Hindu':
                try:
                    for item in content.find_all('item'):
                        title = item.find('title').get_text().strip()
                        description = item.find('description').get_text().strip()
                        if checkKeyword(self.keyword, title) or checkKeyword(self.keyword, description):
                            timestamp = item.find('pubdate').get_text().strip()
                            timestamp = parse(timestamp)
                            link = item.__str__()
                            link = link[link.rfind('<link/>') + 7:link.find('<description>')].strip()
                            section = link[link.rfind('http://www.thehindu.com/news/') + 29:]
                            section = section[0:section.find('/')]
                            polarity = get_sentiment(title).__polarity__()
                            self.news.append(
                                {
                                    'newsid': hashlib.md5(title.lower().encode('utf-8')).hexdigest(),
                                    'link': link,
                                    'image': None,
                                    'section': section.lower(),
                                    'title': title,
                                    'titleParsed': title,
                                    'description': description,
                                    'descriptionParsed': description,
                                    'polarity': polarity,
                                    'created_at': timestamp,
                                    'regional': False,
                                    'source': request.news_source,
                                    'searchKey': self.keyword

                                })
                except Exception as e:
                    print ('Hindu Method', e)
                    pass
            if request.news_source == 'indianExpress':
                try:
                    for div in content.find(class_='leftpanel').find_all('div',{'class':'articles'}):
                        link  = div.div.a['href']
                        image = div.div.img
                        if image:
                            image = image['data-lazy-src'] if image.has_attr('data-lazy-src') else None
                        description = div.p.get_text().strip()
                        title     = div.find(class_='title').get_text().strip()
                        if checkKeyword(self.keyword, title) or checkKeyword(self.keyword, description):
                            timestamp = parse(div.find(class_='date').get_text())
                            polarity = get_sentiment(title).__polarity__()
                            self.news.append(
                                {
                                    'newsid': hashlib.md5(title.lower().encode('utf-8')).hexdigest(),
                                    'link': link,
                                    'image': image,
                                    'section': 'nation',
                                    'title': title,
                                    'titleParsed': title,
                                    'description': description,
                                    'descriptionParsed': description,
                                    'polarity': polarity,
                                    'created_at': timestamp,
                                    'regional': False,
                                    'source': request.news_source,
                                    'searchKey': self.keyword

                                })
                except Exception as e:
                    print("Indian Express ",e)
            if request.news_source == 'Eenadu':
                try:
                    for div in content.find(class_='rightside_HomeSearch').find_all('div',{'class':'leftimage'}):
                        link = div.find('div',{'class':'ArticleListImage'}).a['href']
                        title = div.find('div',{'class':'ArticleListHead'}).a.get_text().strip()
                        description = div.find('div',{'class':'ArticlelistAbstract'}).get_text().strip()
                        image = div.div.div.a.find('img',{'class':'articlelistingImage'})
                        timestamp = div.find('div',{'class':'ArticleListCommentDate'}).get_text().strip()
                        timestamp = parse(timestamp,fuzzy=True)
                        if image:
                            image = image['data-original'] if image.has_attr('data-original') else None
                        if checkKeyword(self.keyword, title) or checkKeyword(self.keyword, description):
                            polarity  = get_sentiment(title).__polarity__()
                            self.news.append(
                                {
                                    'newsid': hashlib.md5(title.lower().encode('utf-8')).hexdigest(),
                                    'link': link,
                                    'image': image,
                                    'section': 'nation',
                                    'title': title,
                                    'titleParsed': title,
                                    'description': description,
                                    'descriptionParsed': description,
                                    'polarity': polarity,
                                    'created_at': timestamp,
                                    'regional': False,
                                    'source': request.news_source,
                                    'searchKey': self.keyword

                                })
                except Exception as e :
                    print("Eenadu Method",e)
                    pass
            if request.news_source == 'ZeeNews':
                try:
                    for div in content.find_all('item'):
                        title = div.title.get_text().strip()
                        link  = div.guid.get_text().strip()
                        description = div.description.get_text().strip()
                        timestamp   = parse(div.pubdate.get_text().strip(),fuzzy=True)
                        image = None

                        if checkKeyword(self.keyword, title) or checkKeyword(self.keyword, description):
                            polarity = get_sentiment(title).__polarity__()
                            self.news.append(
                                {
                                    'newsid': hashlib.md5(title.lower().encode('utf-8')).hexdigest(),
                                    'link': link,
                                    'image': image,
                                    'section': 'nation',
                                    'title': title,
                                    'titleParsed': title,
                                    'description': description,
                                    'descriptionParsed': description,
                                    'polarity': polarity,
                                    'created_at': timestamp,
                                    'regional': False,
                                    'source': request.news_source,
                                    'searchKey': self.keyword

                                })
                except Exception as e:
                    print ("Zee News",e)
                    pass
            if request.news_source == 'google':
                for d in content.find_all('item'):
                    try:
                        title = d.title.get_text()
                        description = BeautifulSoup(d.description.get_text(), 'html.parser').table.tr
                        content = description.findAll("td")[1].findAll("font")[3].get_text()

                        timestamp = parse(d.pubdate.get_text())
                        link = d.__str__()
                        link = link[link.rfind('<link/>') + 7:]
                        link = link[0:link.find('<guid')]
                        link = link[link.rfind('http'):]
                        imagetd = description.findAll("td")[0]
                        image = 'https:' + imagetd.find("img").get("src") if imagetd.find("img") is not None else None
                        section = description.td.get_text()
                        polarity = get_sentiment(title).__polarity__()
                        self.news.append(
                            {
                                'newsid': hashlib.md5(title.lower().encode('utf-8')).hexdigest(),
                                'link': link,
                                'image': image,
                                'section': 'nation',
                                'title': title,
                                'titleParsed': title,
                                'description': content,
                                'descriptionParsed': content,
                                'polarity': polarity,
                                'created_at': timestamp,
                                'regional': False,
                                'source': section,
                                'searchKey': self.keyword

                            })
                    except Exception as e :
                        #print("Google Method",e)
                        pass

    def getnews(self,keyword=None):

        self.news = list()
        self.keyword = keyword.lower()

        for i in range(len(urls)):
            t = Thread(target=self.doWork)
            t.daemon = True
            t.start()

        for url in urls:
            request = Request(url)
            request.keyword = self.keyword
            if request.news_source == 'google':
                url = request.url + quote_plus(self.keyword)
                request.url = url
            self.q.put(request)

        self.q.join()

        return self.news


news = NewsApi()