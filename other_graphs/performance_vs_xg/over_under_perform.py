# =============================================================================
#          File: over_under_perform.py
#        Author: Andre Brener
#       Created: 22 Aug 2017
#   Description: Plot a player's actual goals vs expected goals (xG) over time,
#                shading periods of over- and under-performance.
# =============================================================================
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')


def plot_performance(csv_path):
    df = pd.read_csv(csv_path, index_col=0)

    date = df.index.values.tolist()

    x = np.linspace(1, 100, len(date))
    rg = np.array(df['goals_90'].tolist())
    xg = np.array(df['xg_90'].tolist())

    fig, ax = plt.subplots(figsize=(12, 6))
    plt.plot(x, xg, color='k', lw=2)
    plt.title(
        'Evolución de Goles vs xG: Rodrigo Mora', fontsize=16, weight='bold')
    ax.fill_between(
        x,
        xg,
        rg,
        where=rg >= xg,
        facecolor='lime',
        alpha=0.3,
        interpolate=True,
        label='Rendimiento supera Goles Esperados')
    ax.fill_between(
        x,
        xg,
        rg,
        where=rg < xg,
        facecolor='r',
        alpha=0.3,
        interpolate=True,
        label='Rendimiento por debajo de Goles Esperados')
    ax.annotate(
        'Línea Negra: xG por 90 Minutos',
        xy=(15, 1),
        size=10,
        ha="center",
        color='0.3')
    plt.ylim((0, 1.1))
    plt.xticks(x, date, rotation='vertical')
    plt.tick_params(axis='both', which='major', labelsize=13)
    plt.legend(fontsize='x-large')
    ax.set_facecolor('whitesmoke')
    plt.grid(False)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':

    csv_path = os.path.join(
        os.path.dirname(__file__), 'rodrigo_mora_xg.csv')
    plot_performance(csv_path)
