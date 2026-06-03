# =============================================================================
#          File: team_players_comparison.py
#        Author: Andre Brener
#       Created: 31 Jan 2017
# Last Modified: 13 May 2017
#   Description: Compare players of a team across per-90-minute metrics,
#                producing one bar chart per metric.
# =============================================================================
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

players_in_graph = 7
chosen_player = 'Bergessio'
team = 'San Lorenzo'

STATS_DICT = {
    'total_shots': [
        'es el más tirador del equipo',
        'Top {0} de jugadores de {1} con más tiros por 90 minutos'.format(
            players_in_graph, team), 1
    ],
    'sot': [
        'fue el que más tiró al arco del equipo',
        'Top {0} de jugadores  de {1} con más tiros al arco por 90 minutos'.
        format(players_in_graph, team), 1
    ],
    'goals': [
        'fue el más goleador del equipo en el Torneo',
        'Top {0} de jugadores de {1} con más goles por 90 minutos'.format(
            players_in_graph, team), 1
    ],
    'key_passes': [
        'fue el que hizo más pases que terminaron en tiro',
        'Top {0} de jugadores de {1} que hicieron más pases que terminaron  en tiro por 90 minutos'.
        format(players_in_graph, team), 1
    ],
    'assists': [
        'fue el mejor asistidor de {0} en el Torneo'.format(team),
        'Top {0} de jugadores de {1} con más asistencias por 90 minutos'.
        format(players_in_graph, team), 1
    ]
}

def plot_player_stats(df):
    for col in df.columns:
        if col == 'player':
            continue
        df = df.sort_values(col, ascending=False)
        players = df['player'][:players_in_graph]
        player_colors = []
        for player in players:
            if player == chosen_player:
                player_colors.append('orangered')
            else:
                player_colors.append('deepskyblue')

        first_player = list(players)[0]
        title = '{0} {1}'.format(first_player, STATS_DICT[col][0])
        fig, ax = plt.subplots(figsize=(10, 8))
        plt.title(title, weight='bold', loc='left', fontsize=26, color='0.2')
        x = np.arange(1, players_in_graph + 1)
        y = df[col][:players_in_graph]
        plt.bar(x, y, align='center', color=player_colors)
        plt.xticks(x, players, color='0.3', fontsize=16)
        plt.ylim(0, 1.15 * df[col][:players_in_graph].max())
        ax.set_yticklabels([])
        ax.text(
            0,
            1.10 * df[col][:players_in_graph].max(),
            '{0}'.format(STATS_DICT[col][1]),
            color='0.3',
            fontsize=18,
            horizontalalignment='left')
        for n, val in enumerate(y):
            if STATS_DICT[col][2] > 1:
                value = '{0}%'.format(int(STATS_DICT[col][2] * val))
            else:
                value = round(val, 2)
            ax.annotate(
                value,
                xy=(x[n], val),
                xytext=(x[n], 1.01 * val),
                verticalalignment='bottom',
                horizontalalignment='center',
                color='0.3',
                fontsize=18)
        plt.show()


def main():
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'slo_data.csv')
    df = pd.read_csv(csv_path)
    plot_player_stats(df)


if __name__ == '__main__':
    main()
