import pymongo
from pymongo.errors import BulkWriteError


def mongo_get(col=None, filter=None, fields=None, page_size=100000):
    if col is None:
        raise Exception
    if filter is None:
        filter = {}
    find_params = [filter]
    if fields is not None and type(fields) == dict:
        find_params.append(fields)

    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db[col]

    page = 0

    res = []

    while True:
        print('Querying "{}" page {}...'.format(col, page))

        cursor = collection.find(*find_params).skip(page_size * page).limit(page)

        _res = [doc for doc in cursor]

        res += _res

        if len(_res) < page_size:
            break

        page += 1

    print('Returning {} elements from "{}"'.format(len(res), col))
    return res


def users_get():
    return mongo_get(col='user', filter={}, fields={'user_id': 1, 'name': 1, 'review_count': 1, 'yelping_since': 1, 'average_stars': 1})


# def users_get():
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['user']
#
#     cursor = collection.find({}, {'user_id': 1, 'name': 1, 'review_count': 1, 'yelping_since': 1, 'average_stars': 1})
#     return [doc for doc in cursor]


# def reviews_get(user_id):
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['review']
#
#     cursor = collection.find({'user_id': user_id}, {'business_id': 1, "date": 1}).limit(100000)
#     return [doc for doc in cursor]


def reviews_all_get():
    reviews = mongo_get(col='review', filter={}, fields={'user_id': 1, 'business_id': 1, "date": 1})

    user_reviews = {}

    for doc in reviews:
        if doc['user_id'] not in user_reviews:
            user_reviews.update({doc['user_id']: []})
        user_reviews[doc['user_id']].append(
            {'business_id': doc['business_id'], 'date': doc['date'], '_id': doc['_id']})

    return user_reviews


# def reviews_all_get():
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['review']
#
#     page = 0
#     page_size = 1000
#
#     user_reviews = {}
#
#     while True:
#
#         cursor = collection.find({}, {'user_id': 1, 'business_id': 1, "date": 1}).skip(page_size * page).limit(page)
#
#         index = 0
#         for doc in cursor:
#             if doc['user_id'] not in user_reviews:
#                 user_reviews.update({doc['user_id']: []})
#             user_reviews[doc['user_id']].append(
#                 {'business_id': doc['business_id'], 'date': doc['date'], '_id': doc['_id']})
#             index += 1
#
#         if index < page_size:
#             break
#
#     return user_reviews


# def business_tile_get(user):
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['prepro_business']
#
#     business_ids = list(set([review['business_id'] for review in user['reviews']]))
#
#     cursor = collection.find({'_id': {'$in': business_ids}}, {'tile10': 1}).limit(100000)
#
#     businessess = {doc['_id']: doc['tile10'] for doc in cursor}
#
#     filtered_reviews = []
#     for review in user['reviews']:
#         try:
#             review['tile10'] = businessess[review['business_id']]
#             filtered_reviews.append(review)
#         except KeyError:
#             pass
#
#     user['reviews'] = filtered_reviews
#
#     return user


def business_tile_all_get():
    _businessess = mongo_get(col='prepro_business', filter={}, fields={'tile10': 1})

    businessess = {}

    for doc in _businessess:
        businessess.update({doc['_id']: doc['tile10']})

    return businessess


# def business_tile_all_get():
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['prepro_business']
#
#     page = 0
#     page_size = 1000
#
#     businessess = {}
#
#     while True:
#
#         cursor = collection.find({}, {'tile10': 1}).skip(page_size * page).limit(page)
#
#         index = 0
#         for doc in cursor:
#             businessess.update({doc['_id']: doc['tile10']})
#             index += 1
#
#         if index < page_size:
#             break
#
#     return businessess


def clusters_get():
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['clusters']

    cursor = collection.find({}, {'tiles': 1})
    tiles_map = {}

    for doc in cursor:
        for tile in doc['tiles']:
            tiles_map[tile] = doc['_id']

    return tiles_map


# def business_cluster_get(user, tile_cluster_map):
#     business_tile_get(user)
#     # tile_cluster_map = clusters_get()
#
#     for review in user['reviews']:
#         try:
#             review['cluster'] = tile_cluster_map[review['tile10']]
#         except:
#             review['cluster'] = 'Other'
#
#     return user


# def prep_users_save(user):
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['prepro_user']
#     modified = collection.update_one({'_id': user['_id']}, {'$set': user}, upsert=True).modified_count


def prep_user_batch_save(users, page_size=500):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['prepro_user']

    page = 0

    while True:
        _from = page * page_size
        _to = (page + 1) * page_size
        if _to > len(users):
            _to = len(users)
        batch = users[_from:_to]
        bulk = collection.initialize_unordered_bulk_op()
        for item in batch:
            bulk.find({'_id': item['_id']}).upsert().update({'$set': item})
        try:
            bulk.execute()
        except BulkWriteError as err:
            print(err)
            raise
        page += 1
        if _to == len(users):
            break


def main():
    tile_cluster_map = clusters_get()
    users = users_get()
    businessess = business_tile_all_get()
    reviews = reviews_all_get()

    index = 0
    users_len = len(users)

    # processed_users = []

    for user in users:
        print('Processing user {}/{}...'.format(index, users_len))
        user['reviews'] = reviews[user['_id']]
        filtered_reviews = []
        for review in user['reviews']:
            try:
                review['tile10'] = businessess[review['business_id']]
                try:
                    review['cluster'] = tile_cluster_map[review['tile10']]
                except:
                    review['cluster'] = 'Other'
                filtered_reviews.append(review)
            except KeyError:
                pass

        user['reviews'] = filtered_reviews
        # processed_users.append(user)
        index += 1
    prep_user_batch_save(users)


# def _main():
#     tile_cluster_map = clusters_get()
#     processed_users = []
#     index = 0
#     users = users_get()
#     users_len = len(users)
#     for user in users:
#         print('Processing user {}/{}...'.format(index, users_len))
#         user['reviews'] = reviews_get(user['_id'])
#         business_cluster_get(user, tile_cluster_map)
#         processed_users.append(user)
#         # prep_users_save(user)
#         index += 1
#     prep_user_batch_save(processed_users)

if __name__ == '__main__':
    main()