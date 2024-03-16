from typing import List
from fastapi import FastAPI

from src.footballapi import get_game_by_limit, get_games_tomorrow, get_games_today, get_games_today_predict, get_games_tomorrow_predict
from src.footballapi import add_comand, get_games_predict, get_favorite, helthy_services
from src.models import GameInfo, GameInfoWithPrediction, Favorite
from src.stats import stats, StatInfo

app = FastAPI()

@app.get('/games')
#Десят ближайших игр
async def games(limit: int = 10) -> List[GameInfo]:
    data = get_game_by_limit(limit)
    return data.to_dict('records')

@app.get('/games-today')
#Игры сегодня
async def games_today() -> List[GameInfo]:
    data = get_games_today()
    return data.to_dict('records')

@app.get('/games-tomorrow')
#Игры завтра
async def games_tomorrow() -> List[GameInfo]:
    data = get_games_tomorrow()
    return data.to_dict('records')

@app.get('/games-predict')
#Предсказания ближайших 10 игр
async def games_predict() -> List[GameInfoWithPrediction]:
    data = get_games_predict()
    return data.to_dict('records')

@app.get('/games-today-predict')
#Предсказания игр сегодня
async def games_today_predict() -> List[GameInfoWithPrediction]:
    data = get_games_today_predict()
    return data.to_dict('records')

@app.get('/games-tomorrow-predict')
#Предсказания игр завтра
async def games_tomorrow_predict() -> List[GameInfoWithPrediction]:
    data = get_games_tomorrow_predict()
    return data.to_dict('records')

@app.get('/stats')
#Статистика
async def get_stats() -> List[StatInfo]:
    data = await stats()
    return data.to_dict('records')

@app.post('/add_favorite')
#Добавление команды в избранное
async def add_favorite(req: Favorite) -> str:
    resp = add_comand(req.name, req.user)
    return resp

@app.get('/get_favorite_comand')
#Получение избранных команд
async def get_favorite_comand(user: int):
    return get_favorite(user)

@app.get('/health')
#Проверка сервисов
async def health() -> dict:
    result = helthy_services()
    return result