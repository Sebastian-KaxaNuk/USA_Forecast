import pandas as pd
import logging
logger = logging.getLogger('myAppLogger')

#%%
def build_forecast_summary_table(
    data_dict: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Builds a summary table for each ticker with key price indicators and trading signals.

    Parameters
    ----------
    data_dict : dict[str, pd.DataFrame]
        Dictionary where keys are tickers and values are DataFrames containing:
        'close', 'HighMin', 'HighMax', 'LowMin', 'LowMax' columns.

    Returns
    -------
    pd.DataFrame
        Summary DataFrame with tickers as index and columns:
        ['Precio actual', 'Compra a partir de', 'Precio Mínimo que puede llegar',
         'Vender a partir de', 'Precio Máximo que puede alcanzar', 'Rate']
    """
    summary_records = []

    for ticker, df in data_dict.items():
        try:
            last_row = df.iloc[-1]

            close = last_row["close"]
            high_min = last_row["HighMin"]
            high_max = last_row["MaxMax"]
            low_min = last_row["MaxMin"]
            low_max = last_row["MinMin"]
            min_max = last_row["MinMax"]


            #C22 ES HighMin
            #C2 ES CLOSE
            #C4 ES MINMAX

            # vender_a_partir_de = high_min if high_min < close else min_max
            vender_a_partir_de = min_max if high_min < close else high_min

            rate = (low_min / close) - 1

            summary_records.append({
                "Ticker": ticker,
                "Precio actual": close,
                "Compra a partir de": low_min,
                "Precio Mínimo que puede llegar": low_max,
                "Vender a partir de": vender_a_partir_de,
                "Precio Máximo que puede alcanzar": high_max,
                "Rate": rate
            })

        except Exception as e:
            logging.warning(f"[{ticker}] Error building summary: {e}")

    return pd.DataFrame(summary_records).set_index("Ticker")
