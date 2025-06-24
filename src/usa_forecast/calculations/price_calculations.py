import pandas as pd
import logging
import pyarrow as pa

logger = logging.getLogger('myAppLogger')

#%%

def add_52_week_low_column(
    df: pd.DataFrame,
    column: str,
    window_days: int = 252,
    output_column: str = "52w_low"
) -> pd.DataFrame:
    """
    Adds a column representing the rolling minimum (52-week low) of a given column.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing time series data.
    column : str
        Column from which to compute the 52-week low (e.g., 'close').
    window_days : int, optional
        Rolling window size in days (default is 252, approximating 52 trading weeks).
    output_column : str, optional
        Name of the output column (default is '52w_low').

    Returns
    -------
    pd.DataFrame
        DataFrame with the additional column containing the 52-week low values.

    Raises
    ------
    ValueError
        If the specified column is not in the DataFrame.
    """
    df = df.copy()

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    df[output_column] = df[column].rolling(window=window_days, min_periods=1).min()
    return df

def add_52_week_low_column_arrow(table: pa.Table, low_column: str = "low", output_column: str = "52_week_low") -> pa.Table:
    df = table.to_pandas()
    df[output_column] = df[low_column].rolling(window=252, min_periods=1).min()
    return pa.Table.from_pandas(df)

def calculate_price_targets(
    df: pd.DataFrame,
    column: str,
    lags: tuple[int, ...],
    lookback: int = 100,
    prefix: str = "P"
) -> pd.DataFrame:
    """
    Calculates rolling max/min % changes and price targets for given lags.

    Parameters
    ----------
    df : pd.DataFrame
        Time series DataFrame containing price and percentage lag columns.
    column : str
        Name of the price column (e.g., 'close').
    lags : tuple[int, ...]
        Tuple of integer lag values (e.g., (5, 10, 15)).
    lookback : int
        Number of days to look back for max/min % calculations.
    prefix : str
        Prefix for lag return columns (default 'P').

    Returns
    -------
    pd.DataFrame
        DataFrame with all calculated target columns.
    """
    df = df.copy()

    max_pct_cols = {}
    min_pct_cols = {}
    max_price_targets = {}
    min_price_targets = {}

    for lag in lags:
        lag_col = f"{prefix}{lag}"

        if lag_col not in df.columns:
            raise ValueError(f"Missing lagged return column: '{lag_col}'")

        max_pct = df[lag_col].rolling(window=lookback, min_periods=1).max()
        min_pct = df[lag_col].rolling(window=lookback, min_periods=1).min()

        max_pct_cols[f"Max%_{lag}"] = max_pct
        min_pct_cols[f"Min%_{lag}"] = min_pct

        shifted_price = df[column].shift(lag)
        max_price_targets[f"MaxPT_{lag}"] = shifted_price * (1 + max_pct / 100)
        min_price_targets[f"MinPT_{lag}"] = shifted_price * (1 + min_pct / 100)

    df = df.assign(**max_pct_cols, **min_pct_cols, **max_price_targets, **min_price_targets)

    maxpt_df = pd.concat(max_price_targets.values(), axis=1)
    minpt_df = pd.concat(min_price_targets.values(), axis=1)
    maxpct_df = pd.concat(max_pct_cols.values(), axis=1)

    df["MinMax%"] = maxpct_df.min(axis=1)
    df["Alcance"] = df[column] * (1 + df["MinMax%"] / 100)
    df["Max"] = df["52_week_low"] * (1 + df["MinMax%"] / 100)

    df["MaxMax"] = maxpt_df.max(axis=1)
    df["AvgMax"] = maxpt_df.mean(axis=1)
    df["MinMax"] = maxpt_df.min(axis=1)

    df["MaxMin"] = minpt_df.max(axis=1)
    df["AvgMin"] = minpt_df.mean(axis=1)
    df["MinMin"] = minpt_df.min(axis=1)

    return df

def process_all_tickers(
    data_dict: dict[str, pd.DataFrame],
    column: str = "close",
    lags: tuple[int, ...] = (5, 10, 15),
    lookback: int = 100
) -> dict[str, pd.DataFrame]:
    """
    Applies price target calculations to all tickers in a dictionary.

    Parameters
    ----------
    data_dict : dict[str, pd.DataFrame]
        Dictionary mapping ticker symbols to DataFrames with price data.
    column : str
        Name of the price column to base calculations on.
    lags : tuple[int, ...]
        Tuple of lag days to use for % return calculations.
    lookback : int
        Number of days for rolling max/min window.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary with ticker as key and enriched DataFrame as value.
    """
    results = {}
    for ticker, df in data_dict.items():
        try:
            enriched_df = calculate_price_targets(
                df=df,
                column=column,
                lags=lags,
                lookback=lookback
            )
            results[ticker] = enriched_df
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
    return results

def build_summary_dataframe(data_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Builds a summary DataFrame where each column is a ticker and rows are key metrics:
    - Close: last close price
    - High Min: MinMax
    - High Avg: AvgMax
    - High Max: MaxMax
    - Low Min: MaxMin
    - Low Avg: AvgMin
    - Low Max: MinMin
    - Min Price: last low
    - High Min Adjusted: adjusted target using low and MinMax

    Parameters
    ----------
    data_dict : dict[str, pd.DataFrame]
        Dictionary mapping ticker to enriched DataFrame.

    Returns
    -------
    pd.DataFrame
        Summary table with index as metrics and columns as tickers.
    """
    index_labels = [
        "Close",
        "High Min",         # ← MinMax
        "High Avg",         # ← AvgMax
        "High Max",         # ← MaxMax
        "Low Min",          # ← MaxMin
        "Low Avg",          # ← AvgMin
        "Low Max",          # ← MinMin
        "Min Price",        # ← low
    ]

    summary_df = pd.DataFrame(index=index_labels)

    for ticker, df in data_dict.items():
        last = df.iloc[-1]

        close = last["close"]
        low = last["52_week_low"]
        minmax = last["MinMax"]
        avgmax = last["AvgMax"]
        maxmax = last["MaxMax"]
        maxmin = last["MaxMin"]
        avgmin = last["AvgMin"]
        minmin = last["MinMin"]

        summary_df[ticker] = [
            close,
            minmax,
            avgmax,
            maxmax,
            maxmin,
            avgmin,
            minmin,
            low,
        ]

    return summary_df
