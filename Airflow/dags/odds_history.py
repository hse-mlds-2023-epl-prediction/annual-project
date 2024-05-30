from airflow.operators.python import PythonOperator
from steps.pars.get_odds_last import parser, create_db
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["odds history"],
    dag_id='get_odds_history',
    schedule='@once',
) as dag:
        # инициализируем задачи DAG, указывая параметр python_callable
        parser_step = PythonOperator(task_id='parser', python_callable=parser)
        create_db_step = PythonOperator(task_id='create_db', python_callable=create_db)
        #load_data_step = PythonOperator(task_id='load_data', python_callable=load_data)
        parser_step >> create_db_step