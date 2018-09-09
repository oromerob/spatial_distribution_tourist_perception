import datetime
import sys

from common import _mongo as mongo_utils


def review_distribution_per_city_prepare(user):
    review_distribution_per_city = {}
    for review in user['reviews']:
        if review['cluster'] not in review_distribution_per_city:
            review_distribution_per_city[review['cluster']] = 0
        review_distribution_per_city[review['cluster']] += 1
    user['review_distribution_per_city'] = review_distribution_per_city


classifier_code_map = {
    0: 'Discarded -> 2 or less reviews (1st quartile)',
    1: 'Discarded -> no "grouped_reviews"',
    2: 'Discarded -> other',
    10: 'Other -> only one review (tourist)',
    11: 'Other -> we have less than a 25% of the reviews (tourist)',
    20: 'one of the periods is longer than 2 weeks',
    21: 'two consecutive periods happen with less than 180 days',
    22: 'we have more than 25% and all the reviews are from the same place',
    23: '40% of the review_count are from the same place'
}


def reviewer_classifier(user):
    # user with 2 reviews published in yelp or less is discarded (1st quartile)
    if user['review_count'] <= 2:
        return None, 0

    # if it has only one review -> tourist (local from a city we don't have)
    if len(user['reviews']) == 1:
        # return user['reviews'][0]['cluster']
        return 'Other', 10

    current_location = None
    for period in user['grouped_reviews']:
        try:
            # if one of the periods is longer than 2 weeks
            # (more than the normal stay in a city for a tourist) -> local from that city
            if (period['to'] - period['from']).days > 15:
                return period['cluster'], 20

            if current_location is None or current_location['cluster'] != period['cluster']:
                current_location = period
                continue

            # if two consecutive periods happen with less than 180 days (6 months) difference -> local from that city
            if (period['from'] - current_location['to']).days < 180:
                return period['cluster'], 21

        except Exception as e:
            print(e)
            return None, 1


    reviews_percentage = len(user['reviews']) / user['review_count']
    # if the reviews that we have from the same place are less than 1/4 of the total reviews of the user -> tourist
    if reviews_percentage < 0.25:
        return 'Other', 11

    review_distribution_per_city_prepare(user)
    # if 40% of the review_count are from the same place -> local
    for city, count in user['review_distribution_per_city'].items():
        if count >= user['review_count'] * 2 / 5:
            return city, 23

    reviews_location_set = set([review['cluster'] for review in user['reviews']])
    # if we have more than 25% and all the reviews are from the same place -> local
    if len(reviews_location_set) == 1:
        return reviews_location_set.pop(), 22

    return None, 2


if __name__ == '__main__':
    # users = prepro_user.prepro_users_get()
    users = mongo_utils.mongo_get(collection='prepro_user')
    located_users = []
    index = 0
    users_len = len(users)
    classifier_codes = {}
    print('\n')
    for user in users:
        index += 1
        sys.stdout.write('\rProcessing user {}/{}...'.format(index, users_len))
        sys.stdout.flush()
        user_location, code = reviewer_classifier(user)
        if code is not None:
            if code not in classifier_codes:
                classifier_codes[code] = 0
            classifier_codes[code] += 1
        if user_location is None:
            continue
        # print(user_location)
        user['local'] = user_location
        located_users.append(user)
    ordered_classification_codes = sorted([(key, value) for key, value in classifier_codes.items()], key=lambda x: x[0])
    print('\nSummary:')
    for item in ordered_classification_codes:
        print('{} users classified as: {}'.format(item[1], classifier_code_map[item[0]]))
    mongo_utils.batch_update(located_users, collection='prepro_user', update='{"$set": {"local": item["local"]}}')
    print('yey')