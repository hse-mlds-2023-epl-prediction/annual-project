from sqlalchemy import MetaData, Table, Column, String, Float, Date, DateTime, Integer, UniqueConstraint, inspect
from airflow.providers.postgres.hooks.postgres import PostgresHook
from steps.src.config import conn_id


metadata = MetaData()

table_season = Table(
    'seasons', metadata,
    Column('id', Integer, primary_key=True),
    Column('label', String),
    )


table_odds = Table(
    'odds', metadata,
    Column('id', primary_key=True, autoincrement=True),
    Column('home_name', String),
    Column('away_name', String),
    Column('result', String),
    Column('home_team_result', Integer),
    Column('away_team_result', Integer),
    Column('home_avg_odds', Float),
    Column('draw_avg_odds', Float),
    Column('away_avg_odds', Float),
    Column('season', String),
    Column('date_start_timestamp', DateTime),
)
