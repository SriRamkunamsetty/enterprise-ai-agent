# data/preprocess.py

import pandas as pd
from io import StringIO

def csv_to_dataframe(csv_string: str):
    """Convert CSV string → pandas DataFrame."""
    return pd.read_csv(StringIO(csv_string))

def clean_stock_data(df: pd.DataFrame):
    """Basic preprocessing for ML forecasting."""
    df = df.dropna()
    df['Return'] = df['Close'].pct_change()
    df = df.dropna()
    return df

def summarize(df: pd.DataFrame):
    """Return a simple summary dictionary."""
    return {
        "start": str(df.index[0]),
        "end": str(df.index[-1]),
        "mean_close": float(df["Close"].mean()),
        "min_close": float(df["Close"].min()),
        "max_close": float(df["Close"].max()),
    }