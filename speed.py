import numpy as np
from bisect import bisect_left
from collections import defaultdict
from math import floor
from gen_pickle import load_street_pickle, load_driver_pickle
from utils import gcj2wgs, haversine_distance, vincenty_distance


def estimate_speed(interval=600):
    info = load_street_pickle()
    driver = load_driver_pickle()
    start_time = min([l[0]['time'] for l in info.values()])
    end_time = max([l[-1]['time'] for l in info.values()])
    n_slice = floor((end_time - start_time) / interval) + 1
    intervals = {}
    for street in info.keys():
        intervals[street] = [defaultdict(list) for _ in range(n_slice)]
        for p in info[street]:
            n = (p['time'] - start_time) // interval
            d = driver[p['driverID']][p['orderID']]
            td = [x['time'] for x in d]
            nidx = bisect_left(td, p['time'])
            if nidx < len(d) - 1:
                nxt_long, nxt_lat = gcj2wgs(d[nidx + 1]['long'], d[nidx + 1]['lat'])
                cur_long, cur_lat = gcj2wgs(d[nidx]['long'], d[nidx]['lat'])
                dis = vincenty_distance(nxt_lat, nxt_long, cur_lat, cur_long)
                dtime = d[nidx + 1]['time'] - d[nidx]['time']
                intervals[street][n][p['driverID']].append(dis / dtime * 3600)
    return intervals, n_slice


def fill_missing_speed(intervals, n_slice):
    mean_speed = {}
    for street in intervals:
        mean_speed[street] = [0 for _ in range(n_slice)]
        missing_idx = []
        all_value = []
        for i in range(n_slice):
            if intervals[street][i]:
                mean_speed[street][i] = np.nanmean([np.mean(l) for l in intervals[street][i].values()])
                all_value.append(mean_speed[street][i])
            else:
                missing_idx.append(i)
        for i in missing_idx:
            # alternatives: interpolation
            mean_speed[street][i] = np.mean(all_value)
    return mean_speed, n_slice


def read_speed():
    intervals, n = estimate_speed()
    speed, n = fill_missing_speed(intervals, n)
    return speed, n


if __name__ == '__main__':
    read_speed()