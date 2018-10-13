from spatial_distribution_tourist_perception.common import mongo_utils


def dissimilarity_calculate():
    pass


def main():
    for cluster in mongo_utils.mongo_get(collection='clusters', fields={'tiles': 1, 'name': 1}):
        pass


if __name__ == '__main__':
    main()
