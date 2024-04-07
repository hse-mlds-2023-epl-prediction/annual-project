import pandas as pd
import pickle
from catboost import CatBoostClassifier

df = pd.read_csv('../prepare_data/data/df_temp_65.csv')

df = df[df['gameweek_compSeason_label'] > 2019]

n = 100

train = df.iloc[n:, :]
val = df.iloc[:n, :]

y_train = train['team_1_hue']
x_train = train.drop('team_1_hue', axis=1)

y_val = val['team_1_hue']
x_val = val.drop('team_1_hue', axis=1)

cat = ['gameweek_gameweek',
       'gameweek_compSeason_label',
       'teams_team_1_name',
       'teams_team_2_name',
       'ground_name']

model = CatBoostClassifier(
    iterations=2000,
    learning_rate=0.0005,
    loss_function='MultiClass',
    depth=4,
    l2_leaf_reg=6
    )

model.fit(x_train, y_train, cat_features=cat, verbose=False)

with open('pickle/catboost.pickle', 'wb') as file:
    pickle.dump(model, file)

with open('../../../services/data/catboost.pickle', 'wb') as file:
    pickle.dump(model, file)


name_cols = 'pickle/name_cols.pickle'

col_pkl = list(df.columns)
col_pkl.remove('team_1_hue')

with open(name_cols, 'wb') as file:
    pickle.dump(col_pkl, file)


with open('../../../services/data/name_cols.pickle', 'wb') as file:
    pickle.dump(col_pkl, file)
