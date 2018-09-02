import datetime
import sys
import random
import re
import time

import requests
from bs4 import BeautifulSoup

from common import prepro_user, yelp_user
from tiles import tiles


def yelp_user_get(user_id):
    url = '''https://www.yelp.com/user_details?userid={}'''.format(user_id)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    try:
        user_location = soup.find('h3', {'class': 'user-location'}).getText()
        reviews_list = soup.find('ul', {'class': 'reviews'})
        _reviews = reviews_list.findChildren('li', recursive=False)
    except Exception as e:
        print(e)
        return None
    reviews = []
    for _review in _reviews:
        try:
            try:
                date = datetime.datetime.strptime(_review.find('span', {'class': 'rating-qualifier'}).getText().strip(), '%m/%d/%Y').strftime('%Y-%m-%d')
            except:
                date = datetime.datetime.strptime(re.findall(r'^([0-9\/]*?)\s', _review.find('span', {'class': 'rating-qualifier'}).getText().strip())[0], '%m/%d/%Y').strftime('%Y-%m-%d')
            business_url = _review.find('a', {'class': 'biz-name'})['href']
            # if business_url not in businesses_dict:
            #     businesses_dict.update({business_url: yelp_business_get(business_url)})
            review = {
                '_id': _review.find('div', {'class': 'review'})['data-review-id'],
                'date': date,
                'content': _review.find('div', {'class': 'review-content'}).find('p').getText().strip(),
                'business': {
                    'url': business_url
                }
                # 'business': businesses_dict[business_url]
            }
            # review['business_id'] = review['business']['_id']
            # review['tile10'] = review['business']['tile10']
            reviews.append(review)
        except Exception as e:
            print(_review.find('span', {'class': 'rating-qualifier'}).getText().strip())
            print(e)
    return {
        '_id': user_id,
        'location': user_location,
        'reviews': reviews
    }


def yelp_business_get(business_url):
    url = 'https://www.yelp.com' + business_url
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    map = soup.find('div', {'class': 'lightbox-map'})
    map_state = map['data-map-state']

    latitude = None
    longitude = None
    tile10 = None
    try:
        latitude = float(re.findall(r'"latitude": ([0-9\.\-]*?),', map_state)[0])
        longitude = float(re.findall(r'"longitude": ([0-9\.\-]*?)\}', map_state)[0])
        tile10 = '{}_{}'.format(*tiles.deg2num(latitude, longitude, 10))
    except Exception as e:
        print(e)

    business = {
        '_id': map['data-business-id'],
        'url': business_url,
        'latitude': latitude,
        'longitude': longitude,
        'tile10': tile10
    }

    return business


def yelp_user_upsert(user):
    yelp_user.yelp_user_upsert(user)


def prepro_user_ids_get():
    return {user['_id'] for user in prepro_user.prepro_users_get(fields={})}


def yelp_user_ids_get():
    return {user['_id'] for user in yelp_user.yelp_users_get(fields={})}


def yelp_user_reviews_get():
    users = yelp_user.yelp_users_get(fields={'reviews'})
    user_ids = {user['_id'] for user in users}
    businesses_dict = {}
    for user in users:
        for review in user['reviews']:
            if review['business']['url'] in businesses_dict:
                continue
            businesses_dict.update({review['business']['url']: review['business']})
    return user_ids, businesses_dict


def main():
    # yelp_users, businesses_dict = yelp_user_reviews_get()
    users = prepro_user_ids_get() - yelp_user_ids_get()

    index = 0
    users_len = len(users)
    print()

    for user in users:
        index += 1
        sys.stdout.write('\rProcessing user {}/{}...'.format(index, users_len))
        sys.stdout.flush()
        yelp_user = yelp_user_get(user)

        # save yelp user
        if yelp_user is not None:
            yelp_user_upsert(yelp_user)

        # wait 1 or 3 sec
        wait_random_time(seconds=0)


def wait_random_time(seconds=0):
    random_time = random_time_get(seconds)
    # print('waiting {} seconds...'.format(random_time))
    sys.stdout.write('\rwaiting {} seconds...'.format(random_time))
    sys.stdout.flush()
    time.sleep(random_time)


def random_time_get(seconds):
    return seconds + random.randint(0, 9) / 10


if __name__ == '__main__':
    main()
    # yelp_user_get('oMy_rEb0UBEmMlu-zcxnoQ')
    # for x in range(0, 9):
    #     print(random_time_get())