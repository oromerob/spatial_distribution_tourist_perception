import pymongo

from ._mongo import mongo_get


def yelp_user_upsert(user):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['yelp_user']
    modified = collection.update_one({'_id': user['_id']}, {'$set': user}, upsert=True).modified_count


def yelp_users_get(filter=None, fields=None):
    return mongo_get(
        col='yelp_user',
        filter=filter,
        fields=fields
    )