num_seasons = 12

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
    'get_player': 'https://footballapi.pulselive.com/football/players',
    'get_stat_club': 'https://footballapi.pulselive.com/football/stats/team'}
