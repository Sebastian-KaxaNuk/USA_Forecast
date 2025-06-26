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

#%%
logger = logging.getLogger('myAppLogger')

#%%

def process_ticker(ticker: str,
                   start_date: str,
                   end_date: str,
                   fmp_api_key: str,
                   window_shift: tuple[int, ...]
                   ) -> tuple[str, pd.DataFrame | None]:
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


def main(
        configuration: Configuration,
        ) -> tuple[dict[str, pd.DataFrame | None], dict[str, pd.DataFrame] | None]:

    start_date_str = configuration.start_date.isoformat()
    end_date_str = configuration.end_date.isoformat()

    results = {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_ticker,
                                   ticker,
                                   start_date_str,
                                   end_date_str,
                                   configuration.fmp_api_key,
                                   configuration.window_shift): ticker for ticker in configuration.tickers}
        for future in as_completed(futures):
            ticker, df = future.result()
            if df is not None:
                results[ticker] = df

    final_results = pc.process_all_tickers(data_dict=results,
                                           column="close",
                                           lags=configuration.window_shift,
                                           lookback=100)

    all_dates = final_results[next(iter(final_results))].index
    dates_to_process = ha.generate_summary_dates(all_dates=all_dates, configuration=configuration)

    summary_mode = configuration.summary_mode.lower()

    final_dict = {}

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

    sr.export_results_to_csv(results=final_results, output_dir="Output/Tickers/")

    logger.info("Done for all tickers")

    return final_dict, results
