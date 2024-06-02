import os

from pathlib import Path
import pandas as pd
import numpy as np
import mlflow
import os
import base64
import pickle
from mlxtend.feature_selection import SequentialFeatureSelector as SFS
from mlxtend.plotting import plot_sequential_feature_selection as plot_sfs
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier
from steps.src.config import  mlflow_exp
from steps.src.app import cat_features, pca_pipeline
from sklearn.metrics import f1_score, make_scorer


def load_df(**kwargs):
    ti = kwargs['ti']
    mlflow.set_tracking_uri(uri='http://5.104.75.226:5000')
    run_id = mlflow.search_runs(str(mlflow_exp['df_base']), order_by=['Created desc'])['run_id'][0]

    path = 'data'
    if not os.path.exists(path):
        os.makedirs(path)

    mlflow.artifacts.download_artifacts(
        artifact_uri=f'mlflow-artifacts:/{str(mlflow_exp['df_base'])}/{run_id}/artifacts/df.csv',
        dst_path=path)

    df = pd.read_csv(Path(path, 'df.csv'))
    df_pickle = pickle.dumps(df)
    df_base64 = base64.b64encode(df_pickle).decode('utf-8')
    kwargs['ti'].xcom_push(key='load_df', value=df_base64)


def sfs(**kwargs):
    ti = kwargs['ti']
    # Загрузка данных
    df_base64 = kwargs['ti'].xcom_pull(
        key='load_df', task_ids='load_df')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)

    # Преобразования
    y = df['team_1_hue']
    df.drop(['team_1_hue', 'match_id'], axis=1, inplace=True)
    cat_cols = cat_features(df)
    num_cols = list(set(df.columns.tolist()) - set(cat_cols))

    # Кодирование и нормализация
    X, pipeline = pca_pipeline(
        df,
        y,
        cat_cols,
        num_cols,
        pca=False
        )

    # Веса классов
    class_counts = np.bincount(y)
    total_samples = np.sum(class_counts)
    class_weights = total_samples / (len(class_counts) * class_counts)

    # Модель для отбора
    estimator = CatBoostClassifier(
        verbose=False,
        class_weights=class_weights,
        loss_function='MultiClass')

    f1_w = make_scorer(f1_score, average='weighted')
    sfs = SFS(estimator, k_features=300, forward=True, floating=False, scoring=f1_w, cv=4, n_jobs=-1)
    sfs = sfs.fit(X, y)

    sfs_df = pd.DataFrame.from_dict(sfs.get_metric_dict()).T
    prind(sfs_df)