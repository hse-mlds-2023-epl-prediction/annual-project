from airflow.operators.python import PythonOperator
from steps.get_people import get_id_season, get_club_id, parser
from steps.get_people import load_players, load_goalkippers, load_officials
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["get people"],
    dag_id='people',
    schedule='@once',
) as dag:

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

    load_players = PythonOperator(
        task_id='load_players',
        python_callable=load_players,
        provide_context=True,)
    
    load_goalkippers = PythonOperator(
        task_id='load_goalkippers',
        python_callable=load_goalkippers,
        provide_context=True,)

    load_officials = PythonOperator(
        task_id='load_officials',
        python_callable=load_officials,
        provide_context=True,)
    
    [get_id_season, get_club_id] >> parser >> [load_players, load_goalkippers, load_officials]
