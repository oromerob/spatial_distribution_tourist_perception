from common import mongo_utils, tiles as tile_utils


def cluster_process(tiles, initial_tile, clustered, cluster_):
    if len(cluster_['new']) == 0:
        # cluster_['new'].append(tiles.pop(0))
        cluster_['new'].append(initial_tile)
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


def clusterize(tiles, initial_tile, clustered=None, cluster_=None):
    if clustered is None:
        clustered = []
    if cluster_ is None:
        cluster_ = {
            'done': [],
            'new': []
        }

    tiles, clustered, cluster_ = cluster_process(tiles, initial_tile, clustered, cluster_)

    if len(cluster_['new']) > 0:
        return clusterize(tiles, initial_tile, clustered=clustered, cluster_=cluster_)
    return clustered


def venues_group_by_tile15(venues):
    tile15_dict = {}
    for venue in venues:
        if venue['tile15'] not in tile15_dict:
            tile15_dict[venue['tile15']] = []
        tile15_dict[venue['tile15']].append(venue)
    return tile15_dict


if __name__ == '__main__':
    clusters = mongo_utils.mongo_get(collection='clusters')

    for cluster in clusters:
        venues = mongo_utils.mongo_get(collection='venues', filter={'cluster_id': cluster['_id']})
        tile15_dict = venues_group_by_tile15(venues)
        tile15_ordered_list = sorted([(key, value) for key, value in tile15_dict.items()], key=lambda x: len(x[1]), reverse=True)
        city_cluster = clusterize(set([tile for tile in tile15_dict.keys()]), tile15_ordered_list[0][0])
        city_venues = []
        for tile in city_cluster[0]:
            city_venues += tile15_dict[tile]
        # mongo_utils.batch_upsert(city_venues, collection='city_venues', update="{'$set': item}")
        city = {
            '_id': cluster['_id'],
            'name': cluster['name'],
            'center': tile_utils.tile_center(int(tile15_ordered_list[0][0].split('_')[0]), int(tile15_ordered_list[0][0].split('_')[1]), 15),
            'cluster_id': cluster['_id'],
            'venues_count': len(city_venues)
        }
        mongo_utils.batch_upsert([city], collection='cities', update="{'$set': item}")
        print('yey')