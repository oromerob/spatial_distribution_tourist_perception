import sys

from common import prepro_user


def tourists_get(users):
    index = 0
    users_len = len(users)
    for user in users:
        index += 1
        sys.stdout.write('\rProcessing user {}/{}...'.format(index, users_len))
        sys.stdout.flush()
        user['visited'] = []
        for review in user['reviews']:
            if review['cluster'] != user['location']:
                user['visited'].append(review['cluster'])


def main():
    users = [user for user in prepro_user.prepro_users_get(filter={'location': {'$exists': True}}, fields={'reviews': 1, 'location': 1})]
    tourists_get(users)
    prepro_user.prepro_user_batch_update(users, update="{'$set': {'visited': item['visited']}}")


if __name__ == '__main__':
    main()