import random
from math import log

def exp_var(lbd):
    return -log(1.0 - random.random()) / lbd

def simulate(low_l, high_l, extra = 0):
    start = 10 * 60 # 10am
    end = 21 * 60   # 9pm

    high_demand = [(11 * 60 + 30, 13 * 60 + 30), (17 * 60, 19 * 60)] # (11:30am-1:30pm) (5pm-7pm)
    is_high_demand = lambda x: [i[0] <= x <= i[1] for i in high_demand].count(True)

    prep_times = [3, 5, 8]
    time_to_prep = lambda x: random.uniform(prep_times[x], prep_times[1+x])

    cur_t = start
    arrival, a_time = 0, 0
    def gen_client():
        return (exp_var(high_l if is_high_demand(cur_t) else low_l), time_to_prep(random.randint(0, 1)))

    INF = 1000000000
    free_worker = (-1, INF)
    workers = [free_worker] * 3 # in, out
    arrival, a_time = gen_client()
    arrival += cur_t

    waiting = 0
    clients = 0

    queue = [] # in, time
    while True:
        if arrival > end:
            arrival = INF

        cur_t = min([i[1] for i in workers] + [arrival])

        if cur_t == INF:
            break

        for i in range(3):
            if workers[i][1] == cur_t:
                if workers[i][1] - workers[i][0] > 5:
                    waiting += 1
                clients += 1
                workers[i] = free_worker

        if cur_t == arrival:
            queue.append((arrival, a_time))
            arrival, a_time = gen_client()
            arrival += cur_t

        for i in range(2 + extra * is_high_demand(cur_t)):
            if workers[i] == free_worker and len(queue):
                t_in, t_prep = queue[0]
                queue = queue[1:]
                workers[i] = (t_in, cur_t + t_prep)
    
    # print(waiting, clients, waiting / clients)
    return waiting / clients

random.seed(0)
SIMS = 10

l1 = [random.uniform(0.05, 0.4) for i in range(SIMS)]
l1.sort()
l2 = [l1[i] + exp_var(12.0) for i in range(SIMS)]
result = []
for i in range(SIMS):
    result.append((l1[i], l2[i], 0, simulate(l1[i], l2[i], 0)))
    result.append((l1[i], l2[i], 1, simulate(l1[i], l2[i], 1)))

#print(result)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six
from math import floor

def round(x):
    return floor(x * 100000) / 100000

df = pd.DataFrame()
df['lbd baja dem'] = [round(i[0]) for i in result]
df['lbd alta dem'] = [round(i[1]) for i in result]
df['Extra'] = [str([False, True][i[2]]) for i in result]
df['Porciento'] = [round(i[3]) for i in result]

def render_mpl_table(data, col_width=8.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

render_mpl_table(df, header_columns=0, col_width=2.0).get_figure().savefig('fig')