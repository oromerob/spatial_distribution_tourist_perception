import os

import pymongo


def clusters_get():
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['clusters']

    cursor = collection.find({}, {'tiles': 1})
    return [doc for doc in cursor]


def prepro_business_id_get(tiles):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['prepro_business']

    cursor = collection.find({'tile10': {'$in': tiles}}, {}).limit(100000)
    return [doc['_id'] for doc in cursor]


def business_city_get(business_ids):
    client = pymongo.MongoClient('localhost', 27018)
    db = client.yelp
    collection = db['business']

    cursor = collection.find({'_id': {'$in': business_ids}}, {'city': 1}).limit(100000)
    return [doc['city'] for doc in cursor]


def city_counter(business_cities):
    cities = {}
    for city in business_cities:
        if city not in cities:
            cities[city] = 0
        cities[city] += 1
    cities_unordered = [{'city': city, 'count': count} for city, count in cities.items()]
    cities_unordered.sort(key=lambda x: x['count'], reverse=True)
    return cities_unordered


def csv_save(cluster_cities):
    filename = '{}_cities.csv'.format(cluster_cities[0]['city'])
    content = 'city; venues\n'
    for item in cluster_cities:
        content += '{}; {}\n'.format(item['city'], item['count'])
    with open(os.path.join('..','files', filename), '+w') as f:
        f.write(content)


def main():
    for cluster in clusters_get():
        venues = prepro_business_id_get(cluster['tiles'])
        business_cities = business_city_get(venues)
        city_names = city_counter(business_cities)
        csv_save(city_names)
    #     for item in city_names:
    #         print('name: {} -> {}'.format(item['city'], item['count']))
    # print('yey')

main()