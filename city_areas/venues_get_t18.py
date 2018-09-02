from common import clusters, prepro_business, venues
from tiles import tiles



def main(zoom):
    # 1. get clusters
    _clusters = [doc for doc in clusters.clusters_get(filter={}, fields={'tiles': 1})]

    # 2. for each cluster -> get venues
    for cluster in _clusters:
        _venues = {doc['_id']: doc for doc in prepro_business.prepro_business_get(filter={'tile10': {'$in': cluster['tiles']}}, fields={'latitude': 1, 'longitude': 1})}
        for item in [doc for doc in venues.venues_get(filter={'cluster_id': cluster['_id']})]:
            _venues[item['_id']].update(item)

            # 3. for each venue -> get t18
            tileX, tileY = tiles.deg2num(
                _venues[item['_id']]['latitude'],
                _venues[item['_id']]['longitude'],
                zoom
            )
            _venues[item['_id']]['tile{}'.format(zoom)] = '{}_{}'.format(tileX, tileY)

        # 4. for the venues of the cluster -> update t18
        venues.venues_batch_update([item for item in _venues.values()], update="{'$set': item}")

    pass


if __name__ == '__main__':
    main(15)