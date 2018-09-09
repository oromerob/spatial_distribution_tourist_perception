import sys

from common import _mongo as mongo_utils


if __name__ == '__main__':
    users = mongo_utils.mongo_get(collection='prepro_user', filter={'local': {'$exists': True}})
    index = 0
    users_len = len(users)
    print('\n')
    for user in users:
        index += 1
        sys.stdout.write('\rProcessing user {}/{}...'.format(index, users_len))
        sys.stdout.flush()
        user['visited'] = list(set([review['cluster'] for review in user['grouped_reviews']]) - {user['local'],})
    mongo_utils.batch_update(users, collection='prepro_user', update='{"$set": {"visited": item["visited"]}}')
    print('yey')