import json
import os

from common import _mongo as mongo_utils
from tiles import tiles


def review_venue_ids_get(users, cluster, venue_id_dict):
    for user in users:
        for review in user['reviews']:
            if review['cluster'] == cluster:
                if review['business_id'] not in venue_id_dict:
                    venue_id_dict[review['business_id']] = 0
                venue_id_dict[review['business_id']] += 1


def clusterize_reviews(venues, venue_id_dict, zoom):
    tile_key = 'tile{}'.format(zoom)
    clustered_reviews = {}
    excluded_venues = {}
    for venue_id, review_count in venue_id_dict.items():
        try:
            if venues[venue_id][tile_key] not in clustered_reviews:
                clustered_reviews[venues[venue_id][tile_key]] = 0
            clustered_reviews[venues[venue_id][tile_key]] += review_count
        except Exception as e:
            print(venue_id)
            excluded_venues.update({venue_id: review_count})
    return clustered_reviews, excluded_venues


def review_clusters_add_excluded_venues(venues, venue_rw_count, review_clusters, zoom):
    for venue_id, review_count in venue_rw_count.items():
        _tile = tiles.deg2num(venues[venue_id]['latitude'], venues[venue_id]['latitude'], zoom)
        tile = '{}_{}'.format(_tile[0], _tile[1])
        if tile not in review_clusters:
            review_clusters[tile] = 0
        review_clusters[tile] += review_count


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


def city_clusters_dict_create(locals_review_clusters, visitors_review_clusters, zoom):
    city_clusters = {}
    tiles = {tile for tile in locals_review_clusters.keys()}.union({tile for tile in visitors_review_clusters.keys()})
    for tile in tiles:
        city_clusters[tile] = {
            'all': 0,
            'locals': 0,
            'visitors': 0
        }
    for tile, count in locals_review_clusters.items():
        city_clusters[tile]['all'] += count
        city_clusters[tile]['locals'] += count
    for tile, count in visitors_review_clusters.items():
        city_clusters[tile]['all'] += count
        city_clusters[tile]['visitors'] += count

    city_clusters_list = []
    for tile, counters in city_clusters.items():
        city_clusters_list.append(geojson_dict_formatter(tile, counters, zoom))

    return city_clusters_list


def city_clusters_file_save(cluster, city_clusters, zoom):
    filename = '{}_z{}.json'.format(cluster['_id'], zoom)
    content = json.dumps({'type': 'FeatureCollection', 'features': city_clusters})
    dirname = 'reviews_cluster_map'
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

        venues = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='venues', filter={'cluster_id': cluster['_id']}, fields={'tile18': 1, 'tile15': 1})}

        locals_review_clusters, locals_excluded_venues_rw_count = clusterize_reviews(venues, locals_reviews_venues, zoom)
        visitors_review_clusters, visitors_excluded_venues_rw_count = clusterize_reviews(venues, visitors_reviews_venues, zoom)

        locals_excluded_venues = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='business', filter={'_id': {'$in': [item for item in locals_excluded_venues_rw_count.keys()]}}, fields={'latitude': 1, 'longitude': 1})}
        visitors_excluded_venues = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='business', filter={'_id': {'$in': [item for item in visitors_excluded_venues_rw_count.keys()]}}, fields={'latitude': 1, 'longitude': 1})}

        review_clusters_add_excluded_venues(locals_excluded_venues, locals_excluded_venues_rw_count, locals_review_clusters, zoom)
        review_clusters_add_excluded_venues(visitors_excluded_venues, visitors_excluded_venues_rw_count, visitors_review_clusters, zoom)

        city_clusters = city_clusters_dict_create(locals_review_clusters, visitors_review_clusters, zoom)

        city_clusters_file_save(cluster, city_clusters, zoom)

        print('yey')


        # mongo_utils.batch_upsert(
        #     [doc for doc in city_types_z18.values()],
        #     collection='city_types_areas',
        #     update="{'$set': item}"
        # )
        # mongo_utils.batch_upsert(
        #     [doc for doc in city_types_z15.values()],
        #     collection='city_types_areas',
        #     update="{'$set': item}"
        # )


if __name__ == '__main__':
    main(15)
