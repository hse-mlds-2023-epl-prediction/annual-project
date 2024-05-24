from airflow.operators.python import PythonOperator
from steps.get_basic_club import get_basic_club, load_basic_club
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["basic club info"],
    dag_id='basic_club',
    schedule='@once',
) as dag:

    get_basic_club = PythonOperator(
        task_id='get_basic_club',
        python_callable=get_basic_club,
        provide_context=True)
    
    load_basic_club = PythonOperator(
        task_id='load_basic_club',
        python_callable=load_basic_club,
        provide_context=True)
    
    get_basic_club >> load_basic_club
