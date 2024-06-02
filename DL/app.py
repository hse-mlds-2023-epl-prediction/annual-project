import pandas as pd
from category_encoders import TargetEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

lag_features = [
            'result_lag_1_team_1',
            'result_lag_2_team_1',
            'result_lag_3_team_1',
            'result_lag_4_team_1',
            'result_lag_5_team_1',
            'result_lag_1_team_2',
            'result_lag_2_team_2',
            'result_lag_3_team_2',
            'result_lag_4_team_2',
            'result_lag_5_team_2',
            'game_lag_1',
            'game_lag_2',
            'game_lag_3'
            ]


def cat_features(df: pd.DataFrame, lag_features=lag_features) -> list:
    """
    Функция для определения категориальных признаков
    """

    cat_cols = [
                'gameweek_gameweek',
                'gameweek_compSeason_label',
                'ground_id',
            ]

    cat_cols += df.describe(include='object').columns.to_list() + lag_features

    return cat_cols


def pca_pipeline(df: pd.DataFrame,
                 y: pd.Series,
                 cat_cols: list,
                 num_cols: list,
                 n_components: int = 50,
                 pca: bool = True):
    """
    Функция для преобразования датасета с использованием PCA
    """
    df.loc[:, cat_cols] = df.loc[:, cat_cols].fillna(999)
    df.fillna(0, inplace=True)
    numeric_transformer = Pipeline(steps=[
        ('scaler', MinMaxScaler())])

    categorical_transformer = Pipeline(steps=[
        ('target_encoding', TargetEncoder())])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)])

    if pca:
        pca = PCA(n_components=n_components, random_state=42)
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('pca', pca)])

    else:
        pipeline = Pipeline(steps=[('preprocessor', preprocessor)])

    X_processed = pipeline.fit_transform(df, y)

    return X_processed, pipeline
