from spatial_distribution_tourist_perception.common import mongo_functions, tiles as tile_functions


def _group_step(tiles, initial_tile, grouped, group):
    if len(group['new']) == 0:
        group['new'].append(initial_tile)
        return tiles, grouped, group

    _tiles = group['new']
    group['new'] = []
    for tile in _tiles:
        tileX = int(tile.split('_')[0])
        tileY = int(tile.split('_')[1])
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                tile__ = '{}_{}'.format(tileX + x, tileY + y)
                if tile__ in tiles:
                    group['new'].append(tile__)
                    tiles.remove(tile__)
    group['done'] = group['done'] + _tiles
    if len(group['new']) == 0:
        grouped.append(group['done'])
    return tiles, grouped, group


def _group(tiles, initial_tile, grouped=None, group=None):
    if grouped is None:
        grouped = []
    if group is None:
        group = {
            'done': [],
            'new': []
        }

    tiles, grouped, group = _group_step(tiles, initial_tile, grouped, group)

    if len(group['new']) > 0:
        return _group(tiles, initial_tile, grouped=grouped, group=group)
    return grouped


def _group_business_by_tile15(businesses):
    tile15_dict = {}
    for business in businesses:
        if business['tile15'] not in tile15_dict:
            tile15_dict[business['tile15']] = []
        tile15_dict[business['tile15']].append(business)
    return tile15_dict


def prepare():
    areas = mongo_functions.mongo_get(collection='pre_metropolitan_area')

    for area in areas:
        businesses = mongo_functions.mongo_get(collection='pre_business', filter={'tile10': {'$in': area['tiles']}})
        tile15_dict = _group_business_by_tile15(businesses)
        tile15_ordered_list = sorted([(key, value) for key, value in tile15_dict.items()], key=lambda x: len(x[1]),
                                     reverse=True)
        city_area = _group(set([tile for tile in tile15_dict.keys()]), tile15_ordered_list[0][0])
        city_business = []
        for tile in city_area[0]:
            city_business += tile15_dict[tile]
        # mongo_functions.batch_upsert(city_business, collection='pre_city_business', update="{'$set': item}")
        area['city_center'] = list(tile_functions.tile_center(
            int(tile15_ordered_list[0][0].split('_')[0]),
            int(tile15_ordered_list[0][0].split('_')[1]),
            15
        ))
        area['city_tiles15'] = city_area[0]
        area['city_businesses'] = len(city_business)
    mongo_functions.batch_update(areas, collection='pre_metropolitan_area', update="{'$set': item}")


if __name__ == '__main__':
    prepare()