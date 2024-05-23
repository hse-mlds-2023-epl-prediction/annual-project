import pandas as pd
import requests
from time import sleep
from steps.src.features import col_main
from steps.src.config import uri, headers, conn_id
from steps.src.app import flatten_dict, list_to_dict, pars_dictline, get_col_dict
from steps.src.model_table import table_games
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Column, String, Boolean, Integer, inspect, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
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
    Base = declarative_base()

    class Seasons(Base):
        __tablename__ = 'seasons'
        id = Column(Integer, primary_key=True)
        label = Column(String)

    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()
    # Выполнение запроса для получения всех id из таблицы seasons
    season_ids = session.query(Seasons.id).all()

    # Преобразование результата в список
    season_ids_list = [id_tuple[0] for id_tuple in season_ids]
    session.close()

    kwargs['ti'].xcom_push(key='season_ids_list', value=season_ids_list[:12])


def get_matches(**kwargs):
    ti = kwargs['ti']
    season_ids_list = kwargs['ti'].xcom_pull(
        key='season_ids_list', task_ids='get_id_step')
    
    season_ids_list = season_ids_list[-1:] # Для отладки / удалить / закоментить

    # Парсим основные данные матчи, включая id матчей
    params = {
        'comps': '1',
        'compSeasons': '578',
        'pageSize': '1000',
        'altIds': 'true',
        'sort': 'desc',
        'statuses': 'C'
    }
    df_games = pd.DataFrame()
    response = requests.get(uri['get_bases_games'],  headers=headers, params=params)
    col = get_col_dict(response.json()['content'])

    for season in season_ids_list:
        params['compSeasons'] = season
        response = requests.get(uri['get_bases_games'],  headers=headers, params=params)
        r = response.json()['content']
        value = pars_dictline(r, col)

        temp_df = pd.DataFrame(value, columns=col.values())
        df_games = pd.concat([df_games, temp_df], ignore_index=True)
        sleep(1)

    # Парсим статистику матчей    
    match_id = df_games['id'].astype(int)
    result = []
    s = requests.Session()
    count = 0
    for id in match_id:
        count += 1
        r = s.get(f'{uri["get_matches"]}/{str(id)}', headers=headers)

        if r.status_code != 200:
            print(f'match id:: {id}, RESPONSE: {r.status_code}')
            continue

        if len(r.text) == 0 or len(r.json()['entity']) == 0 or len(r.json()['data']) == 0:
            continue

        r = r.json()
        # change name team
        r['entity']['teams'][0]['team_1'] = r['entity']['teams'][0]['team']
        r['entity']['teams'][1]['team_2'] = r['entity']['teams'][1]['team']

        r['entity']['teams'][0]['score_1'] = r['entity']['teams'][0]['score']
        r['entity']['teams'][1]['score_2'] = r['entity']['teams'][1]['score']

        del r['entity']['teams'][0]['team']
        del r['entity']['teams'][1]['team']

        del r['entity']['teams'][0]['score']
        del r['entity']['teams'][1]['score']

        r['entity']['teams'] = flatten_dict(r['entity']['teams'][0]) | flatten_dict(r['entity']['teams'][1])

        main = flatten_dict(r['entity'])

        team_1_id = str(main['teams_team_1_id'])
        team_2_id = str(main['teams_team_2_id'])

        team_1_stat = r['data'][team_1_id]['M']
        team_2_stat = r['data'][team_2_id]['M']

        team_1_stat_dict = list_to_dict(team_1_stat, name_stat='name', value_stat='value', pref='team_1')
        team_2_stat_dict = list_to_dict(team_2_stat, name_stat='name', value_stat='value', pref='team_2')

        dict_stats = {'match_id': id, **flatten_dict(main), **team_1_stat_dict, **team_2_stat_dict}
        sleep(0.35)

        if count % 100 == 0:
            print(count)
        result.append(dict_stats)

    data = pars_dictline(result, col_main)
    df = pd.DataFrame(data, columns=col_main.values())
    df.to_csv('games.csv', index=False)

    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='df_pickle', value=df_base64)


def create_db(**kwargs):
    metadata, table = table_games()
    hook = PostgresHook(conn_id)
    engine = hook.get_sqlalchemy_engine()
    inspector = inspect(engine)

    if not inspect(engine).has_table(table.name):
        metadata.create_all(engine)

    if inspector.has_table(table.name):
        # Удаляем существующую таблицу
        table.drop(engine)
        print(f"Таблица '{table.name}' удалена.")
    # Загоняем в нижний регистр т.к. insert_rows не умеет работать с регистром
    for column in table.columns: 
        column.name = column.name.lower()

    metadata.create_all(engine)


def load_data(**kwargs):
    ti = kwargs['ti']
    df_base64 = kwargs['ti'].xcom_pull(
        key='df_pickle', task_ids='get_matches_step')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)

    hook = PostgresHook(conn_id)
    engine = hook.get_sqlalchemy_engine()


    df.to_sql('test_games', engine, if_exists='replace', index=False)

    """hook.insert_rows(
            table="games",
            replace=True,
            target_fields=df.columns.tolist(),
            replace_index=['match_id'],
            rows=df.values.tolist()
    )"""
