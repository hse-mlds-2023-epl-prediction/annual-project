from pydantic import BaseModel


class GameInfo(BaseModel):
    home: str
    away: str
    ground: str


class GameInfoWithPrediction(GameInfo):
    predict: int
    proba: float


class Favorite(BaseModel):
    name: str
    user: int
