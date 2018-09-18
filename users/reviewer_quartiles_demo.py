import datetime
import sys

# from common import prepro_user
from common import mongo_utils


def count_reviews_quartile_assign(user, user_quartile, review_count_quartile_limit, review_present_quartile_limit):
    for quartile in review_count_quartile_limit:
        if user['review_count'] <= quartile[1]:
            present_reviews_qurtile_assign(user, user_quartile[quartile[0]], review_present_quartile_limit)
            return
    present_reviews_qurtile_assign(user, user_quartile['4'], review_present_quartile_limit)


def present_reviews_qurtile_assign(user, user_quartile, review_present_quartile_limit):
    user_quartile['total'] += 1
    for quartile in review_present_quartile_limit:
        if len(user['reviews']) <= quartile[1]:
            user_quartile[quartile[0]] += 1
            return
    user_quartile['4'] += 1


def count_review_quartile_assign(user, quartile_splitted_users, review_count_quartile_limit):
    for quartile in review_count_quartile_limit:
        if user['review_count'] <= quartile[1]:
            quartile_splitted_users[quartile[0]].append(user)
            return
    quartile_splitted_users['4'].append(user)


def review_existing_quartile_assign(user, quartile_splitted_users, review_existing_quartile_limit):
    for quartile in review_existing_quartile_limit:
        if len(user['reviews']) <= quartile[1]:
            quartile_splitted_users[quartile[0]]['users'].append(user)
            quartile_splitted_users[quartile[0]]['reviews_total'] += len(user['reviews'])
            return
    quartile_splitted_users['4']['users'].append(user)
    quartile_splitted_users['4']['reviews_total'] += len(user['reviews'])


def review_existing_quartile_splitted_users_create(users, review_existing_quartile_limit):
    quartile_splitted_users = {quartile[0]: {'users': [], 'reviews_total': 0} for quartile in review_existing_quartile_limit}
    quartile_splitted_users['4'] = {'users': [], 'reviews_total': 0}
    for user in users:
        review_existing_quartile_assign(user, quartile_splitted_users, review_existing_quartile_limit)

    for quartile in quartile_splitted_users.values():
        if len(quartile['users']) == 0:
            quartile['min'] = 0
            quartile['max'] = 0
            quartile['total'] = 0
            continue
        quartile['users'] = sorted(quartile['users'], key=lambda x: len(x['reviews']))
        quartile['min'] = len(quartile['users'][0]['reviews'])
        quartile['max'] = len(quartile['users'][-1]['reviews'])
        quartile['total'] = len(quartile['users'])
    return quartile_splitted_users


def review_existing_quartile_create_for_count_review_quartile_generate(quartile_users):
    review_existing_ordered_users = sorted(quartile_users, key=lambda x: len(x['reviews']))
    quartiles_position = {'1': int(len(review_existing_ordered_users) / 4)}
    quartiles_position['2'] = quartiles_position['1'] * 2
    quartiles_position['3'] = quartiles_position['1'] * 3
    review_existing_quartile_limit = [
        ('1', len(review_existing_ordered_users[quartiles_position['1']]['reviews'])),
        ('2', len(review_existing_ordered_users[quartiles_position['2']]['reviews'])),
        ('3', len(review_existing_ordered_users[quartiles_position['3']]['reviews'])),
    ]
    quartile_splitted_users = review_existing_quartile_splitted_users_create(quartile_users, review_existing_quartile_limit)
    return quartile_splitted_users


def count_review_quartile_splitted_users_create(users, review_count_quartile_limit):
    quartile_splitted_users = {quartile[0]: [] for quartile in review_count_quartile_limit}
    quartile_splitted_users['4'] = []
    for user in users:
        count_review_quartile_assign(user, quartile_splitted_users, review_count_quartile_limit)

    quartile_users = {}
    for key, value in quartile_splitted_users.items():
        quartile_users[key] = review_existing_quartile_create_for_count_review_quartile_generate(value)
        for quartile_key, quartile_value in quartile_users[key].items():
            print('Last users for "review_count" quartile {} and "reviews length" quartile {}:'.format(key, quartile_key))
            for user in quartile_value['users'][-10:]:
                print('User "{}" review_count = {}, reviews length = {}'.format(user['_id'], user['review_count'], len(user['reviews'])))
            print('**********\n')
    return quartile_users


def user_quartiles_generate(users):
    review_count_ordered_users = sorted(users, key=lambda x: x['review_count'])
    quartiles_position = {'1': int(len(review_count_ordered_users) / 4)}
    quartiles_position['2'] = quartiles_position['1'] * 2
    quartiles_position['3'] = quartiles_position['1'] * 3
    review_count_quartile_limit = [
        ('1', review_count_ordered_users[quartiles_position['1']]['review_count']),
        ('2', review_count_ordered_users[quartiles_position['2']]['review_count']),
        ('3', review_count_ordered_users[quartiles_position['3']]['review_count']),
    ]
    return count_review_quartile_splitted_users_create(users, review_count_quartile_limit)


if __name__ == '__main__':
    # users = prepro_user.prepro_users_get()
    users = mongo_utils.mongo_get(collection='prepro_user', fields={'review_count': 1, 'reviews': 1})
    quartile_users = user_quartiles_generate(users)

    print('\nSummary:')

    for key, value in quartile_users.items():
        print('"review_count" quartile {}:'.format(key))
        for subkey, subvalue in value.items():
            print('    "reviews" length quartile {}:'.format(subkey))
            print('        "total": {}'.format(subvalue['total']))
            print('        "reviews_total": {}'.format(subvalue['reviews_total']))
            print('        "min": {}'.format(subvalue['min']))
            print('        "max": {}'.format(subvalue['max']))
