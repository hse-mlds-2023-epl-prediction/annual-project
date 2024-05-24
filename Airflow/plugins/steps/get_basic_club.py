# dags/get_basic_club.py
from airflow.decorators import dag, task
import pandas as pd
import numpy as np
import requests
from steps.src.features import col_start_club
from steps.src.config import uri, headers, conn_id
from steps.src.app import pars_dictline
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Column, String, Integer, inspect
import pickle
import base64


def get_basic_club(**kwargs):
    ti = kwargs['ti']
    params = {
        'pageSize': '400',
        'comps': '1',
        'altIds': 'true',
        'page': '0',
    }
    session = requests.Session()
    content = session.get(
        uri['get_basic_club'],
        params=params, headers=headers).json()['content']

    data = pars_dictline(content, col_start_club)
    df_start_club = pd.DataFrame(data, columns=col_start_club.values())
    df_start_club.drop('grounds', axis=1, inplace=True)

    df_pickle = pickle.dumps(df_start_club)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='df_pickle', value=df_base64)


def load_basic_club(**kwargs):
    ti = kwargs['ti']
    df_base64 = kwargs['ti'].xcom_pull(
        key='df_pickle', task_ids='get_basic_club')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)

    hook = PostgresHook(conn_id)
    engine = hook.get_sqlalchemy_engine()

    df.to_sql('club_basic', engine, if_exists='replace', index=False)
