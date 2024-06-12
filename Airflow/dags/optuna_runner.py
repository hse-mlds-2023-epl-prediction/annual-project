from airflow.operators.python import PythonOperator
from steps.predict.get_params import get_data, main
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["optuna"],
    dag_id='optuna',
    schedule='@once',
) as dag:
        # инициализируем задачи DAG, указывая параметр python_callable
        get_data = PythonOperator(task_id='get_data', python_callable=get_data)
        main = PythonOperator(task_id='main', python_callable=main)
        get_data >> main