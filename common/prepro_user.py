import ast
import sys

import pymongo
from pymongo.errors import BulkWriteError

from ._mongo import mongo_get


def prepro_users_get(filter=None, fields=None):
    return mongo_get(
        col='prepro_user',
        filter=filter,
        fields=fields
    )


def prepro_user_batch_update(users, update=None, page_size=500):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['prepro_user']

    page = 0
    users_len = len(users)

    print('\n')
    while True:
        _from = page * page_size
        _to = (page + 1) * page_size
        if _to > len(users):
            _to = len(users)

        sys.stdout.write('\rSaving users {}/{}...'.format(_to, users_len))
        sys.stdout.flush()

        batch = users[_from:_to]
        bulk = collection.initialize_unordered_bulk_op()
        for item in batch:
            # bulk.find({'_id': item['_id']}).update(ast.literal_eval(update))
            bulk.find({'_id': item['_id']}).update(eval(update))
        try:
            bulk.execute()
        except BulkWriteError as err:
            print(err)
            raise
        page += 1
        if _to == len(users):
            break

    client.close()