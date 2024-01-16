
# Все сезоны
# https://fbref.com/en/comps/9/history/Premier-League-Seasons

# Конкретный сезон
# https://fbref.com/en/comps/9/2010-2011/2010-2011-Premier-League-Stats

# Конкретная команда + игроки
# https://fbref.com/en/squads/19538871/2010-2011/Manchester-United-Stats


# 2017-2018

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
file_path = os.path.join(current_dir, 'saved_page.html')


with open(file_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

data = pd.read_csv('./teams2.csv')


ids = data['TeamId'].unique()

# table_with_stats = soup.find('table', class_='stats_table')
# players = table_with_stats.find('tbody').find_all('tr')

# print(players[0])


def deleteEmpty(t):
    text_without_empty_lines = '\n'.join(
        line for line in t.splitlines() if line.strip())
    text_without_spaces = re.sub(r'\s', '', text_without_empty_lines)
    return text_without_spaces


def extract_id_from_player(url):
    pattern = r'/en/players/([a-zA-Z0-9-]+)'

    match = re.search(pattern, url)

    return match.group(1) if match else None


def extract_name_from_country(url):
    pattern = r'/en/country/([a-zA-Z0-9-]+)'

    match = re.search(pattern, url)

    return match.group(1) if match else None


dfs = []

years = ['2013-2014', '2014-2015', '2015-2016', '2016-2017', '2017-2018',
         '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023']

for index, year in enumerate(years):
    for id in ids:
        teamName = data.loc[data['TeamId'] == id].iloc[0]['Team']
        if data[(data['Season'] == year) & (data['TeamId'] == id)].shape[0] < 1:
            print(teamName, year, 'error')
            continue
        url = f'''https://fbref.com/en/squads/{
            id}/{year}/{teamName}-Stats'''
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        championat = soup.find('div', id_='meta')
        table_with_stats = soup.find('table', class_='stats_table')
        teams = table_with_stats.find('tbody').find_all('tr')
        name = []
        playerId = []
        nation = []
        position = []
        age = []
        mp = []
        starts = []
        mins = []
        mins90 = []
        goals = []
        assists = []
        penaltyMade = []
        penaltyAttempt = []
        yellowCard = []
        redCard = []
        teamId = []
        xG = []
        xAG = []
        progressivePasses = []
        progressiveCarriers = []
        try:
            for info in teams:
                name.append(deleteEmpty(info.find('th').find('a').text)
                            if info.find('th').find('a').text else pd.NaT)
                playerId.append(extract_id_from_player(info.find('th').find('a')['href'])
                                if info.find('th').find('a')['href'] else pd.NaT)
                nation.append(extract_name_from_country(info.find('td').find('a')['href'])
                              if info.find('td').find('a')['href'] else pd.NaT)
                position.append(deleteEmpty(info.find_all(
                    'td')[1].text) if info.find_all('td')[1].text else pd.NaT)
                age.append(deleteEmpty(info.find_all('td')[2].text) if info.find_all(
                    'td')[2].text else pd.NaT)
                mp.append(deleteEmpty(info.find_all('td')[3].text) if info.find_all(
                    'td')[3].text else pd.NaT)
                starts.append(deleteEmpty(info.find_all('td')[
                              4].text) if info.find_all('td')[4].text else pd.NaT)
                mins.append(deleteEmpty(info.find_all('td')[
                            5].text) if info.find_all('td')[5].text else pd.NaT)
                mins90.append(deleteEmpty(info.find_all('td')[
                              6].text) if info.find_all('td')[6].text else pd.NaT)
                goals.append(deleteEmpty(info.find_all(
                    'td')[7].text) if info.find_all('td')[7].text else pd.NaT)
                assists.append(deleteEmpty(info.find_all('td')[
                               8].text) if info.find_all('td')[8].text else pd.NaT)
                penaltyMade.append(deleteEmpty(info.find_all(
                    'td')[11].text) if info.find_all('td')[11].text else pd.NaT)
                penaltyAttempt.append(deleteEmpty(info.find_all(
                    'td')[12].text) if info.find_all('td')[12].text else pd.NaT)
                yellowCard.append(deleteEmpty(info.find_all(
                    'td')[13].text) if info.find_all('td')[13].text else pd.NaT)
                redCard.append(deleteEmpty(info.find_all('td')[
                               14].text) if info.find_all('td')[14].text else pd.NaT)

                teamId.append(id)
                if index >= 4:
                    xG.append(deleteEmpty(info.find_all('td')[15].text) if info.find_all(
                        'td')[15].text else pd.NaT)
                    xAG.append(deleteEmpty(info.find_all('td')[17].text) if info.find_all(
                        'td')[17].text else pd.NaT)
                    progressivePasses.append(deleteEmpty(info.find_all(
                        'td')[20].text) if info.find_all('td')[20].text else pd.NaT)
                    progressiveCarriers.append(deleteEmpty(info.find_all(
                        'td')[19].text) if info.find_all('td')[19].text else pd.NaT)
                else:
                    xG.append(pd.NaT)
                    xAG.append(pd.NaT)
                    progressivePasses.append(pd.NaT)
                    progressiveCarriers.append(pd.NaT)

        except Exception as e:
            print(info)
            df = pd.concat(dfs, ignore_index=True)
            file_path = os.path.join(current_dir, 'players.csv')
            df.to_csv(file_path, index=False)
        dataPlayer = {
            'Name': name,
            'PlayerID': playerId,
            'Nation': nation,
            'Position': position,
            'Age': age,
            'MathesPlayed': mp,
            'Starts': starts,
            'Minutes': mins,
            'MinutesDivided90': mins90,
            'Goals': goals,
            'Assists': assists,
            'PenatlyMade': penaltyMade,
            'PenaltyAttempt': penaltyAttempt,
            'YellowCards': yellowCard,
            'RedCards': redCard,
            'xG': xG,
            'xAG': xAG,
            'ProgressivePasses': progressivePasses,
            'ProgressiveCarriers': progressiveCarriers,
            'TeamId': teamId,
        }

        df_additional = pd.DataFrame(dataPlayer)
        dfs.append(df_additional)
        print(year, teamName)
        random_delay = random.uniform(3, 5)
        time.sleep(random_delay)

df = pd.concat(dfs, ignore_index=True)
file_path = os.path.join(current_dir, 'players.csv')
df.to_csv(file_path, index=False)
