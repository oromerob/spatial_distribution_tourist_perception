import math


def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)


def tile_boundaries(xtile, ytile, zoom):
  top_latitude, left_longitude = num2deg(xtile, ytile, zoom)
  bottom_latitude, right_longitude = num2deg(xtile + 1, ytile + 1, zoom)
  # return [float("%.3f" % top_latitude), float("%.3f" % left_longitude),  float("%.3f" % bottom_latitude),  float("%.3f" % right_longitude)]
  return [top_latitude, left_longitude,  bottom_latitude,  right_longitude]


if __name__ == '__main__':
    tile = deg2num(41.3299904, 2.1675144, 10)
    print(tile)