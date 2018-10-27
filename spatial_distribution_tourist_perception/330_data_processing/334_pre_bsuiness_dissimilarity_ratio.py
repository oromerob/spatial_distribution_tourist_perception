from spatial_distribution_tourist_perception.common import mongo_functions


def business_dissimilarity_ratio(business_reviews, total_visitors, total_residents, area):
    business_unique_visitors = {review['user_id'] for review in business_reviews if review['user_from'] != area['_id']}
    business_unique_locals = {review['user_id'] for review in business_reviews if review['user_from'] == area['_id']}
    visitors = len(business_unique_visitors)
    residents = len(business_unique_locals)
    return visitors / total_visitors - residents / total_residents


def city_unique_visitors_get(reviews, area):
    return {review['user_id'] for review in reviews if review['user_from'] != area['_id']}


def city_unique_residents_get(reviews, area):
    return {review['user_id'] for review in reviews if review['user_from'] == area['_id']}


def business_reviews_dict_group(reviews):
    business_reviews_dict = {}
    for review in reviews:
        if review['business_id'] not in business_reviews_dict:
            business_reviews_dict[review['business_id']] = []
        business_reviews_dict[review['business_id']].append(review)
    return business_reviews_dict


def main():
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area', fields={}):
        reviews = mongo_functions.mongo_get(
            collection='pre_review',
            filter={'city_area': area['_id'], 'user_from': {'$exists': True}},
            fields={'business_id': 1, 'user_id': 1, 'tile15': 1, 'tile18': 1, 'user_from': 1}
        )
        city_unique_visitors = city_unique_visitors_get(reviews, area)
        city_unique_residents = city_unique_residents_get(reviews, area)
        total_visitors = len(city_unique_visitors)
        total_residents = len(city_unique_residents)
        business_reviews_dict = business_reviews_dict_group(reviews)
        business_list = []
        for business_id, business_reviews in business_reviews_dict.items():
            business = {
                '_id': business_id,
                'raw_ratio': business_dissimilarity_ratio(business_reviews, total_visitors, total_residents, area)
            }
            business_list.append(business)

        mongo_functions.batch_update(business_list, collection='pre_business', update='{"$set": {"raw_ratio": item["raw_ratio"]}}')

        # reviews_tile18 = {}
        # reviews_tile15 = {}
        # _visitors = set([])
        # _residents = set([])
        # for review in reviews:
        #     if review['tile15'] not in reviews_tile15:
        #         reviews_tile15[review['tile15']] = []
        #     if review['tile18'] not in reviews_tile18:
        #         reviews_tile18[review['tile18']] = []
        #     reviews_tile15[review['tile15']].append(review)
        #     reviews_tile18[review['tile18']].append(review)
        #     if review['user_from'] == area['_id']:
        #         _residents.add(review['user_id'])
        #     else:
        #         _visitors.add(review['user_id'])
        #
        # total_visitors = len(_visitors)
        # total_residents = len(_residents)
        # tile18_ratio = {}
        # for tile, reviews_list in reviews_tile18.items():
        #     residents = 0
        #     visitors = 0
        #     for review in reviews_list:
        #         if review['user_from'] == area['_id']:
        #             residents += 1
        #         else:
        #             visitors += 1
        #     ratio = visitors / total_visitors - residents / total_residents
        #     if ratio < 0:
        #         ratio = -ratio
        #     tile18_ratio[tile] = ratio
        # city_index = 1 / 2 * sum(tile18_ratio.values())
        # print('{} -> {}'.format(area['_id'], city_index))


def export():
    pass


if __name__ == '__main__':
    main()
