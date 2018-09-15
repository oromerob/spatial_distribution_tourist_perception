import pymongo
from public_venue_categories import venue_categories


def clusters_get():
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['clusters']

    cursor = collection.find({}, {'tiles': 1, 'name': 1})
    return [doc for doc in cursor]


def business_ids_get(tiles):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['prepro_business']

    cursor = collection.find({"tile10": {'$in': tiles}}, {})
    return [doc['_id'] for doc in cursor]


def business_get(ids):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['business']

    cursor = collection.find({"_id": {'$in': ids}}, {'name': 1, 'categories': 1})
    return [doc for doc in cursor]

#
# def reviews_count(business_ids):
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['review']
#
#     count = collection.count({'business_id': {'$in': business_ids}})
#     print(count)


def category_dict_prepare():
    category_dict = {}
    for key, list in venue_categories.items():
        for item in list:
            category_dict[item] = key
    return category_dict


def venues_prepare(venues, category_dict, cluster):
    _venues = []
    for venue in venues:
        _categories = set([])
        for cat in venue['categories']:
            if cat in category_dict:
                _categories.add(category_dict[cat])
        if len(_categories) > 0:
            _venues.append({
                '_id': venue['_id'],
                'name': venue['name'],
                'category_clusters': list(_categories),
                'cluster_name': cluster['name'],
                'cluster_id': cluster['_id']
            })
    return _venues


def venues_save(venues):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['venues']
    ids = collection.insert_many(venues).inserted_ids


if __name__ == '__main__':
    category_dict = category_dict_prepare()
    for cluster in clusters_get():
        print('processing venues for ', cluster['name'])
        business_ids = business_ids_get(cluster['tiles'])
        business = business_get(business_ids)
        venues = venues_prepare(business, category_dict, cluster)
        venues_save(venues)
