# dags/get_basic_player.py
from airflow.decorators import dag, task
import pandas as pd
import numpy as np
import requests

from steps.src.features import id_stadium, stadium_col
from steps.src.config import uri, headers, conn_id
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Float, Column, String, Integer, inspect


def parser(**kwargs):
    
    stadium_list = []
    params = {
        'pageSize': '400',
        'comps': '1',
        'altIds': 'true',
        'page': '0',
    }
    session = requests.Session()
    response = session.get(uri['get_stadium'], params=params, headers=headers).json()
    club_list = response['content']

    stadium_list = []
    for club in club_list: 

        for i in range(len(club['grounds'])):
            if club['grounds'][i]['id'] in id_stadium:
                temp_list = [
                            club['name'] if 'name' in club else None,
                            club['id'] if 'id' in club else None,
                            club['grounds'][i]['name'] if 'name' in club['grounds'][i] else None,
                            club['grounds'][i]['id'] if 'id' in club['grounds'][i] else None,
                            club['grounds'][i]['city'] if 'city' in club['grounds'][i] else None,
                            club['grounds'][i]['capacity'] if 'capacity' in club['grounds'][i] else None,
                            club['grounds'][i]['location']['latitude'] if 'location' in club['grounds'][i] and 'latitude' in club['grounds'][i]['location'] else None,
                            club['grounds'][i]['location']['longitude'] if 'location' in club['grounds'][i] and 'longitude' in club['grounds'][i]['location'] else None,
                ]
                stadium_list.append(temp_list)
    # Преобразуем в словарь {name: values}
    data = {name: values for name, values in zip(stadium_col, zip(*stadium_list))}
    return data


def create_db():
    metadata = MetaData()

    table_stadium = Table(
        'stadiums', metadata,
        Column('club', String),
        Column('club_id', Integer),
        Column('stadium', String),
        Column('stadium_id', Integer, primary_key=True),
        Column('city', String),
        Column('capacity', String),
        Column('latitude', Float),
        Column('longitude', Float))
    
    hook = PostgresHook(conn_id) 
    engine = hook.get_sqlalchemy_engine()

    if not inspect(engine).has_table(table_stadium.name):
        metadata.create_all(engine)


def load_data(data, **kwargs):

    data = pd.DataFrame(data)
    hook = PostgresHook(conn_id)

    hook.insert_rows(
            table="stadiums",
            replace=True,
            target_fields=data.columns.tolist(),
            replace_index=['stadium_id'],
            rows=data.values.tolist()
    )