import os
from utils import filter_name


def write_init_adj_mat():
    streets = set()
    with open("./dataset/timeStreet.csv", "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split(" ")

            for i in range(1, len(line)):
                street = line[i]
                streets.add(street)

    # Init
    if os.path.exists("./dataset/adj_matrix.csv"):
        os.remove("./dataset/adj_matrix.csv")

    with open("./dataset/adj_matrix.csv", "a+", encoding="utf-8") as f:
        for key in streets:
            s = key + '\n'
            f.write(s)


def read_adj_mat():
    streets = set()
    transitions = set()
    with open('./dataset/adj_matrix.csv', encoding="utf-8") as f:
        for line in f:
            names = line.strip().split(' ')
            if names[0] == '':
                continue
            streets.add(filter_name(names[0]))
            for i in range(1, len(names)):
                transitions.add((
                    filter_name(names[0]), filter_name(names[i]),
                ))
    streets = list(streets)
    nlen = len(streets)
    adj_mat = []
    for i in range(nlen):
        adj_mat.append([0] * nlen)
        adj_mat[-1][i] = 1
    for t in transitions:
        if t[0] in streets and t[1] in streets:
            i1 = streets.index(t[0])
            i2 = streets.index(t[1])
            adj_mat[i1][i2] = 1
            adj_mat[i2][i1] = 1
    return streets, adj_mat


if __name__ == '__main__':
    streets, adj_mat = read_adj_mat()
    pass
