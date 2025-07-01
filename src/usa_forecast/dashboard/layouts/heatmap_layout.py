import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

def heatmap_layout(mkt_data: dict) -> html.Div:
    ticker_options = [{"label": ticker, "value": ticker} for ticker in mkt_data.keys()]

    layout_mkt = html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4('Parameters', className='card-title'),
                            dcc.Dropdown(
                                id='ticker2-dropdown-front',
                                options=ticker_options,
                                placeholder="Select a ticker",
                                searchable=True,
                                style={'marginBottom': '10px'}
                            ),
                            dbc.Row([
                                dbc.Col(
                                    html.Button('Submit', id='submit2-button-front', n_clicks=0, className="btn btn-primary"),
                                    width="auto"
                                )
                            ])
                        ])
                    ], className="m-3")
                ], width=12)
            ]),
            html.Div(id="table2-front-output", className="m-3", style={"width": "100%", "minHeight": "800px"})
        ])
    ])
    return layout_mkt
