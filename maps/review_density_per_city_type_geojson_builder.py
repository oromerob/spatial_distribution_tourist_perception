import json
import os

from common import mongo_utils, tiles
from __old__.city_areas import city_types_map


def review_venue_ids_get(users, cluster, venue_id_dict):
    for user in users:
        for review in user['reviews']:
            if review['cluster'] == cluster:
                if review['business_id'] not in venue_id_dict:
                    venue_id_dict[review['business_id']] = 0
                venue_id_dict[review['business_id']] += 1


def clusterize_reviews(venues, venue_id_dict, city_types_dict, key, zoom):
    tile_key = 'tile{}'.format(zoom)
    for venue_id, review_count in venue_id_dict.items():
        try:
            city_types_set = set([])
            for category_cluster in venues[venue_id]['category_clusters']:
                city_types_set.update(city_types_map.category_to_city_type[category_cluster])
            for city_type in city_types_set:
                if venues[venue_id][tile_key] not in city_types_dict[city_type]:
                    city_types_dict[city_type][venues[venue_id][tile_key]] = {'locals': 0, 'visitors': 0, 'all': 0}
                city_types_dict[city_type][venues[venue_id][tile_key]][key] += review_count
        except Exception as e:
            pass


def geojson_dict_formatter(tile, counters, zoom):
    xtile, ytile = tile.split('_')
    polygon_boundaries = tiles.tile_boundaries(int(xtile), int(ytile), zoom)
    geo_item = {
        "type": "Feature",
        "properties": counters,
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [polygon_boundaries[1], polygon_boundaries[0]],
                [polygon_boundaries[1], polygon_boundaries[2]],
                [polygon_boundaries[3], polygon_boundaries[2]],
                [polygon_boundaries[3], polygon_boundaries[0]],
                [polygon_boundaries[1], polygon_boundaries[0]]
            ]]
        }
    }
    # print(json.dumps(geo_item))
    return geo_item


def counters_prepare(city_types_dict):
    for city_type, tile_dict in city_types_dict.items():
        for tile, counters in tile_dict.items():
            counters['all'] = counters['locals'] + counters['visitors']
            counters['visitors_proportion'] = counters['visitors'] / counters['all']
            counters['visitors_special'] = counters['visitors'] * counters['visitors_proportion']


def geojson_dict_populate(city_types_dict, geojson_dict, zoom):
    for city_type, tile_dict in city_types_dict.items():
        for tile, counters in tile_dict.items():
            geojson_dict[city_type]['features'].append(geojson_dict_formatter(tile, counters, zoom))


def city_clusters_file_save(cluster, geojson_dict, zoom):
    filename = '{}_z{}.json'.format(cluster['_id'], zoom)
    content = json.dumps(geojson_dict)
    dirname = 'review_density_per_city_type_map'
    os.makedirs(dirname, exist_ok=True)
    with open(os.path.join(dirname, filename), 'w+') as f:
        f.write(content)
        f.flush()


def main(zoom):
    # clusters = mongo_utils.mongo_get(collection='clusters')
    clusters = mongo_utils.mongo_get(collection='cities')
    for cluster in clusters:
        city_types_dict = {
            'tourist': {},
            'shopping': {},
            'nightlife': {},
            'sport': {},
            'cultural': {},
            'historic': {},
            'business': {}
        }
        geojson_dict = {
            'tourist': {'type': 'FeatureCollection', 'features': []},
            'shopping': {'type': 'FeatureCollection', 'features': []},
            'nightlife': {'type': 'FeatureCollection', 'features': []},
            'sport': {'type': 'FeatureCollection', 'features': []},
            'cultural': {'type': 'FeatureCollection', 'features': []},
            'historic': {'type': 'FeatureCollection', 'features': []},
            'business': {'type': 'FeatureCollection', 'features': []}
        }
        locals_reviews_venues = {}
        visitors_reviews_venues = {}

        locals = mongo_utils.mongo_get(collection='prepro_user', filter={'local': cluster['_id']}, fields={'reviews': 1})
        visitors = mongo_utils.mongo_get(collection='prepro_user', filter={'visited': cluster['_id']}, fields={'reviews': 1})

        review_venue_ids_get(locals, cluster['_id'], locals_reviews_venues)
        review_venue_ids_get(visitors, cluster['_id'], visitors_reviews_venues)

        # venues = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='venues', filter={'cluster_id': cluster['_id']}, fields={'tile18': 1, 'tile15': 1, 'category_clusters': 1})}
        venues = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='city_venues', filter={'cluster_id': cluster['_id']}, fields={'tile18': 1, 'tile15': 1, 'category_clusters': 1})}

        clusterize_reviews(venues, locals_reviews_venues, city_types_dict, 'locals', zoom)
        clusterize_reviews(venues, visitors_reviews_venues, city_types_dict, 'visitors', zoom)

        counters_prepare(city_types_dict)
        geojson_dict_populate(city_types_dict, geojson_dict, zoom)

        city_clusters_file_save(cluster, geojson_dict, zoom)

        print('yey')


if __name__ == '__main__':
    main(18)
