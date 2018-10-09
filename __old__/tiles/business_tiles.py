import pymongo

from __old__ import tiles


def business_get():
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['business']
    page = 0
    page_size = 1000

    while True:
        cursor = collection.find({}, {'latitude': 1, 'longitude': 1}).skip(page * page_size).limit(page_size)
        business = [doc for doc in cursor]
        yield business
        if len(business) < page_size:
            break
        page += 1


def data_save(bulk):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['prepro_business']
    ids = collection.insert_many(bulk).inserted_ids


def main():
    for page in business_get():
        for item in page:
            if item['latitude'] and item['longitude']:
                item['tile10X'], item['tile10Y'] = tiles.deg2num(item['latitude'], item['longitude'], 10)
                item['tile10'] = '{}_{}'.format(item['tile10X'], item['tile10Y'])
        data_save(page)
    print('yey')


main()