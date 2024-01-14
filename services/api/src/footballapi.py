from datetime import datetime, timedelta


import requests
from pydantic import BaseModel
from collections import defaultdict
import pandas as pd
from cfg import headers
import numpy as np

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

def prepare(df):
    df_mean = pd.read_csv('../../../ML/official/prepared_data/data/df_mean.csv')
    df_lag = pd.read_csv('../../../ML/official/prepared_data/data//df_lag.csv')

    df = df.merge(df_mean, left_on='teams_team_1_name', right_on='club_name')
    df = df.merge(df_mean, left_on='teams_team_2_name', right_on='club_name', suffixes=('_team_1', '_team_2'))
    df['gameweek_compSeason_label'] = df['gameweek_compSeason_label'].astype('int')

    df = pd.merge(df, df_lag, left_on=['teams_team_1_name', 'gameweek_compSeason_label'], right_on=['club_name', 'season'], how='left')
    df = pd.merge(df, df_lag, left_on=['teams_team_2_name', 'gameweek_compSeason_label'], right_on=['club_name', 'season'], how='left', suffixes=('_lag_team1', '_lag_team2'))

    df.drop(['season_lag_team2', 'season_lag_team1', 'club_name_lag_team1', 'club_name_lag_team2', 'gameDate'], axis=1, inplace=True)

    import pickle
    with open('../../../ML/official/catboost/pickle/catboost.pickle', 'rb') as f:
        model = pickle.load(f)

    with open('../../../ML/official/catboost/pickle/name_cols.pickle', 'rb') as f:
        name_cols = pickle.load(f)

    df = df[name_cols]
    df['gameweek_gameweek'] = df['gameweek_gameweek'].astype('int')

    return model.predict(df), model.predict_proba(df)



def game_tomorrow_predict():
    df = resp()
    tomorrow = datetime.now().date() + timedelta(days=1)

    df = df[df['gameDate'].dt.date == tomorrow]

    predict, proba = prepare(df)
    df = game_tomorrow()
    df['predict'] = predict
    df['proba'] = np.max(proba, axis=1, keepdims=True)

    return df


def game_today_predict():
    df = resp()
    today = datetime.now().date()

    df = df[df['gameDate'].dt.date == today]

    predict, proba = prepare(df)
    df = game_today()
    df['predict'] = predict
    df['proba'] = np.max(proba, axis=1, keepdims=True)

    return df
def get_game_by_limit(n: int):
    df = get_games()
    df = df.iloc[:n, :].drop('gameDate', axis=1)
    df.reset_index(drop=True, inplace=True)

    return df
