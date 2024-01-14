from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

from src.footballapi import get_some_games

class GameInfo(BaseModel):
    Home: str
    Away: str
    Ground: str

app = FastAPI()

@app.get('/games')
async def games() -> List[GameInfo]:
    data = get_some_games(10)
    return data.to_dict('records')
