# Libraries
from dash.dependencies import Input, Output

# Personal Modules
from usa_forecast.dashboard.layouts.target_price_table_layout import actuals_layout
from usa_forecast.dashboard.layouts.front_layout import front_layout

#%%

def app_callback(app, final_dict, forecast_tables_dict):
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/final_data_historical-page':
            return actuals_layout(periods_dict=final_dict)
        elif pathname == '/target_price-page':
            return front_layout(forecast_tables_dict)
        # elif pathname == '/sector-page':
        #     return lsl.create_dashboard(dic_clean_2)
        # elif pathname == '/portfolio-page':
        #     return pl.port_layout(dic_clean_2)
        elif pathname == '/':  # redirige la ruta raíz a page1.layout
            return actuals_layout(periods_dict=final_dict)
        else:
            return '404 Página no encontrada'
