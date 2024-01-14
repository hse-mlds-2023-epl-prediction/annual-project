from typing import List
from fastapi import FastAPI

from src.footballapi import get_game_by_limit, get_games_tomorrow, get_games_today, GameInfo

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
