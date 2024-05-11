# dags/get_id_season.py
from airflow.decorators import dag, task
import pandas as pd
import numpy as np
import requests

from steps.src.features import col_start_player, col_start_club, col_id_season, col_club_stat, col_player_stat, col_games, team_id, col_main, id_stadium
from steps.src.model_table import metadata, table_season
from steps.src.app import create_table
from steps.src.config import uri_get_season, headers, conn_id
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Column, String, Integer, inspect


def parser(**kwargs):

    #ti = kwargs['ti']
    params = {
        'page': '0',
        'pageSize': '1000',
        'detail': '2',
        }
    session = requests.Session()
    content = session.get(uri_get_season['get_season'], params=params, headers=headers).json()['content']

    for league in content:
        if league['abbreviation'] == 'EN_PR':
            value=league['compSeasons']

    #ti.xcom_push(key='json', value=value)
    return value


def create_db():
    
    hook = PostgresHook(conn_id) 
    engine = hook.get_sqlalchemy_engine()

    if not inspect(engine).has_table(table_season.name):
        metadata.create_all(engine)


def load_data(value, **kwargs):

    #ti = kwargs['ti']
    #value = ti.xcom_pull(key='json', task_ids='parser')
    data = pd.DataFrame(value)
    hook = PostgresHook(conn_id)

    hook.insert_rows(
            table="seasons",
            replace=True,
            target_fields=data.columns.tolist(),
            replace_index=['id'],
            rows=data.values.tolist()
    )