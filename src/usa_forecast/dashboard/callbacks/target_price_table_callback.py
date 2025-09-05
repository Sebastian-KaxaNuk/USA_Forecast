# Libraries
from dash.dependencies import Input, Output, State
import dash_table
import dash_html_components as html
import pandas as pd
import dash
from src.usa_forecast.services.update_logic import update_with_latest_data
from dash_table.Format import Format, Scheme, Symbol

import logging
#logging
logger = logging.getLogger('myAppLogger')

#%%

def register_callback_actuals(app, configuration, mkt_data):
    @app.callback(
        Output('period-dropdown1', 'options'),
        Output('period-dropdown1', 'value'),
        Output('store', 'data'),
        Output('ticker-dropdown1', 'options'),
        Input('reload-button', 'n_clicks')
    )
    def reload_data(n_clicks):
        if n_clicks:
            final_dict, _ = update_with_latest_data(configuration=configuration, mkt_data=mkt_data)
            period_keys = list(final_dict.keys())
            options = [{'label': str(k), 'value': str(k)} for k in period_keys]
            default_value = str(period_keys[-1])
            store_data = {str(k): df.to_dict(orient='split') for k, df in final_dict.items()}
            ticker_options = [{'label': t, 'value': t} for t in final_dict[period_keys[-1]].columns]
            return options, default_value, store_data, ticker_options
        raise dash.exceptions.PreventUpdate

    @app.callback(
        Output('table-output', 'children'),
        Input('submit-button', 'n_clicks'),
        State('period-dropdown1', 'value'),
        State('store', 'data'),
        State('ticker-dropdown1', 'value')
    )
    def render_table(n_clicks, selected_period_str, store_data, selected_tickers):
        if n_clicks and selected_period_str and store_data:
            df_dict = store_data.get(selected_period_str)
            if df_dict is None:
                return html.Div("No data available for the selected period.")
            df = pd.DataFrame(**df_dict)
            df.reset_index(inplace=True)
            if df.columns[0] == "index":
                df.rename(columns={"index": "Date"}, inplace=True)
            if selected_tickers:
                cols = ["Date"] if "Date" in df.columns else []
                df = df[cols + selected_tickers]
            numeric_cols = df.select_dtypes(include='number').columns
            df[numeric_cols] = df[numeric_cols].round(2)

            columns = []
            for col in df.columns:
                if col in numeric_cols:
                    fmt = Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_prefix('$')
                    columns.append({"name": col, "id": col, "type": "numeric", "format": fmt})
                else:
                    columns.append({"name": col, "id": col})

            return html.Div([
                html.H4(f"Forecast Summary — Period: {selected_period_str}",
                        style={"textAlign": "center", "fontFamily": "Arial", "fontWeight": "bold"}),
                dash_table.DataTable(
                    columns=columns,
                    data=df.to_dict("records"),
                    page_size=40,
                    fixed_rows={"headers": True},
                    fixed_columns={"headers": True, "data": 1},
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    # style_table={'overflowX': 'auto', 'width': '100%', 'minWidth': '100%'},
                    # style_table={
                    #     'overflowX': 'auto',
                    #     'overflowY': 'auto',
                    #     'maxHeight': '72vh',
                    #     'height': '72vh',
                    #     'width': '100%',
                    #     'minWidth': '100%',
                    # },
                    style_table={
                        'overflowX': 'auto',
                        'overflowY': 'auto',
                        'maxHeight': '85vh',
                        'height': '85vh',
                        'width': '100%',
                        'minWidth': '100%',
                    },
                    style_cell={
                        "textAlign": "center",
                        "fontFamily": "Arial",
                        "padding": "6px",
                        "whiteSpace": "normal",
                        "minWidth": "150px",
                        "maxWidth": "300px"
                    },
                    style_header={
                        'fontWeight': 'bold',
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'border': '1px solid black'
                    },
                    style_data={'border': '1px solid grey'}
                )
            ])
        return html.Div("Please select a period and press Submit.")