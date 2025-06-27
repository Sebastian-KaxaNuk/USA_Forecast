from src.usa_forecast.config_handlers.excel_configurator import ExcelConfigurator
import pandas as pd
import json
from urllib.request import urlopen
import certifi

#%%

configurator = ExcelConfigurator(
    file_path='Config/parameters_configuration.xlsx',
)

configuration = configurator.get_configuration()

#%%

API_KEY = configuration.fmp_api_key
symbol = "AMZN"
from_date = "2025-06-27"
to_date = "2025-06-27"

#%%

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

def fetch_eod_last_1m_price_data(ticker: str,
                                 api_key: str) -> pd.DataFrame:
    """
    :param ticker:
    :param api_key:
    :return:
    """
    url_one_min = (
        f"https://financialmodelingprep.com/api/v3/historical-chart/1min/{ticker}?apikey={api_key}"
    )

    data_one = get_jsonparsed_data(url=url_one_min)

    if not isinstance(data_one, list):
        raise ValueError(f"Unexpected data format returned from API for {ticker}")

    df = pd.DataFrame(data_one)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df = df.sort_index()

    last_data = df.tail(1)

    # last_data_clean = last_data.T

    return last_data

