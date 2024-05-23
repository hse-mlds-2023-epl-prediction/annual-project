# dags/get_odds_history.py
import pendulum
from airflow.decorators import dag, task
import pandas as pd
import numpy as np
import requests
import json

from steps.src.app import convert_data
from steps.src.features import seasons_odds
from steps.src.config import headers, conn_id
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Column, String, Integer, inspect, Float, DateTime


cookies = {
    'op_cookie-test': 'ok',
    'op_user_cookie': '7597410855',
    'op_user_hash': '35f97067bd7e85cbaa8f006219e40b74',
    'op_user_time': '1708675248',
    'op_user_time_zone': '3',
    'op_user_full_time_zone': '41',
    'OptanonAlertBoxClosed': '2024-02-23T08:03:09.345Z',
    'eupubconsent-v2': 'CP6bRogP6bRogAcABBENAoEsAP_gAAAAAChQg1NX_H__bW9r8Xr3aft0eY1P99j77sQxBhfJE-4FzLvW_JwXx2ExNA26tqIKmRIEu3ZBIQFlHJDUTVigaogVryDMYkGcgTNKJ6BkiFMRM2dYCF5vmQtj-QKY5vp9d3fx2D-t_dv83dzyz8VHn3e5fme0cJCdA58tDfv9bRKb-5IPd_58v4v09F_rk2_eTVl_tevp7B-uft87_XU-9_ffeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAgSACAvMdABAXmSgAgLzKQAQF5gAAA.f_wAAAAAAAAA',
    '_ga': 'GA1.1.273426941.1708675381',
    '_sg_b_n': '1708761104999',
    '_sg_b_p': '%2Ffootball%2Fengland%2Fpremier-league-2021-2022%2Fresults%2F',
    '_sg_b_v': '6%3B25721%3B1708786459',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Sat+Feb+24+2024+17%3A54%3A23+GMT%2B0300+(Moscow+Standard+Time)&version=202401.1.0&browserGpcFlag=0&isIABGlobal=false&consentId=42fe7d70-e5dd-4748-99c5-a7ca36036812&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CV2STACK42%3A1&hosts=H194%3A1%2CH302%3A1%2CH236%3A1%2CH198%3A1%2CH203%3A1%2CH190%3A1%2CH301%3A1%2CH303%3A1%2CH304%3A1%2CH230%3A1%2CH305%3A1&genVendors=V2%3A1%2C&AwaitingReconsent=false&geolocation=NL%3BNH',
    '_ga_5YY4JY41P1': 'GS1.1.1708786457.3.1.1708786463.54.0.0',
}



def parser():

    matches = []
    session = requests.Session()
    for season in seasons_odds:
        response = session.get(
            f"https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/{season['id']}/X0/1/0/page/1",
            params={},
            cookies=cookies,
            headers=headers,
        )
        result = response.json()
        pages = result['d']['pagination']['pages'] - 1
        converted_data = convert_data(result['d']['rows'], season['name'])
        matches.extend(converted_data)

        for i in range(pages):
            currentPage = i + 1
            url = f"https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/{season['id']}/X0/1/0/page/{currentPage}"
            result = response = session.get(
                url,
                params={},
                cookies=cookies,
                headers=headers,
            )

            data = result.json()
            rows = data['d']['rows']
            converted_data = convert_data(rows, season['name'])
            matches.extend(converted_data)
    return matches


def create_db():
    metadata = MetaData()

    table_odds = Table(
        'odds', metadata,
        Column('id', primary_key=True, autoincrement=True),
        Column('home_name', String),
        Column('away_name', String),
        Column('result', String),
        Column('home_team_result', Integer),
        Column('away_team_result', Integer),
        Column('home_avg_odds', Float),
        Column('draw_avg_odds', Float),
        Column('away_avg_odds', Float),
        Column('season', String),
        Column('date_start_timestamp', DateTime),
    )
    hook = PostgresHook(conn_id)
    engine = hook.get_sqlalchemy_engine()

    if not inspect(engine).has_table(table_odds.name):
        metadata.create_all(engine)


def load_data(value, **kwargs):

    #ti = kwargs['ti']
    #value = ti.xcom_pull(key='json', task_ids='parser')
    data = pd.DataFrame(value)
    hook = PostgresHook(conn_id)

    hook.insert_rows(
            table="odds",
            replace=True,
            target_fields=data.columns.tolist(),
            replace_index=['id'],
            rows=data.values.tolist()
    )