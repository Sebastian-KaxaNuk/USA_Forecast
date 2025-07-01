# Libraries
from dash.dependencies import Input, Output

# Personal Modules
from usa_forecast.dashboard.layouts.target_price_table_layout import actuals_layout
from usa_forecast.dashboard.layouts.front_layout import front_layout
from usa_forecast.dashboard.layouts.heatmap_layout import heatmap_layout

#%%

def app_callback(app, final_dict, forecast_tables_dict, mkt_data):
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == "/heatmap_analysis-page":
            return heatmap_layout(mkt_data)
        elif pathname == '/final_data_historical-page':
            return actuals_layout(periods_dict=final_dict)
        elif pathname == '/target_price-page':
            return front_layout(forecast_tables_dict)
        elif pathname == '/':
            return actuals_layout(periods_dict=final_dict)
        else:
            return '404 Página no encontrada'