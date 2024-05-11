import requests
from time import sleep

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
