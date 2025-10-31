import pandas as pd

def get_basic_stats(df: pd.DataFrame):
    stats = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_cells": df.isnull().sum().sum(),
        "numeric_cols": df.select_dtypes(include='number').columns.tolist(),
        "categorical_cols": df.select_dtypes(exclude='number').columns.tolist(),
    }
    return stats

def get_column_summary(df: pd.DataFrame):
    return df.head(5).to_dict(orient="records")