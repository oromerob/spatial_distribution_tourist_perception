import datetime
import os

import pymongo

from spatial_distribution_tourist_perception.common import mongo_functions


def business_dissimilarity_ratio(business_reviews, total_visitors, total_residents, area):
    business_unique_visitors = {review['user_id'] for review in business_reviews if review['user_from'] != area['_id']}
    business_unique_locals = {review['user_id'] for review in business_reviews if review['user_from'] == area['_id']}
    visitors = len(business_unique_visitors)
    residents = len(business_unique_locals)
    visitors_ratio = visitors / total_visitors if visitors != 0 else 0
    residents_ratio = residents / total_residents if residents != 0 else 0
    return visitors_ratio - residents_ratio


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


def _business_categories_get():
    return mongo_functions.mongo_distinct_get('norm_categories', collection='pre_business')


def _business_sorted_get(filter=None, fields=None, limit=100, sort=None):
    if sort is None:
        sort = {}
    if filter is None:
        filter = {}
    find_params = [filter]
    if fields is not None and type(fields) == dict:
        find_params.append(fields)

    client = pymongo.MongoClient('localhost', 27018)
    db = client.cett
    col = db['pre_business']

    cursor = col.find(*find_params).sort(*sort).limit(limit)
    res = [doc for doc in cursor]

    client.close()
    return res


def write_csv_file(filepath, content):
    with open(os.path.join('334_pre_business_dissimilarity_ratio', filepath), 'w+') as f:
        f.write(content)
        f.flush()


def export():
    categories = _business_categories_get()
    business = {}
    csv_fields = ['_id', 'area_id', 'ratio', 'name', 'review_count', 'stars', 'categories'] + categories
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area'):
        for category in categories:
            for order in [1, -1]:
                _business = _business_sorted_get(
                    filter={'tile10': {'$in': area['tiles']}, 'norm_categories': category, 'raw_ratio': {'$exists': True}},
                    sort=('raw_ratio', order),
                    fields={'categories': 1, 'name': 1, 'review_count': 1, 'stars': 1, 'norm_categories': 1, 'raw_ratio': 1}
                )
                for venue in _business:
                    if venue['_id'] in business:
                        continue
                    venue['area_id'] = area['_id']
                    venue['categories'] = ','.join(venue['categories'])
                    venue['ratio'] = venue['raw_ratio']
                    for _cat in categories:
                        venue[_cat] = ''
                        if _cat in venue['norm_categories']:
                            venue[_cat] = '1'
                    csv_values = []
                    for field in csv_fields:
                        csv_values.append(str(venue[field]))
                    business.update({venue['_id']: csv_values})
    lines = [';'.join(line) for line in business.values()]
    content = ';'.join(csv_fields) + '\n'+ '\n'.join(lines)
    write_csv_file('business_category_ratio.csv', content)
    print('yey')


def _business_dict_build(_business, business_dict, categories, area, csv_fields):
    for venue in _business:
        if venue['_id'] in business_dict:
            continue
        venue['area_id'] = area['_id']
        venue['categories'] = ','.join(venue['categories'])
        venue['ratio'] = venue['raw_ratio']
        for _cat in categories:
            venue[_cat] = ''
            if _cat in venue['norm_categories']:
                venue[_cat] = '1'
        csv_values = []
        for field in csv_fields:
            csv_values.append(str(venue[field]))
            business_dict.update({venue['_id']: csv_values})


def export_city_business():
    categories = _business_categories_get()
    csv_fields = ['_id', 'area_id', 'ratio', 'name', 'review_count', 'stars', 'categories'] + categories
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area'):
        business_dict = {}
        _business = mongo_functions.mongo_get(
            collection='pre_business',
            filter={'tile10': {'$in': area['tiles']}, 'raw_ratio': {'$exists': True}},
            fields={'categories': 1, 'name': 1, 'review_count': 1, 'stars': 1, 'norm_categories': 1, 'raw_ratio': 1}
        )
        _business_dict_build(_business, business_dict, categories, area, csv_fields)
        lines = [';'.join(line) for line in business_dict.values()]
        content = ';'.join(csv_fields) + '\n' + '\n'.join(lines)
        write_csv_file('{}_business_ratio.csv'.format(area['_id'].replace(' ', '_')), content)


def city_unique_users_get():
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area', fields={}):
        reviews = mongo_functions.mongo_get(
            collection='pre_review',
            filter={'city_area': area['_id'], 'user_from': {'$exists': True}},
            fields={'user_from': 1, 'user_id': 1}
        )
        city_unique_visitors = city_unique_visitors_get(reviews, area)
        city_unique_residents = city_unique_residents_get(reviews, area)
        total_visitors = len(city_unique_visitors)
        total_residents = len(city_unique_residents)
        print('{} unique visitors -> {}'.format(area['_id'], total_visitors))
        print('{} unique residents -> {}'.format(area['_id'], total_residents))


def yearly_dissimilarity_ratio():
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area', fields={}):
        business_dict = {}
        for year, reviews in _reviews_per_year(area).items():

            city_unique_visitors = city_unique_visitors_get(reviews, area)
            city_unique_residents = city_unique_residents_get(reviews, area)
            total_visitors = len(city_unique_visitors)
            total_residents = len(city_unique_residents)
            business_reviews_dict = business_reviews_dict_group(reviews)

            for business_id, business_reviews in business_reviews_dict.items():
                if business_id not in business_dict:
                    business_dict[business_id] = {
                        '_id': business_id,
                        'ratio_yearly': {}
                    }
                business_dict[business_id]['ratio_yearly'][str(year)] = float('{0:.9f}'.format(business_dissimilarity_ratio(business_reviews, total_visitors, total_residents, area)))

        business_list = [item for item in business_dict.values()]
        mongo_functions.batch_update(business_list, collection='pre_business', update='{"$set": {"ratio_yearly": item["ratio_yearly"]}}')


def _reviews_per_year(area):
    reviews = mongo_functions.mongo_get(
        collection='pre_review',
        filter={'city_area': area['_id'], 'user_from': {'$exists': True}},
        fields={'business_id': 1, 'user_id': 1, 'tile15': 1, 'tile18': 1, 'user_from': 1, 'date': 1}
    )
    reviews_per_year_dict = {}
    for review in reviews:
        year = datetime.datetime.strptime(review['date'], '%Y-%m-%d').year
        if year not in reviews_per_year_dict:
            reviews_per_year_dict[year] = []
        reviews_per_year_dict[year].append(review)
    return reviews_per_year_dict


if __name__ == '__main__':
    # main()
    # export()
    # export_city_business()

    # city_unique_users_get()

    yearly_dissimilarity_ratio()
