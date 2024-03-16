import pickle
from typing import List
from fastapi import FastAPI, Depends

from src.footballapi import get_game_by_limit, get_games_tomorrow, get_games_today, get_games_today_predict, get_games_tomorrow_predict, get_games_predict, GameInfo, GameInfoWithPrediction
from src.stats import stats, StatInfo
from src.redis import cache

app = FastAPI()

@app.get('/games')
async def games(limit: int = 10) -> List[GameInfo]:
    data = get_game_by_limit(limit)
    return data.to_dict('records')

@app.get('/games-today')
async def games_today(redis_client: cache = Depends(cache)) -> List[GameInfo]:
    if (games_today := redis_client.get('games_today')) is not None:
        return pickle.loads(games_today)

    data = get_games_today()
    dict = data.to_dict('records')
    redis_client.set('games_today', pickle.dumps(dict))
    return dict

@app.get('/games-tomorrow')
async def games_tomorrow() -> List[GameInfo]:
    data = get_games_tomorrow()
    return data.to_dict('records')

@app.get('/games-predict')
async def games_predict() -> List[GameInfoWithPrediction]:
    data = get_games_predict()
    return data.to_dict('records')

@app.get('/games-today-predict')
async def games_today_predict() -> List[GameInfoWithPrediction]:
    data = get_games_today_predict()
    return data.to_dict('records')

@app.get('/games-tomorrow-predict')
async def games_tomorrow_predict() -> List[GameInfoWithPrediction]:
    data = get_games_tomorrow_predict()
    return data.to_dict('records')

@app.get('/stats')
async def get_stats() -> List[StatInfo]:
    data = await stats()
    return data.to_dict('records')
