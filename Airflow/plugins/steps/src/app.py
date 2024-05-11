from sqlalchemy import MetaData, Table, Column, String, Float, Date, DateTime, Integer, DateTime, UniqueConstraint, inspect
from airflow.providers.postgres.hooks.postgres import PostgresHook
from steps.src.model_table import table_season
from steps.src.config import conn_id


def create_table(table: Table, conn_id):
    # Функция создания таблицы
    hook = PostgresHook(conn_id)
    engine = hook.get_sqlalchemy_engine()
    metadata = MetaData()

    if not inspect(engine).has_table(table.name):
        metadata.create_all(engine)
