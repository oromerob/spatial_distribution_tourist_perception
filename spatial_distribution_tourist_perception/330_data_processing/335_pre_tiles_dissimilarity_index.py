from spatial_distribution_tourist_perception.common import mongo_functions


def tile_dissimilarity_ratio(tourist_unique_counter, residents_unique_counter, total_tourist, total_residents):
    return tourist_unique_counter / total_tourist - residents_unique_counter / total_residents


def city_unique_tourist_get(reviews, area):
    return {review['user_id'] for review in reviews if review['user_from'] != area['_id']}


def city_unique_residents_get(reviews, area):
    return {review['user_id'] for review in reviews if review['user_from'] == area['_id']}


def tile_reviews_dict_group(reviews, zoom):
    tile_reviews_dict = {}
    for review in reviews:
        if review['tile{}'.format(zoom)] not in tile_reviews_dict:
            tile_reviews_dict[review['tile{}'.format(zoom)]] = []
        tile_reviews_dict[review['tile{}'.format(zoom)]].append(review)
    return tile_reviews_dict


def main():
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area', fields={}):
        reviews = mongo_functions.mongo_get(
            collection='pre_review',
            filter={'city_area': area['_id'], 'user_from': {'$exists': True}},
            fields={'tile_id': 1, 'user_id': 1, 'tile15': 1, 'tile18': 1, 'user_from': 1}
        )
        city_unique_tourist = city_unique_tourist_get(reviews, area)
        city_unique_residents = city_unique_residents_get(reviews, area)
        total_tourist = len(city_unique_tourist)
        total_residents = len(city_unique_residents)
        for zoom in [15, 18]:
            tile_reviews_dict = tile_reviews_dict_group(reviews, zoom)
            pre_tile_list = []
            for tile, tile_reviews in tile_reviews_dict.items():
                tourist_reviews = [review['user_id'] for review in tile_reviews if review['user_from'] != area['_id']]
                resident_reviews = [review['user_id'] for review in tile_reviews if review['user_from'] == area['_id']]
                pre_tile = {
                    '_id': '{}_{}'.format(tile, zoom),
                    'area_id': area['_id'],
                    'tourist_unique': list(set(tourist_reviews)),
                    'resident_unique': list(set(resident_reviews)),
                    'tourist_review_counter': len(tourist_reviews),
                    'resident_review_counter': len(resident_reviews)
                }
                pre_tile['tourist_unique_counter'] = len(pre_tile['tourist_unique'])
                pre_tile['resident_unique_counter'] = len(pre_tile['resident_unique'])
                pre_tile['ratio_signed'] = tile_dissimilarity_ratio(
                    pre_tile['tourist_unique_counter'], 
                    pre_tile['resident_unique_counter'], 
                    total_tourist, 
                    total_residents
                )
                pre_tile['ratio'] = pre_tile['ratio_signed'] if pre_tile['ratio_signed'] > 0 else -1 * pre_tile['ratio_signed']
                pre_tile_list.append(pre_tile)

            mongo_functions.batch_upsert(pre_tile_list, collection='pre_tile', update='{"$set": item}')


def export():
    pass


if __name__ == '__main__':
    main()
