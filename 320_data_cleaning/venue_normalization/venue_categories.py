from common.public_venue_categories_2 import venue_categories
from common import mongo_utils


def category_dict_prepare():
    category_dict = {}
    for key, list in venue_categories.items():
        for item in list:
            category_dict[item] = key
    return category_dict


def venues_prepare(venues, category_dict, cluster):
    _venues = []
    for venue in venues:
        _categories = set([])
        for cat in venue['categories']:
            if cat in category_dict:
                _categories.add(category_dict[cat])
        if len(_categories) > 0:
            _venues.append({
                '_id': venue['_id'],
                'name': venue['name'],
                'category_clusters': list(_categories),
                'cluster_name': cluster['name'],
                'cluster_id': cluster['_id']
            })
    return _venues


if __name__ == '__main__':
    category_dict = category_dict_prepare()
    for cluster in mongo_utils.mongo_get(collection='clusters', fields={'tiles': 1, 'name': 1}):
        print('processing venues for ', cluster['name'])
        business_ids = [doc['_id'] for doc in mongo_utils.mongo_get(collection='prepro_business', filter={"tile10": {'$in': cluster['tiles']}}, fields={})]
        business = mongo_utils.mongo_get(collection='business', filter={"_id": {'$in': business_ids}}, fields={'name': 1, 'categories': 1})
        venues = venues_prepare(business, category_dict, cluster)
        mongo_utils.batch_upsert(venues, collection='venues_2', update='{"$set": item}')
        print('Inserted {} items for "{}" cluster'.format(len(venues), cluster['name']))