from common import _mongo as mongo_utils


def main(zoom):
    clusters = mongo_utils.mongo_get(col='clusters', filter={})
    for cluster in clusters:
        tiles = mongo_utils.mongo_get(col='city_types_areas', filter={'cluster_id': cluster['_id'], 'zoom': zoom, 'city_type': 'business'})
        ordered_tiles = sorted(tiles, key=lambda x: x['venues'], reverse=True)
        print('yeye')


if __name__ == '__main__':
    main(15)