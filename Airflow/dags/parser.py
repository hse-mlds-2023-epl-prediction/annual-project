from airflow.operators.python import PythonOperator # импортируем класс оператора 
from steps.pars import pars # импортируем фукнции с логикой шагов
#from steps.messages import send_telegram_success_message, send_telegram_failure_message
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["parser"],
    dag_id='parser',
    schedule='@once',
    #on_success_callback=send_telegram_success_message,
    #on_failure_callback=send_telegram_failure_message
    ) as dag:

    # инициализируем задачи DAG, указывая параметр python_callable
    parser = PythonOperator(task_id='parser', python_callable=pars)
    #extract_step = PythonOperator(task_id='extract_step', python_callable=extract)
    #transform_step = PythonOperator(task_id='transform_step', python_callable=transform)
    #load_step = PythonOperator(task_id='load_step', python_callable=load) 

    parser# >> extract_step >> transform_step >> load_step