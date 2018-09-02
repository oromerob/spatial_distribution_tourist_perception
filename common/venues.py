import sys

import pymongo
from pymongo.errors import BulkWriteError

from ._mongo import mongo_get, batch_update


def venues_get(filter=None, fields=None):
    return mongo_get(col='venues', filter=filter, fields=fields)


def venues_batch_update(items, update=None, page_size=500):
    return batch_update(items, collection='venues', update=update, page_size=page_size)

# def venues_batch_update(items, update=None, page_size=500):
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['venues']
#
#     page = 0
#     items_len = len(items)
#
#     print('\n')
#     while True:
#         _from = page * page_size
#         _to = (page + 1) * page_size
#         if _to > len(items):
#             _to = len(items)
#
#         sys.stdout.write('\rSaving items {}/{}...'.format(_to, items_len))
#         sys.stdout.flush()
#
#         batch = items[_from:_to]
#         bulk = collection.initialize_unordered_bulk_op()
#         for item in batch:
#             bulk.find({'_id': item['_id']}).update(eval(update))
#         try:
#             bulk.execute()
#         except BulkWriteError as err:
#             print(err)
#             raise
#         page += 1
#         if _to == len(items):
#             break
#
#     client.close()