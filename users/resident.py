import datetime
import sys

from common import prepro_user


def user_reviews_prepare(user):
    _reviews = []
    for review in user['reviews']:
        review['_date'] = int(review['date'].replace('-', ''))
        review['datetime'] = datetime.datetime.strptime(review['date'], '%Y-%m-%d')
        _reviews.append(review)
    reviews = sorted(_reviews, key=lambda x: x['_date'])
    user['reviews'] = reviews


def user_location_get(user):
    # at least 2 reviews
    if len(user['reviews']) < 2:
        return None

    # order the reviews
    user_reviews_prepare(user)

    # at least 15 days difference
    first_review_date = user['reviews'][0]['datetime']
    last_review_date = user['reviews'][-1]['datetime']
    review_date_range = (last_review_date - first_review_date).days
    if review_date_range < 15:
        return None

    # users with only one location automatically assigned to it
    locations_set = {review['cluster'] for review in user['reviews']}
    if len(locations_set) == 1:
        return locations_set.pop()
    if len(locations_set) == len(user['reviews']):
        return None

    try:
        locations_dict = {}
        current_location = None
        current_location_from = None
        current_location_to = None
        for review in user['reviews']:

            if review['cluster'] == current_location:
                current_location_to = review['datetime']
                continue

            if current_location is not None:
                # add the period to the location_dict
                if current_location not in locations_dict:
                    locations_dict.update({current_location: None})
                duration = current_location_to - current_location_from
                if locations_dict[current_location] is None:
                    locations_dict[current_location] = duration
                else:
                    locations_dict[current_location] += duration

            # set the new location
            current_location = review['cluster']
            current_location_from = review['datetime']
            current_location_to = review['datetime']

        # add the final period to the location_dict
        if current_location not in locations_dict:
            locations_dict.update({current_location: None})
        duration = current_location_to - current_location_from
        if locations_dict[current_location] is None:
            locations_dict[current_location] = duration
        else:
            locations_dict[current_location] += duration

        locations = sorted([(key, value) for key, value in locations_dict.items()], key=lambda x: x[1], reverse=True)

        if len(locations) > 1 and locations[0][0] <= locations[1][0]:
            return None

        user_main_location = locations[0][0]

        return user_main_location

    except KeyError:
        return 'Other'


if __name__ == '__main__':
    users = prepro_user.prepro_users_get()
    located_users = []
    index = 0
    users_len = len(users)
    print('\n')
    for user in users:
        index += 1
        sys.stdout.write('\rProcessing user {}/{}...'.format(index, users_len))
        sys.stdout.flush()
        user_location = user_location_get(user)
        if user_location is None:
            continue
        # print(user_location)
        user['location'] = user_location
        located_users.append(user)
    prepro_user.prepro_user_batch_update(located_users, update="{'$set': {'location': item['location']}}")
    print('yey')