#Modules
from src.usa_forecast.data_download import fmp_mkt_data as fmd
from src.usa_forecast.calculations import lags_adding as la
from src.usa_forecast.calculations import price_calculations as pc
from src.usa_forecast.aux_functions import save_read_csv_excel as sr
from src.usa_forecast.services import historical_analysis as ha
from src.usa_forecast.entities.configuration import Configuration

#Libraries
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from datetime import date

logger = logging.getLogger('myAppLogger')

#%%

def is_data_up_to_date(
    file_path: str,
    start_date: date,
    end_date: date,
    lags: tuple[int, ...],
    stay_update: str
) -> bool:
    """
    Checks if the local file exists and is valid for use without re-downloading data.

    Parameters
    ----------
    file_path : str
        Path to the local ticker CSV file.
    start_date : date
        Required start date for the analysis.
    end_date : date
        Required end date for the analysis.
    lags : tuple[int, ...]
        Tuple of lag values (e.g., (5, 10, 15)).
    stay_update : str
        String indicating whether to use local data if available ("True" or "False").

    Returns
    -------
    bool
        True if file exists, contains required date range and columns. False otherwise.
    """
    if stay_update != "True" or not os.path.exists(file_path):
        return False

    try:
        # logger.info(f"Reading data from {file_path}")
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index)

        file_min_date = df.index.min().date()
        file_max_date = df.index.max().date()

        start_date = pd.to_datetime(start_date).date()
        end_date = pd.to_datetime(end_date).date()

        logger.debug(f"File covers: {file_min_date} to {file_max_date}. Needed: {start_date} to {end_date}")

        has_dates = file_min_date <= start_date and file_max_date >= end_date

        required_columns = {f"P{lag}" for lag in lags} | {"52_week_low"}
        has_columns = required_columns.issubset(df.columns)

        return has_dates and has_columns

    except Exception as e:
        logger.error(f"Error in {file_path}: {e}")
        return False

def process_ticker(ticker: str,
                   start_date: str,
                   end_date: str,
                   fmp_api_key: str,
                   window_shift: tuple[int, ...]
                   ) -> tuple[str, pd.DataFrame | None]:
    """
    :param ticker:
    :param start_date:
    :param end_date:
    :param fmp_api_key:
    :param window_shift:
    :return:
    """

    try:
        data = fmd.fetch_eod_price_data(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            api_key=fmp_api_key
        )

        df_lagged = la.add_lagged_return_columns(
            df=data,
            column="close",
            lags=window_shift
        )

        df_final = pc.add_52_week_low_column(
            df=df_lagged,
            column="low",
            window_days=252,
            output_column="52_week_low"
        )

        logger.info(f"Done for {ticker}")
        return ticker, df_final

    except Exception as e:
        logger.warning(f"Error processing ticker {ticker}: {e}")
        return ticker, None

def main(configuration: Configuration) -> tuple[dict[str, pd.DataFrame | None], dict[str, pd.DataFrame] | None]:
    start_date_str = configuration.start_date.isoformat()
    end_date_str = configuration.end_date.isoformat()

    results: dict[str, pd.DataFrame] = {}
    tickers_to_download = []

    for ticker in configuration.tickers:
        file_path = f"Output/Tickers/{ticker}.csv"

        if is_data_up_to_date(
            file_path=file_path,
            start_date=pd.Timestamp(configuration.start_date),
            end_date=pd.Timestamp(configuration.end_date),
            lags=configuration.window_shift,
            stay_update=configuration.stay_update
        ):
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            results[ticker] = df
            logger.info(f"[{ticker}] Loaded from local file.")
        else:
            tickers_to_download.append(ticker)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(
                process_ticker,
                ticker,
                start_date_str,
                end_date_str,
                configuration.fmp_api_key,
                configuration.window_shift
            ): ticker for ticker in tickers_to_download
        }

        for future in as_completed(futures):
            ticker, df = future.result()
            if df is not None:
                results[ticker] = df
                df.to_csv(f"Output/Tickers/{ticker}.csv")

    final_results = pc.process_all_tickers(
        data_dict=results,
        column="close",
        lags=configuration.window_shift,
        lookback=100
    )

    all_dates = final_results[next(iter(final_results))].index
    dates_to_process = ha.generate_summary_dates(all_dates=all_dates, configuration=configuration)

    summary_mode = configuration.summary_mode.lower()
    final_dict: dict[str, pd.DataFrame] = {}

    for date in dates_to_process:
        snapshot_dict = ha.extract_snapshot(data_dict=final_results, snapshot_date=date)
        summary_df = pc.build_summary_dataframe(data_dict=snapshot_dict)
        summary_df.to_csv(f"Output/Historical_Summaries/{date.date()}.csv")
        final_dict[date.date()] = summary_df

    if summary_mode != "latest":
        latest_date = max(df.index.max() for df in final_results.values())
        latest_snapshot = ha.extract_snapshot(data_dict=final_results, snapshot_date=latest_date)
        latest_summary_df = pc.build_summary_dataframe(data_dict=latest_snapshot)
        latest_summary_df.to_csv(f"Output/Historical_Summaries/{latest_date.date()}.csv")
        final_dict[latest_date.date()] = latest_summary_df

    sr.export_results_to_csv(results=final_results, output_dir="Output/Tickers/")

    logger.info("Done for all tickers")

    return final_dict, final_results