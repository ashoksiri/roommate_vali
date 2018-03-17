
from apiclient.http import BatchHttpRequest
from apiclient.discovery import build
from socialapis import translate
import json
import logging
from isodate import parse_duration
import requests


logger = logging.getLogger(__name__)


class Youtube(object):

    def __init__(self,developer_key):
        self.developer_key = developer_key
        YOUTUBE_API_SERVICE_NAME="youtube"
        YOUTUBE_API_VERSION="v3"
        self.youtube =  build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=developer_key)
        self.DEFAULT_VIDEO_SIZE = 50

    channelSnippet = "brandingSettings,contentDetails,contentOwnerDetails,id,invideoPromotion,localizations,snippet,statistics,status,topicDetails"
    videoSnippet = "contentDetails,id,liveStreamingDetails,localizations,player,recordingDetails,snippet,statistics,status,topicDetails"
    commentSnippet = "id,snippet"


    def post_comment(self,videoId,access_token,message):

        session = requests.Session()
        url = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        body = {
            "snippet": {
                "videoId": videoId,
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": message
                    }
                }
            }
        }
        body = json.dumps(body)

        response = session.post(url=url, data=body, headers=headers)
        return response


    class VideoModel(dict):
        """
           A simple model that wraps Apsma Request
           """
        __getattr__ = dict.get
        __delattr__ = dict.__delitem__
        __setattr__ = dict.__setitem__


    DELETE_FIELDS = ['etag','kind']


    def delete_keys_from_dict(self,dict_del, lst_keys):
        for k in lst_keys:
            try:
                del dict_del[k]
            except KeyError:
                pass
        for v in dict_del.values():
            if isinstance(v, dict):
                self.delete_keys_from_dict(v, lst_keys)

        return dict_del

    def castStatistics(self,statistics):
        temp_stats = {}
        for key,value in statistics.items():
            temp_stats[key] = int(value)
        return temp_stats

    def videoStats(self,request, response, exception):

        if response:
            try:
                item = response['items'][0]
                videoId = item['id']
                video = self.videos.get(videoId)
                video['videoId'] = videoId
                videoSnippet = item['snippet']
                video['channelId'] = videoSnippet.get('channelId')
                video['title'] = videoSnippet['title']
                video['snippet'] = videoSnippet
                video['contentDetails'] = item.get('contentDetails', None)
                if video.get('contentDetails'):
                    if not isinstance(video.get('contentDetails', {}).get('duration'), int):
                        video['contentDetails']['duration'] = int(
                            parse_duration(item.get('contentDetails').get('duration')).total_seconds())
                video['status'] = item.get('status', {})
                video['statistics'] = self.castStatistics(item.get('statistics', {}))
                video['topicDetails'] = item.get('topicDetails', {})
                video['liveStreamingDetails'] = item.get('liveStreamingDetails', {})
                self.videos[videoId] = video
            except Exception as e:
                logger.error(e)



    def comments(self,request, response, exception):

       if response:
            items = response['items']
            if len(items) > 0:
                videoId = items[0]['snippet']['videoId']
                video = self.videos[videoId]
                video['comments'] = [self.delete_keys_from_dict(item,self.DELETE_FIELDS) for item in items]
                self.videos[videoId] = video

    def channelInfo(self,request,response,exception):

        if response:
            item = response['items'][0]
            channelId = item['id']
            for id , video in self.videos.items():
                if video.get('snippet').get('channelId') == channelId:
                    video = self.videos[id]
                    video['channel'] = item
                    self.videos[id] = video

    def getrecent_videos(self,q,n=10,nextPageToken=None):

        flag = True
        video_counter = 0
        self.videos = {}
        self.channels = {}

        batch = self.youtube.new_batch_http_request()

        if n < self.DEFAULT_VIDEO_SIZE:
            DEFAULT_VIDEO_SIZE = n

        while flag:

            if nextPageToken:
                search_response = self.youtube.search().list(q=q, part="id,snippet", maxResults=DEFAULT_VIDEO_SIZE, type='video',
                                                        pageToken=nextPageToken,order='date').execute()
            else:
                search_response = self.youtube.search().list(q=q, part="id,snippet", maxResults=DEFAULT_VIDEO_SIZE, type='video',
                                                        order = 'date').execute()

            nextPageToken = search_response.get('nextPageToken')

            if not nextPageToken:
                flag = False

            for search_result in search_response:
                if 'items' in search_result:
                    video_counter += len(search_response[search_result])
                    for item in search_response[search_result]:
                        try:

                            self.videos[item['id']['videoId']] = item
                            self.channels[item['snippet']['channelId']] = item

                            batch.add(self.youtube.commentThreads().list(part=self.commentSnippet,
                                                                    videoId=item['id']['videoId'],
                                                                    maxResults=50,
                                                                    textFormat='plainText'), callback=self.comments)
                            batch.add(self.youtube.videos().list(part=self.videoSnippet,
                                                            id=item['id']['videoId']), callback=self.videoStats)
                            batch.add(self.youtube.channels().list(part=self.channelSnippet,
                                                              id=item['snippet']['channelId'],
                                                              maxResults=30), callback=self.channelInfo)
                        except Exception as e:
                            print(e)


            batch.execute()

            if video_counter >= n:
                break

        videos = self.delete_keys_from_dict(self.videos, self.DELETE_FIELDS)
        videos = list(videos.values())
        videos = translate().process_videos(data=videos)
        return videos


    def get_channel_videos(self,q,n=10,nextPageToken=None,channelId=None):

        flag = True
        video_counter = 0
        self.videos = {}
        self.channels = {}

        batch = self.youtube.new_batch_http_request()

        if n < self.DEFAULT_VIDEO_SIZE:
            DEFAULT_VIDEO_SIZE = n

        while flag:

            if nextPageToken:
                search_response = self.youtube.search().list(q=q, part="id,snippet", maxResults=DEFAULT_VIDEO_SIZE, type='video',
                                                        pageToken=nextPageToken,order='date',channelId=channelId).execute()
            else:
                search_response = self.youtube.search().list(q=q, part="id,snippet", maxResults=DEFAULT_VIDEO_SIZE, type='video',
                                                        order = 'date',channelId=channelId).execute()

            nextPageToken = search_response.get('nextPageToken')

            if not nextPageToken:
                flag = False

            for search_result in search_response:
                if 'items' in search_result:
                    video_counter += len(search_response[search_result])
                    for item in search_response[search_result]:
                        self.videos[item['id']['videoId']] = item
                        self.channels[item['snippet']['channelId']] = item

                        batch.add(self.youtube.commentThreads().list(part=self.commentSnippet,
                                                                videoId=item['id']['videoId'],
                                                                maxResults=50,
                                                                textFormat='plainText'), callback=self.comments)
                        batch.add(self.youtube.videos().list(part=self.videoSnippet,
                                                        id=item['id']['videoId']), callback=self.videoStats)
                        batch.add(self.youtube.channels().list(part=self.channelSnippet,
                                                          id=item['snippet']['channelId'],
                                                          maxResults=30), callback=self.channelInfo)

            batch.execute()

            if video_counter >= n:
                break

        videos = self.delete_keys_from_dict(self.videos, self.DELETE_FIELDS)
        videos = list(videos.values())
        videos = translate().process_videos(data=videos)
        return videos


    def getvideos(self,q, n=10,nextPageToken=None):

        flag = True
        self.videos = {}
        self.channels = {}
        video_counter = 0


        batch = self.youtube.new_batch_http_request()

        if n < self.DEFAULT_VIDEO_SIZE:
            DEFAULT_VIDEO_SIZE = n

        while flag:

            if nextPageToken:
                search_response = self.youtube.search().list(q=q, part="id,snippet", maxResults=DEFAULT_VIDEO_SIZE, type='video',
                                                        pageToken=nextPageToken).execute()
            else:
                search_response = self.youtube.search().list(q=q, part="id,snippet", maxResults=DEFAULT_VIDEO_SIZE, type='video',
                                                        ).execute()


            nextPageToken = search_response.get('nextPageToken')

            if not nextPageToken:
                flag = False



            for search_result in search_response:
                if 'items' in search_result:
                    video_counter += len(search_response[search_result])
                    for item in search_response[search_result]:
                        self.videos[item['id']['videoId']] = item

                        self.channels[item['snippet']['channelId']] = item

                        batch.add(self.youtube.commentThreads().list(part=self.commentSnippet,
                                                                videoId=item['id']['videoId'],
                                                                maxResults=50,
                                                                textFormat='plainText'),callback=self.comments)
                        batch.add(self.youtube.videos().list(part=self.videoSnippet,
                                                        id=item['id']['videoId']),callback=self.videoStats)
                        batch.add(self.youtube.channels().list(part=self.channelSnippet,
                                                          id=item['snippet']['channelId'],
                                                          maxResults=30),callback=self.channelInfo)

            batch.execute()

            if video_counter >= n:
                break

        videos = self.delete_keys_from_dict(self.videos,self.DELETE_FIELDS)
        videos = list(videos.values())
        videos = translate().process_videos(data=videos)
        return videos

if __name__ == '__main__':
    youtube = Youtube(developer_key='AIzaSyBpWXegO6Vp9-73v8ifTA1kjwchGeXRj2E')
    data = youtube.getvideos(q='narendramodi',n=10)
    print(len(data))