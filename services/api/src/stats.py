import os
import pandas as pd
from pydantic import BaseModel

class StatInfo(BaseModel):
    team_name: str
    avg_score_home: float
    avg_yellow_cards_count_home: float
    avg_score_away: float
    avg_yellow_cards_count_away: float

async def stats():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__)) + '/data/2023_2024_matches.csv')

    avg_scores_home = df.groupby('home_team_name')['home_team_score'].mean()
    avg_scores_away = df.groupby('away_team_name')['away_team_score'].mean()

    avg_yellow_cards_count_home = df.groupby('home_team_name')['home_team_yellow_cards_count'].mean()
    avg_yellow_cards_count_away = df.groupby('away_team_name')['away_team_yellow_cards_count'].mean()


    df_home = pd.DataFrame({
        'team_name': avg_scores_home.index,
        'avg_score_home': avg_scores_home.values,
        'avg_yellow_cards_count_home': avg_yellow_cards_count_home.values
    })
    df_away = pd.DataFrame({
        'team_name': avg_scores_away.index,
        'avg_score_away': avg_scores_away.values,
        'avg_yellow_cards_count_away': avg_yellow_cards_count_away.values
    })

    result_df = pd.merge(df_home, df_away, on='team_name', how='outer')

    return result_df
