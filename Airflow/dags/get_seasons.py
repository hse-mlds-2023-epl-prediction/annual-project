from airflow.operators.python import PythonOperator
from steps.get_id_season import parser, create_db, load_data
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["create table seasons"],
    dag_id='get_seasons',
    schedule='@once',
) as dag:

    # инициализируем задачи DAG, указывая параметр python_callable
    parser_step = PythonOperator(task_id='parser___', python_callable=parser)
    create_db_step = PythonOperator(task_id='create_db', python_callable=create_db)
    load_data_step = PythonOperator(task_id='load_data', python_callable=load_data, op_args=[parser()])
    parser_step >> create_db_step >> load_data_step
