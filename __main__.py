#Libraries & Modules
from src.usa_forecast.config_handlers.excel_configurator import ExcelConfigurator
from src.usa_forecast.data_download import fmp_mkt_data as fmd
from src.usa_forecast.calculations import lags_adding as la
from src.usa_forecast.calculations import price_calculations as pc
from src.usa_forecast.aux_functions import save_read_csv_excel as sr

import sys
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger('myAppLogger')

sys.path.extend(["src"])

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

results = {}

for ticker in configuration.tickers:
    try:
        df = fmd.fetch_eod_price_data(
            ticker=ticker,
            start_date=start_date_str,
            end_date=end_date_str,
            api_key=configuration.fmp_api_key
        )

        df = la.add_lagged_return_columns(
            df=df,
            column="close",
            lags=configuration.window_shift
        )

        df = pc.add_52_week_low_column(
            df=df,
            column="low",
            window_days=252,
            output_column="52_week_low")

        results[ticker] = df

        logger.info(f"Done for {ticker}")

    except Exception as e:
        logger.warning(f"Error processing ticker {ticker}: {e}")

#%%

final_results = pc.process_all_tickers(data_dict=results,
                                       column="close",
                                       lags=configuration.window_shift,
                                       lookback=100)

#%%

summary_df = pc.build_summary_dataframe(data_dict=final_results)
summary_df.to_excel("Output/USA_Forecast.xlsx")

#%%

sr.export_results_to_csv(results=final_results, output_dir="Output/Tickers/")

logger.info("Done for all tickers")
