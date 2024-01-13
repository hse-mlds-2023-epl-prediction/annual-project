from datetime import datetime, timedelta

import requests
from collections import defaultdict
import pandas as pd
from cfg import headers

def get_data():
    s = requests.Session()
    response = s.get(
        'https://footballapi.pulselive.com/football/fixtures?comps=1&teams=1,2,127,130,131,43,4,6,7,34,10,163,11,12,23,15,18,21,25,38&compSeasons=578&page=0&pageSize=12&sort=asc&statuses=U,L&altIds=true',
        headers=headers,
    )
    data = response.json()['content']
    return data


def resp():
    r = get_data()
    games = defaultdict(list)
    for game in r:
        games['gameweek_gameweek'].append(game['gameweek']['gameweek'])
        games['gameweek_compSeason_label'].append(game['gameweek']['compSeason']['label'][:4])
        games['gameDate'].append(game['provisionalKickoff']['label'])
        games['teams_team_1_name'].append(game['teams'][0]['team']['name'])
        games['teams_team_2_name'].append(game['teams'][1]['team']['name'])
        games['ground_name'].append(game['ground']['name'])

    df = pd.DataFrame(games)

    df['gameDate'] = df['gameDate'].apply(lambda x: ' '.join(x.replace(',', '').split()[1:4][::-1]))
    df['gameDate'] = pd.to_datetime(df['gameDate'], format='%Y %b %d')

    return df

def return_game():
    df = resp()
    df = df[['gameDate', 'teams_team_1_name', 'teams_team_2_name', 'ground_name']]
    df.columns = ['gameDate', 'Home', 'Away', 'Ground']
    return df

def game_today():
    df = return_game()
    today = datetime.now().date()
    df = df[df['gameDate'].dt.date == today].drop('gameDate', axis=1)

    return df

def game_tomorrow():
    df = return_game()
    tomorrow = datetime.now().date() + timedelta(days=1)
    df = df[df['gameDate'].dt.date == tomorrow].drop('gameDate', axis=1)

    return df
