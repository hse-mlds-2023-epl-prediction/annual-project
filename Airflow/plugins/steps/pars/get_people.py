# dags/get_people.py
import pandas as pd
import requests
from time import sleep
from steps.src.features import col_club_stat
from steps.src.config import uri, headers, conn_id, num_seasons
from steps.src.app import flatten_dict, list_to_dict, pars_dictline, pars_dictfeature
from steps.src.model_table import table_games
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Column, String, Boolean, Integer, inspect, create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from collections import defaultdict
import base64
import os
import pickle


load_dotenv()
DBNAME = os.getenv('DBNAME')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')


def get_id_season(**kwargs):
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)

    Session = sessionmaker(bind=engine)
    session = Session()
    # Выполнение запроса для получения всех id из таблицы seasons
    result = session.execute(text("SELECT id FROM seasons"))
    season_ids_list = [int(row[0]) for row in result.fetchall()][:num_seasons]
    print(*season_ids_list)
    session.close()
    kwargs['ti'].xcom_push(
        key='season_ids_list', value=season_ids_list)


def get_club_id(**kwargs):
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)

    Session = sessionmaker(bind=engine)
    session = Session()

    result = session.execute(text("SELECT DISTINCT id FROM club_basic"))
    club_ids_list = [int(row[0]) for row in result.fetchall()]
    session.close()

    kwargs['ti'].xcom_push(
        key='club_ids_list', value=club_ids_list)


def parser(**kwargs):
    ti = kwargs['ti']
    season_ids_list = kwargs['ti'].xcom_pull(
        key='season_ids_list', task_ids='get_id_season')
    club_id = kwargs['ti'].xcom_pull(
        key='club_ids_list', task_ids='get_club_id')
    s = requests.Session()
    
    players, goalkippers, officials = defaultdict(list), defaultdict(list), defaultdict(list)
    
    for id_s in list(season_ids_list):
        for id_t in club_id:

            params = {
                    'pageSize': '30',
                    'compSeasons': id_s,
                    'altIds': 'true',
                    'page': '0',
                    'type': 'player',
                    }   

            response = s.get(
            f'https://footballapi.pulselive.com/football/teams/{id_t}/compseasons/{id_s}/staff',
            params=params,
            headers=headers,
            )

            if response.status_code != 200:
                print('response error')
                continue

            season = response.json()['compSeason']['label'].split('/')[0]
            team = response.json()['team']['club']['name']


            for player in response.json()['players']:
                appearances = player['appearances']

                if appearances == 0:
                    continue
                player_id = player.get('playerId', None)
                position = player['info']['position'] if 'position' in player['info'] else None

                if position != 'G':                
                    
                    players['season'].append(season)
                    players['team'].append(team)
                    players['player_id'].append(player_id)
                    players['position'].append(position)
                    players['height'].append(player.get('height', None))
                    players['weight'].append(player.get('weight', None))
                    players['appearances'].append(appearances)
                    players['name'].append(player['name']['display'])
                    players['goals'].append(player.get('goals', None))
                    players['assists'].append(player.get('assists', None))
                    players['tackles'].append(player.get('tackles', None))
                    players['shots'].append(player.get('shots', None))
                    players['keyPasses'].append(player.get('keyPasses', None))
                    players['cleanSheets'].append(player.get('cleanSheets', None))

                if position == 'G': 
                    goalkippers['season'].append(season)
                    goalkippers['team'].append(team)
                    goalkippers['player_id'].append(player_id)
                    goalkippers['position'].append(position)
                    goalkippers['height'].append(player.get('height', None))
                    goalkippers['weight'].append(player.get('weight', None))
                    goalkippers['appearances'].append(appearances)
                    goalkippers['name'].append(player['name']['display'])
                    goalkippers['cleanSheets'].append(player.get('cleanSheets', None))
                    goalkippers['saves'].append(player.get('saves', None))
                    goalkippers['goalsConceded'].append(player.get('goalsConceded', None))

            for official in response.json().get('officials', None):
                role = official.get('role', None)
                name = official['name']['display']
                age = int(official['age'].split()[0]) if 'age' in official else None

                officials['season'].append(season)
                officials['team'].append(team)
                officials['name'].append(name)
                officials['role'].append(role)
                officials['age'].append(age)

    players = pd.DataFrame(players)
    df_pickle_players = pickle.dumps(players)
    df_base64_players = base64.b64encode(df_pickle_players).decode('utf-8')
    kwargs['ti'].xcom_push(key='players', value=df_base64_players)

    goalkippers = pd.DataFrame(goalkippers)
    df_pickle_goalkippers = pickle.dumps(goalkippers)
    df_base64_goalkippers = base64.b64encode(df_pickle_goalkippers).decode('utf-8')
    kwargs['ti'].xcom_push(key='goalkippers', value=df_base64_goalkippers)

    officials = pd.DataFrame(officials)
 


def load_players(**kwargs):
    ti = kwargs['ti']
    df_base64 = ti.xcom_pull(key='players', task_ids='parser')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)
    print(df)
    hook = PostgresHook(conn_id)

    engine = hook.get_sqlalchemy_engine()
    df.to_sql('players', engine, if_exists='replace', index=False)


def load_goalkippers(**kwargs):
    ti = kwargs['ti']
    df_base64 = ti.xcom_pull(key='goalkippers', task_ids='parser')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)
    print(df)
    hook = PostgresHook(conn_id)

    engine = hook.get_sqlalchemy_engine()
    df.to_sql('goalkippers', engine, if_exists='replace', index=False)


def load_officials(**kwargs):
    ti = kwargs['ti']
    df_base64 = ti.xcom_pull(key='officials', task_ids='parser')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)
    print(df)
    hook = PostgresHook(conn_id)

    engine = hook.get_sqlalchemy_engine()
    df.to_sql('officials', engine, if_exists='replace', index=False)