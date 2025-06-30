#Personal Modules
from src.usa_forecast.config_handlers.excel_configurator import ExcelConfigurator
from src.usa_forecast import usa_forecast_code as fc
from src.usa_forecast.aux_functions.open_browser_code import open_browser
from src.usa_forecast.dashboard.dash_components.navigation import navbar
from src.usa_forecast.services.update_logic import update_with_latest_data
from src.usa_forecast.calculations import build_forecast_summary_table as bf
from src.usa_forecast.services import historical_analysis as ha

import pandas as pd
from datetime import datetime

#Logger
import logging
from threading import Timer

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger('myAppLogger')

logger.info("Logger configured successfully.")

#Dash
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

#%%

configurator = ExcelConfigurator(
    file_path='Config/parameters_configuration.xlsx',
)

configuration = configurator.get_configuration()

#%%

final_dict, mkt_data = fc.main(configuration=configuration)

#%%

reload = True

if reload:
    final_dict, mkt_data = update_with_latest_data(configuration=configuration, mkt_data=mkt_data)

#%%

forecast_tables_dict: dict[datetime.date, pd.DataFrame] = {}

for snapshot_date, snapshot_data in final_dict.items():
    try:
        forecast_table = bf.build_forecast_summary_table(data_dict=mkt_data)
        forecast_tables_dict[snapshot_date] = forecast_table
    except Exception as e:
        logger.warning(f"Error building forecast table for {snapshot_date}: {e}")

latest_timestamp = max(df.index.max() for df in mkt_data.values())  # esto es Timestamp
latest_snapshot = ha.extract_snapshot(data_dict=mkt_data, snapshot_date=latest_timestamp)

latest_forecast_table = bf.build_forecast_summary_table(data_dict=latest_snapshot)

forecast_tables_dict[latest_timestamp.date()] = latest_forecast_table

#%%

keys = list(forecast_tables_dict.keys())

df = forecast_tables_dict[keys[0]]

#%%

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content'),
    html.Footer(
        html.Div(
            [
                html.Hr(),
                dcc.Markdown(
                    """
                **USA Forecast-Dash**  
                """
                ),
                html.P(
                    [
                        html.Img(src=dash.get_asset_url("image.jpg")),
                        html.Span("   "),
                        html.A("GitHub Repository",
                               href="https://github.com/Sebastian-KaxaNuk/USA_Forecast", target="_blank"),
                    ]
                ),
            ],
            style={"text-align": "center"},
            className="p-3",
        ),
    )
])

#%%

if __name__ == "__main__":
    logger.info('-----------------------------------------')
    logger.info("Dash is running on http://127.0.0.1:8031/")
    logger.info('-----------------------------------------')
    Timer(1, open_browser).start()
    app.run(debug=False, port=8031)
