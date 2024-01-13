import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score as auc
import numpy as np

def split_data(data, label, target, year=2023):
    #Input: data - dataframe
    #       label - name feature where is season
    #       target - namee target feature
    #       year - year for split by validation part

    #Output: x_train
    #        y_train
    #        x_val
    #        y_val

    train = data[data[label] != year]
    val = data[data[label] == year]

    y_train = train[target]
    x_train = train.drop(target, axis=1)

    y_val = val[target]
    x_val = val.drop(target, axis=1)

    return x_train, y_train, x_val, y_val


             

def rm_high_corr_feat(df, thr, exc_col):
    features_to_remove = set()

    corr_matrix = df.iloc[:, exc_col:].corr()

    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > thr:
                colname = corr_matrix.columns[i]
                features_to_remove.add(colname)

    # remove feature with corr > thr
    df = df.drop(columns=features_to_remove)

    # 
    if len(features_to_remove) > 0:
        return rm_high_corr_feat(df, thr, exc_col)
    else:
        return df