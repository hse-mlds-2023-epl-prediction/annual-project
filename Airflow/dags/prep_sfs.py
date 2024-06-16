from airflow.operators.python import PythonOperator
from steps.prepare.sfs import load_df, sfs
import pendulum

from airflow import DAG
with DAG(
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    tags=["sfs"],
    dag_id='sfs',
    schedule='@once',
) as dag:

    load_df = PythonOperator(
        task_id='load_df',
        python_callable=load_df,
        provide_context=True)

    sfs = PythonOperator(
        task_id='sfs',
        python_callable=sfs,
        provide_context=True)

    load_df >> sfs