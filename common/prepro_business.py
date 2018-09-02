from ._mongo import mongo_get


def prepro_business_get(filter=None, fields=None):
    return mongo_get(col='prepro_business', filter=filter, fields=fields)