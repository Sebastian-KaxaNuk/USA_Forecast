from src.usa_forecast.config_handlers.excel_configurator import ExcelConfigurator
from src.usa_forecast import usa_forecast_code as fc

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger('myAppLogger')

logger.info("Logger configured successfully.")

#%%

configurator = ExcelConfigurator(
    file_path='Config/parameters_configuration.xlsx',
)

configuration = configurator.get_configuration()

#%%

final_dict, mkt_data = fc.main(configuration=configuration)
