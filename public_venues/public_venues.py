import pymongo


public_venues_tags = ["Botanical Gardens","Buses","Cable Cars","Campgrounds","Castles","Churches","Colleges & Universities","Cultural Center","Farms","Flea Markets","Funeral Services & Cemeteries","Lakes","Metro Stations","Mosques","Municipality","Parking","Parks","Playgrounds","Public Art","Public Markets","Public Plazas","Public Services & Government","Public Transportation","Stadiums & Arenas","Street Art","Town Hall","Train Stations","Trains","Transportation","Dog Parks","Skate Parks","Bike Parking","Landmarks & Historical Buildings","Community Gardens","Community Centers","Market Stalls"]


def business_ids_get():
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['business']

    cursor = collection.find({"categories": {'$in': public_venues_tags}}, {})
    return [doc['_id'] for doc in cursor]


def reviews_count(business_ids):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['review']

    count = collection.count({'business_id': {'$in': business_ids}})
    print(count)


business_ids = business_ids_get()
reviews_count(business_ids)