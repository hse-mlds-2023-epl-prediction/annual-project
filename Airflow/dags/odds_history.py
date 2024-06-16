from airflow.operators.python import PythonOperator
from steps.pars.get_odds_last import parser_odds, get_clubs, prepare, load_data
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["odds history"],
    dag_id='get_odds_history',
    schedule='@once',
) as dag:
        # инициализируем задачи DAG, указывая параметр python_callable
        parser_odds = PythonOperator(task_id='parser_odds', python_callable=parser_odds)
        get_clubs = PythonOperator(task_id='get_clubs', python_callable=get_clubs)
        prepare = PythonOperator(task_id='prepare', python_callable=prepare)
        load_data = PythonOperator(task_id='load_data', python_callable=load_data)
        [parser_odds, get_clubs] >> prepare >> load_data
        