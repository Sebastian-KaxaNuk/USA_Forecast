#Personal Modules
from src.usa_forecast.config_handlers.excel_configurator import ExcelConfigurator
from src.usa_forecast import usa_forecast_code as fc
from src.usa_forecast.aux_functions.open_browser_code import open_browser
from src.usa_forecast.dashboard.dash_components.navigation import navbar
from src.usa_forecast.services.update_logic import update_with_latest_data

#Logger
import logging
from threading import Timer
import pandas as pd

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

#@TODO: NO QUITAR LAS COLUMNAS
reload = False

if reload:
    final_dict, mkt_data = update_with_latest_data(configuration=configuration, mkt_data=mkt_data)

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
            high_min = last_row["MaxMin"]
            high_max = last_row["MaxMax"]
            low_min = last_row["MinMin"]
            low_max = last_row["MinMax"]

            vender_a_partir_de = high_min if high_min < close else high_min
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

summary_table = build_forecast_summary_table(data_dict=final_dict)


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
