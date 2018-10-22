from spatial_distribution_tourist_perception.common import tiles as tile_functions, mongo_functions


def prepare():
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area'):
        business = mongo_functions.mongo_get(
            collection='pre_business',
            filter={'tile15': {'$in': area['city_tiles15']}},
            fields={'tile10': 1, 'tile15': 1, 'tile18': 1, 'norm_categories': 1}
        )
        business_ids = [doc['_id'] for doc in business]
        reviews = mongo_functions.mongo_get(collection='review', filter={'business_id': {'$in': business_ids}})
        business_dict = {doc['_id']: doc for doc in business}
        for review in reviews:
            review['tile10'] = business_dict[review['business_id']]['tile10']
            review['tile15'] = business_dict[review['business_id']]['tile15']
            review['tile18'] = business_dict[review['business_id']]['tile18']
            review['norm_categories'] = business_dict[review['business_id']]['norm_categories']
            review['city_area'] = area['_id']
        mongo_functions.batch_upsert(reviews, collection='pre_review', update="{'$set': item}")


if __name__ == '__main__':
    prepare()
