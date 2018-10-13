import json
import os

from spatial_distribution_tourist_perception.common import mongo_functions, map_functions

ZOOMS = [15, 18]


def business_count_per_tile(businessess, zoom):
    business_counter = {}
    for business in businessess:
        if business['tile{}'.format(zoom)] not in business_counter:
            business_counter[business['tile{}'.format(zoom)]] = 0
        business_counter[business['tile{}'.format(zoom)]] += 1
    return [{'tile': key, 'business': value} for key, value in business_counter.items()]


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
            business_counter_tiled = business_count_per_tile(businessess, zoom)
            polygons = []
            for tile in business_counter_tiled:
                polygons.append(map_functions.geojson_polygon_formatter(
                    {'business': tile['business']},
                    tile['tile'],
                    zoom
                ))
            geojson_file_create(area['_id'], zoom, polygons)
    areas_json_create(areas)


if __name__ == '__main__':
    prepare()
