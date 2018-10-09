from common import mongo_utils


def main():
    venues = mongo_utils.mongo_get(collection='city_venues', fields={'category_clusters': 1, 'latitude': 1, 'longitude': 1})
    venue_ids = [doc['_id'] for doc in venues]
    businessess = {doc['_id']: doc for doc in mongo_utils.mongo_get(collection='business', filter={'_id': {'$in': venue_ids}}, fields={'name': 1, 'review_count': 1, 'categories': 1})}
    for venue in venues:
        businessess[venue['_id']].update(venue)

    business_list = sorted([doc for doc in businessess.values()], key=lambda x: x['review_count'], reverse=True)

    lines = [';'.join(business_list[0].keys())]
    for item in business_list:
        for key, value in item.items():
            if type(value) == int:
                item[key] = str(value)
            elif type(value) == list:
                item[key] = ','.join(value)
        lines.append(';'.join([str(value) for value in item.values()]))

    csv = '\n'.join(lines)

    with open('public_venues_category.csv', 'w+') as f:
        f.write(csv)
        f.flush()

    print('yey')


if __name__ == '__main__':
    main()