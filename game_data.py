import os

from datetime import timedelta

import requests
import pandas as pd

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from constants import COMPETITION, COMPETITION_DICT, END_DATE, START_DATE


def date_range(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield (start_date + timedelta(n)).strftime('%Y%m%d')


def get_games_id(start_date, end_date, comp):

    dates = [d for d in date_range(start_date, end_date)]
    games_id = []

    chrome_options = Options()
    chrome_options.add_argument('--dns-prefetch-disable')
    driver = Chrome(options=chrome_options)

    try:
        for day in dates:
            driver.get(
                'http://www.espn.com.ar/futbol/resultados/_/liga/{}/fecha/{}'.
                format(comp, day)
            )

            game_link_driver = driver.find_elements(
                By.CLASS_NAME, 'mobileScoreboardLink'
            )

            for game_driver in game_link_driver:
                game_id = game_driver.get_attribute('href')[46:53]
                games_id.append((game_id, day))
    finally:
        driver.quit()

    return games_id


def get_score(html):

    if not len(html):
        return None

    contents = [p.contents[0] for p in html]
    score_string = (contents[0].strip())

    if not len(score_string):
        return None

    score = int(score_string)
    return score


def get_possession_values(possession_html):

    if not len(possession_html):
        return [0, 0]

    for item in possession_html:
        possession_data = item.find_all('span', {"class": "chartValue"})

    pos_contents = [p.contents[0] for p in possession_data]

    pos_percentage = [int(item[:-1]) for item in pos_contents]

    return pos_percentage


def get_teams(teams_html):

    if not teams_html:
        return None

    team_names = [tag.text.strip() for tag in teams_html]

    return team_names


def split_shots(shots):
    shots = shots.split()
    total_shots = int(shots[0])
    sot = int(shots[1][1:-1])
    return total_shots, sot


def get_shots(shots_html):

    if not len(shots_html):
        return None

    for item in shots_html:
        shots_data = item.find_all('span', {"class": "number"})

    shots_contents = [s.contents[0] for s in shots_data]

    home_shots, home_sot = split_shots(shots_contents[0])
    away_shots, away_sot = split_shots(shots_contents[1])

    shots_total = [home_shots, away_shots]
    shots_ongoal = [home_sot, away_sot]

    return [shots_total, shots_ongoal]


def get_fouls(fouls_html):

    fouls_contents = [p.contents[0] for p in fouls_html]

    fouls = [int(foul) for foul in fouls_contents]

    return fouls


def get_cards(cards_html):

    cards_content = [p.contents[0] for p in cards_html]

    cards = [int(i) for i in cards_content]

    return cards


def get_penalty_shooters(summary_html):

    if not len(summary_html):
        return None

    s_contents = [p.contents[0] for p in summary_html]

    if s_contents[0] == '\n':
        return None

    temp_contents = [i.strip() for i in s_contents]

    penalty_contents = [i for i in temp_contents if 'penalty' in i.lower()]

    shooters = []

    for item in penalty_contents:
        temp = item.split()
        shooters.append(temp[0] + ' ' + temp[1])

    return shooters


def get_players(players_html):

    if not len(players_html):
        return None

    pl_contents = [p.contents[0] for p in players_html]

    pl_contents = [i.strip() for i in pl_contents if len(i.strip()) > 0]

    home_players = [pl for pl in pl_contents[:18]]
    away_players = [pl for pl in pl_contents[18:]]

    return [home_players, away_players]


def penalty_attribution(shooters, home_players, away_players):

    home_penalties = 0
    away_penalties = 0

    for shooter in shooters:
        if shooter in home_players:
            home_penalties += 1
        elif shooter in away_players:
            away_penalties += 1

    return home_penalties, away_penalties


def get_penalties(game_id):

    url = 'http://www.espn.com.ar/futbol/partido?juegoId=' + str(game_id)

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    summary_html = soup.find_all("div", {"class": "detail"})
    players_html = soup.find_all("span", {"class": "name"})

    shooters = get_penalty_shooters(summary_html)
    players = get_players(players_html)

    if not players:
        return None

    home_players, away_players = players

    home_penalties, away_penalties = penalty_attribution(
        shooters, home_players, away_players
    )

    return [home_penalties, away_penalties]


def get_scorers(html):

    if not len(html):
        return None

    list_html = [tag.find_all('li') for tag in html]

    goal_scorers = []
    for content in list_html:
        goal_contents = [p.contents[0] for p in content]
        for scorer in goal_contents:
            goal_scorers.append(scorer.strip())

    return goal_scorers


def get_goal_minutes(html, goal_scorers, home_players, away_players):

    if not goal_scorers:
        return None

    minutes_html = [tag.find_all('span') for tag in html]

    minutes_scored_raw = []
    for content in minutes_html:
        minutes_contents = [p.contents[0] for p in content]
        for minute in minutes_contents:
            minutes_scored_raw.append(minute)

    goals_scored_raw = {}
    goals_scored = {}

    for i in range(len(goal_scorers)):
        goals_scored_raw[goal_scorers[i]] = minutes_scored_raw[i]

    # Own goals or goals in minutes 90'

    for key in goals_scored_raw.keys():
        if 'OG' in goals_scored_raw[key]:
            if key in home_players:
                goals_scored[away_players[0]] = goals_scored_raw[key]
            elif key in away_players:
                goals_scored[home_players[0]] = goals_scored_raw[key]
        elif '+' in goals_scored_raw[key]:
            index = goals_scored_raw[key].index('+')
            goals_scored[key] = str(
                int(goals_scored_raw[key][index - 3:index - 1]) +
                int(goals_scored_raw[key][index + 1])
            ) + "'"
        else:
            goals_scored[key] = goals_scored_raw[key]

    return goals_scored


def goal_attribution(goals_scored, home_players, away_players):

    home_goals_raw = []
    away_goals_raw = []

    if not goals_scored:
        return [], []

    home_goals_raw = [
        val for k, val in goals_scored.items() if k in home_players
    ]

    away_goals_raw = [
        val for k, val in goals_scored.items() if k in away_players
    ]

    home_goals = []
    away_goals = []

    for element in home_goals_raw:
        for i in range(len(element)):
            if element[i] == "'":
                if element[i - 2] == '(':
                    home_goals.append(int(element[i - 1]))
                else:
                    home_goals.append(int(element[i - 2:i]))

    for element in away_goals_raw:
        for i in range(len(element)):
            if element[i] == "'":
                if element[i - 2] == '(':
                    away_goals.append(int(element[i - 1]))
                else:
                    away_goals.append(int(element[i - 2:i]))

    home_goals_sorted = sorted(home_goals)
    away_goals_sorted = sorted(away_goals)

    return home_goals_sorted, away_goals_sorted


def first_goal_team(home_goals, away_goals):

    if not len(home_goals):
        first_goal = 'away'
    elif not len(away_goals):
        first_goal = 'home'
    elif home_goals[0] < away_goals[0]:
        first_goal = 'home'
    else:
        first_goal = 'away'

    return first_goal


def two_zero_team(home_goals, away_goals, top_minutes):

    if len(home_goals) < 2 and len(away_goals) < 2:
        return None
    elif not len(home_goals):
        if away_goals[1] < top_minutes:
            two_zero = 'away'
        else:
            return None
    elif not len(away_goals):
        if home_goals[1] < top_minutes:
            two_zero = 'home'
        else:
            return None
    elif len(home_goals) == 1:
        if away_goals[1] < home_goals[0] and away_goals[1] < top_minutes:
            two_zero = 'away'
        else:
            return None
    elif len(away_goals) == 1:
        if home_goals[1] < away_goals[0] and home_goals[1] < top_minutes:
            two_zero = 'home'
        else:
            return None
    else:
        if away_goals[1] < home_goals[0] and away_goals[1] < top_minutes:
            two_zero = 'away'
        elif home_goals[1] < away_goals[0] and home_goals[1] < top_minutes:
            two_zero = 'home'
        else:
            return None

    return two_zero


def get_game_goals(game_id):

    url = 'http://www.espn.com.ar/futbol/comentario?juegoId=' + str(game_id)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    players_html = soup.find_all("span", {"class": "name"})
    goals_html = soup.find_all("ul", {"data-event-type": "goal"})

    players = get_players(players_html)

    if not players:
        return None

    home_players, away_players = players

    goal_scorers = get_scorers(goals_html)
    goals_scored = get_goal_minutes(
        goals_html, goal_scorers, home_players, away_players
    )
    home_goals, away_goals = goal_attribution(
        goals_scored, home_players, away_players
    )

    return home_goals, away_goals


def get_game_data(game_id, day, two_zero_minutes=200):

    print(game_id)

    url = 'http://www.espn.com.ar/futbol/numeritos?juegoId=' + str(game_id)

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    home_html = soup.find_all("span", {"class": "score icon-font-after"})
    away_html = soup.find_all("span", {"class": "score icon-font-before"})
    possession_html = soup.find_all("div", {"class": "possession"})
    teams_html = soup.find_all("span", {"class": "abbrev"})
    shots_html = soup.find_all("div", {"class": "shots"})
    fouls_html = soup.find_all("td", {"data-stat": "foulsCommitted"})
    yellow_html = soup.find_all("td", {"data-stat": "yellowCards"})
    red_html = soup.find_all("td", {"data-stat": "redCards"})

    home_goals = get_score(home_html)
    away_goals = get_score(away_html)
    pos_percentage = get_possession_values(possession_html)
    teams = get_teams(teams_html)
    shots = get_shots(shots_html)
    fouls = get_fouls(fouls_html)
    yellow = get_cards(yellow_html)
    red = get_cards(red_html)
    goal_minutes = get_game_goals(game_id)

    if not teams or not shots:
        return None

    first_goal = first_goal_team(goal_minutes[0], goal_minutes[1])

    two_zero = two_zero_team(
        goal_minutes[0], goal_minutes[1], two_zero_minutes
    )

    if first_goal == 'home':
        first_goal = teams[0]
    elif first_goal == 'away':
        first_goal = teams[1]

    if two_zero == 'home':
        two_zero = teams[0]
    elif two_zero == 'away':
        two_zero = teams[1]

    game = [
        game_id, day, teams[0], teams[1], home_goals, away_goals, shots[0][0],
        shots[0][1], shots[1][0], shots[1][1], pos_percentage[0],
        pos_percentage[1], fouls[0], fouls[1], yellow[0], yellow[1], red[0],
        red[1], first_goal, two_zero
    ]

    return game


def get_home_points(df):
    if df['home_goals'] > df['away_goals']:
        return 3
    elif df['home_goals'] < df['away_goals']:
        return 0
    else:
        return 1


def get_away_points(df):
    if df['home_goals'] < df['away_goals']:
        return 3
    elif df['home_goals'] > df['away_goals']:
        return 0
    else:
        return 1


def run_game_data(games_id):
    list_of_games_data = []

    for game, day in games_id:
        game_data = get_game_data(game, day)
        if not game_data:
            continue
        hp = 0
        ap = 0
        penalties = get_penalties(game)
        if penalties:
            hp = penalties[0]
            ap = penalties[1]
            game_data.append(hp)
            game_data.append(ap)
        if game_data:
            list_of_games_data.append(game_data)

    return list_of_games_data


def main(start_date, end_date, competition, competitions):

    comp = competitions[competition]
    games_id = get_games_id(start_date, end_date, comp)
    list_of_games_data = run_game_data(games_id)

    df = pd.DataFrame(list_of_games_data)

    cols = [
        'game_id', 'date', 'home_name', 'away_name', 'home_goals',
        'away_goals', 'home_totalshots', 'away_totalshots', 'home_shotsgoal',
        'away_shotsgoal', 'home_possession', 'away_possession', 'home_fouls',
        'away_fouls', 'home_yellow', 'away_yellow', 'home_red', 'away_red',
        'first_goal', 'two_zero', 'home_penalties', 'away_penalties'
    ]
    df.columns = cols

    df['home_points'] = df.apply(get_home_points, axis=1)
    df['away_points'] = df.apply(get_away_points, axis=1)
    df['competition'] = competition

    path = os.path.join('data', 'game_data')
    os.makedirs(path, exist_ok=True)

    file_name = os.path.join(
        path, 'games_data_{}_{}.csv'.format(start_date, end_date)
    )

    df.to_csv(file_name, index=False)
    print("File saved to {}".format(file_name))


if __name__ == '__main__':

    main(START_DATE, END_DATE, COMPETITION, COMPETITION_DICT)
