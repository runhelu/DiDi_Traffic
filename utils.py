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


def categorize(all_data):
    # type: (pd.DataFrame) -> dict
    info = defaultdict(lambda: defaultdict(list))
    columns = ['driverID', 'orderID', 'time', 'lat', 'long']
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
    return dict(info)


def generate_pickle(start=0, limit=None):
    data = pd.read_csv(
        "gps_20161101",
        names=[
            "driverID",
            "orderID",
            "time",
            "lat",
            "long"],
        skiprows=start,
        nrows=limit
    )
    info = categorize(data)
    with open('info.pickle', 'w+') as f:
        pickle.dump(info, f)
    return info


def convert_lat(lat):
    # type: (float) -> float
    return float(lat)


def convert_long(long):
    # type: (float) -> float
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
    ddx = seq[1]['lat'] - seq[0]['lat']
    ddy = seq[1]['long'] - seq[0]['long']
    for i in range(2, len(seq)):
        dx = seq[i]['lat'] - seq[i - 1]['lat']
        dy = seq[i]['long'] - seq[i - 1]['long']
        ang = get_angle(ddx, ddy, dx, dy)
        if ang < 150:
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
    if 34.256816 <= long <= 34.282591 and 108.929953 <= lat <= 108.978677:
        location = '{},{}'.format(long, lat)
        url = "http://api.map.baidu.com/geocoder/v2/?location={}&output=json&language=en&ak={}".format(
            location, ak
        )
        resp = requests.get(url).json()
        if resp['status'] != 0:
            return False, ''
        street = str(resp['result']['addressComponent']['street'])
        return True, street


def assign_street_name(info, driver_id, order_id, sep):
    for i in range(len(sep) // 2):
        start = sep[i * 2]
        stop = sep[i * 2 + 1]
        midpoint = ((start[2] + stop[2]) / 2, (start[3] + stop[3]) / 2)
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
                        transitions.append(
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
    for did in info.keys():
        for oid in info[did].keys():
            sep = seperate_road(info, did, oid)
            assign_street_name(info, did, oid, sep)
    return build_adjacent_matrix(info)


if __name__ == "__main__":
    if os.path.exists("./info.pickle"):
        with open('info.pickle') as f:
            info = pickle.load(f)
    else:
        info = generate_pickle()
    collect_street(info)
    import ipdb
    ipdb.set_trace()

