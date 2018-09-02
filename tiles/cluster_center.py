# import pymongo

from common import _mongo as mongo_utils


# def clusters_get():
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['clusters']
#
#     cursor = collection.find({}, {'tiles': 1})
#     return [doc for doc in cursor]


# def venues_location_get(tiles):
#     client = pymongo.MongoClient('localhost', 27018)
#     db = client.yelp
#     collection = db['prepro_business']
#
#     cursor = collection.find({'tile10': {'$in': tiles}}).limit(100000)
#     return [doc for doc in cursor]


def center(venues):
    aggregated_lat = 0
    aggregated_lon = 0  
    for venue in venues:
        aggregated_lat += venue['latitude']
        aggregated_lon += venue['longitude']
    center_lat = aggregated_lat / len(venues)
    center_lon = aggregated_lon / len(venues)
    return center_lat, center_lon


def main():
    clusters = [doc for doc in mongo_utils.mongo_get(col='clusters', filter={}, fields={'tiles': 1})]
    for cluster in clusters:
        # venues = venues_location_get(cluster['tiles'])
        venues = [doc for doc in mongo_utils.mongo_get(
            col='prepro_business',
            filter={'tile10': {'$in': cluster['tiles']}},
            fields={'latitude': 1, 'longitude': 1}
        )]
        center_lat, center_lon = center(venues)
        cluster['center'] = [center_lat, center_lon]
        print('{},{}'.format(center_lat, center_lon))
    mongo_utils.batch_update(clusters, collection='clusters', update="{'$set': {'center': item['center']}}")
    print('yey')


if __name__ == '__main__':
    main()