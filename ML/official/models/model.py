import pandas as pd
from catboost import CatBoostClassifier
import numpy as np
from pathlib import Path
import pickle
from src.config import param_boost, n_components
from src.app import cat_features, pca_pipeline

# Загрузка датасета
path = '../prepare_data/data/df_general.csv'
df = pd.read_csv(Path(path).resolve())
y = df['team_1_hue']
df.drop(['team_1_hue', 'match_id'], axis=1, inplace=True)

# Трансформация датасета
cat_cols = cat_features(df)
num_cols = list(set(df.columns.tolist()) - set(cat_cols))
X, pipeline = pca_pipeline(
    df,
    y,
    cat_cols,
    num_cols,
    n_components=n_components,
    pca=True
    )

# Подсчет весов классов
class_counts = np.bincount(y)
total_samples = np.sum(class_counts)
class_weights = total_samples / (len(class_counts) * class_counts)

# Обучение модели
model = CatBoostClassifier(
    verbose=False,
    class_weights=class_weights,
    loss_function='MultiClass',
    **param_boost)
model.fit(X, y)

# Cохранение модели и пайплайна
with open('../../../services/data/model.pickle', 'wb') as file:
    pickle.dump(model, file)

with open('../../../services/data/pipeline.pickle', 'wb') as file:
    pickle.dump(pipeline, file)
