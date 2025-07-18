#Personal Modules
from usa_forecast.config_handlers.excel_configurator import ExcelConfigurator
from usa_forecast import usa_forecast_code as fc
from usa_forecast.aux_functions.open_browser_code import open_browser
from usa_forecast.calculations import build_forecast_summary_table as bf
from usa_forecast.services import historical_analysis as ha
from usa_forecast.dashboard.app_callback import app_callback
from usa_forecast.dashboard.callbacks.target_price_table_callback import register_callback_actuals
from usa_forecast.dashboard.layouts.target_price_table_layout import actuals_layout
from usa_forecast.dashboard.callbacks.front_callback import register_callback_forecast_table
from usa_forecast.dashboard.callbacks.heatmap_callback import register_callback_show_p_columns
from usa_forecast.dashboard.callbacks.plot_callback import register_callback_candlestick_chart
from dash.dependencies import Input, Output
from usa_forecast.dashboard.dash_components.navigation import build_navbar

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

import sys
import os
current_dir = os.getcwd()

src_path = os.path.normpath(os.path.join(current_dir, 'src'))

if src_path not in sys.path:
    sys.path.append(src_path)

#%%

configurator = ExcelConfigurator(
    file_path='Config/parameters_configuration.xlsx',
)

configuration = configurator.get_configuration()

#%%

final_dict, mkt_data = fc.main(configuration=configuration)

#%%

lista = list(final_dict.keys())

df = final_dict[lista[0]]


#%%

forecast_tables_dict: dict[datetime.date, pd.DataFrame] = {}

for snapshot_date in final_dict.keys():
    try:
        snapshot_ts = pd.Timestamp(snapshot_date)
        snapshot = ha.extract_snapshot(data_dict=mkt_data, snapshot_date=snapshot_ts)
        forecast_table = bf.build_forecast_summary_table(data_dict=snapshot)
        forecast_tables_dict[snapshot_date] = forecast_table
    except Exception as e:
        logger.warning(f"Error building forecast table for {snapshot_date}: {e}")

#%%

lista1 = list(forecast_tables_dict.keys())

df1 = forecast_tables_dict[lista1[0]]
df2 = forecast_tables_dict[lista1[1]]


#%%

latest_timestamp = max(df.index.max() for df in mkt_data.values())
latest_snapshot = ha.extract_snapshot(data_dict=mkt_data, snapshot_date=latest_timestamp)

latest_forecast_table = bf.build_forecast_summary_table(data_dict=latest_snapshot)

forecast_tables_dict[latest_timestamp.date()] = latest_forecast_table

#%%

# app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
#
# app.layout = html.Div([
#     dcc.Location(id='url', refresh=False),
#     html.Div(id="navbar-container"),
#     html.Div(id='page-content', children=actuals_layout(final_dict)),
#     html.Footer(
#         html.Div(
#             [
#                 html.Hr(),
#                 dcc.Markdown(
#                 """
#                 **USA Forecast-Dash**
#                 """
#                 ),
#                 html.P(
#                     [
#                         html.Img(src=dash.get_asset_url("image.jpg")),
#                         html.Span("   "),
#                         html.A("GitHub Repository",
#                                href="https://github.com/Sebastian-KaxaNuk/USA_Forecast", target="_blank"),
#                     ]
#                 ),
#             ],
#             style={"text-align": "center"},
#             className="p-3",
#         ),
#     )
# ])

current_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
assets_folder = os.path.join(current_dir, "assets")

app = dash.Dash(
    __name__,
    assets_folder=assets_folder,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = html.Div(
    style={
        "display": "flex",
        "flexDirection": "column",
        "minHeight": "100vh",
    },
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(id="navbar-container"),
        html.Div(
            id='page-content',
            style={"flex": "1", "padding": "0 20px"}
        ),
        html.Footer(
            html.Div(
                [
                    html.Hr(),
                    dcc.Markdown("**USA Forecast-Dash**"),
                    html.P([
                        html.Img(src=dash.get_asset_url("image.jpg")),
                        html.Span(" "),
                        html.A("GitHub Repository", href="https://github.com/Sebastian-KaxaNuk/USA_Forecast", target="_blank"),
                    ])
                ],
                style={"text-align": "center"},
                className="p-3"
            )
        )
    ]
)

@app.callback(
    Output("navbar-container", "children"),
    Input("url", "pathname")
)
def update_navbar(pathname):
    return build_navbar(pathname or "/target_price-page")

app_callback(app, final_dict, forecast_tables_dict, mkt_data)
register_callback_show_p_columns(app, mkt_data)
register_callback_actuals(app, configuration, mkt_data)
register_callback_forecast_table(app, configuration, mkt_data)
register_callback_candlestick_chart(app, mkt_data)

if __name__ == "__main__":
    logger.info('-----------------------------------------')
    logger.info("Dash is running on http://127.0.0.1:8031/")
    logger.info('-----------------------------------------')
    Timer(1, open_browser).start()
    app.run(debug=False, port=8031)