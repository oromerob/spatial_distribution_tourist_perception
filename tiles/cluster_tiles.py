import pymongo


def tiles_get():
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['prepro_business']

    tiles = collection.find().distinct('tile10')
    if not tiles:
        raise ValueError

    tiles_sorted = sorted(tiles, key=lambda x: x.split('_')[0])
    return tiles_sorted


def cluster_process(tiles, clustered, cluster_):
    if len(cluster_['new']) == 0:
        cluster_['new'].append(tiles.pop(0))
        return tiles, clustered, cluster_

    _tiles = cluster_['new']
    cluster_['new'] = []
    for tile in _tiles:
        tileX = int(tile.split('_')[0])
        tileY = int(tile.split('_')[1])
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                tile__ = '{}_{}'.format(tileX + x, tileY + y)
                if tile__ in tiles:
                    cluster_['new'].append(tile__)
                    tiles.remove(tile__)
    cluster_['done'] = cluster_['done'] + _tiles
    if len(cluster_['new']) == 0:
        clustered.append(cluster_['done'])
    return tiles, clustered, cluster_


def cluster(tiles, clustered=None, cluster_=None):
    if clustered is None:
        clustered = []
    if cluster_ is None:
        cluster_ = {
            'done': [],
            'new': []
        }

    tiles, clustered, cluster_ = cluster_process(tiles, clustered, cluster_)

    if len(cluster_['new']) > 0:
        return cluster(tiles, clustered=clustered, cluster_=cluster_)
    if len(tiles) > 0:
        return cluster(tiles, clustered=clustered)
    return clustered


def clusters_save(bulk):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['clusters']
    ids = collection.insert_many(bulk).inserted_ids


def venues_count(tiles):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['prepro_business']
    venue_count = collection.count({'tile10': {'$in': tiles}})
    return venue_count


if __name__ == '__main__':
    tiles = tiles_get()
    clusters = cluster(tiles)

    clusters_ = []
    for cluster__ in clusters:
        cluster_ = {
            '_id': cluster__[0],
            'tiles': cluster__,
            'venues': venues_count(cluster__)
        }
        if cluster_['venues'] > 100:
            clusters_.append(cluster_)

    clusters_sorted = sorted(clusters_, key=lambda x: x['venues'], reverse=True)

    clusters_save(clusters_[:11])
    print('yey')