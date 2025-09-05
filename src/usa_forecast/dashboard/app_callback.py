# Libraries
from dash.dependencies import Input, Output

# Personal Modules
from src.usa_forecast.dashboard.layouts.target_price_table_layout import actuals_layout
from src.usa_forecast.dashboard.layouts.front_layout import front_layout
from src.usa_forecast.dashboard.layouts.heatmap_layout import heatmap_layout
from src.usa_forecast.dashboard.layouts.plot_layout import candlestick_layout
from src.usa_forecast.dashboard.layouts.stock_analysis_layout import market_analysis_layout

#%%

def app_callback(app, final_dict, forecast_tables_dict, mkt_data):
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == "/heatmap_analysis-page":
            return heatmap_layout(mkt_data=mkt_data)
        elif pathname == '/final_data_historical-page':
            return actuals_layout(periods_dict=final_dict)
        elif pathname == '/target_price-page':
            return front_layout(forecast_tables_dict=forecast_tables_dict)
        elif pathname == '/candlestick-page':
            return candlestick_layout(mkt_data=mkt_data)
        elif pathname == '/stock_analysis-page':
            return market_analysis_layout(market_data_dict=mkt_data)
        elif pathname == '/':
            return actuals_layout(periods_dict=final_dict)
        else:
            return '404 Página no encontrada'