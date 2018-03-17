# import threading
# import time
#
# class MyThread(threading.Thread):
#
#     def run(self):
#         count = 0
#         while True:
#             count = count + 1
#             print " No of loop {} and Thread name is {} \n".format(count , self.name)
#             time.sleep(5)
#
#
# if __name__ == '__main__':
#
#     for i in range(0,100):
#         m = MyThread()
#         m.start()
#         print "print from main thread  {}".format(i)

import pymongo
from dateutil.parser import parse

from_date = parse('2016-01-01')
to_date = parse('2017-12-17')


db = pymongo.MongoClient('mongodb://10.1.4.64:27017')

print(db.db_apsma.tweet.find({'searchKey':'narendramodi','created_at':{'$lte': to_date,'$gte': from_date}}).count())
print(db.db_apsma.facebook.find({'searchKey':'narendramodi','created_at':{'$lte': to_date,'$gte': from_date}}).count())
print(db.db_apsma.video.find({'searchKey':'narendramodi'}).count())
print(db.db_apsma.news.find({'searchKey':'narendramodi'}).count())


db.close()


