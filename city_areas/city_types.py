from common import clusters as clusters_db, prepro_business as prepro_business_db, venues as venues_db, _mongo as mongo_utils
from city_areas.city_types_map import category_to_city_type


def city_types_dict_update(cluster_id, tile, zoom, city_type, city_types_dict):
    key = '{}_{}_z{}_{}'.format(cluster_id, tile, zoom, city_type)
    if key not in city_types_dict:
        city_types_dict[key] = {
            '_id': key,
            'cluster_id': cluster_id,
            'tile': tile,
            'zoom': zoom,
            'city_type': city_type,
            'venues': 0
        }
    city_types_dict[key]['venues'] += 1


def main():
    clusters = [doc for doc in clusters_db.clusters_get(filter={})]
    for cluster in clusters:
        city_types_z18 = {}
        city_types_z15 = {}
        venues = [doc for doc in venues_db.venues_get(filter={'cluster_id': cluster['_id']}, fields={'category_clusters': 1, 'tile18': 1, 'tile15': 1})]
        for venue in venues:
            city_types = set([])
            for category in venue['category_clusters']:
                city_types.update(category_to_city_type[category])
            for item in city_types:
                city_types_dict_update(cluster['_id'], venue['tile18'], 18, item, city_types_z18)
                city_types_dict_update(cluster['_id'], venue['tile15'], 15, item, city_types_z15)
        mongo_utils.batch_upsert(
            [doc for doc in city_types_z18.values()],
            collection='city_types_areas',
            update="{'$set': item}"
        )
        mongo_utils.batch_upsert(
            [doc for doc in city_types_z15.values()],
            collection='city_types_areas',
            update="{'$set': item}"
        )


if __name__ == '__main__':
    main()