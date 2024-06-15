import optuna
import numpy as np
import mlflow
from dotenv import load_dotenv
import pickle
import base64
import os
import io
import pandas as pd
from sklearn.metrics import make_scorer, accuracy_score, f1_score
from sklearn.model_selection import TimeSeriesSplit
from catboost import CatBoostClassifier
from steps.src.config import mlflow_exp, num_trial
from steps.src.app import cat_features, compute_class_weights
from steps.src.models_py import CatBoostParams

load_dotenv()


def get_data(**kwargs):
    ti = kwargs['ti']
    experiment_ids=str(mlflow_exp['df_base'])
    runs = mlflow.search_runs(experiment_ids=experiment_ids, order_by=['Created desc'])
    runs = runs[runs['status']=='FINISHED']
    run_id = runs.iloc[0,0]
    if run_id:
        artifact_uri=f'mlflow-artifacts:/{experiment_ids}/{run_id}/artifacts/df.csv'
        local_path = mlflow.artifacts.download_artifacts(artifact_uri)
        df = pd.read_csv(local_path)
        print(df)
        df_pickle = pickle.dumps(df)
        df_base64 = base64.b64encode(df_pickle).decode('utf-8')
        kwargs['ti'].xcom_push(key='get_data', value=df_base64)
    else:
        print("error")
        return None
    

def compute_weights(**kwargs):
    ti = kwargs['ti']
    df_base64 = ti.xcom_pull(key='get_data', task_ids='get_data')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)

    y = df['team_1_hue']
    class_weights = compute_class_weights(y)
    class_weights_dict = {i: weight for i, weight in enumerate(class_weights)}

    kwargs['ti'].xcom_push(key='compute_weights', value=class_weights_dict)


def get_params(**kwargs):
    ti = kwargs['ti']
    experiment_ids=str(mlflow_exp['optuna'])

    # get run_id with max f1
    df = mlflow.search_runs(experiment_ids=experiment_ids)
    df = df.sort_values(by='start_time', ascending=False).iloc[:num_trial, :]
    df.sort_values(by='metrics.f1_score', ascending=False, inplace=True)
    run_id = df.iloc[0, 0]
    print(f'run_id: {run_id}')
    # get params
    run = mlflow.get_run(run_id)
    params = run.data.params

    kwargs['ti'].xcom_push(key='get_params', value=params)


def train_model(**kwargs):
    ti = kwargs['ti']
    df_base64 = ti.xcom_pull(key='get_data', task_ids='get_data')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)

    param = ti.xcom_pull(key='get_params', task_ids='get_params')
    param = CatBoostParams(**param)
    param = param.dict()
    
    cat_cols = cat_features(df)
    df[cat_cols] = df[cat_cols].astype(str)
    
    class_weights_dict = ti.xcom_pull(key='compute_weights', task_ids='compute_weights')

    X = df.drop(['team_1_hue'], axis=1)
    y = df['team_1_hue']

    # Define the model
    model = CatBoostClassifier(class_weights=class_weights_dict, **param)
    model.fit(X, y, cat_features=cat_cols)

    with mlflow.start_run(experiment_id=mlflow_exp['model']) as run:
        model_info = mlflow.catboost.log_model(cb_model=model, artifact_path="models") 



