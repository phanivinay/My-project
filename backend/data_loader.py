# backend/data_loader.py
import pandas as pd

def load_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xls', '.xlsx')):
        # Header is on the 6th row (1-based) → index 5 in pandas
        df = pd.read_excel(uploaded_file, header=5)
        # Remove any Unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
    else:
        raise ValueError("Unsupported file type. Use CSV or Excel.")
    return df

# backend/data_loader.py

def auto_clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df.empty:
        return df

    # Fix column names (strip whitespace)
    df.columns = df.columns.str.strip()

    # Force-convert known numeric columns
    for col in df.columns:
        if 'Duration' in col or 'Minutes' in col or 'Score' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert timestamp
    if 'Call Timestamp' in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Handle missing values
    for col in df.columns:
        if df[col].dtype in ['object', 'string', 'category']:
            mode = df[col].mode()
            df[col].fillna(mode[0] if not mode.empty else "Unknown", inplace=True)
        else:
            df[col].fillna(df[col].median(), inplace=True)

    return df