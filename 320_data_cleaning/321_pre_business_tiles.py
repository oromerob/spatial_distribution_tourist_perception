from common import mongo_utils, tiles


def prepare():
    businesses = mongo_utils.mongo_get(collection='business')
    pre_businessess = []
    for business in businesses:

        try:
            business['tile10'] = '_'.join(
                [str(item) for item in tiles.deg2num(business['latitude'], business['longitude'], 10)])
            business['tile15'] = '_'.join(
                [str(item) for item in tiles.deg2num(business['latitude'], business['longitude'], 15)])
            business['tile18'] = '_'.join(
                [str(item) for item in tiles.deg2num(business['latitude'], business['longitude'], 18)])
            pre_businessess.append(business)
        except TypeError:
            pass
        except Exception as e:
            raise

    mongo_utils.batch_upsert(pre_businessess, collection='pre_business', update='{"$set": item}')


if __name__ == '__main__':
    prepare()
