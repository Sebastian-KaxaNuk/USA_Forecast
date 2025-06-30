from dash.dependencies import Input, Output, State
import dash_table
import dash_html_components as html
import pandas as pd
import dash
from src.usa_forecast.calculations import build_forecast_summary_table as bf
from src.usa_forecast.services import historical_analysis as ha
from src.usa_forecast.services.update_logic import update_with_latest_data


def register_callback_forecast_table(app, configuration, mkt_data):

    @app.callback(
        Output('period-dropdown1_front', 'options'),
        Output('period-dropdown1_front', 'value'),
        Output('store_forecast', 'data'),
        Input('reload-button_front', 'n_clicks')
    )
    def reload_forecast_data(n_clicks):
        if n_clicks:
            final_dict, updated_mkt_data = update_with_latest_data(configuration=configuration, mkt_data=mkt_data)

            forecast_tables_dict = {}
            for snapshot_date in final_dict:
                try:
                    forecast_table = bf.build_forecast_summary_table(data_dict=updated_mkt_data)
                    forecast_tables_dict[snapshot_date] = forecast_table
                except Exception:
                    continue

            latest_timestamp = max(df.index.max() for df in updated_mkt_data.values() if not df.empty)
            latest_snapshot = ha.extract_snapshot(data_dict=updated_mkt_data, snapshot_date=latest_timestamp)
            latest_forecast_table = bf.build_forecast_summary_table(data_dict=latest_snapshot)
            forecast_tables_dict[latest_timestamp.date()] = latest_forecast_table

            period_keys = list(forecast_tables_dict.keys())
            options = [{'label': str(k), 'value': str(k)} for k in period_keys]
            default_value = str(period_keys[-1])
            store_data = {str(k): df.to_dict(orient='split') for k, df in forecast_tables_dict.items()}

            return options, default_value, store_data

        raise dash.exceptions.PreventUpdate

    @app.callback(
        Output('table_front-output', 'children'),
        Input('submit-button_front', 'n_clicks'),
        State('period-dropdown1_front', 'value'),
        State('store_forecast', 'data')
    )
    def render_forecast_table(n_clicks, selected_period_str, store_data):
        if n_clicks and selected_period_str and store_data:
            df_dict = store_data.get(selected_period_str)
            if df_dict is None:
                return html.Div("No data available for the selected period.")

            df = pd.DataFrame(**df_dict)
            df.reset_index(inplace=True)
            if df.columns[0] == "index":
                df.rename(columns={"index": "Ticker"}, inplace=True)

            numeric_cols = df.select_dtypes(include='number').columns
            df[numeric_cols] = df[numeric_cols].round(2)

            return html.Div([
                html.H4(
                    f"Forecast Summary — Period: {selected_period_str}",
                    style={
                        "textAlign": "center",
                        "fontFamily": "Arial",
                        "fontWeight": "bold",
                        "marginBottom": "20px",
                        "marginTop": "10px"
                    }
                ),
                dash_table.DataTable(
                    columns=[{"name": col, "id": col} for col in df.columns],
                    data=df.to_dict("records"),
                    page_size=20,
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
                        'minWidth': '100%'
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
                        'textAlign': 'center',
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'color': 'black',
                        'border': '1px solid black'
                    },
                    style_data={
                        'textAlign': 'center',
                        'fontFamily': 'Arial',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'fontSize': '1rem',
                        'border': '1px solid grey'
                    }
                )
            ])

        return html.Div("Please select a period and press Submit.")
