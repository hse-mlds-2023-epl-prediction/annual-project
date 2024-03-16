import pickle
from typing import List
from fastapi import FastAPI, Depends

from src.footballapi import get_game_by_limit, get_games_tomorrow, get_games_today, get_games_today_predict, get_games_tomorrow_predict, get_games_predict, GameInfo, GameInfoWithPrediction
from src.stats import stats, StatInfo
from src.redis import cache, DEFAULT_CACHE_TTL

app = FastAPI()

@app.get('/games')
async def games(limit: int = 10, redis_client: cache = Depends(cache)) -> List[GameInfo]:
    cache_key = f'games_{limit}'
    if (games := redis_client.get(cache_key)) is not None:
        return pickle.loads(games)
    data = get_game_by_limit(limit)

    dict_data = data.to_dict('records')
    redis_client.set(cache_key, pickle.dumps(dict_data))
    redis_client.expire(cache_key, DEFAULT_CACHE_TTL)
    return dict_data

@app.get('/games-today')
async def games_today(redis_client: cache = Depends(cache)) -> List[GameInfo]:
    if (games_today := redis_client.get('games_today')) is not None:
        return pickle.loads(games_today)

    data = get_games_today()
    dict_data = data.to_dict('records')
    redis_client.set('games_today', pickle.dumps(dict_data))
    redis_client.expire('games_today', DEFAULT_CACHE_TTL)
    return dict_data

@app.get('/games-tomorrow')
async def games_tomorrow(redis_client: cache = Depends(cache)) -> List[GameInfo]:
    if (games_tomorrow := redis_client.get('games_tomorrow')) is not None:
        return pickle.loads(games_tomorrow)

    data = get_games_tomorrow()
    dict_data = data.to_dict('records')
    redis_client.set('games_tomorrow', pickle.dumps(dict_data))
    redis_client.expire('games_tomorrow', DEFAULT_CACHE_TTL)
    return dict_data

@app.get('/games-predict')
async def games_predict(redis_client: cache = Depends(cache)) -> List[GameInfoWithPrediction]:
    if (games_predict := redis_client.get('games_predict')) is not None:
        return pickle.loads(games_predict)

    data = get_games_predict()
    dict_data = data.to_dict('records')
    redis_client.set('games_predict', pickle.dumps(dict_data))
    redis_client.expire('games_predict', DEFAULT_CACHE_TTL)
    return dict_data


@app.get('/games-today-predict')
async def games_today_predict(redis_client: cache = Depends(cache)) -> List[GameInfoWithPrediction]:
    if (games_today_predict := redis_client.get('games_today_predict')) is not None:
        return pickle.loads(games_today_predict)

    data = get_games_today_predict()
    dict_data = data.to_dict('records')
    redis_client.set('games_today_predict', pickle.dumps(dict_data))
    redis_client.expire('games_today_predict', DEFAULT_CACHE_TTL)
    return dict_data


@app.get('/games-tomorrow-predict')
async def games_tomorrow_predict(redis_client: cache = Depends(cache)) -> List[GameInfoWithPrediction]:
    if (games_tomorrow_predict := redis_client.get('games_tomorrow_predict')) is not None:
        return pickle.loads(games_tomorrow_predict)

    data = get_games_tomorrow_predict()
    dict_data = data.to_dict('records')
    redis_client.set('games_tomorrow_predict', pickle.dumps(dict_data))
    redis_client.expire('games_tomorrow_predict', DEFAULT_CACHE_TTL)
    return dict_data

@app.get('/stats')
async def get_stats(redis_client: cache = Depends(cache)) -> List[StatInfo]:
    if (stats_cache := redis_client.get('stats')) is not None:
        return pickle.loads(stats_cache)

    data = await stats()
    dict_data = data.to_dict('records')
    redis_client.set('stats', pickle.dumps(dict_data))
    redis_client.expire('stats', DEFAULT_CACHE_TTL)
    return dict_data
