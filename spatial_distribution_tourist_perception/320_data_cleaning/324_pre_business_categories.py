from spatial_distribution_tourist_perception.common import mongo_functions, public_venue_categories


def category_dict_prepare():
    category_dict = {}
    for key, list in public_venue_categories.venue_categories.items():
        for item in list:
            category_dict[item] = key
    return category_dict


def business_prepare(businessess, category_dict):
    for business in businessess:
        business['norm_categories'] = list({category_dict[category] for category in business['categories'] if category in category_dict})


def prepare():
    category_dict = category_dict_prepare()
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area', fields={'tiles': 1, 'name': 1}):
        print('processing business for ', area['_id'])
        business = mongo_functions.mongo_get(
            collection='pre_business',
            filter={"tile10": {'$in': area['tiles']}},
            fields={'name': 1, 'categories': 1}
        )
        business_prepare(business, category_dict)
        mongo_functions.batch_update(
            business,
            collection='pre_business',
            update='{"$set": {"norm_categories": item["norm_categories"]}}'
        )


if __name__ == '__main__':
    prepare()