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
#from optuna.integration.mlflow import MLflowCallback
from steps.src.config import mlflow_exp, num_trial
from steps.src.app import pca_pipeline , cat_features, compute_class_weights

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


def objective(trial, X, y, tscv, cat_cols):
        
    param = {
        "iterations": trial.suggest_int("iterations", 500, 2000),
        "depth": trial.suggest_int("depth", 2, 7),
        "learning_rate": trial.suggest_float("learning_rate", 0.001, 0.1, log=True),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 10),
        "random_strength": trial.suggest_float("random_strength", 1, 20),
        "bagging_temperature": trial.suggest_float("bagging_temperature", 0, 1),
        "border_count": trial.suggest_int("border_count", 32, 255),
        "leaf_estimation_iterations": trial.suggest_int("leaf_estimation_iterations", 1, 10),
        "loss_function": "MultiClass",
        "task_type": "CPU",
        "random_seed": 0,
        "verbose": False,
    }
    
    model = CatBoostClassifier(**param)
    preds = []
    tests = []
    
    with mlflow.start_run(experiment_id=str(mlflow_exp['optuna'])):
        for train_index, test_index in tscv.split(X, y):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]

            class_weights = compute_class_weights(y_train)
            class_weights_dict = {i: weight for i, weight in enumerate(class_weights)}

            model = CatBoostClassifier(class_weights=class_weights_dict, 
                                       **param)
            model.fit(X_train, y_train, eval_set=(X_test, y_test), cat_features=cat_cols, plot=False)
            pred = model.predict(X_test)
            preds.extend(pred.reshape(-1).tolist())
            tests.extend(y_test.tolist())

        f1_weighted = f1_score(tests, preds, average='weighted')
        f1_macro = f1_score(tests, preds, average='macro')
        accuracy = np.mean(np.array(preds) == np.array(tests))
        mlflow.log_params(param)
        mlflow.log_metric('accuracy', accuracy)
        mlflow.log_metric('f1_weighted', f1_weighted)
        mlflow.log_metric('f1_macro', f1_macro)
        mlflow.log_metric('len_preds', len(preds))
         
    return f1_macro
    
def main(**kwargs):
    ti = kwargs['ti']
    df_base64 = ti.xcom_pull(key='get_data', task_ids='get_data')
    df_pickle = base64.b64decode(df_base64)
    df = pickle.loads(df_pickle)
        
    cat_cols = cat_features(df)

    df[cat_cols] = df[cat_cols].astype(str)
    y = df['team_1_hue']
    df.drop(['team_1_hue', 'match_id'], axis=1, inplace=True)
    
    tscv = TimeSeriesSplit(n_splits=19 , test_size=20)
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, df, y, tscv, cat_cols), n_trials=num_trial)