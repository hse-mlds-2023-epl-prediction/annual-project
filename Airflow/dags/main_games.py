from airflow.operators.python import PythonOperator
from steps.pars.get_matches import get_id_season, get_matches, create_db, load_data
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["get games info"],
    dag_id='games',
    schedule='@once',
) as dag:

    # инициализируем задачи DAG, указывая параметр python_callable
    get_id_step = PythonOperator(
        task_id='get_id_step',
        python_callable=get_id_season,
        provide_context=True)

    get_matches_step = PythonOperator(
        task_id='get_matches_step',
        python_callable=get_matches,
        provide_context=True,)

    create_db_step = PythonOperator(
        task_id='create_db',
        python_callable=create_db,
        )

    load_data_step = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        provide_context=True,)

    [create_db_step, get_id_step] >> get_matches_step >> load_data_step