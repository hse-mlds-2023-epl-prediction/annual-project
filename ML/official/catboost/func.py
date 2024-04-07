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

    if len(features_to_remove) > 0:
        return rm_high_corr_feat(df, thr, exc_col)
    else:
        return df
