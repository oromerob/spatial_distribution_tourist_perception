from spatial_distribution_tourist_perception.common import mongo_functions


def main():
    metropolitan_area_counter = 0
    city_counter = 0
    for area in mongo_functions.mongo_get(collection='pre_metropolitan_area', fields={'businesses': 1, 'city_businesses': 1}):
        metropolitan_area_counter += area['businesses']
        city_counter += area['city_businesses']
    print('tiles in metropolitan_area {}'.format(metropolitan_area_counter))
    print('tiles in cities {}'.format(city_counter))


if __name__ == '__main__':
    main()