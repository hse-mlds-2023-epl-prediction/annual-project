# dags/get_id_season.py
from airflow.decorators import dag, task
import pandas as pd
import numpy as np
import requests
from steps.src.config import uri, headers, conn_id
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Column, String, Integer, inspect


def parser(**kwargs):
    ti = kwargs['ti']
    params = {
        'page': '0',
        'pageSize': '1000',
        'detail': '2',
        }
    session = requests.Session()
    content = session.get(uri['get_season'], params=params, headers=headers).json()['content']

    for league in content:
        if league['abbreviation'] == 'EN_PR':
            value=league['compSeasons']

    ti.xcom_push(key='json', value=value)


def create_db():    
    metadata = MetaData()
    table_season = Table(
        'seasons', metadata,
        Column('id', Integer, primary_key=True),
        Column('label', String),
        )
    hook = PostgresHook(conn_id) 
    engine = hook.get_sqlalchemy_engine()

    if not inspect(engine).has_table(table_season.name):
        metadata.create_all(engine)


def load_data(**kwargs):
    ti = kwargs['ti']
    value = ti.xcom_pull(key='json', task_ids='parser')
    data = pd.DataFrame(value)
    hook = PostgresHook(conn_id)

    hook.insert_rows(
            table="seasons",
            replace=True,
            target_fields=data.columns.tolist(),
            replace_index=['id'],
            rows=data.values.tolist()
    )
