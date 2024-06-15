from typing import List
from fastapi import FastAPI, Depends

from src.footballapi import get_game_by_limit, get_games_tomorrow
from src.footballapi import get_games_today, get_games_today_predict
from src.footballapi import get_games_tomorrow_predict, get_games_predict
from src.footballapi import get_favorite, helthy_services, add_comand
from src.models import GameInfo, GameInfoWithPrediction, Favorite
from src.stats import stats, StatInfo
from src.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from databases import Database

app = FastAPI()

DEFAULT_CACHE_TTL = 1
DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

database = Database(DATABASE_URL)
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class GameInfoEntity(Base):
    __tablename__ = "game_info_entity"

    id = Column(Integer, primary_key=True, index=True)
    home = Column(String)
    away = Column(String)
    ground = Column(String)
    predict = Column(Integer, nullable=True)
    proba = Column(Float, nullable=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/games')
@cache(expire=DEFAULT_CACHE_TTL)
async def games(limit: int = 10, db: Session = Depends(get_db)) -> List[GameInfo]:
    """
    Десят ближайших игр
    """
    # return get_game_by_limit(limit).to_dict('records')
    return db.query(GameInfoEntity).all()


@app.get('/games-today')
@cache(expire=DEFAULT_CACHE_TTL)
async def games_today(db: Session = Depends(get_db)) -> List[GameInfo]:
    """
    Игры сегодня
    """
    # return get_games_today().to_dict('records')
    new_entity = GameInfoEntity(home='11', away='22', ground='33')

    db.add(new_entity)

    db.commit()

@app.get('/games-tomorrow')
@cache(expire=DEFAULT_CACHE_TTL)
async def games_tomorrow() -> List[GameInfo]:
    """
    Игры завтра
    """
    return get_games_tomorrow().to_dict('records')


@app.get('/games-predict')
@cache(expire=DEFAULT_CACHE_TTL)
async def games_predict() -> List[GameInfoWithPrediction]:
    """
    Предсказания ближайших 10 игр
    """
    return get_games_predict().to_dict('records')


@app.get('/games-today-predict')
@cache(expire=DEFAULT_CACHE_TTL)
async def games_today_predict() -> List[GameInfoWithPrediction]:
    """
    Предсказания игр сегодня
    """
    return get_games_today_predict().to_dict('records')


@app.get('/games-tomorrow-predict')
@cache(expire=DEFAULT_CACHE_TTL)
async def games_tomorrow_predict() -> List[GameInfoWithPrediction]:
    """
    Предсказания игр на завтра
    """
    return get_games_tomorrow_predict().to_dict('records')


@app.get('/stats')
@cache(expire=DEFAULT_CACHE_TTL)
async def get_stats() -> List[StatInfo]:
    """
    Статистика
    """
    data = await stats()
    return data.to_dict('records')


@app.post('/add_favorite')
async def add_favorite(req: Favorite) -> str:
    """
    Добавление команды в избранное
    """
    resp = add_comand(req.name, req.user)
    return resp


@app.get('/get_favorite_comand')
async def get_favorite_comand(user: int):
    """
    Получение избранных команд
    """
    return get_favorite(user)


@app.get('/health')
async def health() -> dict:
    """
    Проверка сервисов
    """
    result = helthy_services()
    return result


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}"
        )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
