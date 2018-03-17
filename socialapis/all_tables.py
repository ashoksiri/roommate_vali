from pymongo import MongoClient
mangodb = MongoClient("mongodb://10.1.4.64:27017")['geodatabase']

def getGeoLocation(locname,country):
    if country:
        # dbs = _mysql.connect(host="10.1.4.57", port=3306, user="root", passwd="Cosmos12#", db="geodatabase")
        try:
            collection = mangodb[country]
            # get_myobj = collection.find({'$and':[{"country_name":country},{"name":locname}]}).count()
            # myquery = '$and:[{"country_name": "' + country + '"},{"name": "' + locname + '"}]'
            gexer = '$regex : /'+locname+'/i'

            get_myobj = collection.find({"$and":[{"country_name": country}, { "name" :  {'$regex' : locname, '$options' : 'i'}}]}).limit(1)
            for i in get_myobj:
                lat = i["latitude"]
                lng = i["longitude"]
                return {"lat": lat, "lon": lng}
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

