import pymongo


non_public_venues_tags = ["Hotels & Travel","Hotels","Travel Services","Golf","Resorts","Bed & Breakfast","Golf Lessons","Golf Equipment","Travel Agents","Hostels","Mini Golf","Ski Resorts","Golf Cart Dealers","Golf Cart Rentals","Golf Equipment Shops","Disc Golf","Hotel bar","Souvenir Shops"]


def business_ids_get():
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['business']

    cursor = collection.find({"categories": {'$nin': non_public_venues_tags}}, {})
    return [doc['_id'] for doc in cursor]


def reviews_count(business_ids):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['review']

    count = collection.count({'business_id': {'$in': business_ids}})
    print(count)


business_ids = business_ids_get()
reviews_count(business_ids)