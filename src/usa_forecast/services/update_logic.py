# Reimport required packages and redefine the update function after reset
import pandas as pd
import logging
from usa_forecast.data_download import fmp_mkt_data as fmd
from usa_forecast.calculations import price_calculations as pc
from usa_forecast.services import historical_analysis as ha
from usa_forecast.calculations import lags_adding as la
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger('myAppLogger')

def update_with_latest_data(
    configuration,
    mkt_data: dict[str, pd.DataFrame]
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    """
    Updates the current market data with the latest 1-minute data (if available) for today's date.

    Returns:
        final_dict: snapshots por fecha
        updated_results: data diaria actualizada por ticker
    """
    updated_results: dict[str, pd.DataFrame] = {}

    def update_ticker(ticker: str, df: pd.DataFrame) -> tuple[str, pd.DataFrame | None]:
        try:
            latest_minute = fmd.fetch_eod_last_1m_price_data(
                ticker=ticker,
                api_key=configuration.fmp_api_key
            )

            last_minute_date = latest_minute.index[-1].date()
            df.index = pd.to_datetime(df.index)

            if df.index[-1].date() == last_minute_date:
                df = pd.concat([df.iloc[:-1], latest_minute])
            else:
                df = pd.concat([df, latest_minute])

            df = df[~df.index.duplicated(keep="last")]
            df = df.sort_index()

            df = la.add_lagged_return_columns(
                df=df,
                column="close",
                lags=configuration.window_shift
            )

            df = pc.add_52_week_low_column(
                df=df,
                column="low",
                window_days=252,
                output_column="52_week_low"
            )

            df = pc.calculate_price_targets(
                df=df,
                column="close",
                lags=configuration.window_shift,
                lookback=100
            )

            df.to_csv(f"Output/Tickers/{ticker}.csv")
            return ticker, df

        except Exception as e:
            logger.warning(f"[{ticker}] Error updating with 1m data: {e}")
            return ticker, df  # fallback con datos anteriores

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(update_ticker, ticker, df): ticker
            for ticker, df in mkt_data.items()
        }

        for future in as_completed(futures):
            ticker, updated_df = future.result()
            updated_results[ticker] = updated_df

    final_results = pc.process_all_tickers(
        data_dict=updated_results,
        column="close",
        lags=configuration.window_shift,
        lookback=100
    )

    all_dates = final_results[next(iter(final_results))].index
    dates_to_process = ha.generate_summary_dates(all_dates=all_dates, configuration=configuration)

    final_dict: dict[str, pd.DataFrame] = {}

    for date in dates_to_process:
        snapshot = ha.extract_snapshot(data_dict=final_results, snapshot_date=date)
        summary = pc.build_summary_dataframe(data_dict=snapshot)
        summary.to_csv(f"Output/Historical_Summaries/{date.date()}.csv")
        final_dict[date.date()] = summary

    latest_date = max(df.index.max() for df in final_results.values())
    latest_snapshot = ha.extract_snapshot(data_dict=final_results, snapshot_date=latest_date)
    latest_summary_df = pc.build_summary_dataframe(data_dict=latest_snapshot)
    latest_summary_df.to_csv("Output/summary_latest.csv")
    final_dict[latest_date.date()] = latest_summary_df

    logger.info("Latest market data and summaries updated.")

    return final_dict, updated_results

