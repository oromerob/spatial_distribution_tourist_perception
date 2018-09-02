from ._mongo import mongo_get


def reviews_get(filter=None, fields=None):
    return mongo_get(col='review', filter=filter, fields=fields)
