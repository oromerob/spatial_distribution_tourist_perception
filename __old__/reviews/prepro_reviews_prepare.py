from common import mongo_utils, tiles as tile_utils


def main():
    # cities = mongo_utils.mongo_get(collection='cities')
    users = mongo_utils.mongo_get(collection='prepro_user', filter={'local': {'$exists': True}}, fields={'reviews': 1, 'local': 1})
    city_venue_dict = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='city_venues', fields={'category_clusters': 1, 'tile15': 1, 'tile18': 1})}
    reviews = []
    for user in users:
        for review in user['reviews']:
            if review['business_id'] not in city_venue_dict:
                continue
            review['user_tourist'] = False
            if user['local'] != review['cluster']:
                review['user_tourist'] = True
            review['venue_categories'] = city_venue_dict[review['business_id']]['category_clusters']
            review['tile15'] = city_venue_dict[review['business_id']]['tile15']
            review['tile18'] = city_venue_dict[review['business_id']]['tile18']
            reviews.append(review)
    mongo_utils.batch_upsert(reviews, collection='prepro_reviews', update="{'$set': item}")
    print('yey')


if __name__ == '__main__':
    main()
