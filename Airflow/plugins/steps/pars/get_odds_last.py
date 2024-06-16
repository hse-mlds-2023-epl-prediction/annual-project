# dags/get_odds_history.py
import pendulum
from airflow.decorators import dag, task
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from dateutil import parser
from steps.src.app import convert_data
from steps.src.config import conn_id
from steps.src.features import cookies_odd, headers_odd, seasons_odd, odds_map_name
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


def convert_data(rows, season):
    data = []
    for row in rows:
        has_ods = len(row['odds'])
        data.append({
            'home_name': row['home-name'],
            'away_name': row['away-name'],
            'result': row['result'],
            'home_team_result': row['homeResult'],
            'away_team_result': row['awayResult'],
            'home_avg_odds': row['odds'][0]['avgOdds'] if has_ods else 1,
            'draw_avg_odds': row['odds'][1]['avgOdds'] if has_ods else 1,
            'away_avg_odds': row['odds'][2]['avgOdds'] if has_ods else 1,
            'season': season,
            'date_start_timestamp': row['date-start-timestamp']
        })
    return data


def parser_odds(**kwargs):
    matches = []
    ti = kwargs['ti']
    for season in seasons_odd:
        response = requests.get(
            f"https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/{season['id']}/X0/1/0/page/1",
            params={},
            cookies=cookies_odd,
            headers=headers_odd,
        )
        result = response.json()
        pages = result['d']['pagination']['pages'] - 1
        converted_data = convert_data(result['d']['rows'], season['name'])
        matches.extend(converted_data)

        for i in range(pages):
            currentPage = i + 1
            url = f"https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/{season['id']}/X0/1/0/page/{currentPage}"
            result = response = requests.get(
                url,
                params={},
                cookies=cookies_odd,
                headers=headers_odd,
            )

            data = result.json()
            rows = data['d']['rows']
            converted_data = convert_data(rows, season['name'])
            matches.extend(converted_data)

    df = pd.DataFrame(matches)
    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='df_pickle', value=df_base64)


def get_clubs(**kwargs):
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)

    Session = sessionmaker(bind=engine)
    session = Session()

    result = session.execute(text("SELECT DISTINCT name FROM club_stats ORDER BY name ASC"))
    club_name = [row[0] for row in result.fetchall()]
    session.close()

    kwargs['ti'].xcom_push(
        key='get_clubs', value=club_name)
    

def prepare(**kwargs):
    ti = kwargs['ti']
    df_base64 = kwargs['ti'].xcom_pull(
        key='df_pickle', task_ids='parser_odds')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)
    
    name_club = kwargs['ti'].xcom_pull(
        key='get_clubs',  task_ids='get_clubs')
    
    # Меняем наименование команд как везде
    df['home_name'] = df['home_name'].apply(lambda x: odds_map_name[x])
    df['away_name'] = df['away_name'].apply(lambda x: odds_map_name[x])
    df['season'] = df['season'].apply(lambda x: x[:4])
    
    # Меняем формат даты
    df['date'] = df['date_start_timestamp'].apply(lambda x: datetime.utcfromtimestamp(x).date())
    df['date'] = pd.to_datetime(df['date'])
    
    # Оставляем нужные колонки
    features = ['home_name', 'away_name',  'home_avg_odds', 'draw_avg_odds', 'away_avg_odds', 'date']
    df = df[features]
    
    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='prepare', value=df_base64)
    
    
def load_data(**kwargs):
    ti = kwargs['ti']
    df_base64 = ti.xcom_pull(key='prepare', task_ids='prepare')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)
    print(df)
    hook = PostgresHook(conn_id)

    engine = hook.get_sqlalchemy_engine()
    df.to_sql('odds', engine, if_exists='replace', index=False)