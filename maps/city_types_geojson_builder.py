import json
import os

from common import _mongo as mongo_utils
from tiles import tiles


def geojson_dict_formatter(city_type_tiled_object, zoom):
    xtile, ytile = city_type_tiled_object['tile'].split('_')
    polygon_boundaries = tiles.tile_boundaries(int(xtile), int(ytile), zoom)
    geo_item = {
        "type": "Feature",
        "properties": {"venues": city_type_tiled_object['venues']},
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


def main(zoom):
    clusters = mongo_utils.mongo_get(col='clusters', filter={})
    for cluster in clusters:
        tiles = mongo_utils.mongo_get(col='city_types_areas', filter={'cluster_id': cluster['_id'], 'zoom': zoom})
        city_types = {}
        for tile in tiles:
            if tile['city_type'] not in city_types:
                city_types[tile['city_type']] = []
            city_types[tile['city_type']].append(geojson_dict_formatter(tile, zoom))
        for key, city_type_tiles in city_types.items():
            filename = '{}_{}_z{}.json'.format(cluster['_id'], key, zoom)
            content = json.dumps({'type': 'FeatureCollection', 'features': city_type_tiles})
            with open(os.path.join('city_types_map', filename), 'w+') as f:
                f.write(content)
                f.flush()
        print('yey')


if __name__ == '__main__':
    main(15)