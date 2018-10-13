import json
import os

from spatial_distribution_tourist_perception.common import mongo_utils

DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'dataset')


def list_dir_json_files(path):
    files = os.listdir(path)
    json_files = [item for item in files if item[-5:] == '.json']
    return json_files


def data_import(filename):
    concept = filename[:-5]
    id_field = CONCEPT_ID_FIELD[concept] if concept in CONCEPT_ID_FIELD else None
    # if id_field is None:
    #     return
    data = data_read(filename)
    bulk = data_save_prepare(id_field, data)
    mongo_utils.batch_upsert(bulk, collection=concept, update="{'$set': item}")


def data_save_prepare(id_field, bulk):
    if id_field is None:
        return bulk
    for item in bulk:
        item['_id'] = item[id_field]
    return bulk


CONCEPT_ID_FIELD = {
    'business': 'business_id',
    'checkin': 'business_id',
    'photos': 'photo_id',
    'review': 'review_id',
    'user': 'user_id'
}


def data_read(filename):
    with open(os.path.join(DATASET_PATH, filename), 'r') as f:
        lines = []
        for line in f:
            lines.append(json.loads(line))
        return lines


def main():
    for item in list_dir_json_files(DATASET_PATH):
        data_import(item)


if __name__ == '__main__':
    main()
