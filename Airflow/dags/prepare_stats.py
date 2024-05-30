from airflow.operators.python import PythonOperator
from steps.prepare.prep_stats import prepare_club, prepare_game, prepare_players, get_df
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["get dataframe"],
    dag_id='dataframe',
    schedule='@once',
) as dag:

    # инициализируем задачи DAG, указывая параметр python_callable
    prepare_club = PythonOperator(
        task_id='prepare_club',
        python_callable=prepare_club,
        provide_context=True)

    prepare_game = PythonOperator(
        task_id='prepare_game',
        python_callable=prepare_game,
        provide_context=True,)

    prepare_players = PythonOperator(
        task_id='prepare_players',
        python_callable=prepare_players,
        provide_context=True,)

    get_df = PythonOperator(
        task_id='get_df',
        python_callable=get_df,
        provide_context=True,)

    [prepare_club, prepare_game, prepare_players] >> get_df