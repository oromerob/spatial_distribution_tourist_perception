import copy
import json
import os

from common import _mongo as mongo_utils
from tiles import tiles
from city_areas import city_types_map

# CITY_TYPES = {
#     'tourist': {'locals': 0, 'visitors': 0, 'all': 0, 'visitors_proportion': 0},
#     'shopping': {'locals': 0, 'visitors': 0, 'all': 0, 'visitors_proportion': 0},
#     'nightlife': {'locals': 0, 'visitors': 0, 'all': 0, 'visitors_proportion': 0},
#     'sport': {'locals': 0, 'visitors': 0, 'all': 0, 'visitors_proportion': 0},
#     'cultural': {'locals': 0, 'visitors': 0, 'all': 0, 'visitors_proportion': 0},
#     'historic': {'locals': 0, 'visitors': 0, 'all': 0, 'visitors_proportion': 0},
#     'business': {'locals': 0, 'visitors': 0, 'all': 0, 'visitors_proportion': 0}
# }

CITY_TYPES_DICT = {
    'tourist': {},
    'shopping': {},
    'nightlife': {},
    'sport': {},
    'cultural': {},
    'historic': {},
    'business': {}
}

GEOJSON_DICT = {
    'tourist': {'type': 'FeatureCollection', 'features': []},
    'shopping': {'type': 'FeatureCollection', 'features': []},
    'nightlife': {'type': 'FeatureCollection', 'features': []},
    'sport': {'type': 'FeatureCollection', 'features': []},
    'cultural': {'type': 'FeatureCollection', 'features': []},
    'historic': {'type': 'FeatureCollection', 'features': []},
    'business': {'type': 'FeatureCollection', 'features': []}
}


def review_venue_ids_get(users, cluster, venue_id_dict):
    for user in users:
        for review in user['reviews']:
            if review['cluster'] == cluster:
                if review['business_id'] not in venue_id_dict:
                    venue_id_dict[review['business_id']] = 0
                venue_id_dict[review['business_id']] += 1


# def clusterize_reviews(venues, venue_id_dict, key, zoom, clustered_reviews):
def clusterize_reviews(venues, venue_id_dict, key, zoom):
    tile_key = 'tile{}'.format(zoom)
    # clustered_reviews = {}
    # excluded_venues = {}
    for venue_id, review_count in venue_id_dict.items():
        try:
            # if venues[venue_id][tile_key] not in clustered_reviews:
            #     clustered_reviews[venues[venue_id][tile_key]] = copy.copy(CITY_TYPES)
            city_types_set = set([])
            for category_cluster in venues[venue_id]['category_clusters']:
                city_types_set.update(city_types_map.category_to_city_type[category_cluster])
            for city_type in city_types_set:
                if venues[venue_id][tile_key] not in CITY_TYPES_DICT[city_type]:
                    CITY_TYPES_DICT[city_type][venues[venue_id][tile_key]] = {'locals': 0, 'visitors': 0, 'all': 0}
                    # clustered_reviews[venues[venue_id][tile_key]] = copy.copy(CITY_TYPES)
                # if city_type not in clustered_reviews[venues[venue_id][tile_key]]:
                #     clustered_reviews[venues[venue_id][tile_key]][city_type] = {'locals': 0, 'visitors': 0, 'all': 0}
                # clustered_reviews[venues[venue_id][tile_key]][city_type][key] += review_count
                CITY_TYPES_DICT[city_type][venues[venue_id][tile_key]][key] += review_count
        except Exception as e:
            # print(e)
            # print(venue_id)
            # excluded_venues.update({venue_id: review_count})
            pass
    # return clustered_reviews  # , excluded_venues


# def review_clusters_add_excluded_venues(venues, venue_rw_count, review_clusters, zoom):
#     for venue_id, review_count in venue_rw_count.items():
#         _tile = tiles.deg2num(venues[venue_id]['latitude'], venues[venue_id]['latitude'], zoom)
#         tile = '{}_{}'.format(_tile[0], _tile[1])
#         if tile not in review_clusters:
#             review_clusters[tile] = 0
#         review_clusters[tile] += review_count


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

#
# def city_type_counters_aggregates(zoom):
#     for city_type, geojson_obj in CITY_TYPES_DICT.items():
#         for tile in

def counters_prepare():
    for city_type, tile_dict in CITY_TYPES_DICT.items():
        for tile, counters in tile_dict.items():
            counters['all'] = counters['locals'] + counters['visitors']
            counters['visitors_proportion'] = counters['visitors'] / counters['all']


def geojson_dict_populate(zoom):
    for city_type, tile_dict in CITY_TYPES_DICT.items():
        for tile, counters in tile_dict.items():
            GEOJSON_DICT[city_type]['features'].append(geojson_dict_formatter(tile, counters, zoom))


# def city_clusters_dict_create(clustered_reviews, zoom):
#     city_clusters_list = []
#     for tile, city_type_dict in clustered_reviews.items():
#         for city_type, counters in city_type_dict.items():
#             counters['all'] = counters['locals'] + counters['visitors']
#             counters['visitors_proportion'] = counters['visitors'] / counters['all']
#             #counters['visitors_per_local'] = counters['visitors'] / counters['locals']
#         city_clusters_list.append(geojson_dict_formatter(tile, city_type_dict, zoom))
#     return city_clusters_list


# def city_clusters_file_save(cluster, city_clusters, zoom):
#     filename = '{}_z{}.json'.format(cluster['_id'], zoom)
#     content = json.dumps({'type': 'FeatureCollection', 'features': city_clusters})
#     dirname = 'review_density_per_city_type_map'
#     os.makedirs(dirname, exist_ok=True)
#     with open(os.path.join(dirname, filename), 'w+') as f:
#         f.write(content)
#         f.flush()


def city_clusters_file_save(cluster, zoom):
    filename = '{}_z{}.json'.format(cluster['_id'], zoom)
    content = json.dumps(GEOJSON_DICT)
    dirname = 'review_density_per_city_type_map'
    os.makedirs(dirname, exist_ok=True)
    with open(os.path.join(dirname, filename), 'w+') as f:
        f.write(content)
        f.flush()


def main(zoom):
    clusters = mongo_utils.mongo_get(collection='clusters')
    for cluster in clusters:
        locals = mongo_utils.mongo_get(collection='prepro_user', filter={'local': cluster['_id']}, fields={'reviews': 1})
        visitors = mongo_utils.mongo_get(collection='prepro_user', filter={'visited': cluster['_id']}, fields={'reviews': 1})
        locals_reviews_venues = {}
        visitors_reviews_venues = {}
        review_venue_ids_get(locals, cluster['_id'], locals_reviews_venues)
        review_venue_ids_get(visitors, cluster['_id'], visitors_reviews_venues)

        venues = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='venues', filter={'cluster_id': cluster['_id']}, fields={'tile18': 1, 'tile15': 1, 'category_clusters': 1})}

        # locals_review_clusters, locals_excluded_venues_rw_count = clusterize_reviews(venues, locals_reviews_venues, zoom)
        # visitors_review_clusters, visitors_excluded_venues_rw_count = clusterize_reviews(venues, visitors_reviews_venues, zoom)

        # clustered_reviews = {}
        # clusterize_reviews(venues, locals_reviews_venues, 'locals', zoom, clustered_reviews)
        # clusterize_reviews(venues, visitors_reviews_venues, 'visitors', zoom, clustered_reviews)

        clusterize_reviews(venues, locals_reviews_venues, 'locals', zoom)
        clusterize_reviews(venues, visitors_reviews_venues, 'visitors', zoom)

        # locals_excluded_venues = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='business', filter={'_id': {'$in': [item for item in locals_excluded_venues_rw_count.keys()]}}, fields={'latitude': 1, 'longitude': 1})}
        # visitors_excluded_venues = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='business', filter={'_id': {'$in': [item for item in visitors_excluded_venues_rw_count.keys()]}}, fields={'latitude': 1, 'longitude': 1})}

        # review_clusters_add_excluded_venues(locals_excluded_venues, locals_excluded_venues_rw_count, locals_review_clusters, zoom)
        # review_clusters_add_excluded_venues(visitors_excluded_venues, visitors_excluded_venues_rw_count, visitors_review_clusters, zoom)

        # city_clusters = city_clusters_dict_create(clustered_reviews, zoom)
        #
        # city_clusters_file_save(cluster, city_clusters, zoom)

        counters_prepare()
        geojson_dict_populate(zoom)

        city_clusters_file_save(cluster, zoom)

        # print(CITY_TYPES_DICT)
        print('yey')


if __name__ == '__main__':
    main(15)
