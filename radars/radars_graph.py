import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('ggplot')


def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])


def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    x1, x2 = ranges[0]
    d = data[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        sdata.append((d - y1) / (y2 - y1) * (x2 - x1) + x1)
    return sdata


class ComplexRadar():
    def __init__(self, fig, variables, ranges, n_ordinate_levels=6):
        angles = np.arange(90, 450, 360. / len(variables))

        axes = [
            fig.add_axes(
                [0.1, 0.1, 0.8, 0.8], polar=True, label="axes{}".format(i))
            for i in range(len(variables))
        ]
        l, text = axes[0].set_thetagrids(angles, labels=variables)
        [txt.set_rotation(angle - 90) for txt, angle in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i], num=n_ordinate_levels)
            gridlabel = ["{}".format(round(x, 2)) for x in grid]
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1]  # hack to invert grid
                # gridlabels aren't reversed
            gridlabel[0] = ""  # clean up origin
            gridlabel[1] = ""
            ax.set_rgrids(grid, labels=gridlabel, angle=angles[i])
            ax.set_ylim(*ranges[i])
        # Variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]

    def plot(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], *args, **kw)

    def fill(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)


def change_zeros(val):
    if val == 0:
        return 0.001
    return val


def plot_graph(df, stats, players_plot):

    player_cols = [pl[0] for pl in players_plot]

    for player in player_cols:
        df[player] = df[player].apply(change_zeros)

    stat_names = list(stats.keys())
    stat_ranges = list(stats.values())

    fig = plt.figure(figsize=(9, 9))
    radar = ComplexRadar(fig, stat_names, stat_ranges)

    for pl, bc, fc in players_plot:
        radar.plot(df[pl], bc)
        radar.fill(df[pl], fc, alpha=0.2)
    plt.show()


if __name__ == '__main__':

    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'players_data_2016.csv')
    df = pd.read_csv(file_path, sep=';', index_col=0).T.reset_index()

    player_cols = [col for col in df.columns if col != 'index']

    players = [('Ortigoza', 'b', 'b')]

    global_stats = {
        'Goles (Descontando Penales)': (0.001, 0.85),
        'Tiros Totales': (0.10, 4.40),
        'Precision de Tiros %': (0.001, 80),
        'Dribles Correctos': (0.10, 4.60),
        'Pases en Profundidad': (0.001, 0.40),
        'Centros': (0.001, 3.2),
        'Asistencias': (0.001, 0.45),
        'Pases Clave': (0.19, 3.05),
        'Pases Correctos %': (30, 95),
        'Tackles + Intercepciones': (0.08, 8.40),
        'Perdidas': (5.80, 0.39),
        'Duelos Aereos Ganados %': (0.001, 70),
        'Conversion de Goles %': (0.001, 100)
    }

    dms_stats = {
        'Goles': (0.001, 0.60),
        'Asistencias': (0.001, 0.45),
        'Pases Correctos %': (30, 90),
        'Intercepciones': (0.1, 7),
        'Quites': (0.1, 5.7),
        'Faltas': (4.9, 0.1)
    }

    plot_graph(df, global_stats, players)
