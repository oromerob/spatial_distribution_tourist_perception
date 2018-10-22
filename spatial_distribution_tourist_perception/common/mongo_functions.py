import sys

import pymongo
from pymongo.errors import BulkWriteError


def mongo_get(collection=None, filter=None, fields=None, page_size=100000):
    if collection is None:
        raise Exception
    if filter is None:
        filter = {}
    find_params = [filter]
    if fields is not None and type(fields) == dict:
        find_params.append(fields)

    client = pymongo.MongoClient('localhost', 27018)
    db = client.cett
    col = db[collection]

    page = 0

    res = []

    print()
    while True:
        sys.stdout.write('\rQuerying "{}" page {}...'.format(collection, page))
        sys.stdout.flush()
        # print('Querying "{}" page {}...'.format(collection, page))

        cursor = col.find(*find_params).skip(page_size * page).limit(page_size)

        _res = [doc for doc in cursor]

        res += _res

        if len(_res) < page_size:
            break

        page += 1

    client.close()

    print('Returning {} elements from "{}"'.format(len(res), collection))
    return res


def batch_update(items, collection=None, update=None, page_size=500):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.cett
    col = db[collection]

    page = 0
    items_len = len(items)

    print('\n')
    while True:
        _from = page * page_size
        _to = (page + 1) * page_size
        if _to > len(items):
            _to = len(items)

        sys.stdout.write('\rSaving items {}/{}...'.format(_to, items_len))
        sys.stdout.flush()

        batch = items[_from:_to]
        bulk = col.initialize_unordered_bulk_op()
        for item in batch:
            bulk.find({'_id': item['_id']}).update(eval(update))
        try:
            bulk.execute()
        except BulkWriteError as err:
            print(err)
            raise
        page += 1
        if _to == len(items):
            break

    print('\n')
    client.close()


def batch_upsert(items, collection=None, update=None, page_size=500):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.cett
    col = db[collection]

    page = 0
    items_len = len(items)

    print('\n')
    while True:
        _from = page * page_size
        _to = (page + 1) * page_size
        if _to > len(items):
            _to = len(items)

        sys.stdout.write('\rSaving items {}/{}...'.format(_to, items_len))
        sys.stdout.flush()

        batch = items[_from:_to]
        bulk = col.initialize_unordered_bulk_op()
        for item in batch:
            bulk.find({'_id': item['_id']}).upsert().update(eval(update))
        try:
            bulk.execute()
        except BulkWriteError as err:
            print(err)
            raise
        page += 1
        if _to == len(items):
            break

    print('\n')
    client.close()
