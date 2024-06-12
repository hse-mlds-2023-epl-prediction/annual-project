import requests
from time import sleep
import pandas as pd
from category_encoders import TargetEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from steps.src.config import headers


def flatten_dict(dict_, parent_key='', separator='_'):
    """ flatten dict
    Input: dict_: dict

      parent_key: str
      separator: str

    return: dict"""

    if type(dict_) != dict:
        raise ValueError("dict_ must be type dict")

    output_dict = {}
    for key, value in dict_.items():
        new_key = parent_key + separator + key if parent_key else key

        if isinstance(value, dict):
            nested_dict = flatten_dict(value, new_key, separator)
            output_dict.update(nested_dict)
        else:
            output_dict[new_key] = value

    return output_dict


def get_col_dict(list_dict):
    """ 
    Input: list_dict: list[dict, dict]
    return: dict"""

    name_col_dict = {}
    count = 0

    flatten = list(map(flatten_dict, list_dict))

    for key in flatten[0].keys():
      name_col_dict[count] = key
      count += 1

    return name_col_dict


def pars_dictline(list_dict, name_col_dict):
    """ Use if each dict - line
    Input: list[dict]
    return: List[value]"""

    n = len(name_col_dict)
    flatten = list(map(flatten_dict, list_dict))
    pars_list = [[dict_feat[name_col_dict[i]] if name_col_dict[i] in dict_feat else None for i in range(n)] for dict_feat in flatten]

    return pars_list


def list_to_dict(list_dict, name_stat='name', value_stat='value', pref=''):
    """ Use if each dict - feature
    Input: list_dict: list [dict, dict]

      name_stat: key for dicts stat where are name feature
      value_stat: key for dicts stat where are value feature

    return: dict"""

    result_dict = {}

    for feat in list_dict:
        result_dict[pref+'_'+feat[name_stat]] = feat[value_stat]

    return result_dict



def pars_dictfeature(response_url, seasons, iter, main_info, stats, name_stat='name', value_stat='value'):
    """ Use if each dict - feature
    Input: response_url: url:str

          seasons: List/Series id season sorted
          iter: List/Series id club/players
          main_info: key dict response where main info
          stats: key dict where are dicts with stats whose are feature
          name_stat: key for dicts stat where are name feature
          value_stat: key for dicts stat where are value feature

    return: List[dict]"""
    result = []

    params = {
        'comps': '1',
        'compSeasons': str(seasons[0]),
        }


    s = requests.Session()
    for id in iter: #пробегаем по каждому клубу/игроку
        for season in seasons: #пробегаем по каждому сезону

            params = {
                'comps': '1',
                'compSeasons': str(season),
                }

            response = s.get(f'{response_url}/{str(id)}', params=params, headers=headers)

            if response.status_code != 200:
                print(f'id: {id}, season id: {season} RESPONSE: {response.status_code}')
                continue

            if len(response.text) == 0 or len(response.json()[stats]) == 0:
                continue

            stat = response.json()[stats]
            main = response.json()[main_info]

            temp_dict = list_to_dict(stat, name_stat='name', value_stat='value')


            dict_stats = {'season_id': season, **flatten_dict(main), **temp_dict}
            result.append(dict_stats)
            sleep(0.25)

    return result



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



def cat_features(df: pd.DataFrame) -> list:
    """
    Функция для определения категориальных признаков
    """
    lag_features = [
                'result_lag_1_team_1',
                'result_lag_2_team_1',
                'result_lag_3_team_1',
                'result_lag_4_team_1',
                'result_lag_5_team_1',
                'result_lag_1_team_2',
                'result_lag_2_team_2',
                'result_lag_3_team_2',
                'result_lag_4_team_2',
                'result_lag_5_team_2',
                'game_lag_1',
                'game_lag_2',
                'game_lag_3'
                ]

    cat_cols = [
                'gameweek_gameweek',
                'gameweek_compSeason_label',
                'ground_id',
            ]

    cat_cols += df.describe(include='object').columns.to_list() + lag_features

    return cat_cols


def pca_pipeline(df: pd.DataFrame,
                 y: pd.Series,
                 cat_cols: list,
                 num_cols: list,
                 n_components: int = 50,
                 pca: bool = True):
    """
    Функция для преобразования датасета с использованием PCA
    """
    df.loc[:, cat_cols] = df.loc[:, cat_cols].fillna(999)
    df.fillna(0, inplace=True)
    numeric_transformer = Pipeline(steps=[
        ('scaler', MinMaxScaler())])

    categorical_transformer = Pipeline(steps=[
        ('target_encoding', TargetEncoder())])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)])

    if pca:
        pca = PCA(n_components=n_components, random_state=42)
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('pca', pca)])

    else:
        pipeline = Pipeline(steps=[('preprocessor', preprocessor)])

    X_processed = pipeline.fit_transform(df, y)

    return X_processed, pipeline