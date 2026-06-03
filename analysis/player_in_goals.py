import os

import requests
import pandas as pd

from bs4 import BeautifulSoup
from constants import COMPETITION, COMPETITION_DICT, END_DATE, START_DATE
from game_data import get_game_goals, get_games_id, get_players, get_teams


def get_team_names(game_id):

    url = 'http://www.espn.com.ar/futbol/numeritos?juegoId=' + str(game_id)

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    teams_html = soup.find_all("div", {"class": "possession"})

    teams = get_teams(teams_html)

    return teams


def get_subs_times(subs_times_html):

    subs_times = [n.contents[0] for n in subs_times_html]

    sub_minutes = []

    for m in subs_times:
        if '+' in m:
            index = m.index('+')
            minute = int(m[index - 2:index]) + int(m[index + 1])
        else:
            minute = int(m)

        sub_minutes.append(minute)

    return sub_minutes


def get_subs_names(subs_html):

    str_span = [str(s) for s in subs_html]

    subs_in = [el[27:-7] for el in str_span if 'En:' in el]
    subs_out = [el[50:-7] for el in str_span if 'Fuera:' in el]

    return subs_in, subs_out


def get_subs(subs_html, subs_times_html):

    subs_times = get_subs_times(subs_times_html)

    subs_in, subs_out = get_subs_names(subs_html)

    subs = list(zip(subs_times, subs_in, subs_out))

    return subs


def get_subs_per_team(subs, home_players, away_players):

    home_subs = 0
    away_subs = 0

    for minute, sub_in, sub_out in subs:
        if sub_in in home_players:
            home_subs += 1
        elif sub_in in away_players:
            away_subs += 1

    return home_subs, away_subs


def get_end_of_game(eof_html):

    end_of_game = int(eof_html[0].get("data-minute"))

    return end_of_game


def total_team_played(end_of_game, home_team, away_team):

    team_total_played = {}

    team_total_played[home_team] = end_of_game
    team_total_played[away_team] = end_of_game

    return team_total_played


def get_red_card_times(red_times_html):

    if not len(red_times_html):
        return []

    if not len(red_times_html[0].contents):
        return []

    red_times = [n.contents[0] for n in red_times_html]

    red_card_times = []

    for i in red_times:
        if '+' in i:
            index = i.index('+')
            minute = int(i[index - 2:index]) + int(i[index + 1])
        else:
            minute = int(i)
        red_card_times.append(minute)

    return red_card_times


def get_red_card_names(red_html, red_times):

    if not len(red_times):
        return []

    details = [n.contents[0] for n in red_html]

    red_names = [d[:16].strip() for d in details if 'Tarjeta roja' in d]

    return red_names


def get_red_cards(red_html, red_times_html):
    red_times = get_red_card_times(red_times_html)
    red_names = get_red_card_names(red_html, red_times)

    red_cards = list(zip(red_times, red_names))

    return red_cards


def get_players_that_played(home_players, away_players, home_subs, away_subs):

    home_players_played = [home_players[i] for i in range(11 + home_subs)]
    away_players_played = [away_players[i] for i in range(11 + away_subs)]

    return home_players_played, away_players_played


def time_per_player(home_players_played, away_players_played, end_of_game,
                    subs, red_cards):

    players_time = {}

    for player in home_players_played:
        players_time[player] = end_of_game

    for player in away_players_played:
        players_time[player] = end_of_game

    for minute, sub_in, sub_out in subs:
        players_time[sub_in] = end_of_game - minute
        players_time[sub_out] = minute

    for minute, player in red_cards:
        players_time[player] = minute

    return players_time


def player_in_goal(players_time, home_players_played, away_players_played,
                   home_team, away_team, home_goals_sorted, away_goals_sorted,
                   end_of_game):

    player_in_goals = {}

    for player in players_time:
        if player in home_players_played:
            player_in_goals[player] = [home_team, 0, 0, players_time[player]]
        elif player in away_players_played:
            player_in_goals[player] = [away_team, 0, 0, players_time[player]]

    if len(home_goals_sorted):
        for goal in home_goals_sorted:
            for player in players_time:
                pt = int(players_time[player])
                if goal < pt or end_of_game - goal < pt:
                    if player in home_players_played:
                        player_in_goals[player][1] += 1
                    elif player in away_players_played:
                        player_in_goals[player][2] += 1

    if len(away_goals_sorted):
        for goal in away_goals_sorted:
            for player in players_time:
                pt = int(players_time[player])
                if goal < pt or end_of_game - goal < pt:
                    if player in home_players_played:
                        player_in_goals[player][2] += 1
                    elif player in away_players_played:
                        player_in_goals[player][1] += 1

    return player_in_goals


def get_players_in_goals(game_id):

    url = 'http://www.espn.com.ar/futbol/comentario?juegoId=' + str(game_id)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    players_html = soup.find_all("span", {"class": "name"})
    subs_times_html = soup.find_all("span",
                                    {"data-event-type": "substitution"})
    end_of_game_html = soup.find_all("li", {"data-time": "FT"})
    subs_html = soup.find_all("span")
    red_times_html = soup.find_all("span", {"data-event-type": "red-card"})
    red_html = soup.find_all("div", {"class": "detail"})

    teams = get_team_names(game_id)
    if teams is None:
        return None
    home_team, away_team = teams

    players = get_players(players_html)
    if players is None:
        return None
    home_players, away_players = players
    home_goals_sorted, away_goals_sorted = get_game_goals(game_id)

    end_of_game = get_end_of_game(end_of_game_html)
    subs = get_subs(subs_html, subs_times_html)
    home_subs, away_subs = get_subs_per_team(subs, home_players, away_players)
    home_players_played, away_players_played = get_players_that_played(
        home_players, away_players, home_subs, away_subs)

    red_cards = get_red_cards(red_html, red_times_html)

    players_time = time_per_player(home_players_played, away_players_played,
                                   end_of_game, subs, red_cards)
    player_in_goals = player_in_goal(
        players_time, home_players_played, away_players_played, home_team,
        away_team, home_goals_sorted, away_goals_sorted, end_of_game)
    team_total_played = total_team_played(end_of_game, home_team, away_team)

    team_goal_difference = {}
    team_goal_difference[home_team] = [
        len(home_goals_sorted), len(away_goals_sorted)
    ]
    team_goal_difference[away_team] = [
        len(away_goals_sorted), len(home_goals_sorted)
    ]

    return player_in_goals, team_total_played, team_goal_difference


def get_players_data(games_id):

    total_players_goals = {}
    total_team_data = {}
    for game, day in games_id:
        print(game)
        result = get_players_in_goals(game)
        if result is not None:
            player_data, team_time, team_goal_difference = result
            for team in team_time.keys():
                if team in total_team_data:
                    total_team_data[team][0] += team_time[team]
                    total_team_data[team][1] += team_goal_difference[team][0]
                    total_team_data[team][2] += team_goal_difference[team][1]
                else:
                    total_team_data[team] = [
                        team_time[team], team_goal_difference[team][0],
                        team_goal_difference[team][1]
                    ]
            for player in player_data.keys():
                if player in total_players_goals.keys():
                    total_players_goals[player][1] += player_data[player][1]
                    total_players_goals[player][2] += player_data[player][2]
                    total_players_goals[player][3] += player_data[player][3]
                else:
                    total_players_goals[player] = player_data[player]
    return total_players_goals, total_team_data


def get_final_dict(d1, d2):

    for player in d1.keys():
        for team in d2.keys():
            if d1[player][0] == team:
                d1[player].append(d2[team][0] - d1[player][3])
                d1[player].append(d2[team][1])
                d1[player].append(d2[team][2])

    return d1


def dict_to_list(d):

    dictlist = []
    for key, value in d.items():
        temp = [
            key, value[0], value[1], value[2],
            value[3], value[4], value[5], value[6]
        ]
        dictlist.append(temp)

    return dictlist


def get_calculations(df):

    df['team_goals'] = df['team_goals_for'] - df['goals_for']
    df['ag_team_goals'] = df['team_goals_against'] - df['goals_against']

    df['90m_player_goals'] = 90 * \
        df['goals_for'] / df['minutes_played']

    df['ag_90m_player_goals'] = 90 * \
        df['goals_against'] / df['minutes_played']

    df['90m_team_goals'] = 90 * \
        df['team_goals'] / df['minutes_benched']

    df['ag_90m_team_goals'] = 90 * \
        df['ag_team_goals'] / df['minutes_benched']

    df = df.fillna(0)

    return df


def main(start_date, end_date, competition, competitions):

    comp = competitions[competition]
    games_id = get_games_id(start_date, end_date, comp)
    total_players_data, total_team_data = get_players_data(games_id)

    total_data = get_final_dict(total_players_data, total_team_data)
    players_data = dict_to_list(total_data)

    cols = [
        'player', 'team', 'goals_for', 'goals_against', 'minutes_played',
        'minutes_benched', 'team_goals_for', 'team_goals_against'
    ]

    df = pd.DataFrame(players_data, columns=cols)

    final_df = get_calculations(df)

    path = 'data/player_in_goals'
    os.makedirs(path, exist_ok=True)
    file_name = '{}/players_data_{}_{}.csv'.format(path, start_date, end_date)

    final_df.to_csv(file_name, index=False)


if __name__ == '__main__':

    main(START_DATE, END_DATE, COMPETITION, COMPETITION_DICT)
