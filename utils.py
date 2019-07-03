import requests
from geopy.distance import vincenty
from math import sin, cos, sqrt, fabs, atan2, radians
from math import pi as PI


# Copy from https://github.com/sshuair/coord-convert/blob/master/coord_convert/transform.py
# Unable to install fiona


# define ellipsoid
a = 6378245.0
f = 1 / 298.3
b = a * (1 - f)
ee = 1 - (b * b) / (a * a)


def outOfChina(lng, lat):
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)


def transformLat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(fabs(x))
    ret = ret + (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret = ret + (20.0 * sin(y * PI) + 40.0 * sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret = ret + (160.0 * sin(y / 12.0 * PI) + 320.0 * sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret


def transformLon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * sqrt(fabs(x))
    ret = ret + (20.0 * sin(6.0 * x * PI) + 20.0 * sin(2.0 * x * PI)) * 2.0 / 3.0
    ret = ret + (20.0 * sin(x * PI) + 40.0 * sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret = ret + (150.0 * sin(x / 12.0 * PI) + 300.0 * sin(x * PI / 30.0)) * 2.0 / 3.0
    return ret


def wgs2gcj(wgsLon, wgsLat):
    """wgs coord to gcj

    Arguments:
        wgsLon {float} -- lon
        wgsLat {float} -- lat

    Returns:
        tuple -- gcj coords
    """

    if outOfChina(wgsLon, wgsLat):
        return wgsLon, wgsLat
    dLat = transformLat(wgsLon - 105.0, wgsLat - 35.0)
    dLon = transformLon(wgsLon - 105.0, wgsLat - 35.0)
    radLat = wgsLat / 180.0 * PI
    magic = sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * cos(radLat) * PI)
    gcjLat = wgsLat + dLat
    gcjLon = wgsLon + dLon
    return gcjLon, gcjLat


def gcj2wgs(gcjLon, gcjLat):
    g0 = (gcjLon, gcjLat)
    w0 = g0
    g1 = wgs2gcj(w0[0], w0[1])
    # w1 = w0 - (g1 - g0)
    w1 = tuple(map(lambda x: x[0] - (x[1] - x[2]), zip(w0, g1, g0)))
    # delta = w1 - w0
    delta = tuple(map(lambda x: x[0] - x[1], zip(w1, w0)))
    while abs(delta[0]) >= 1e-6 or abs(delta[1]) >= 1e-6:
        w0 = w1
        g1 = wgs2gcj(w0[0], w0[1])
        # w1 = w0 - (g1 - g0)
        w1 = tuple(map(lambda x: x[0] - (x[1] - x[2]), zip(w0, g1, g0)))
        # delta = w1 - w0
        delta = tuple(map(lambda x: x[0] - x[1], zip(w1, w0)))
    return w1


def filter_name(s):
    if s.startswith('二环路沿线商业经济带'):
        s = s.replace('二环路沿线商业经济带', '')
    if s.endswith('辅路'):
        s = s.replace('辅路', '')
    for p in '东西南北':
        if s.endswith('{}段'.format(p)):
            s = s.replace('{}段'.format(p), '')
    return s


def request_info(long, lat):
    # type: (float, float) -> (bool, str)
    with open('baidu_ak') as f:
        ak = f.readline().strip()
    # if 34.256816 <= long <= 34.282591 and 108.929953 <= lat <= 108.978677:
    location = '{},{}'.format(long, lat)
    url = "http://api.map.baidu.com/geocoder/v2/?location={}&output=json&language=en&ak={}".format(
        location, ak
    )
    succ = False
    while not succ:
        try:
            resp = requests.get(url).json()
            succ = True
        except:
            pass
    if resp['status'] != 0:
        return False, ''
    street = str(resp['result']['addressComponent']['street'])
    return True, street


# from https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0088
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(a**0.5, (1-a)**0.5)
    d = R * c
    return round(d, 4)


def vincenty_distance(lat1, lon1, lat2, lon2):
    return vincenty((lat1, lon1), (lat2, lon2)).km
