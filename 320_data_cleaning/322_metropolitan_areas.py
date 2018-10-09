from common import mongo_utils


def metropolitan_area_name(metropolitan_area):
    city_names = [doc['city'] for doc in mongo_utils.mongo_get(
        collection='pre_business',
        filter={'tile10': {'$in': metropolitan_area['tiles']}},
        fields={'city': 1}
    )]
    names = {}
    for city in city_names:
        if city not in names:
            names[city] = 0
        names[city] += 1
    names_list = [{'city': city, 'count': count} for city, count in names.items()]
    names_list.sort(key=lambda x: x['count'], reverse=True)
    metropolitan_area['name'] = names_list[0]['city']
    metropolitan_area['_id'] = metropolitan_area['name']


def center(businesses):
    aggregated_lat = 0
    aggregated_lon = 0
    for business in businesses:
        aggregated_lat += business['latitude']
        aggregated_lon += business['longitude']
    center_lat = aggregated_lat / len(businesses)
    center_lon = aggregated_lon / len(businesses)
    return center_lat, center_lon


def metropolitan_area_center(metropolitan_area):
    businesses = mongo_utils.mongo_get(
        collection='pre_business',
        filter={'tile10': {'$in': metropolitan_area['tiles']}},
        fields={'latitude': 1, 'longitude': 1}
    )
    center_lat, center_lon = center(businesses)
    metropolitan_area['center'] = [center_lat, center_lon]


def groups_filter(tiles_grouped):
    metropolitan_area = []
    for group in tiles_grouped:
        cluster_ = {
            'tiles': group,
            'businesses': business_count(group)
        }
        if cluster_['businesses'] > 1000:
            metropolitan_area.append(cluster_)

    metropolitan_area_sorted = sorted(metropolitan_area, key=lambda x: x['businesses'], reverse=True)

    return metropolitan_area_sorted


def business_count(tiles):
    return len(mongo_utils.mongo_get(collection='pre_business', filter={'tile10': {'$in': tiles}}, fields={}))


def group_check_surroundings(tiles, grouped, group):
    if len(group['new']) == 0:
        group['new'].append(tiles.pop(0))
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


def tiles_group(tiles_sorted, grouped=None, group=None):
    if grouped is None:
        grouped = []
    if group is None:
        group = {
            'done': [],
            'new': []
        }

    tiles_sorted, grouped, group = group_check_surroundings(tiles_sorted, grouped, group)

    if len(group['new']) > 0:
        return tiles_group(tiles_sorted, grouped=grouped, group=group)
    if len(tiles_sorted) > 0:
        return tiles_group(tiles_sorted, grouped=grouped)
    return grouped


def prepare():
    tiles = {doc['tile10'] for doc in mongo_utils.mongo_get(collection='pre_business', fields={'tile10': 1})}
    tiles_sorted = sorted(tiles, key=lambda x: x.split('_')[0])
    tiles_grouped = tiles_group(tiles_sorted)
    metropolitan_areas = groups_filter(tiles_grouped)
    for metropolitan_area in metropolitan_areas:
        metropolitan_area_center(metropolitan_area)
        metropolitan_area_name(metropolitan_area)
    mongo_utils.batch_upsert(metropolitan_areas, collection='pre_metropolitan_area', update="{'$set': item}")


if __name__ == '__main__':
    prepare()
