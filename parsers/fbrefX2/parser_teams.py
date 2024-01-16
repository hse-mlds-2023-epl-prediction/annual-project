
# Все сезоны
# https://fbref.com/en/comps/9/history/Premier-League-Seasons

# Конкретный сезон
# https://fbref.com/en/comps/9/2010-2011/2010-2011-Premier-League-Stats

# Конкретная команда + игроки
# https://fbref.com/en/squads/19538871/2010-2011/Manchester-United-Stats

# Все матчи конкретной команды в конкретном сезоне
# https://fbref.com/en/squads/19538871/2010-2011/matchlogs/c9/schedule/Manchester-United-Scores-and-Fixtures-Premier-League
# Конкретный матч
# https://fbref.com/en/matches/08d4f4e2/Manchester-United-Newcastle-United-August-16-2010-Premier-League
import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import re
import random
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(current_dir, 'saved_page.html')


def deleteEmpty(t):
    text_without_empty_lines = '\n'.join(
        line for line in t.splitlines() if line.strip())
    text_without_spaces = re.sub(r'\s', '', text_without_empty_lines)
    return text_without_spaces


def extract_id_from_player(url):
    pattern = r'/en/players/([a-zA-Z0-9-]+)'

    match = re.search(pattern, url)

    return match.group(1) if match else None


def extract_id_from_team(url):
    pattern = r'/en/squads/([a-zA-Z0-9-]+)'

    match = re.search(pattern, url)

    return match.group(1) if match else None


def extract_team_name(url):
    segments = url.split('/')
    team_name_part = segments[-2] if segments[-1] == "" else segments[-1]
    team_name = team_name_part.split('-')
    team_name.pop()

    return '-'.join(team_name)


dfs = []

years = ['2013-2014', '2014-2015', '2015-2016', '2016-2017', '2017-2018',
         '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023']

for index, year in enumerate(years):
    url = f'https://fbref.com/en/comps/9/{year}/{year}-Premier-League-Stats'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table_with_stats = soup.find('table', class_='stats_table')
    teams = table_with_stats.find('tbody').find_all('tr')
    seasonRank = []
    team = []
    games = []
    wins = []
    ties = []
    losses = []
    goalScored = []
    goalAgainst = []
    goalDiff = []
    points = []
    pointsAVG = []
    attendanceHomePerGame = []
    topTeamScorer = []
    topTeamGoals = []
    teamId = []
    try:
        for team_info in teams:
            seasonRank.append(deleteEmpty(team_info.find('th').text)
                              if team_info.find('th').text else pd.NaT)
            team.append(extract_team_name(team_info.find('td').find('a')['href'])
                        if team_info.find('td').find('a')['href'] else pd.NaT)
            games.append(deleteEmpty(team_info.find_all('td')[
                1].text) if team_info.find_all('td')[1].text else pd.NaT)
            wins.append(deleteEmpty(team_info.find_all('td')[
                        2].text) if team_info.find_all('td')[2].text else pd.NaT)
            ties.append(deleteEmpty(team_info.find_all('td')[
                        3].text) if team_info.find_all('td')[3].text else pd.NaT)
            losses.append(deleteEmpty(team_info.find_all('td')[
                4].text) if team_info.find_all('td')[4].text else pd.NaT)
            goalScored.append(deleteEmpty(team_info.find_all(
                'td')[5].text) if team_info.find_all('td')[5].text else pd.NaT)
            goalAgainst.append(deleteEmpty(team_info.find_all(
                'td')[6].text) if team_info.find_all('td')[6].text else pd.NaT)
            goalDiff.append(deleteEmpty(team_info.find_all(
                'td')[7].text) if team_info.find_all('td')[7].text else pd.NaT)
            points.append(deleteEmpty(team_info.find_all('td')[
                8].text) if team_info.find_all('td')[8].text else pd.NaT)
            pointsAVG.append(deleteEmpty(team_info.find_all(
                'td')[9].text) if team_info.find_all('td')[9].text else pd.NaT)
            teamId.append(extract_id_from_team(
                team_info.find('td').find('a')['href']) if team_info.find('td').find('a')['href'] else pd.NaT)
            if index >= 4:
                attendanceHomePerGame.append(
                    deleteEmpty(team_info.find_all('td')[14].text) if team_info.find_all('td')[14].text else pd.NaT)
                topTeamScorer.append(extract_id_from_player(
                    team_info.find_all('td')[15].find('a')['href']) if team_info.find_all('td')[15].find('a') else pd.NaT)
                topTeamGoals.append(deleteEmpty(
                    team_info.find_all('td')[15].find('span').text) if team_info.find_all('td')[15].find('span') else pd.NaT)
            else:
                attendanceHomePerGame.append(
                    deleteEmpty(team_info.find_all('td')[10].text) if team_info.find_all('td')[10].text else pd.NaT)
                topTeamScorer.append(extract_id_from_player(
                    team_info.find_all('td')[11].find('a')['href']) if team_info.find_all('td')[11].find('a') else pd.NaT)
                topTeamGoals.append(deleteEmpty(
                    team_info.find_all('td')[11].find('span').text) if team_info.find_all('td')[11].find('span') else pd.NaT)

    except Exception as e:
        print(team_info)
    data = {
        'TeamId': teamId,
        'SeasonRank': seasonRank,
        'Team': team,
        'Games': games,
        'Wins': wins,
        'Ties': ties,
        'Losses': losses,
        'GoalScored': goalScored,
        'GoalAgainst': goalAgainst,
        'GoalDiff': goalDiff,
        'Points': points,
        'PointsAVG': pointsAVG,
        'AttendanceHomePerGame': attendanceHomePerGame,
        'TopTeamScorer': topTeamScorer,
        'TopTeamGoals': topTeamGoals,
        'Season': year
    }

    df_additional = pd.DataFrame(data)
    dfs.append(df_additional)
    print(year)
    random_delay = random.uniform(3, 5)
    time.sleep(random_delay)

df = pd.concat(dfs, ignore_index=True)
file_path = os.path.join(current_dir, 'teams2.csv')
df.to_csv(file_path, index=False)
