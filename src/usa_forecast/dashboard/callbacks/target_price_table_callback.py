# Libraries
from dash.dependencies import Input, Output, State
import dash_table
import dash_html_components as html
import datetime
import pandas as pd

import logging
#logging
logger = logging.getLogger('myAppLogger')

#%%

# def register_callback_actuals(app, periods_dict: dict):
#
#     @app.callback(
#         Output('table-output', 'children'),
#         Input('submit-button', 'n_clicks'),
#         State('period-dropdown1', 'value')
#     )
#     def render_table(n_clicks, selected_period_str):
#         if n_clicks and selected_period_str:
#             try:
#                 selected_date = datetime.datetime.strptime(selected_period_str, "%Y-%m-%d").date()
#                 df = periods_dict.get(selected_date)
#
#                 if df is not None and not df.empty:
#                     return dash_table.DataTable(
#                         columns=[{"name": col, "id": col} for col in df.columns],
#                         data=df.to_dict("records"),
#                         page_size=12,
#                         style_table={"overflowX": "auto"},
#                         style_cell={"textAlign": "center", "fontFamily": "Arial"},
#                         style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"},
#                         style_data={"backgroundColor": "white"}
#                     )
#                 else:
#                     return html.Div("No data available for the selected period.")
#             except Exception as e:
#                 return html.Div(f"Error parsing period: {e}")
#         return html.Div("Please select a period and press Submit.")

def register_callback_actuals(app, periods_dict: dict):
    @app.callback(
        Output('table-output', 'children'),
        Input('submit-button', 'n_clicks'),
        State('period-dropdown1', 'value')
    )
    def render_table(n_clicks, selected_period_str):
        if n_clicks and selected_period_str:
            try:
                selected_date = datetime.datetime.strptime(selected_period_str, "%Y-%m-%d").date()
                df = periods_dict.get(selected_date)

                if df is not None and not df.empty:
                    df = df.copy()

                    if df.index.name is None:
                        df.index.name = "Index"

                    df.reset_index(inplace=True)

                    numeric_cols = df.select_dtypes(include='number').columns
                    df[numeric_cols] = df[numeric_cols].round(2)

                    return dash_table.DataTable(
                        columns=[{"name": col, "id": col} for col in df.columns],
                        data=df.to_dict("records"),
                        page_size=12,
                        fixed_rows={"headers": True},
                        fixed_columns={"headers": True, "data": 1},
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        page_action="native",
                        page_current=0,
                        style_table={
                            'overflowX': 'auto',
                            'width': '100%',
                            'minWidth': '100%',
                        },
                        style_cell={
                            "textAlign": "center",
                            "fontFamily": "Arial",
                            "padding": "6px",
                            "whiteSpace": "normal",
                            "width": "1%",
                            "minWidth": "150px",
                            "maxWidth": "300px"
                        },
                        style_header={
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'color': 'black',
                            'fontFamily': 'Arial',
                            'fontSize': '1.1rem',
                            'border': '1px solid black',
                            'whiteSpace': 'normal',
                            'height': 'auto'
                        },
                        style_data={
                            'textAlign': 'center',
                            'fontFamily': 'Arial',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'fontSize': '1rem',
                            'border': '1px solid grey'
                        },
                        # style_data_conditional=[
                        #     {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
                        #     {"if": {"state": "active"}, "backgroundColor": "#d9edf7"},
                        # ]
                    )
                else:
                    return html.Div("No data available for the selected period.")
            except Exception as e:
                return html.Div(f"Error parsing period: {e}")

        return html.Div("Please select a period and press Submit.")