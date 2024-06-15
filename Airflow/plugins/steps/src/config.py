num_seasons = 10

mlflow_exp = {
    'df_base': '6',
    'optuna': '7',
    'model': '8'
}

num_trial = 12

headers = {
    'authority': 'footballapi.pulselive.com',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'if-none-match': 'W/"0747914aff6e8740e3fb239d0232b2d3d"',
    'origin': 'https://www.premierleague.com',
    'referer': 'https://www.premierleague.com/',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "YaBrowser";v="23"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.962 YaBrowser/23.9.1.962 Yowser/2.5 Safari/537.36',
}

conn_id = 'airflow' # Устанавливается в интерфейсе аирфлоу

uri = {
    'get_season': 'https://footballapi.pulselive.com/football/competitions',
    'get_stadium': 'https://footballapi.pulselive.com/football/teams',
    'get_bases_games': 'https://footballapi.pulselive.com/football/fixtures',
    'get_matches': 'https://footballapi.pulselive.com/football/stats/match',
    'get_player_stat': 'https://footballapi.pulselive.com/football/stats/team',
    'get_basic_club': 'https://footballapi.pulselive.com/football/teams',
    'get_player': 'https://footballapi.pulselive.com/football/stats/player',
    'get_stat_club': 'https://footballapi.pulselive.com/football/stats/team',
    'get_base_player': 'https://footballapi.pulselive.com/football/players'
    }

del_game_col = [
    'gameweek_compSeason_competition_source',
    'gameweek_compSeason_competition_level',
    'gameweek_compSeason_competition_description',
    'gameweek_compSeason_competition_abbreviation',
    'gameweek_compSeason_competition_id',
    'ground_source',
    'kickoff_completeness',
    'provisionalKickoff_completeness',
    'teams_team_1_club_name',
    'teams_team_1_club_shortName',
    'teams_team_1_teamType',
    'teams_team_1_shortName',
    'teams_team_1_id',
    'teams_team_2_club_name',
    'teams_team_2_club_shortName',
    'teams_team_2_teamType',
    'teams_team_2_shortName',
    'teams_team_2_id',
    'neutralGround',
    'replay',
    'status',
    'phase',
    'fixtureType',
    'extraTime',
    'shootout',
]
