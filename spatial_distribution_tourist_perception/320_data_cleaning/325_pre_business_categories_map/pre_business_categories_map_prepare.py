import json
import os

from spatial_distribution_tourist_perception.common import mongo_functions, map_functions

ZOOMS = [15, 18]


def tile_features_prepare(businessess, zoom):
    tile_features = {}
    for business in businessess:
        if business['tile{}'.format(zoom)] not in tile_features:
            tile_features[business['tile{}'.format(zoom)]] = {
                'Monuments': 0,
                'Museums & art galleries': 0,
                'Cinemas & concert & theatres': 0,
                'Nightclubs & bars': 0,
                'Cafés & restaurants': 0,
                'Shops & consumptive activies': 0,
                'Offices & work premises': 0,
                'Sport stadia & events': 0,
                'Public mobility': 0,
                'Private transports': 0
            }
        for category in business['norm_categories']:
            tile_features[business['tile{}'.format(zoom)]][category] += 1
    return [{'tile': key, 'properties': value} for key, value in tile_features.items()]


def features_prepare(businessess, zoom):
    tile_features = tile_features_prepare(businessess, zoom)
    features = []
    for item in tile_features:
        features.append(map_functions.geojson_polygon_formatter(
            item['properties'],
            item['tile'],
            zoom
        ))
    return features


def geojson_file_create(area_name, zoom, features):
    filename = '{}_z{}.json'.format(area_name, zoom)
    content = json.dumps({'type': 'FeatureCollection', 'features': features})
    with open(os.path.join('data', filename), 'w+') as f:
        f.write(content)
        f.flush()


def areas_json_create(areas):
    _areas = {area['_id']: {'name': area['_id'], 'center': area['center']} for area in areas}
    content = json.dumps(_areas)
    with open(os.path.join('data', 'areas.json'), 'w+') as f:
        f.write(content)
        f.flush()


def prepare():
    areas = mongo_functions.mongo_get(collection='pre_metropolitan_area')
    for area in areas:
        businessess = mongo_functions.mongo_get(collection='pre_business', filter={'tile10': {'$in': area['tiles']}})

        for zoom in ZOOMS:
            features = features_prepare(businessess, zoom)
            geojson_file_create(area['_id'], zoom, features)
    areas_json_create(areas)


if __name__ == '__main__':
    prepare()
