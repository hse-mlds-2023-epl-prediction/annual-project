# dags/get_odds_history.py
import pendulum
from airflow.decorators import dag, task
import pandas as pd
import numpy as np
import requests
import json

from steps.src.features import col_start_player, col_start_club, col_id_season, col_club_stat, col_player_stat, col_games, team_id, col_main, id_stadium
from steps.src.model_table import table_odds, metadata
from steps.src.app import create_table
from steps.src.config import conn_id
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import MetaData, Table, Column, String, Integer, inspect


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

headers = {
    'authority': 'www.oddsportal.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/json',
    # 'cookie': 'op_cookie-test=ok; op_user_cookie=7597410855; op_user_hash=35f97067bd7e85cbaa8f006219e40b74; op_user_time=1708675248; op_user_time_zone=3; op_user_full_time_zone=41; OptanonAlertBoxClosed=2024-02-23T08:03:09.345Z; eupubconsent-v2=CP6bRogP6bRogAcABBENAoEsAP_gAAAAAChQg1NX_H__bW9r8Xr3aft0eY1P99j77sQxBhfJE-4FzLvW_JwXx2ExNA26tqIKmRIEu3ZBIQFlHJDUTVigaogVryDMYkGcgTNKJ6BkiFMRM2dYCF5vmQtj-QKY5vp9d3fx2D-t_dv83dzyz8VHn3e5fme0cJCdA58tDfv9bRKb-5IPd_58v4v09F_rk2_eTVl_tevp7B-uft87_XU-9_ffeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAgSACAvMdABAXmSgAgLzKQAQF5gAAA.f_wAAAAAAAAA; _ga=GA1.1.273426941.1708675381; _sg_b_n=1708761104999; _sg_b_p=%2Ffootball%2Fengland%2Fpremier-league-2021-2022%2Fresults%2F; _sg_b_v=6%3B25721%3B1708786459; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Feb+24+2024+17%3A54%3A23+GMT%2B0300+(Moscow+Standard+Time)&version=202401.1.0&browserGpcFlag=0&isIABGlobal=false&consentId=42fe7d70-e5dd-4748-99c5-a7ca36036812&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CV2STACK42%3A1&hosts=H194%3A1%2CH302%3A1%2CH236%3A1%2CH198%3A1%2CH203%3A1%2CH190%3A1%2CH301%3A1%2CH303%3A1%2CH304%3A1%2CH230%3A1%2CH305%3A1&genVendors=V2%3A1%2C&AwaitingReconsent=false&geolocation=NL%3BNH; _ga_5YY4JY41P1=GS1.1.1708786457.3.1.1708786463.54.0.0',
    'referer': 'https://www.oddsportal.com/football/england/premier-league-2021-2022/results/',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

seasons = [
    {'id': 'jDTEm9zs', 'name': '2023-2024'},
    {'id': 'nmP0jyrt', 'name': '2022-2023'},
    {'id': 'tdkpynmB', 'name': '2021-2022'},
    {'id': 'AJuiuwWt', 'name': '2020-2021'},
    {'id': 'h2NtrDMq', 'name': '2019-2020'},
    {'id': 'zoZ4r7jR', 'name': '2018-2019'},
    {'id': 'UqQ8LECO', 'name': '2017-2018'},
    {'id': '8Ai8InSt', 'name': '2016-2017'},
    {'id': 'OhnzLqf7', 'name': '2015-2016'},
    {'id': 'hK4hu76a', 'name': '2014-2015'},
    {'id': 'OtIGJDpL', 'name': '2013-2014'}
]


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


def parser(**kwargs):

    matches = []
    for season in seasons:
        response = requests.get(
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
            result = response = requests.get(
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

    hook = PostgresHook(conn_id) 
    engine = hook.get_sqlalchemy_engine()

    if not inspect(engine).has_table(table_odds.name):
        metadata.create_all(engine)
