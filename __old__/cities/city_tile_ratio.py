from common import mongo_utils

tile_object_example = {
    'city': '',
    'venues': 0,
    'review_counters': {
        'tourist': 0,
        'locals': 0,
        'total': 0
    },
    'city_type_counters': {

    }
}


def tiled_reviews_group(review, tiled_reviews_dict, zoom):
    tile_key = 'tile{}'.format(zoom)
    if review[tile_key] not in tiled_reviews_dict:
        tiled_reviews_dict[review[tile_key]] = {'tourist': [], 'local': []}
    if review['user_tourist']:
        tiled_reviews_dict[review[tile_key]]['tourist'].append(review)
    else:
        tiled_reviews_dict[review[tile_key]]['local'].append(review)


def main():
    for city in mongo_utils.mongo_get(collection='cities'):
        reviews = mongo_utils.mongo_get(collection='prepro_reviews', filter={'cluster': city['_id']})
        tiled15_reviews = {}
        tiled18_reviews = {}
        for review in reviews:
            tiled_reviews_group(review, tiled15_reviews, 15)
            tiled_reviews_group(review, tiled18_reviews, 18)
        print('yey')


if __name__ == '__main__':
    main()
