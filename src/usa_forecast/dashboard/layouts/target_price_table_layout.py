import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def actuals_layout(periods_dict: dict) -> html.Div:
    period_options = [{"label": str(k), "value": str(k)} for k in periods_dict.keys()]
    tickers = list(periods_dict[list(periods_dict.keys())[0]].columns)
    ticker_options = [{"label": t, "value": t} for t in tickers]

    layout = html.Div([
        dcc.Store(id="store", data={str(k): df.to_dict("split") for k, df in periods_dict.items()}),
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4('Parameters', className='card-title'),
                            dcc.Dropdown(
                                id='period-dropdown1',
                                options=period_options,
                                placeholder="Select a period",
                                value=str(list(periods_dict.keys())[0]),
                                searchable=True,
                                style={'marginBottom': '10px'}
                            ),
                            dcc.Dropdown(
                                id='ticker-dropdown1',
                                options=ticker_options,
                                placeholder="Select one or more tickers",
                                multi=True,
                                searchable=True,
                                style={'marginBottom': '10px'}
                            ),
                            dbc.Row([
                                dbc.Col(html.Button('Submit', id='submit-button', n_clicks=0, className="btn btn-primary"), width="auto"),
                                dbc.Col(html.Button('Reload Model', id='reload-button', n_clicks=0, className="btn btn-warning"), width="auto")
                            ])
                        ])
                    ], className="m-3")
                ], width=12)
            ]),
            html.Div(
                id="table-output",
                className="m-3",
                style={
                    "flexGrow": "1",
                    "height": "calc(100vh - 150px)",  # Ajusta según el tamaño de navbar y botones
                    "overflowY": "auto",
                    "overflowX": "auto",
                }
            )
        ])
    ])
    return layout