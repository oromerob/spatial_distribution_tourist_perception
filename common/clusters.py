# import sys
#
# import pymongo
# from pymongo.errors import BulkWriteError

from ._mongo import mongo_get


def clusters_get(filter=None, fields=None):
    return mongo_get(
        col='clusters',
        filter=filter,
        fields=fields
    )