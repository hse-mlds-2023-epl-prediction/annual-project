from sqlalchemy import MetaData, Table, Column, String, Float, Date, DateTime, Integer, UniqueConstraint, inspect
from airflow.providers.postgres.hooks.postgres import PostgresHook
from steps.src.config import conn_id


metadata = MetaData()





