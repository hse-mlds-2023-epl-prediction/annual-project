from pydantic import BaseModel


class GameInfo(BaseModel):
    Home: str
    Away: str
    Ground: str


class GameInfoWithPrediction(GameInfo):
    Predict: int
    Proba: float


class Favorite(BaseModel):
    name: str
    user: int
