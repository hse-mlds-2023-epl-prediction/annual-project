from datetime import datetime
from pydantic import BaseModel


class GameInfo(BaseModel):
    home: str
    away: str
    ground: str
    date: datetime


class GameInfoWithPrediction(GameInfo):
    predict: int
    proba: list[float]


class Favorite(BaseModel):
    name: str
    user: int
