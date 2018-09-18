"""
Utils to work with tiles.
Taken from https://stackoverflow.com/questions/28476117/easy-openstreetmap-tile-displaying-for-python
"""
import math


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return xtile, ytile


def num2deg(xtile, ytile, zoom):
    """
    http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    This returns the NW-corner of the square.
    Use the function with xtile+1 and/or ytile+1 to get the other corners.
    With xtile+0.5 & ytile+0.5 it will return the center of the tile.
    """
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def tile_center(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = (xtile + 0.5) / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (ytile + 0.5) / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def tile_boundaries(xtile, ytile, zoom):
    top_latitude, left_longitude = num2deg(xtile, ytile, zoom)
    bottom_latitude, right_longitude = num2deg(xtile + 1, ytile + 1, zoom)
    return [top_latitude, left_longitude,  bottom_latitude,  right_longitude]
