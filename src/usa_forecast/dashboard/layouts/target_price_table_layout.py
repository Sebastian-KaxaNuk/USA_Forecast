import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def actuals_layout(periods_dict: dict) -> html.Div:
    period_options = [
        {"label": str(k), "value": str(k)} for k in periods_dict.keys()
    ]

    layout = html.Div([
        dcc.Store(id="store"),
        html.Div([
            html.Div(id='selected-period-container1', style={'display': 'none'}),

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
                                searchable=True
                            ),
                            dbc.Row([
                                dbc.Col([
                                    html.Button(
                                        'Submit',
                                        id='submit-button',
                                        n_clicks=0,
                                        className="btn btn-primary"
                                    )
                                ], width="auto"),
                                dbc.Col([
                                    html.Button(
                                        'Update Model',
                                        id='download-button',
                                        n_clicks=0,
                                        className="btn btn-secondary"
                                    )
                                ], width="auto"),
                            ], justify="start", className="mt-3")
                        ])
                    ], className="m-3"),
                ], width=12)
            ]),

            html.Div(id="table-output", className="m-3")

        ])
    ])
    return layout