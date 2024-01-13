
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


import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import re
import random
import time
import asyncio
import aiohttp
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'saved_page.html')

# до 2016-2017 стата уменьшеная


with open(file_path, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

data = pd.read_csv('./teams2.csv')

ids = data['TeamId'].unique()

# table_with_stats = soup.find('table', class_='stats_table')
# players = table_with_stats.find('tbody').find_all('tr')

# print(players[0])
month_names = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}


def deleteEmpty(t):
    text_without_empty_lines = '\n'.join(
        line for line in t.splitlines() if line.strip())
    text_without_spaces = re.sub(r'\s', '', text_without_empty_lines)
    return text_without_spaces


def extract_id_from_team(url):
    pattern = r'/en/squads/([a-zA-Z0-9-]+)'

    match = re.search(pattern, url)

    return match.group(1) if match else None


def extract_id_from_player(url):
    pattern = r'/en/players/([a-zA-Z0-9-]+)'

    match = re.search(pattern, url)

    return match.group(1) if match else None


def extract_name_from_country(url):
    pattern = r'/en/country/([a-zA-Z0-9-]+)'

    match = re.search(pattern, url)

    return match.group(1) if match else None


def get_date(d):
    arr = d.split(' ')
    print(arr)
    return datetime.datetime(int(arr[3]), month_names[arr[1]], int(arr[2][:-1])).timestamp()


async def main():

    async with aiohttp.ClientSession() as session:

        pokemon_url = 'https://fbref.com/en/matches/0e815975/Arsenal-Liverpool-August-14-2016-Premier-League'
        async with session.get(pokemon_url) as resp:
            pokemon = await resp.read()
            soup = BeautifulSoup(pokemon, 'html.parser')
            box = soup.find('div', class_='scorebox')
            homeTeamId = extract_id_from_team(
                box.find('div').find('div').find('strong').find('a')['href'])
            homeTeamScore = box.find('div').find(
                'div', class_='scores').find('div').text
            homeTeamCaptain = extract_id_from_player(box.find('div').find_all(
                'div', class_='datapoint')[1].find('a')['href'])
            awayTeamId = extract_id_from_team(
                box.find_all('div')[9].find('div').find('strong').find('a')['href'])
            awayTeamScore = box.find_all('div')[9].find(
                'div', class_='scores').find('div').text
            awayTeamCaptain = extract_id_from_player(box.find_all('div')[9].find_all(
                'div', class_='datapoint')[1].find('a')['href'])

            date = get_date(box.find('div', class_='scorebox_meta').find(
                'div').find('strong').text)
            attendance = float(box.find('div', class_='scorebox_meta').find_all(
                'div')[4].find_all('small')[1].text.replace(',', '.'))
            location = box.find('div', class_='scorebox_meta').find_all(
                'div')[5].find_all('small')[1].text
            eventsHomeTeam = soup.find(id='events_wrap').find(
                'div').find_all('div', class_='event a')
            print(eventsHomeTeam[0].find('div').text)
asyncio.run(main())
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

            match_date = scorebox_meta_venuetime.attrs['data-venue-date']
            match_time = scorebox_meta_venuetime.attrs['data-venue-time']

            premier_league_link = scorebox_meta.find('a', string=re.compile('Premier League'))
            match_week = premier_league_link.next_sibling.strip().split(' ')[1].replace(')', '')

            attendance = scorebox_meta.find('small', string=re.compile('Attendance'))

            if attendance:
                attendance = attendance.parent.next_sibling.next_sibling.get_text()

            venue_data = scorebox_meta.find('small', string=re.compile('Venue'))

            if venue_data:
                venue_data = venue_data.parent.next_sibling.next_sibling.get_text().split(',')
                venue_data = list(map(lambda venue_str: venue_str.strip(), venue_data))
            else:
                venue_data = [None, None]

            referee = scorebox_meta.find('small', string=re.compile('Officials'))

            if referee:
                referee = referee.parent.next_sibling.next_sibling.select_one('span').get_text().replace('\xa0', ' ')

            team_stats = soup.select_one('#team_stats')
            home_team_stats_info = get_team_stats_info(team_stats)
            away_team_stats_info = get_team_stats_info(team_stats, False)

            team_stats_extra = soup.select_one('#team_stats_extra')
            home_team_extra_stats_info = get_team_extra_stats_info(team_stats_extra)
            away_team_extra_stats_info = get_team_extra_stats_info(team_stats_extra, False)

            fbref_id = url.split('/')[-2]

            home_team_score = home_team_scorebox_info['team_score']
            away_team_score = away_team_scorebox_info['team_score']

            data = {
                'fbref_match_id': fbref_id,
                'match_week': int(match_week.strip()),
                'match_date': match_date,
                'match_time': match_time,
                'home_team_score': home_team_score,
                'away_team_score': away_team_score,
                'venue': venue_data[0],
                'venue_city': venue_data[1],
                'attendance': attendance,
                'referee': referee,
                'home_team_possession_percent': home_team_stats_info['possession_percent'],
                'away_team_possession_percent': away_team_stats_info['possession_percent'],
                'home_team_passing_total_count': home_team_stats_info['passing_total_count'],
                'away_team_passing_total_count': away_team_stats_info['passing_total_count'],
                'home_team_passing_accuracy_count': home_team_stats_info['passing_accuracy_count'],
                'away_team_passing_accuracy_count': away_team_stats_info['passing_accuracy_count'],
                'home_team_passing_accuracy_percent': home_team_stats_info['passing_accuracy_percent'],
                'away_team_passing_accuracy_percent': away_team_stats_info['passing_accuracy_percent'],
                'home_team_shots_on_target_percent': home_team_stats_info['shots_on_target_percent'],
                'away_team_shots_on_target_percent': away_team_stats_info['shots_on_target_percent'],
                'home_team_shots_on_target_count': home_team_stats_info['shots_on_target_count'],
                'away_team_shots_on_target_count': away_team_stats_info['shots_on_target_count'],
                'home_team_shots_total_count': home_team_stats_info['shots_total_count'],
                'away_team_shots_total_count': away_team_stats_info['shots_total_count'],
                'home_team_saves_percent': home_team_stats_info['saves_percent'],
                'away_team_saves_percent': away_team_stats_info['saves_percent'],
                'home_team_saves_count': home_team_stats_info['saves_count'],
                'away_team_saves_count': away_team_stats_info['saves_count'],
                'home_team_saves_attempt': home_team_stats_info['saves_attempt'],
                'away_team_saves_attempt': away_team_stats_info['saves_attempt'],
                'home_team_yellow_cards_count': home_team_stats_info['yellow_cards_count'],
                'away_team_yellow_cards_count': away_team_stats_info['yellow_cards_count'],
                'home_team_red_cards_count': home_team_stats_info['red_cards_count'],
                'away_team_red_cards_count': away_team_stats_info['red_cards_count'],
            }

        random_delay = random.uniform(3, 5)
        time.sleep(random_delay)

df = pd.concat(dfs, ignore_index=True)
file_path = os.path.join(current_dir, 'matches.csv')
df.to_csv(file_path, index=False)

