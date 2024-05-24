# dags/get_player_stat.py
import pandas as pd
import requests
from time import sleep
from steps.src.features import col_main, col_player_stat
from steps.src.config import uri, headers, conn_id, num_seasons
from steps.src.app import flatten_dict, list_to_dict, pars_dictline, pars_dictfeature
from steps.src.model_table import table_games
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Column, String, Boolean, Integer, inspect, create_engine, text
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

    kwargs['ti'].xcom_push(
        key='season_ids_list', value=season_ids_list[:num_seasons])


def get_club_id(**kwargs):
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)
    Base = declarative_base()

    Session = sessionmaker(bind=engine)
    session = Session()

    result = session.execute(text("SELECT DISTINCT id FROM club_basic"))
    club_ids_list = [row[0] for row in result.fetchall()]
    session.close()

    kwargs['ti'].xcom_push(
        key='club_ids_list', value=club_ids_list)


def parser(**kwargs):
    ti = kwargs['ti']
    season_ids_list = kwargs['ti'].xcom_pull(
        key='season_ids_list', task_ids='get_id_season')
    club_id = kwargs['ti'].xcom_pull(
        key='club_ids_list', task_ids='get_club_id')

    stat_list = pars_dictfeature(uri['get_player'],
                                 season_ids_list,
                                 club_id,
                                 'entity',
                                 'stats',
                                 )

    data = pars_dictline(stat_list, col_player_stat)
    player_stat = pd.DataFrame(data, columns=col_player_stat.values())
    df_pickle = pickle.dumps(player_stat)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='json', value=df_base64)


def load_data(**kwargs):
    ti = kwargs['ti']
    df_base64 = ti.xcom_pull(key='json', task_ids='parser')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)
    hook = PostgresHook(conn_id)

    engine = hook.get_sqlalchemy_engine()
    df.to_sql('player_stats', engine, if_exists='replace', index=False)
