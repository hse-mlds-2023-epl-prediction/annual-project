# dags/pars.py
import pendulum
from airflow.decorators import dag, task
import pandas as pd
import numpy as np
import pandas as pd
import numpy as np
import requests

from pathlib import Path  

from features import headers, col_start_player, col_start_club, col_id_season, col_club_stat, col_player_stat, col_games, team_id, col_main, id_stadium

from func import flatten_dict, pars_dictline, list_to_dict, pars_dictfeature

def pars(**kwargs):
    dir = 'data/'
    num_season = 10
    page = 0
    params = {
        'pageSize': '200',
        'compSeasons': '578',
        'altIds': 'true',
        'page': str(page),
        'type': 'player',
        'id': '-1',
        'compSeasonId': '578',
    }

    response = requests.get('https://footballapi.pulselive.com/football/players', params=params, headers=headers)

    players_list = []
    s = requests.Session()

    while len(response.json()['content']) > 0:
        players_list.extend(response.json()['content'])

        page += 1

        params = {
            'pageSize': '200',
            'compSeasons': '578',
            'altIds': 'true',
            'page': str(page),
            'type': 'player',
            'id': '-1',
            'compSeasonId': '578',
        }
        response = s.get('https://footballapi.pulselive.com/football/players', params=params, headers=headers)

    data = pars_dictline(players_list, col_start_player)
    df_start_player = pd.DataFrame(data, columns=col_start_player.values())

    #player id save as int
    df_start_player['id'] = df_start_player['id'].astype(int)

    #save DataFrame csv
    filepath = Path(dir +'/df_start_player.csv')  
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    df_start_player.to_csv(filepath, index=False)

    print('Get base info about players')