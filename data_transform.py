import numpy as np
import pandas as pd
from adj_mat import read_adj_mat
from speed import read_speed


def make_adj_csv(n_streets, adj_mat, stype='stgcn'):
    if stype == 'stgcn':
        adj = np.full((n_streets, n_streets), 1)
        for i in range(n_streets):
            adj[i][i] = 0
            for j in range(i + 1, n_streets):
                if adj_mat[i][j]:
                    adj[i][j] = 0
                    adj[j][i] = 0
        """
        for k in range(n_streets):
            for i in range(n_streets):
                for j in range(n_streets):
                    adj[i][j] = min(adj[i][j], adj[i][k] + adj[k][j])
        """
        df = pd.DataFrame(adj)
        df.to_csv('adj.csv', index=False, header=False)
    elif stype == 'tgcn':
        adj = np.array(adj_mat, ndmin=2)
        df = pd.DataFrame(adj)
        df.to_csv('adj.csv', index=False, header=False)


def make_speed_csv(d_slice, streets, speed, stype='stgcn'):
    n_streets = len(streets)
    if stype == 'stgcn':
        data = np.zeros(shape=(d_slice, n_streets))
        for i, s in enumerate(streets):
            data[:, i] = speed[s]
        df = pd.DataFrame(data)
        df.to_csv('speed.csv', index=False, header=False, na_rep='0.0')
    elif stype == 'tgcn':
        # mysterious first line??
        # keep it same as other
        data = np.zeros(shape=(d_slice, n_streets))
        for i, s in enumerate(streets):
            data[:, i] = speed[s]
        df = pd.DataFrame(data)
        df.to_csv('speed.csv', index=False, header=False, na_rep='0.0')
    else:
        raise Exception("unsupported stype")


if __name__ == '__main__':
    streets, adj_mat = read_adj_mat()
    speed, d_slice = read_speed()
    make_adj_csv(len(streets), adj_mat, 'tgcn')
    make_speed_csv(d_slice, streets, speed, 'tgcn')
