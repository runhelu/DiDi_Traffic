import os


def write_init_adj_mat():
    streets = set()
    with open("timeStreet.csv", "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split(" ")

            for i in range(1, len(line)):
                street = line[i]
                streets.add(street)

    # Init
    if os.path.exists("adj_matrix.csv"):
        os.remove("adj_matrix.csv")

    with open("adj_matrix.csv", "a+", encoding="utf-8") as f:
        for key in streets:
            s = key + '\n'
            f.write(s)


def read_adj_mat():
    def filter_name(s):
        if s.startswith('二环路沿线商业经济带'):
            s = s.replace('二环路沿线商业经济带', '')
        if s.endswith('辅路'):
            s = s.replace('辅路', '')
        for p in '东西南北':
            if s.endswith('{}段'.format(p)):
                s = s.replace('{}段'.format(p), '')
        return s

    streets = set()
    transitions = set()
    with open('./adj_matrix.csv', encoding="utf-8") as f:
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
