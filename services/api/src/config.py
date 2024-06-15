from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    footbalapi_url: str = """https://footballapi.pulselive.com/football/
                            fixtures?comps=1&teams=1,2,127,130,131,43,4,6,7,34,10,163,11,12,23,15,18,21,25,38
                            &compSeasons=578&page=0&pageSize=12&sort=asc&
                            statuses=U,L&altIds=true"""

    headers: dict = {
        'authority': 'footballapi.pulselive.com',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'if-none-match': 'W/"0747914aff6e8740e3fb239d0232b2d3d"',
        'origin': 'https://www.premierleague.com',
        'referer': 'https://www.premierleague.com/',
        'sec-ch-ua': '''"Chromium";v="116",
                        "Not)A;Brand";v="24",
                        "YaBrowser";v="23"''',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
                         (KHTML, like Gecko) Chrome/116.0.5845.962
                         YaBrowser/23.9.1.962 Yowser/2.5 Safari/537.36''',
    }

    redis_host: str
    redis_port: int

    db_host: str
    db_port: str
    db_user: str
    db_password: str
    db_name: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding='utf-8'
        )


settings = Settings()

uri = {
    'streamlit': '5.104.75.226:8501',
    'mlflow': '5.104.75.226:5000',
    'minio': '5.104.75.226:9001/login',
    'airflow': '176.109.107.7:8080',
}

teams = [('Arsenal', 'ARS', 1.0),
         ('Aston Villa', 'AVL', 2.0),
         ('Bournemouth', 'BOU', 127.0),
         ('Brentford', 'BRE', 130.0),
         ('Brighton & Hove Albion', 'BHA', 131.0),
         ('Burnley', 'BUR', 43.0),
         ('Cardiff City', 'CAR', 46.0),
         ('Chelsea', 'CHE', 4.0),
         ('Crystal Palace', 'CRY', 6.0),
         ('Everton', 'EVE', 7.0),
         ('Fulham', 'FUL', 34.0),
         ('Huddersfield Town', 'HUD', 159.0),
         ('Hull City', 'HUL', 41.0),
         ('Leeds United', 'LEE', 9.0),
         ('Leicester City', 'LEI', 26.0),
         ('Liverpool', 'LIV', 10.0),
         ('Luton Town', 'LUT', 163.0),
         ('Manchester City', 'MCI', 11.0),
         ('Manchester United', 'MUN', 12.0),
         ('Middlesbrough', 'MID', 13.0),
         ('Newcastle United', 'NEW', 23.0),
         ('Norwich City', 'NOR', 14.0),
         ('Nottingham Forest', 'NFO', 15.0),
         ('Queens Park Rangers', 'QPR', 17.0),
         ('Sheffield United', 'SHU', 18.0),
         ('Southampton', 'SOU', 20.0),
         ('Stoke City', 'STK', 42.0),
         ('Sunderland', 'SUN', 29.0),
         ('Swansea City', 'SWA', 45.0),
         ('Tottenham Hotspur', 'TOT', 21.0),
         ('Watford', 'WAT', 33.0),
         ('West Bromwich Albion', 'WBA', 36.0),
         ('West Ham United', 'WHU', 25.0),
         ('Wolverhampton Wanderers', 'WOL', 38.0)]
