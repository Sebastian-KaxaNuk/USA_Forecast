#Modules
from src.usa_forecast.config_handlers.excel_configurator import ExcelConfigurator
from src.usa_forecast.data_download import fmp_mkt_data as fmd
from src.usa_forecast.calculations import lags_adding as la
from src.usa_forecast.calculations import price_calculations as pc
from src.usa_forecast.aux_functions import save_read_csv_excel as sr
from src.usa_forecast.services import historical_analysis as ha

#Libraries
import sys
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.extend(["src"])

#%%

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger('myAppLogger')

logger.info("Logger configured successfully.")

#%%

configurator = ExcelConfigurator(
    file_path='Config/parameters_configuration.xlsx',
)

configuration = configurator.get_configuration()

#%%

start_date_str = configuration.start_date.isoformat()
end_date_str = configuration.end_date.isoformat()

#%%

def process_ticker(ticker: str) -> tuple[str, pd.DataFrame | None]:
    try:
        data = fmd.fetch_eod_price_data(
            ticker=ticker,
            start_date=start_date_str,
            end_date=end_date_str,
            api_key=configuration.fmp_api_key
        )

        df_lagged = la.add_lagged_return_columns(
            df=data,
            column="close",
            lags=configuration.window_shift
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

#%%

results = {}

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process_ticker, ticker): ticker for ticker in configuration.tickers}
    for future in as_completed(futures):
        ticker, df = future.result()
        if df is not None:
            results[ticker] = df

#%%

final_results = pc.process_all_tickers(data_dict=results,
                                       column="close",
                                       lags=configuration.window_shift,
                                       lookback=100)

#%%

summary_df = pc.build_summary_dataframe(data_dict=final_results)
summary_df.to_excel("Output/USA_Forecast.xlsx")

#%%

all_dates = final_results[next(iter(final_results))].index

#%%

dates_to_process = ha.generate_summary_dates(all_dates=all_dates, configuration=configuration)

#%%

for date in dates_to_process:
    snapshot_dict = ha.extract_snapshot(data_dict=final_results, snapshot_date=date)
    summary_df = pc.build_summary_dataframe(data_dict=snapshot_dict)
    summary_df.to_csv(f"Output/Summaries/summary_{date.date()}.csv")

latest_date = max(df.index.max() for df in final_results.values())
latest_snapshot = ha.extract_snapshot(data_dict=final_results, snapshot_date=latest_date)
latest_summary_df = pc.build_summary_dataframe(data_dict=latest_snapshot)
latest_summary_df.to_csv(f"Output/{latest_date}.csv")

#%%

sr.export_results_to_csv(results=final_results, output_dir="Output/Tickers/")

logger.info("Done for all tickers")
