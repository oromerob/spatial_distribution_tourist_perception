from . import tiles


def geojson_polygon_formatter(properties, tile, zoom):
    xtile, ytile = tile.split('_')
    polygon_boundaries = tiles.tile_boundaries(int(xtile), int(ytile), zoom)
    polygon = {
        "type": "Feature",
        "properties": properties,
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [polygon_boundaries[1], polygon_boundaries[0]],
                [polygon_boundaries[1], polygon_boundaries[2]],
                [polygon_boundaries[3], polygon_boundaries[2]],
                [polygon_boundaries[3], polygon_boundaries[0]],
                [polygon_boundaries[1], polygon_boundaries[0]]
            ]]
        }
    }
    return polygon