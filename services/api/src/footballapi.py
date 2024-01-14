from datetime import datetime, timedelta
import requests
from pydantic import BaseModel
from collections import defaultdict
import pandas as pd

from src.config import settings

class GameInfo(BaseModel):
    Home: str
    Away: str
    Ground: str

def make_request():
    s = requests.Session()
    response = s.get(
        settings.footbalapi_url,
        headers=settings.headers,
    )
    data = response.json()['content']

    return data

def get_dataframe():
    r = make_request()
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

def get_games():
    df = get_dataframe()
    df = df[['gameDate', 'teams_team_1_name', 'teams_team_2_name', 'ground_name']]
    df.columns = ['gameDate', 'Home', 'Away', 'Ground']
    return df

def get_games_today():
    df = get_games()
    today = datetime.now().date()
    df = df[df['gameDate'].dt.date == today].drop('gameDate', axis=1)

    return df

def get_games_tomorrow():
    df = get_games()
    tomorrow = datetime.now().date() + timedelta(days=1)
    df = df[df['gameDate'].dt.date == tomorrow].drop('gameDate', axis=1)

    return df

def get_game_by_limit(n: int):
    df = get_games()
    df = df.iloc[:n, :].drop('gameDate', axis=1)
    df.reset_index(drop=True, inplace=True)

    return df
