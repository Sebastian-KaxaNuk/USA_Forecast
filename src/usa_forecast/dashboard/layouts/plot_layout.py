import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

def candlestick_layout(mkt_data: dict) -> html.Div:
    ticker_options = [{"label": ticker, "value": ticker} for ticker in mkt_data.keys()]

    layout_candle = html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4('Candlestick Chart Parameters', className='card-title'),
                            dcc.Dropdown(
                                id='ticker_candle-dropdown-front',
                                options=ticker_options,
                                placeholder="Select a ticker",
                                searchable=True,
                                style={'marginBottom': '10px'}
                            ),
                            dbc.Row([
                                dbc.Col(
                                    html.Button('Submit', id='submit_candle-button-front', n_clicks=0,
                                                className="btn btn-primary"),
                                    width="auto"
                                ),
                                dbc.Col(
                                    html.Button('Toggle Dark Mode', id='toggle-darkmode-button-front', n_clicks=0,
                                                className="btn btn-dark"),
                                    width="auto"
                                )
                            ])
                        ])
                    ], className="m-3")
                ], width=12)
            ]),
            html.Div(id="candlestick-chart-container", className="m-3", style={"width": "100%", "minHeight": "800px"})
        ])
    ])
    return layout_candle