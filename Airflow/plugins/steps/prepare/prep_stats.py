# steps/pars/get_club_stat.py
import pandas as pd
import numpy as np
import requests
from dateutil import parser
from collections import defaultdict
from time import sleep
from steps.src.features import col_club_stat
from steps.src.config import num_trial, del_game_col, mlflow_exp
from steps.src.app import pars_dictline, pars_dictfeature
from steps.src.model_table import table_games
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import base64
import os
import pickle
import mlflow


load_dotenv()
DBNAME = os.getenv('DBNAME')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
    

def prepare_club(**kwargs):
    # clubs_stat.csv
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)
    conn = engine.connect()
    
    # Добавляем колонку season (год сезона)
    sql = """
    SELECT cs.*, s.label AS season
    FROM club_stats AS cs
    JOIN seasons AS s ON cs.season_id = s.id
    """
    
    df = pd.read_sql(sql, conn)
    print(df)
    df['season'] = df['season'].apply(lambda x: int(x[:4]))
    df.drop(['name',
            'club_shortName',
            'shortName', 
            'id', 
            'teamType'], axis=1, inplace=True)
    
    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='prepare_club', value=df_base64)
    

def prepare_game(**kwargs):
    # games.csv
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)
    conn = engine.connect()
    
    sql = "SELECT * FROM games"
    df = pd.read_sql(sql, conn)
    # Удаляем колонки
    df.drop(del_game_col, axis=1, inplace=True)
    print(df)
    
    # Заполняем результаты матчей
    df['team_1_losses'] = np.where(df['teams_score_1'] < df['teams_score_2'], 1, 0)
    df['team_2_wins'] = np.where(df['teams_score_1'] < df['teams_score_2'], 1, 0)
    df['draw'] = np.where(df['teams_score_1'] == df['teams_score_2'], 1, 0)
    df['team_1_wins'] = np.where(df['teams_score_1'] > df['teams_score_2'], 1, 0)
    df['team_2_losses'] = np.where(df['teams_score_1'] > df['teams_score_2'], 1, 0)
    
    df['gameweek_compSeason_label'] = df['gameweek_compSeason_label'].apply(lambda x: int(x[:4]))
    # Выиграла команда 1 -1, проиграла -0, ничья - 2
    df['team_1_hue'] = np.where(df['team_1_wins']==1, 1,\
                            np.where(df['draw']==1, 2, 0)) 
    df.fillna(0)
    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='prepare_game', value=df_base64)
    

def get_players(**kwargs):
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)
    conn = engine.connect()
    
    sql = """
    SELECT *
    FROM players
    """
    
    df = pd.read_sql(sql, conn)
    print(df)   
    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='get_players', value=df_base64)


def get_goalkippers(**kwargs):
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)
    conn = engine.connect()
    
    sql = """
    SELECT *
    FROM goalkippers
    """
    
    df = pd.read_sql(sql, conn)
    print(df)   
    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='get_goalkippers', value=df_base64)


    
def prepare_players(**kwargs):
    # player_team
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)
    conn = engine.connect()
    
    # Добавляем колонку season (год сезона)
    sql = """
    SELECT ps.*, s.label AS season
    FROM player_stats AS ps
    JOIN seasons AS s ON ps.season_id = s.id
    """
    df = pd.read_sql(sql, conn)
    df['season'] = df['season'].apply(lambda x: int(x[:4]))
    df['age'] = df['season'] - df['birth_date_label'].apply(lambda x: int(x.split()[-1]))
    df[['_wins', '_losses', '_draws', '_appearances']] = df[['_wins',
                                                             '_losses',
                                                             '_draws',
                                                             '_appearances'
                                                             ]].fillna(0)
    df['per_wins'] = df['_wins'] / df['_appearances']
    print(df.columns)
    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='prepare_players', value=df_base64)    
  
    
def get_df(**kwargs):
    # Инициализация
    ti = kwargs['ti']
    conn_str = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
    engine = create_engine(conn_str)
    conn = engine.connect()
    
    # Загрузка 
    df_base64 = kwargs['ti'].xcom_pull(
        key='prepare_club', task_ids='prepare_club')
    df_pickle = base64.b64decode(df_base64)
    df_club = pickle.loads(df_pickle)
    
    df_base64 = kwargs['ti'].xcom_pull(
        key='prepare_game', task_ids='prepare_game')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)
    
    df_base64 = kwargs['ti'].xcom_pull(
        key='prepare_players', task_ids='prepare_players')
    df_pickle = base64.b64decode(df_base64)
    player_team_ = pickle.loads(df_pickle)

    df_base64 = kwargs['ti'].xcom_pull(
        key='get_players', task_ids='get_players')
    df_pickle = base64.b64decode(df_base64)
    player_team = pickle.loads(df_pickle)

    df_base64 = kwargs['ti'].xcom_pull(
        key='get_goalkippers', task_ids='get_goalkippers')
    df_pickle = base64.b64decode(df_base64)
    df_gk = pickle.loads(df_pickle)
    
    sql_player = "SELECT * FROM players"
    df_player = pd.read_sql(sql_player, conn)
    
    sql_goal = "SELECT * FROM goalkippers"
    df_goal = pd.read_sql(sql_goal, conn)
    
    sql_odds = "SELECT * FROM odds"
    df_odds = pd.read_sql(sql_odds, conn)

    
    home_games = df[['gameweek_compSeason_label', 'teams_team_1_name']].rename(
        columns={'gameweek_compSeason_label':'Season', 'teams_team_1_name': 'Team'})
    away_games = df[['gameweek_compSeason_label', 'teams_team_2_name']].rename(
        columns={'gameweek_compSeason_label':'Season','teams_team_2_name': 'Team'})
    
    # Создаем датафрейм с информацией по играм каждой команды в сезоне
    loc_home = [2, 9] + list(range(list(df.columns).index('team_1_formation_used'), list(df.columns).index('team_1_att_cmiss_left')))
    loc_away = [2, 13] + list(range(list(df.columns).index('team_2_formation_used'), list(df.columns).index('team_2_att_cmiss_left')))

    df_home = df.iloc[:, loc_home]
    df_away = df.iloc[:, loc_away]

    col_home = [i.replace('team_1_', '') for i in list(df_home.columns)]
    col_away = [i.replace('team_2_', '') for i in list(df_away.columns)]
    
    indx_del_home = [i for i, item in enumerate(col_home) if item not in col_away]
    indx_del_away = [i for i, item in enumerate(col_away) if item not in col_home]

    df_home = df_home.drop(df_home.columns[indx_del_home], axis=1)
    df_away = df_away.drop(df_away.columns[indx_del_away], axis=1)

    col_home = {i: i.replace('team_1_', '') for i in list(df_home.columns)}
    col_away = {i: i.replace('team_2_', '') for i in list(df_away.columns)}

    df_home.rename(columns=col_home, inplace=True)
    df_away.rename(columns=col_away, inplace=True)
    
    df_home = df_home.groupby(['gameweek_compSeason_label', 'teams_name']).sum().reset_index()
    df_away = df_away.groupby(['gameweek_compSeason_label', 'teams_name']).sum().reset_index()    
    
    df_games = pd.merge(df_home, df_away, how='left',
                        left_on=['gameweek_compSeason_label', 'teams_name'],
                        right_on=['gameweek_compSeason_label', 'teams_name'])
    
    df_club.drop(labels=['_attendance_count',
                         '_attendance_total',
                         '_attendance_average',
                         '_attendance_highest',
                         '_attendance_lowest'], axis=1, inplace=True)
    
    feature_list_games = ['match_id',
                          'gameweek_gameweek',
                          'gameweek_compSeason_label',
                          'teams_team_1_name',
                          'teams_team_2_name',
                          'team_1_hue',
                          'month',
                          'day_week',
                          'hour',
                          'ground_id']
    df.drop('ground_name', axis=1, inplace=True)
    # Преобразуем временные данные
    df['month'] = df['kickoff_label'].apply(lambda x: x.split()[2])
    df['day_week'] = df['kickoff_label'].apply(lambda x: x.split()[0])
    df['hour'] = df['kickoff_label'].apply(lambda x: x.split()[4].split(':')[0])
    feature_list_games.extend(['kickoff_label', 'month', 'day_week', 'hour', 'ground_id'])

    # Создаем лаг на статистику команды в 1 сезон
    list_na = list(df_club.isna().sum()[df_club.isna().sum() > 0].index)
    df_club[list_na] = df_club[list_na].fillna(df_club[df_club['season']!=2023][list_na].mean())
    cols_mean = list(df_club.columns)[4:-1]
    cols_mean = ['club_name'] + cols_mean
    df_club_lag = df_club.drop(labels=['season_id', 'club_abbr', 'club_id'], axis=1)
    df_club_lag['season'] = df_club_lag['season'] + 1
    df_num_mean = df_club[df_club['season']!=2023][cols_mean].groupby('club_name', as_index=False).mean()
    
    # Соединяем численные признаки с базовой инфой
    df_1 = df[feature_list_games].merge(df_num_mean,
                                        left_on='teams_team_1_name',
                                        right_on='club_name',
                                        how='left')
    df_1 = df_1.merge(df_num_mean,
                      left_on='teams_team_2_name',
                      right_on='club_name',
                      suffixes=('_team_1', '_team_2'),
                      how='left')
    
    df_1.drop(['club_name_team_1', 'club_name_team_2'], axis=1, inplace=True)
    
    # Добавляем лаги
    df_general = pd.merge(df_1,
                          df_club_lag,
                          left_on=['teams_team_1_name', 'gameweek_compSeason_label'],
                          right_on=['club_name', 'season'], how='left')
    
    df_general = pd.merge(df_general,
                          df_club_lag,
                          left_on=['teams_team_2_name', 'gameweek_compSeason_label'],
                          right_on=['club_name', 'season'],
                          how='left', suffixes=('_lag_team1', '_lag_team2'))
    
    df_general.sort_values(by=['match_id'], ascending=False , inplace=True)    
    
    df_general.drop(['season_lag_team2',
                     'season_lag_team1',
                     'club_name_lag_team1',
                     'club_name_lag_team2'], axis=1, inplace=True)
    
    # Работаем с статистикой игроков
    player_team['season'] = player_team['season'].astype(int)
    player_team_t = player_team.copy()
    player_team_t['season'] = player_team_t['season'] + 1
    
    #Cдвигаем статистику на год
    df_player_lag = pd.merge(player_team[['season', 'team', 'player_id', 'position', 'name']],
                             player_team_t.drop(['player_id', 'position', 'team'],
                                                axis=1), on=['season', 'name'], how='left')
    df_player_lag = df_player_lag[df_player_lag['season'] != df_player_lag['season'].min()]
    
    # Сдвигаем статистику вратарей на год
    df_goal['season'] = pd.to_numeric(df_goal['season'], errors='coerce')
    df_goal_t = df_goal.copy()
    df_goal_t['season'] = df_goal_t['season'] + 1
    df_goal_lag = pd.merge(df_goal[['season', 'team', 'player_id', 'position', 'name']],
                        df_goal_t.drop(['player_id', 'position', 'team'], axis=1),
                        on=['season', 'name'], how='left')
    df_goal_lag = df_goal_lag[df_goal_lag['season'] != df_goal_lag['season'].min()]
    df_goal_lag
    
    def flatten_team(df, team_dict, col, type):
        
        df = df[col]
        for i in range(len(df)):

            for j in range(len(col)):
                team_dict[type + '_' + str(i) + '_' + col[j]].append(df.iloc[i, j])

        return team_dict
    
    team_dict = defaultdict(list)
    col_players = ['name', 'appearances', 'height',	'weight', 'goals', 'assists', 'tackles', 'shots', 'keyPasses', 'cleanSheets']
    col_gk = ['name', 'appearances', 'height',	'weight', 'saves', 'cleanSheets', 'goalsConceded']

    # Работаем с игроками
    for season in list(df_player_lag['season'].unique()):
        for team in df_player_lag['team'].unique():
            if df_player_lag[(df_player_lag['season']==season) & (df_player_lag['team']==team)].shape[0] > 11:

                team_dict['season'].append(season)
                team_dict['team'].append(team)

                #players
                df_f = df_player_lag[(df_player_lag['season']==int(season)) & (df_player_lag['team']==str(team)) & (df_player_lag['position']=='F')].sort_values(by='appearances', ascending=False)[:3]
                df_m = df_player_lag[(df_player_lag['season']==int(season)) & (df_player_lag['team']==team) & (df_player_lag['position']=='M')].sort_values(by='appearances', ascending=False)[:6]
                df_d = df_player_lag[(df_player_lag['season']==int(season)) & (df_player_lag['team']==team) & (df_player_lag['position']=='D')].sort_values(by='appearances', ascending=False)[:7]

                team_dict = flatten_team(df_f, team_dict, col_players, 'F')
                team_dict = flatten_team(df_m, team_dict, col_players, 'M')
                team_dict = flatten_team(df_d, team_dict, col_players, 'D')

                #goalkeepers
                df_gk = df_goal_lag[(df_goal_lag['season']==int(season)) & (df_goal_lag['team']==team)].sort_values(by='appearances', ascending=False)[:1]
                team_dict = flatten_team(df_gk, team_dict, col_gk, 'GK')

    df_team_players = pd.DataFrame(team_dict)
    
    # Собираем датасет, в котором резузльтаты 6 последних матчей команды (лаги)
    
    df_res_home = df[['match_id', 'teams_team_1_name', 'team_1_hue']]
    df_res_guest = df[['match_id', 'teams_team_2_name', 'team_1_hue']]
    df_res_guest['team_1_hue'].replace({1:0, 0:1}, inplace=True)

    df_res_home.rename(columns={'teams_team_1_name':'team', 'team_1_hue': 'result'}, inplace=True)
    df_res_guest.rename(columns={'teams_team_2_name':'team', 'team_1_hue': 'result'}, inplace=True)
    
    df_res = pd.concat([df_res_home, df_res_guest], axis=0)
    df_res.sort_values(by='match_id', inplace=True)
    df_res.reset_index(drop=True, inplace=True)
    

    team_lag = 6
    df_team_lag = pd.DataFrame(columns=df_res.columns.tolist() + ['result_lag_' + str(i) for i in range(1, team_lag)])
    for team in df_res['team'].unique():
        df_temp = df_res[df_res['team']==team]
        for i in range(1, team_lag):
            lag = df_temp['result'].shift(i)
            df_temp['result_lag_' + str(i)] = lag

        df_team_lag = pd.concat([df_team_lag, df_temp], axis=0)
        
    # Собираем датасет, в котором резузльтаты матчей между двумя командами (лаги)
    t = df[['match_id', 'teams_team_1_name', 'teams_team_2_name', 'team_1_hue']]
    
    # Датефрейм который агригирует результаты команды независимо от того, играла она дома или в гостях
    df_game_team = pd.DataFrame(columns=t.columns)
    for team_1 in t['teams_team_1_name'].unique():
        for team_2 in t['teams_team_2_name'].unique():
            df_temp_1 = t[(t['teams_team_1_name']==team_1) & (t['teams_team_2_name']==team_2)]
            df_temp_2 = t[(t['teams_team_1_name']==team_2) & (t['teams_team_2_name']==team_1)]

            df_temp_2['team_1_hue'].replace({1:0, 0:1}, inplace=True)
            df_temp_2.rename(columns={'teams_team_1_name':'teams_team_2_name',
                                      'teams_team_2_name':'teams_team_1_name'}, inplace=True)
            df_temp = pd.concat([df_temp_1, df_temp_2], axis=0)
            df_game_team = pd.concat([df_game_team, df_temp], axis=0)
    df_game_team.sort_values(by='match_id', inplace=True) 
    
    # 3 лага в результатах матчей между двумя командами
    n_lag = 3
    df_game_lag = pd.DataFrame(columns=df_game_team.columns.tolist() + ['game_lag_' + str(i) for i in range(1, n_lag+1)])
    for team_1 in df_game_team['teams_team_1_name'].unique():
        for team_2 in df_game_team['teams_team_2_name'].unique():
            df_temp = df_game_team[(df_game_team['teams_team_1_name']==team_1) & (df_game_team['teams_team_2_name']==team_2)]
            #Добавляем лаги
            if df_temp.shape[0] > 0:
                for i in range(1, n_lag+1):
                    lag = df_temp['team_1_hue'].shift(i)

                    df_temp['game_lag_' + str(i)] = lag
        
            df_game_lag = pd.concat([df_game_lag, df_temp], axis=0)

    df_game_lag.sort_values(by='match_id', inplace=True)
    df_game_lag.drop('team_1_hue', axis=1, inplace=True)
    
    # Соединим датасеты df_general
    # df_team_players
    # df_team_lag по каждой команде
    # df_game_lag объединяем по двум командам
    
    df_general = pd.merge(df_general,
                          df_team_players,
                          left_on=['teams_team_1_name', 'gameweek_compSeason_label'],
                          right_on=['team', 'season'],
                          how='left')
    
    df_general = pd.merge(df_general,
                          df_team_players,
                          left_on=['teams_team_2_name', 'gameweek_compSeason_label'],
                          right_on=['team', 'season'],
                          how='left',
                          suffixes=('_team_1', '_team_2'))

    df_general.drop(['season_team_1', 'season_team_2', 'team_team_1', 'team_team_2'], axis=1, inplace=True)
    
    df_general = pd.merge(df_general,
                        df_team_lag,
                        how='left',
                        left_on=['match_id', 'teams_team_1_name'],
                        right_on=['match_id', 'team'])

    df_general = pd.merge(df_general,
                        df_team_lag,
                        how='left',
                        left_on=['match_id', 'teams_team_2_name'],
                        right_on=['match_id', 'team'],
                        suffixes=('_team_1', '_team_2'))

    df_general.drop(['team_team_1', 'team_team_2'], axis=1, inplace=True)

    df_general = pd.merge(df_general, df_game_lag, how='left', on=['match_id', 'teams_team_1_name', 'teams_team_2_name'])
        
    df_general['kickoff_label'] = pd.to_datetime(df_odds['date']).dt.date
    
    df_odds['date'] = pd.to_datetime(df_odds['date']).dt.date
    df_general = pd.merge(df_general,
                          df_odds,
                          how='left',
                          left_on=['teams_team_1_name', 'teams_team_2_name', 'kickoff_label'],
                          right_on=['home_name', 'away_name', 'date'])
    
    drp_list = ['home_name', 'away_name', 'date', 'kickoff_label', 'result_team_1', 'result_team_2']    
    df_general.drop(drp_list, axis=1, inplace=True)
    df_general = df_general[df_general['gameweek_compSeason_label'] != df_general['gameweek_compSeason_label'].min()]
    df_general.sort_values(by=['match_id'], inplace=True)
    
    duplicate_columns = ['month.1', 'day_week.1', 'hour.1', 'ground_id.1']
    df_general.drop(columns=duplicate_columns, inplace=True, errors='ignore')
    df_general.drop_duplicates(inplace=True)
    
    df_pickle = pickle.dumps(df_general)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='get_df', value=df_base64)


def tracking(**kwargs):
    df_base64 = kwargs['ti'].xcom_pull(
        key='get_df', task_ids='get_df')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)

    path = 'data'
    name_df = 'df.csv'
    
    
    with mlflow.start_run(experiment_id=str(mlflow_exp['df_base'])) as run:
        if not os.path.exists(path):
            os.makedirs(path)
        artifact_path = Path(path, name_df)
        df.to_csv(artifact_path, index=False)
        mlflow.log_artifact(artifact_path)

    print(print(f"Датасет залогирован в ране {run.info.run_id}"))