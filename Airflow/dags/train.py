from airflow.operators.python import PythonOperator
from steps.predict.train_model import get_data, compute_weights,  get_params, train_model
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["train"],
    dag_id='train',
    schedule='@once',
) as dag:
        # инициализируем задачи DAG, указывая параметр python_callable
        get_data = PythonOperator(task_id='get_data', python_callable=get_data)
        compute_weights = PythonOperator(task_id='compute_weights', python_callable=compute_weights)
        get_params = PythonOperator(task_id='get_params', python_callable=get_params)
        train_model = PythonOperator(task_id='train_model', python_callable=train_model)
        [get_data, get_params] >> compute_weights >> train_model