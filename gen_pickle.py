import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
import logging
from collections import defaultdict
from utils import filter_name


logging.basicConfig(format="%(asctime)s: [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_cache_csv():
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
            "./dataset/cache_{}_{}.csv".format(names[i][0], names[i][1]),
            names=[
                "driverID",
                "orderID",
                "time",
                "lat",
                "long",
                'street'],
            sep=' ',
            header=None
        )
        yield data


def categorize_by_driver(info, all_data, with_street=False):
    # type: (dict, pd.DataFrame, bool) -> dict
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


def categorize_by_street(info, all_data):
    columns = ['driverID', 'orderID', 'time', 'lat', 'long', 'street']
    for _, p in all_data.iterrows():
        # isnan(p['street'])
        if isinstance(p['street'], float):
            continue
        info[filter_name(p['street'])].append({
            k: p[k] for k in columns
        })
        for street in info:
            info[street] = sorted(
                info[street],
                key=lambda t: t['time']
            )
    return info


def generate_info_pickle(start=0, limit=None):
    info = defaultdict(lambda: defaultdict(list))
    for i in range(100):
        limit = 1000
        if i % 10 == 0:
            print("Progress: {}/{}".format(i * limit, 1000 * limit))
        data = pd.read_csv(
            "./dataset/gps_20161101",
            names=[
                "driverID",
                "orderID",
                "time",
                "lat",
                "long"],
            skiprows=start + i * limit,
            nrows=limit
        )
        info = categorize_by_driver(info, data)
    info = dict(info)
    with open('./dataset/info.pickle', 'wb') as f:
        pickle.dump(info, f)
    return info


def generate_driver_pickle(start=0, limit=None):
    info = defaultdict(lambda: defaultdict(list))
    for data in read_cache_csv():
        info = categorize_by_driver(info, data, with_street=True)
    info = dict(info)
    with open('./dataset/driver.pickle', 'wb') as f:
        pickle.dump(info, f)
    return info


def generate_street_pickle(start=0, limit=None):
    info = defaultdict(list)
    for data in read_cache_csv():
        info = categorize_by_street(info, data)
    info = dict(info)
    with open('./dataset/street.pickle', 'wb') as f:
        pickle.dump(info, f)
    return info


def load_info_pickle():
    if os.path.exists("./dataset/info.pickle"):
        with open('./dataset/info.pickle', 'rb') as f:
            info = pickle.load(f)
    else:
        info = generate_info_pickle()
    return info


def load_driver_pickle():
    if os.path.exists("./dataset/driver.pickle"):
        with open('./dataset/driver.pickle', 'rb') as f:
            info = pickle.load(f)
    else:
        info = generate_driver_pickle()
    return info


def load_street_pickle():
    if os.path.exists("./dataset/street.pickle"):
        with open('./dataset/street.pickle', 'rb') as f:
            info = pickle.load(f)
    else:
        info = generate_street_pickle()
    return info


if __name__ == "__main__":
    info = load_street_pickle()

