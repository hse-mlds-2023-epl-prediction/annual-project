import pandas as pd
import numpy as np
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path  

from features import headers, col_start_player, col_start_club, col_id_season, col_club_stat, col_player_stat, col_games, col_main, id_stadium

from func import flatten_dict, get_col_dict, pars_dictline, list_to_dict, pars_dictfeature




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

#================================Get base info about players======================
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
filepath = Path('pars/parsing EPL/official site/data/df_start_player.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
df_start_player.to_csv(filepath, index=False)

print('Get base info about players')
#=============================Get basic info about clubs=========================

params = {
    'pageSize': '400',
    'comps': '1',
    'altIds': 'true',
    'page': '0',
}

response = requests.get('https://footballapi.pulselive.com/football/teams', params=params, headers=headers)
club_list = response.json()['content']

data = pars_dictline(club_list, col_start_club)
df_start_club = pd.DataFrame(data, columns=col_start_club.values())

#club id save as int
df_start_club['club_id'] = df_start_club['club_id'].astype('int')

#save DataFrame csv
filepath = Path('pars/parsing EPL/official site/data/df_start_club.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
df_start_club.to_csv(filepath, index=False)

print('Get basic info about clubs')
#================================get stadium info=====================================
stadium_list = []
for club in club_list: #датафрейм со стадионами

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

stadium_col = [
    'club',
    'club_id',
    'stadium',
    'stadium_id',
    'city',
    'capacity',
    'latitude',
    'longitude'
]

df_stadium = pd.DataFrame(stadium_list, columns=stadium_col)
df_stadium[['club_id', 'stadium_id']] = df_stadium[['club_id', 'stadium_id']].astype(int)

filepath = Path('pars/parsing EPL/official site/data/df_stadium.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
df_stadium.to_csv(filepath, index=False)
#===================================get id seasons===================================

params = {
    'page': '0',
    'pageSize': '100',
}

response = requests.get('https://footballapi.pulselive.com/football/competitions/1/compseasons', params=params, headers=headers)

data = pars_dictline(response.json()['content'], col_id_season)
id_season = pd.DataFrame(data, columns=col_id_season.values()) 

#id save as int
id_season['id'] = id_season['id'].astype(int)
#save DataFrame csv
filepath = Path('pars/parsing EPL/official site/data/id_season.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
id_season.to_csv(filepath)


club_id = df_start_club['club_id'].unique()
player_id = df_start_player['id'].unique()


#========================get info about club========================================
response_url = 'https://footballapi.pulselive.com/football/stats/team'
seasons = id_season['id'].iloc[:10]
iter = club_id
main_info = 'entity'
stats = 'stats'
list_club = pars_dictfeature(response_url, seasons, iter, main_info, stats, name_stat='name', value_stat='value')

data = pars_dictline(list_club, col_club_stat)
club_stat = pd.DataFrame(data, columns=col_club_stat.values())

#save DataFrame csv
filepath = Path('pars/parsing EPL/official site/data/club_stat.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
club_stat.to_csv(filepath, index=False)


#=============================get info about players========================

response_url = 'https://footballapi.pulselive.com/football/stats/player'
iter = player_id
list_player = pars_dictfeature(response_url, seasons, iter, main_info, stats, name_stat='name', value_stat='value')

data = pars_dictline(list_player, col_player_stat)
player_stat = pd.DataFrame(data, columns=col_player_stat.values())

#save DataFrame csv
filepath = Path('pars/parsing EPL/official site/data/player_stat.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)  
player_stat.to_csv(filepath, index=False)


#================================get basic info about games=============================
params = {
    'comps': '1',
    'compSeasons': '578',
    'pageSize': '1000',
    'altIds': 'true',
    'sort': 'desc',
    'statuses': 'C'
}


response = requests.get('https://footballapi.pulselive.com/football/fixtures',  headers=headers, params=params)

df_games = pd.DataFrame()

s = requests.Session()

for season in id_season['id'].iloc[:10]:

    params['compSeasons'] = season
    response = s.get('https://footballapi.pulselive.com/football/fixtures',  headers=headers, params=params)
    r = response.json()['content']
    value = pars_dictline(r, col_games)

    temp_df = pd.DataFrame(value, columns=col_games.values())

    df_games = pd.concat([df_games, temp_df], ignore_index=True)
    sleep(0.25)

df_games['id'].astype(int)

#save DataFrame csv
filepath = Path('pars/parsing EPL/official site/data/df_games.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)  
df_games.to_csv(filepath, index=False)

#=================================get main info about games===============================

match_id = df_games['id'].astype(int)
url = 'https://footballapi.pulselive.com/football/stats/match'

result = []
s = requests.Session()
count = 0
for id in match_id: #iter for each match
    count += 1
    r = s.get(f'{url}/{str(id)}', headers=headers)

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
df_main = pd.DataFrame(data, columns=col_main.values())

#save DataFrame csv
filepath = Path('pars/parsing EPL/official site/data/df_main.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)  
df_main.to_csv(filepath, index=False)