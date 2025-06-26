#Personal Modules
from src.usa_forecast.config_handlers.excel_configurator import ExcelConfigurator
from src.usa_forecast import usa_forecast_code as fc
from src.usa_forecast.aux_functions.open_browser_code import open_browser
from src.usa_forecast.dashboard.dash_components.navigation import navbar

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
