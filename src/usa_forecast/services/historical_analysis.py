#Libraries
import pandas as pd

#%%

FREQUENCY_MAP = {
    "weekly": "W",
    "monthly": "M",
    "quarterly": "QE",
    "semiannual": "2Q",
    "annual": "A"
}


def generate_summary_dates(
        all_dates: pd.DatetimeIndex,
        configuration
) -> pd.DatetimeIndex:
    """
    Generates the list of dates on which to build the summary_df,
    based on the configuration parameters and max lag buffer.

    Parameters
    ----------
    all_dates : pd.DatetimeIndex
        Full list of business dates.
    configuration : Configuration
        Loaded configuration entity.

    Returns
    -------
    pd.DatetimeIndex
        Dates selected for generating summaries.
    """
    max_lag = max(configuration.window_shift)
    available_dates = all_dates[max_lag:]

    mode = configuration.summary_mode.lower()

    if mode == "latest":
        return pd.DatetimeIndex([available_dates[-1]])

    elif mode == "daily":
        return pd.DatetimeIndex(available_dates)

    elif mode == "custom":
        return pd.DatetimeIndex([d for d in available_dates if
                                 configuration.summary_start_date <= d.date() <= configuration.summary_end_date])

    elif mode == "frequency":
        freq_key = configuration.summary_frequency.lower()
        if freq_key not in FREQUENCY_MAP:
            raise ValueError(f"Invalid summary_frequency: {configuration.summary_frequency}")

        pandas_freq = FREQUENCY_MAP[freq_key]
        candidate_dates = pd.date_range(start=configuration.summary_start_date, end=configuration.summary_end_date,
                                        freq=pandas_freq)
        return pd.DatetimeIndex([d for d in candidate_dates if d in available_dates])

    else:
        raise ValueError(f"Invalid summary_mode: {configuration.summary_mode}")

def extract_snapshot(
                     data_dict: dict[str, pd.DataFrame],
                     snapshot_date: pd.Timestamp
                     ) -> dict[str, pd.DataFrame]:
    """
    Extracts the most recent available row for each ticker on a specific snapshot date.

    Parameters
    ----------
    data_dict : dict[str, pd.DataFrame]
        Dictionary of DataFrames by ticker, each with a datetime index.
    snapshot_date : pd.Timestamp
        Target date for extracting the snapshot.

    Returns
    -------
    dict[str, pd.DataFrame]
        New dictionary with a single-row DataFrame per ticker, corresponding to the snapshot date.
    """
    snapshot = {}

    for ticker, df in data_dict.items():
        if snapshot_date in df.index:
            snapshot[ticker] = df.loc[[snapshot_date]]
        else:
            valid_dates = df.index[df.index <= snapshot_date]
            if not valid_dates.empty:
                snapshot[ticker] = df.loc[[valid_dates[-1]]]

    return snapshot
