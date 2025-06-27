# Reimport required packages and redefine the update function after reset
import pandas as pd
import logging
from src.usa_forecast.data_download import fmp_mkt_data as fmd
from src.usa_forecast.calculations import price_calculations as pc
from src.usa_forecast.services import historical_analysis as ha
from src.usa_forecast.calculations import lags_adding as la

logger = logging.getLogger('myAppLogger')


def update_with_latest_data(
        configuration,
        mkt_data: dict[str, pd.DataFrame]
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    """
    Updates the current market data with the latest 1-minute data (if available) for today's date.

    Parameters
    ----------
    configuration : Configuration
        Configuration object with API key and lags.
    mkt_data : dict[str, pd.DataFrame]
        Dictionary with current market data loaded from CSV or API.

    Returns
    -------
    tuple
        Updated final_results and updated_results, both as dictionaries of DataFrames.
    """
    updated_results = {}

    for ticker, df in mkt_data.items():
        try:
            latest_minute = fmd.fetch_eod_last_1m_price_data(
                ticker=ticker, api_key=configuration.fmp_api_key
            )
            last_minute_date = latest_minute.index[-1].date()

            if df.index[-1].date() == last_minute_date:
                df = pd.concat([df.iloc[:-1], latest_minute])
            else:
                df = pd.concat([df, latest_minute])

            df.index = pd.to_datetime(df.index.date)

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

            updated_results[ticker] = df
            df.to_csv(f"Output/Tickers/{ticker}.csv")

        except Exception as e:
            logger.warning(f"[{ticker}] Error updating with 1m data: {e}")
            updated_results[ticker] = df  # fallback: conserva lo anterior

    final_results = pc.process_all_tickers(
        data_dict=updated_results,
        column="close",
        lags=configuration.window_shift,
        lookback=100
    )

    # También genera el último summary actualizado
    latest_date = max(df.index.max() for df in final_results.values())
    latest_snapshot = ha.extract_snapshot(data_dict=final_results, snapshot_date=latest_date)
    latest_summary_df = pc.build_summary_dataframe(data_dict=latest_snapshot)
    latest_summary_df.to_csv("Output/summary_latest.csv")

    return final_results, updated_results
