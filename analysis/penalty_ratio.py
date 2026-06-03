# =============================================================================
#          File: penalty_ratio.py
#        Author: Andre Brener
#       Created: 29 Sep 2017
# Last Modified: 29 Sep 2017
#   Description: Rank teams by penalties won and conceded per game and plot
#                the top teams.
# =============================================================================
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from constants import TEAM_DICT

plt.style.use('fivethirtyeight')

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'data', 'game_data')


def load_data(data_dir):
    file_list = [
        f for f in os.listdir(data_dir)
        if os.path.isfile(os.path.join(data_dir, f))
    ]
    df_list = [pd.read_csv(os.path.join(data_dir, f)) for f in file_list]
    df = pd.concat(df_list)
    return df


def group_team_penalties(df, against=False):
    grp_dfs = []
    for home_status in ['home', 'away']:
        pen_term = home_status
        for_term = 'for'
        if against:
            for_term = 'against'
            if home_status == 'home':
                pen_term = 'away'
            else:
                pen_term = 'home'
        team_col = '{}_name'.format(home_status)
        penalty_col = '{}_penalties'.format(pen_term)
        grp_df = df[[team_col, penalty_col
                     ]].groupby(team_col).agg(['sum', 'count']).reset_index()

        grp_df.columns = [
            'team', '{}_{}_penalties'.format(for_term, home_status),
            '{}_games'.format(home_status)
        ]
        grp_dfs.append(grp_df)

    final_df = get_final_df(grp_dfs)
    return final_df


def get_final_df(grp_dfs):
    total_df = grp_dfs[0]
    for df in grp_dfs[1:]:
        total_df = pd.merge(total_df, df)

    return total_df


def get_calculations(data_dir):
    df = load_data(data_dir)
    grp_dfs = [group_team_penalties(df, ag) for ag in [True, False]]
    total_df = get_final_df(grp_dfs)
    total_df['for_total_penalties'] = total_df[
        'for_home_penalties'] + total_df['for_away_penalties']
    total_df['against_total_penalties'] = total_df[
        'against_home_penalties'] + total_df['against_away_penalties']
    total_df['total_games'] = total_df['home_games'] + total_df['away_games']

    total_df['for_penalties_per_game'] = total_df[
        'for_total_penalties'] / total_df['total_games']
    total_df['against_penalties_per_game'] = total_df[
        'against_total_penalties'] / total_df['total_games']

    total_df = total_df[total_df['total_games'] > 5]

    df_dict = {}
    for ag in ['against', 'for']:
        col = '{}_penalties_per_game'.format(ag)
        df_dict[ag] = total_df[['team', col]].sort_values(col, ascending=False)

    return df_dict


def get_graph(df_dict, teams_in_graph, team_dict):
    for key, df in df_dict.items():
        title_term = 'a favor'
        if key == 'against':
            title_term = 'en contra'
        first_team = team_dict[list(df['team'])[0]]
        title = '{} es el equipo con más penales {}'.format(first_team,
                title_term)
        col = '{}_penalties_per_game'.format(key)
        team_names = [team_dict[team] for team in df['team'][:teams_in_graph]]
        fig, ax = plt.subplots(figsize=(10, 8))
        plt.title(title, weight='bold', loc='left', fontsize=26, color='0.2')
        x = np.arange(1, teams_in_graph + 1)
        y = df[col][:teams_in_graph]
        mean_values = [df[col].mean()] * teams_in_graph
        plt.bar(x, y, align='center')
        plt.plot(x, mean_values, color='r', label='Promedio')
        plt.ylim(0, 1.15 * df[col][:teams_in_graph].max())
        plt.legend()
        plt.ylabel('Penales por partido')
        plt.xticks(x, team_names, color='0.3', fontsize=13)
        sub_title = 'Penales {} por partido'.format(title_term)
        ax.text(
            0.4,
            1.10 * df[col][:teams_in_graph].max(),
            sub_title,
            color='0.3',
            fontsize=18,
            horizontalalignment='left')

        for n, val in enumerate(y):
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


if __name__ == '__main__':

    df_dict = get_calculations(DATA_DIR)
    get_graph(df_dict, 8, TEAM_DICT)
