import datetime
import sys

from spatial_distribution_tourist_perception.common import mongo_functions


def _user_reviews_prepare(user):
    if 'reviews' not in user:
        print('wait!')
        return
    _reviews = []
    for review in user['reviews']:
        review['_date'] = int(review['date'].replace('-', ''))
        review['datetime'] = datetime.datetime.strptime(review['date'], '%Y-%m-%d')
        _reviews.append(review)
    reviews = sorted(_reviews, key=lambda x: x['_date'])
    user['reviews'] = reviews

    # group reviews made in less than 2 weeks from the same metropolitan area
    grouped_reviews = []
    current_group = None

    for review in reviews:

        if current_group is not None:

            # if the review is from the same metropolitan area and the date is 15 days or less later -> add to city_area
            if review['city_area'] == current_group['city_area'] and (review['datetime'] - current_group['to']).days <= 15:
                current_group['to'] = review['datetime']
                current_group['reviews'].append(review)
                continue

            # else close group
            grouped_reviews.append(current_group)

        # create a new group
        current_group = {
            'city_area': review['city_area'],
            'from': review['datetime'],
            'to': review['datetime'],
            'reviews': [review]
        }

    # close the final group
    grouped_reviews.append(current_group)
    user['grouped_reviews'] = grouped_reviews


def user_reviews_dict_create():
    reviews = mongo_functions.mongo_get(collection='pre_review', filter={'city_area': {'$exists': True}})
    user_reviews_dict = {}
    for review in reviews:
        if review['user_id'] not in user_reviews_dict:
            user_reviews_dict[review['user_id']] = []
        user_reviews_dict[review['user_id']].append(review)
    return user_reviews_dict


def prepare():
    user_reviews_dict = user_reviews_dict_create()
    _users = mongo_functions.mongo_get(collection='user')
    users = []
    index = 0
    users_len = len(_users)
    print('\n')
    while len(_users) > 0:
        index += 1
        sys.stdout.write('\rProcessing user {}/{}...'.format(index, users_len))
        sys.stdout.flush()
        _user = _users.pop()
        if _user['_id'] in user_reviews_dict:
            _user.update({'reviews': user_reviews_dict[_user['_id']]})
            _user_reviews_prepare(_user)
            users.append(_user)
    mongo_functions.batch_upsert(users, collection='pre_user', update='{"$set": item}')


if __name__ == '__main__':
    prepare()
