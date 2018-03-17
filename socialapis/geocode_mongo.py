countries = {'BG': 'bulgaria', 'TM': 'turkmenistan', 'HM': 'heard and mcdonald island', 'ST': 'sao tome and principe', 'NA': 'namibia', 'ES': 'spain', 'AR': 'malvinas argentinas, argentina', 'BR': 'brazil', 'TT': 'trinidad and tobago', 'SA': 'kingdom of saudi arabia', 'GT': 'guatemala', 'ET': 'ethiopia', 'ZM': 'zambia', 'SY': 'syrian arab republic', 'YT': 'mayotte', 'KI': 'kiribati', 'TV': 'tuvalu', 'BY': 'belarus', 'IR': 'islamic republic of iran', 'DZ': 'algeria', 'DJ': 'djibouti', 'NE': 'niger', 'BV': 'bouvet island', 'AM': 'armenia', 'CI': "cote d'ivoire", 'AS': 'american samoa', 'CX': 'christmas island', 'CN': 'china', 'OM': 'oman', 'GD': 'grenada', 'SZ': 'swaziland', 'LY': 'libya', 'RO': 'romania', 'MD': 'moldova, republic of', 'VI': 'virgin islands', 'CL': 'chile', 'VC': 'saint vincent and the grenadines', 'SC': 'seychelles', 'EE': 'estonia', 'UZ': 'uzbekistan', 'YE': 'yemen', 'GE': 'georgia', 'QA': 'qatar', 'FR': 'france', 'ME': 'montenegro', 'VN': 'vietnam', 'GW': 'guinea bissau', 'AF': 'afghanistan', 'AL': 'albania', 'VA': 'vatican city', 'BJ': 'benin', 'BW': 'botswana', 'IQ': 'iraq', 'LU': 'luxembourg', 'CH': 'switzerland', 'VG': 'virgin islands, british', 'GQ': 'equatorial guinea', 'GR': 'greece', 'PK': 'pakistan', 'BZ': 'belize', 'KZ': 'kazakhstan', 'IE': 'ireland, scotland', 'WS': 'samoa', 'KP': "korea, democratic people's republic of", 'EG': 'egypt', 'JE': 'jersey', 'CF': 'central african republic', 'LB': 'lebanon', 'GS': 'south georgia and the south sandwich islands', 'IO': 'british indian ocean territory', 'ZW': 'zimbabwe', 'HT': 'haiti', 'PS': 'palestine, state of'}



import MySQLdb
rem_countries = countries.copy()
from pymongo import MongoClient



COLS = ['name',
        'latitude',
        'longitude',
        'feature_class',
        'feature_code',
        'country_code',
        'alt_code',
        'time_zone',
        'country_name']

def convert_to_mongo(r,values):
 try:
    return {COLS[0]: r[0],
     COLS[1]: float(r[1]),
     COLS[2]: float(r[2]),
     COLS[3]: r[3],
     COLS[4]: r[4],
     COLS[5]: r[5],
     COLS[6]: r[6],
     COLS[7]: r[7],
     COLS[8]: values
     }
 except ValueError as e:
     print(rem_countries)
     print(r)
     print(e)



for key, values in countries.items():
    try:
        print("working now on " + key )
        collection = MongoClient('mongodb://10.1.4.64:27017')['geodatabase'][values]
        # collection = mango[values]
        db = MySQLdb.connect("10.1.4.57","root","Cosmos12#","geodatabase" )
        cursor= db.cursor()
        my_query = "select `COL 3`,`COL 5`, `COL 6`,`COL 7`,`COL 8`, `COL 9` , `COL 10` ,`COL 18` from geodatabase."+key+" where `COL 5` != '' or `COL 5` is not NULL"
        cursor.execute(my_query)
    # cursor.execute("select `name`,`latitude`, `longitude`,`feature_class`,`feature_code`, `country_code` , `alt_code` ,`time_zone` from geodatabase.IN where `latitude` != '' or `latitude` is not NULL")
        documents = [convert_to_mongo(r,values) for r in cursor.fetchall()]
        collection.insert(documents)
        print("Collection "+values+" successfully created")
        del rem_countries[key]

        # mango.close()
        db.close()
    except ValueError as e:
        print(e)