import json
import certifi
from urllib.request import urlopen
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc

def get_jsonparsed_data(url: str) -> list[dict]:
    """
    Parses JSON data from a given URL using SSL certificate validation.

    Parameters
    ----------
    url : str
        Fully constructed URL to query the API.

    Returns
    -------
    list[dict]
        Parsed JSON content from the API response as a list of dictionaries.
    """
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

def fetch_eod_price_data_arrow(ticker: str, start_date: str, end_date: str, api_key: str) -> pa.Table:
    url = (
        "https://financialmodelingprep.com/stable/historical-price-eod/full"
        f"?symbol={ticker}&from={start_date}&to={end_date}&apikey={api_key}"
    )
    data = get_jsonparsed_data(url)
    if not isinstance(data, list):
        raise ValueError(f"Unexpected format returned for {ticker}")
    return pa.Table.from_pylist(data)

def fetch_eod_price_data(
    ticker: str,
    start_date: str,
    end_date: str,
    api_key: str
) -> pd.DataFrame:
    """
    Fetches historical end-of-day (EOD) stock price data from Financial Modeling Prep.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol (e.g., "AAPL").
    start_date : str
        Start date in 'YYYY-MM-DD' format.
    end_date : str
        End date in 'YYYY-MM-DD' format.
    api_key : str
        Your API key from Financial Modeling Prep.

    Returns
    -------
    pd.DataFrame
        DataFrame with historical EOD data indexed by date.

    Raises
    ------
    ValueError
        If the API response is not a valid list of dictionaries.
    """
    url = (
        "https://financialmodelingprep.com/stable/historical-price-eod/full"
        f"?symbol={ticker}&from={start_date}&to={end_date}&apikey={api_key}"
    )

    data = get_jsonparsed_data(url)

    if not isinstance(data, list):
        raise ValueError(f"Unexpected data format returned from API for {ticker}")

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df.sort_index()