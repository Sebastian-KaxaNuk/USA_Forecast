# from dash.dependencies import Input, Output, State
# import dash_table
# import dash_html_components as html
# import pandas as pd
# import re
# from dash_table.Format import Format, Scheme, Symbol
#
# def register_callback_show_p_columns(app, mkt_data: dict):
#
#     @app.callback(
#         Output('table2-front-output', 'children'),
#         Input('submit2-button-front', 'n_clicks'),
#         State('ticker2-dropdown-front', 'value'),
#     )
#     def display_ticker_data(n_clicks, selected_ticker):
#         if not n_clicks or not selected_ticker:
#             return html.Div("Please select a ticker and press Submit.")
#
#         df = mkt_data.get(selected_ticker)
#         if df is None:
#             return html.Div(f"No data available for ticker {selected_ticker}")
#
#         if not isinstance(df.index, pd.DatetimeIndex):
#             try:
#                 df.index = pd.to_datetime(df.index)
#             except Exception:
#                 return html.Div("Index is not datetime and could not be converted.")
#
#         p_columns = [col for col in df.columns if re.fullmatch(r"P\d+", col)]
#         if not p_columns:
#             return html.Div("No P-columns found for this ticker.")
#
#         filtered_df = df[p_columns].copy()
#         filtered_df = filtered_df.tail(60).copy()
#         filtered_df["Date"] = filtered_df.index.strftime("%Y-%m-%d")
#         filtered_df.reset_index(drop=True, inplace=True)
#         filtered_df.rename(columns={"index": "Date"}, inplace=True)
#
#         filtered_df[p_columns] = filtered_df[p_columns] # Convertir a porcentaje
#         filtered_df[p_columns] = filtered_df[p_columns].round(2)
#
#         columns = [{"name": "Date", "id": "Date"}]
#         for col in p_columns:
#             columns.append({
#                 "name": col,
#                 "id": col,
#                 "type": "numeric",
#                 "format": Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_suffix('%')
#             })
#
#         return dash_table.DataTable(
#             columns=columns,
#             data=filtered_df.to_dict("records"),
#             page_size=40,
#             fixed_rows={"headers": True},  # Header fijo
#             style_table={'overflowX': 'auto', 'width': '100%'},
#             style_cell={
#                 "textAlign": "center",
#                 "fontFamily": "Arial",
#                 "padding": "6px",
#                 "whiteSpace": "normal",
#                 "minWidth": "80px",
#                 "maxWidth": "200px"
#             },
#             style_header={
#                 'fontWeight': 'bold',
#                 'backgroundColor': 'rgb(230, 230, 230)',
#                 'border': '1px solid black'
#             },
#             style_data={
#                 'border': '1px solid grey'
#             }
#         )

from dash.dependencies import Input, Output, State
import dash_table
import dash_html_components as html
import pandas as pd
import re
from dash_table.Format import Format, Scheme, Symbol

def register_callback_show_p_columns(app, mkt_data: dict):

    @app.callback(
        Output('table2-front-output', 'children'),
        Input('submit2-button-front', 'n_clicks'),
        State('ticker2-dropdown-front', 'value'),
    )
    def display_ticker_data(n_clicks, selected_ticker):
        if not n_clicks or not selected_ticker:
            return html.Div("Please select a ticker and press Submit.")

        df = mkt_data.get(selected_ticker)
        if df is None:
            return html.Div(f"No data available for ticker {selected_ticker}")

        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except Exception:
                return html.Div("Index is not datetime and could not be converted.")

        p_columns = [col for col in df.columns if re.fullmatch(r"P\d+", col)]
        if not p_columns:
            return html.Div("No P-columns found for this ticker.")

        filtered_df = df[p_columns].copy()
        filtered_df = filtered_df.tail(200).copy()
        filtered_df["Date"] = filtered_df.index.strftime("%Y-%m-%d")
        filtered_df.reset_index(drop=True, inplace=True)

        filtered_df[p_columns] = filtered_df[p_columns]
        filtered_df[p_columns] = filtered_df[p_columns].round(2)

        # Crear lista de columnas
        columns = [{"name": "Date", "id": "Date"}]
        for col in p_columns:
            columns.append({
                "name": col,
                "id": col,
                "type": "numeric",
                "format": Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_suffix('%')
            })

        style_data_conditional = []

        for col in p_columns:
            # Rojos (negativos)
            style_data_conditional += [
                {
                    'if': {'filter_query': f'{{{col}}} <= -10', 'column_id': col},
                    'backgroundColor': '#990000',
                    'color': 'white'
                },
                {
                    'if': {'filter_query': f'-10 < {{{col}}} <= -5', 'column_id': col},
                    'backgroundColor': '#cc0000',
                    'color': 'white'
                },
                {
                    'if': {'filter_query': f'-5 < {{{col}}} < 0', 'column_id': col},
                    'backgroundColor': '#ff9999',
                    'color': 'black'
                },
            ]

            # Verdes (positivos)
            style_data_conditional += [
                {
                    'if': {'filter_query': f'{{{col}}} >= 10', 'column_id': col},
                    'backgroundColor': '#006600',
                    'color': 'white'
                },
                {
                    'if': {'filter_query': f'5 <= {{{col}}} < 10', 'column_id': col},
                    'backgroundColor': '#339933',
                    'color': 'white'
                },
                {
                    'if': {'filter_query': f'0 < {{{col}}} < 5', 'column_id': col},
                    'backgroundColor': '#99ff99',
                    'color': 'black'
                },
            ]

        return dash_table.DataTable(
            columns=columns,
            data=filtered_df.to_dict("records"),
            fixed_rows={"headers": True},
            style_table={
                'overflowX': 'auto',
                'overflowY': 'auto',
                'height': '800px',
                'maxHeight': '800px',
                'border': '1px solid grey',
                'width': '100%'
            },
            style_cell={
                "textAlign": "center",
                "fontFamily": "Arial",
                "padding": "6px",
                "whiteSpace": "normal",
                "minWidth": "80px",
                "maxWidth": "200px",
                "height": "auto",
            },
            style_data={
                'border': '1px solid grey'
            },
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': 'rgb(230, 230, 230)',
                'border': '1px solid black'
            },
            style_data_conditional=style_data_conditional
        )