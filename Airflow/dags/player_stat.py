from airflow.operators.python import PythonOperator
from steps.pars.get_player_stat import get_id_season, get_club_id, parser, load_data
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["get player stat"],
    dag_id='player_stat',
    schedule='@once',
) as dag:

    # инициализируем задачи DAG, указывая параметр python_callable
    get_id_season = PythonOperator(
        task_id='get_id_season',
        python_callable=get_id_season,
        provide_context=True)

    get_club_id = PythonOperator(
        task_id='get_club_id',
        python_callable=get_club_id,
        provide_context=True,)

    parser = PythonOperator(
        task_id='parser',
        python_callable=parser,
        provide_context=True,)

    load_data = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        provide_context=True,)

    [get_id_season, get_club_id] >> parser >> load_data