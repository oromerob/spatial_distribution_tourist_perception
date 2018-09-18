import datetime
import sys

# from common import prepro_user
from common import mongo_utils


def user_reviews_prepare(user):
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

            # if the review is from the same metropolitan area and the date is 15 days or less later -> add to cluster
            if review['cluster'] == current_group['cluster'] and (review['datetime'] - current_group['to']).days <= 15:
                current_group['to'] = review['datetime']
                current_group['reviews'].append(review)
                continue

            # else close group
            grouped_reviews.append(current_group)

        # create a new group
        current_group = {
            'cluster': review['cluster'],
            'from': review['datetime'],
            'to': review['datetime'],
            'reviews': [review]
        }

    # close the final group
    grouped_reviews.append(current_group)
    user['grouped_reviews'] = grouped_reviews


if __name__ == '__main__':
    # users = prepro_user.prepro_users_get()
    users = mongo_utils.mongo_get(collection='prepro_user')
    index = 0
    users_len = len(users)
    print('\n')
    for user in users:
        index += 1
        sys.stdout.write('\rProcessing user {}/{}...'.format(index, users_len))
        sys.stdout.flush()
        user_reviews_prepare(user)
    mongo_utils.batch_update(users, collection='prepro_user', update="{'$set': {'grouped_reviews': item['grouped_reviews'], 'reviews': item['reviews']}}")
    # prepro_user.prepro_user_batch_update(located_users, update="{'$set': {'location': item['location']}}")
    print('yey')