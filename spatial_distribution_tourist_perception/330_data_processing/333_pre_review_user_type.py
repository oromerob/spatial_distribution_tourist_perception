from spatial_distribution_tourist_perception.common import mongo_functions


def prepare():
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area', fields={}):
        reviews = mongo_functions.mongo_get(
            collection='pre_review',
            filter={'city_area': area['_id']},
            fields={'user_id': 1}
        )

        try:
            user_ids = list({review['user_id'] for review in reviews})
        except Exception as e:
            print(e)
            return

        try:
            user_type_dict = {}
            while len(user_ids) > 0:
                current_user_ids = user_ids[:100000]
                user_ids = user_ids[100000:]
                user_type_dict.update({user['_id']: user['local'] for user in mongo_functions.mongo_get(
                    collection='pre_user',
                    filter={'_id': {'$in': current_user_ids}, 'local': {'$exists': True}},
                    fields={'local': 1}
                )})
        except Exception as e:
            print(e)
            return

        _reviews = []
        while len(reviews) > 0:
            review = reviews.pop()
            try:
                review['user_from'] = user_type_dict[review['user_id']]
                _reviews.append(review)
            except KeyError:
                pass
            except Exception as e:
                print(e)
                pass
        mongo_functions.batch_update(
            _reviews,
            collection='pre_review',
            update='{"$set": {"user_from": item["user_from"]}}'
        )


if __name__ == '__main__':
    prepare()
