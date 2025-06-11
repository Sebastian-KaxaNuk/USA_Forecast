import pandas as pd

#%%

def add_lagged_return_columns(
    df: pd.DataFrame,
    column: str,
    lags: tuple[int],
    prefix: str = "P"
) -> pd.DataFrame:
    """
    Adds percentage return columns based on specified lags to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the time series data.
    column : str
        Name of the column to calculate lagged returns from (e.g., 'close').
    lags : tuple[int]
        Tuple of integer lags (e.g., [5, 10, 15]) to compute returns over.
    prefix : str, optional
        Prefix for the new columns (default is "P").

    Returns
    -------
    pd.DataFrame
        DataFrame with new lagged percentage return columns added.

    Example
    -------
    Adds 'P5' and 'P10' columns to the DataFrame.
    """
    df = df.copy()

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    lag_columns = []

    for lag in lags:
        col_name = f"{prefix}{lag}"
        df[col_name] = (df[column] / df[column].shift(lag) - 1) * 100
        lag_columns.append(col_name)

    df["Total_%"] = df[lag_columns].sum(axis=1)

    return df


