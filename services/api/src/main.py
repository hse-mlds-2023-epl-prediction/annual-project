from typing import List
from fastapi import FastAPI

from src.footballapi import get_game_by_limit, get_games_tomorrow, get_games_today, get_games_today_predict, get_games_tomorrow_predict, get_games_predict, GameInfo, GameInfoWithPrediction
from src.stats import stats, StatInfo

app = FastAPI()

@app.get('/games')
async def games(limit: int = 10) -> List[GameInfo]:
    data = get_game_by_limit(limit)
    return data.to_dict('records')

@app.get('/games-today')
async def games_today() -> List[GameInfo]:
    data = get_games_today()
    return data.to_dict('records')

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
