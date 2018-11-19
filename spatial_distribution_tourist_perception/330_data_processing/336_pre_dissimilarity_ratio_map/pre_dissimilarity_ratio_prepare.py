import copy
import json
import os

from spatial_distribution_tourist_perception.common import mongo_functions, map_functions

ZOOMS = [15, 18]
years = []
categories = []


def _get_all_years():
    global years
    _years = set([])
    business_years_reviews = mongo_functions.mongo_get(
        collection='pre_business',
        filter={'ratio_yearly': {'$exists': True}},
        fields={'ratio_yearly': 1}
    )
    for business in business_years_reviews:
        [_years.add(year) for year in business['ratio_yearly'].keys()]
    years = list(_years)

def ratios_group(businesses, zoom):
    global years
    global categories
    business_dict = {}
    for business in businesses:
        tile = business['tile{}'.format(zoom)]
        if tile not in business_dict:
            business_dict[tile] = {category: {year: [] for year in years} for category in categories}
        for category in business['norm_categories']:
            for year, ratio in business['ratio_yearly'].items():
                business_dict[tile][category][year].append(ratio)
                business_dict[tile]['All'][year].append(ratio)
    return business_dict


def _features_prepare(ratios_dict):
    _features_dict = copy.copy(ratios_dict)
    for tile, categories in ratios_dict.items():
        for category, years in categories.items():
            for year, values in years.items():
                ratio_sum = sum(ratios_dict[tile][category][year])
                _features_dict[tile][category][year] = ratio_sum / len(ratios_dict[tile][category][year]) if ratio_sum != 0 else 0
    return [{'tile': key, 'properties': value} for key, value in _features_dict.items()]


def features_prepare(ratios_dict, zoom):
    tile_features = _features_prepare(ratios_dict)
    features = []
    for item in tile_features:
        features.append(map_functions.geojson_polygon_formatter(
            item['properties'],
            item['tile'],
            zoom
        ))
    return features


def _business_categories_get():
    global categories
    categories = mongo_functions.mongo_distinct_get('norm_categories', collection='pre_business')
    categories.append('All')


def geojson_file_create(area_name, zoom, features):
    filename = '{}_z{}.json'.format(area_name, zoom)
    content = json.dumps({'type': 'FeatureCollection', 'features': features})
    with open(os.path.join('data', filename), 'w+') as f:
        f.write(content)
        f.flush()


def prepare():
    areas = mongo_functions.mongo_get(collection='pre_metropolitan_area')
    for area in areas:
        businesses = mongo_functions.mongo_get(
            collection='pre_business',
            filter={'tile10': {'$in': area['tiles']}, 'ratio_yearly': {'$exists': True}},
            fields={'ratio_yearly': 1, 'tile15': 1, 'tile18': 1, 'norm_categories': 1}
        )

        for zoom in ZOOMS:
            ratios_dict = ratios_group(businesses, zoom)
            features = features_prepare(ratios_dict, zoom)
            geojson_file_create(area['_id'], zoom, features)


if __name__ == '__main__':
    _get_all_years()
    _business_categories_get()
    prepare()