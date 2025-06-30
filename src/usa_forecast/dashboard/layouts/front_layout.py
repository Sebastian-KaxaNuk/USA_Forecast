import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def front_layout(forecast_tables_dict: dict) -> html.Div:
    period_options = [{"label": str(k), "value": str(k)} for k in forecast_tables_dict.keys()]

    layout = html.Div([
        dcc.Store(id="store_forecast", data={str(k): df.to_dict("split") for k, df in forecast_tables_dict.items()}),
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4('Parameters', className='card-title'),
                            dcc.Dropdown(
                                id='period-dropdown1_front',
                                options=period_options,
                                placeholder="Select a period",
                                value=str(list(forecast_tables_dict.keys())[0]),
                                searchable=True,
                                style={'marginBottom': '10px'}
                            ),
                            dbc.Row([
                                dbc.Col(html.Button('Submit', id='submit-button_front', n_clicks=0, className="btn btn-primary"), width="auto"),
                                dbc.Col(html.Button('Reload Model', id='reload-button_front', n_clicks=0, className="btn btn-warning"), width="auto")
                            ])
                        ])
                    ], className="m-3")
                ], width=12)
            ]),
            html.Div(id="table_front-output", className="m-3", style={"width": "100%"})
        ])
    ])
    return layout
