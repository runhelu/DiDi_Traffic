import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
import logging
import requests
from collections import defaultdict


logging.basicConfig(format="%(asctime)s: [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def categorize(info, all_data, with_street=False):
    # type: (dict, pd.DataFrame) -> dict
    columns = ['driverID', 'orderID', 'time', 'lat', 'long']
    if with_street:
        columns.append('street')
    for _, p in all_data.iterrows():
        info[p['driverID']][p['orderID']].append({
            k: p[k] for k in columns
        })
    for driverID in info.keys():
        for orderID in info[driverID]:
            info[driverID][orderID] = sorted(
                info[driverID][orderID],
                key=lambda t: t['time']
            )
    return info


def generate_pickle(start=0, limit=None):
    info = defaultdict(lambda: defaultdict(list))
    for i in range(100):
        limit = 1000
        if i % 10 == 0:
            print("Progress: {}/{}".format(i * limit, 1000 * limit))
        data = pd.read_csv(
            "gps_20161101",
            names=[
                "driverID",
                "orderID",
                "time",
                "lat",
                "long"],
            skiprows=start + i * limit,
            nrows=limit
        )
        info = categorize(info, data)
    info = dict(info)
    with open('info.pickle', 'wb') as f:
        pickle.dump(info, f)
    return info


def generate_cache_pickle(start=0, limit=None):
    info = defaultdict(lambda: defaultdict(list))
    names = [
        (0, 10000),
        (10000, 30000),
        (30000, 40000),
        (40000, 50000),
        (50000, 60000),
        (60000, 70000),
        (70000, 80000),
        (80000, 90000),
        (90000, 100000),
    ]
    for i in range(len(names)):
        print("Progress: {}/{}".format(names[i][0], 100000))
        data = pd.read_csv(
            "cache_{}_{}.csv".format(names[i][0], names[i][1]),
            names=[
                "driverID",
                "orderID",
                "time",
                "lat",
                "long",
                'street'],
            sep=' '
        )
        info = categorize(info, data, with_street=True)
    info = dict(info)
    with open('cache.pickle', 'wb') as f:
        pickle.dump(info, f)
    return info


def convert_lat(lat):
    # type: (float) -> float
    # TODO: remap latitude to visualible metric on the map
    return float(lat)


def convert_long(long):
    # type: (float) -> float
    # TODO: remap longtitude to visualible metric on the map
    return float(long)


def plot_driver(info, driver_id):
    # type: (dict, list) -> None
    x = []
    y = []
    for did in driver_id:
        for oid in info[did].keys():
            x.append(map(
                lambda t: convert_lat(t['lat']),
                info[did][oid]
            ))
            y.append(map(
                lambda t: convert_long(t['long']),
                info[did][oid]
            ))
    plt.plot(x, y, '.')
    plt.show()


def seperate_road(info, driver_id, order_id):
    # type: (dict, str, str) -> list
    def get_angle(x1, y1, x2, y2):
        return np.arccos(
            np.dot([x1, y1], [x2, y2]) / np.sqrt(x1 ** 2 + y1 ** 2) / np.sqrt(x2 ** 2 + y2 ** 2)
        ) * 180.0 / np.pi

    seq = info[driver_id][order_id]
    result = [('start', 0, seq[0]['lat'], seq[0]['long'])]
    if len(seq) == 1:
        result.append(
            ('stop', len(seq) - 1, seq[-1]['lat'], seq[-1]['long'])
        )
        return result

    ddx = seq[1]['lat'] - seq[0]['lat']
    ddy = seq[1]['long'] - seq[0]['long']
    for i in range(2, len(seq)):
        dx = seq[i]['lat'] - seq[i - 1]['lat']
        dy = seq[i]['long'] - seq[i - 1]['long']
        ang = get_angle(ddx, ddy, dx, dy)
        if ang > 30:
            result.append(
                ('stop', i - 1, seq[i - 1]['lat'], seq[i - 1]['long']),
            )
            result.append(
                ('start', i, seq[i]['lat'], seq[i]['long']),
            )
        ddx = dx
        ddy = dy
    result.append(
        ('stop', len(seq) - 1, seq[-1]['lat'], seq[-1]['long'])
    )
    return result


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


def assign_street_name(info, driver_id, order_id, sep):
    for i in range(len(sep) // 2):
        start = sep[i * 2]
        stop = sep[i * 2 + 1]
        midpoint = ((start[3] + stop[3]) / 2, (start[2] + stop[2]) / 2)
        success, street = request_info(midpoint[0], midpoint[1])
        if not success:
            continue
        for j in range(start[1], stop[1] + 1):
            info[driver_id][order_id][j]['street'] = street


def build_adjacent_matrix(info):
    # type: (dict) -> (list, list)
    streets = set()
    transitions = set()
    for did in info.keys():
        for oid in info[did].keys():
            last_street = ''
            for t in info[did][oid]:
                streets.add(t['street'])
                if t['street'] != last_street:
                    if last_street != '':
                        transitions.add(
                            tuple(sorted([
                                      last_street,
                                      t['street']
                            ])))
                last_street = t['street']
    streets = list(streets)
    nlen = len(streets)
    adj_mat = []
    for i in range(nlen):
        adj_mat.append([0] * nlen)
        adj_mat[-1][i] = 1
    for trans in transitions:
        p = streets.index(trans[0])
        q = streets.index(trans[1])
        adj_mat[p][q] = 1
        adj_mat[q][p] = 1
    return streets, adj_mat


def collect_street(info):
    tot = 0
    for did in info.keys():
        for oid in info[did].keys():
            tot += 1
            if tot % 50 == 0:
                print(tot)
            sep = seperate_road(info, did, oid)
            assign_street_name(info, did, oid, sep)
    return build_adjacent_matrix(info)


def calculate_angle_diff(info, driver_id, order_id):
    # type: (dict, str, str) -> list
    def get_angle(x1, y1, x2, y2):
        return np.arccos(
            np.dot([x1, y1], [x2, y2]) / np.sqrt(x1 ** 2 + y1 ** 2) / np.sqrt(x2 ** 2 + y2 ** 2)
        ) * 180.0 / np.pi

    seq = info[driver_id][order_id]
    result = []
    non_result = []
    if len(seq) == 1:
        return result, non_result

    ddx = seq[1]['lat'] - seq[0]['lat']
    ddy = seq[1]['long'] - seq[0]['long']
    for i in range(2, len(seq)):
        dx = seq[i]['lat'] - seq[i - 1]['lat']
        dy = seq[i]['long'] - seq[i - 1]['long']
        ang = get_angle(ddx, ddy, dx, dy)
        if seq[i]['street'] != seq[i - 1]['street']:
            result.append(ang)
        else:
            non_result.append(ang)
        ddx = dx
        ddy = dy
    return result, non_result


def decide_angle(info):
    all = []
    non_all = []
    for did in info.keys():
        for oid in info[did].keys():
            ang, non_ang = calculate_angle_diff(info, did, oid)
            if ang:
                all += ang
                print(did, oid, 'ang', np.nanmean(ang))
            if non_ang:
                non_all += non_ang
                print(did, oid, 'non ang', np.nanmean(non_ang))
    print('all', np.nanmean(all))
    print('non all', np.nanmean(non_all))


def load_info_pickle():
    if os.path.exists("./info.pickle"):
        with open('info.pickle', 'rb') as f:
            info = pickle.load(f)
    else:
        info = generate_pickle()
    return info


def load_cache_pickle():
    if os.path.exists("./cache.pickle"):
        with open('cache.pickle', 'rb') as f:
            info = pickle.load(f)
    else:
        info = generate_cache_pickle()
    return info


if __name__ == "__main__":
    info = load_cache_pickle()
    decide_angle(info)

