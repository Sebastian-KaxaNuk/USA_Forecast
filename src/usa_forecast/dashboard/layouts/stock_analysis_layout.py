import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta


def market_analysis_layout(market_data_dict: dict) -> html.Div:
    """
    Layout profesional para análisis de mercado OHLC con métricas de trading

    Args:
        market_data_dict: Diccionario con tickers como keys y DataFrames como valores
    """

    # Obtener lista de tickers disponibles
    ticker_options = [{"label": ticker, "value": ticker} for ticker in market_data_dict.keys()]

    # Calcular rango de fechas por defecto (últimos 3 meses)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)

    layout = html.Div([
        # Store para guardar los datos
        dcc.Store(id="store_market_data",
                  data={ticker: df.to_dict("split") for ticker, df in market_data_dict.items()}),
        dcc.Store(id="store_analysis_results"),

        # Header principal
        html.Div([
            html.H2("Market Analysis Dashboard",
                    className="text-center mb-4",
                    style={"fontFamily": "Arial", "fontWeight": "bold", "color": "#2c3e50"})
        ]),

        # Panel de control
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Analysis Parameters", className="mb-0",
                                style={"color": "#34495e", "fontWeight": "bold"})
                    ]),
                    dbc.CardBody([
                        # Selector de Ticker
                        html.Div([
                            html.Label("Select Ticker:",
                                       style={"fontWeight": "bold", "marginBottom": "5px"}),
                            dcc.Dropdown(
                                id='ticker-dropdown_analysis',
                                options=ticker_options,
                                placeholder="Choose a ticker to analyze",
                                value=list(market_data_dict.keys())[0] if ticker_options else None,
                                searchable=True,
                                clearable=False,
                                style={'marginBottom': '15px'}
                            )
                        ]),

                        # Selector de rango de fechas
                        html.Div([
                            html.Label("Date Range:",
                                       style={"fontWeight": "bold", "marginBottom": "5px"}),
                            dcc.DatePickerRange(
                                id='date-picker-range_analysis',
                                start_date=start_date,
                                end_date=end_date,
                                display_format='YYYY-MM-DD',
                                style={'marginBottom': '15px', 'width': '100%'}
                            )
                        ]),

                        # Opciones de análisis
                        html.Div([
                            html.Label("Analysis Options:",
                                       style={"fontWeight": "bold", "marginBottom": "5px"}),
                            dbc.Checklist(
                                id="analysis-options_checklist",
                                options=[
                                    {"label": " Technical Indicators", "value": "technical"},
                                    {"label": " Volume Analysis", "value": "volume"},
                                    {"label": " Price Targets Analysis", "value": "targets"},
                                    {"label": " Risk Metrics", "value": "risk"}
                                ],
                                value=["technical", "targets"],
                                inline=False,
                                style={'marginBottom': '15px'}
                            )
                        ]),

                        # Botones de acción
                        dbc.Row([
                            dbc.Col([
                                dbc.Button('Run Analysis',
                                           id='submit-button_analysis',
                                           n_clicks=0,
                                           color="primary",
                                           className="me-2",
                                           style={"width": "100%"})
                            ], width=6),
                            dbc.Col([
                                dbc.Button('Reset',
                                           id='reset-button_analysis',
                                           n_clicks=0,
                                           color="secondary",
                                           outline=True,
                                           style={"width": "100%"})
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm")
            ], width=12, lg=4),

            # Panel de métricas rápidas
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Key Metrics", className="mb-0",
                                style={"color": "#34495e", "fontWeight": "bold"})
                    ]),
                    dbc.CardBody([
                        html.Div(id="quick-metrics_output",
                                 style={"minHeight": "200px"})
                    ])
                ], className="shadow-sm")
            ], width=12, lg=8)
        ], className="mb-4"),

        # Área principal de resultados
        html.Div([
            # Tabs para diferentes vistas
            dbc.Tabs([
                dbc.Tab(label="Price Analysis", tab_id="price-tab"),
                dbc.Tab(label="Technical Indicators", tab_id="technical-tab"),
                dbc.Tab(label="Volume Analysis", tab_id="volume-tab"),
                dbc.Tab(label="Trading Signals", tab_id="signals-tab"),
                dbc.Tab(label="Summary Report", tab_id="summary-tab"),
                dbc.Tab(label="OHLC + Levels", tab_id="ohlc-levels-tab"),
            ], id="analysis-tabs", active_tab="price-tab"),

            # Contenido de las tabs
            html.Div(id="tab-content_analysis",
                     style={"minHeight": "500px", "padding": "20px"})
        ], className="mt-4"),

        # Loading component
        dcc.Loading(
            id="loading_analysis",
            children=[html.Div(id="loading-output_analysis")],
            type="default",
            style={"position": "absolute", "top": "50%", "left": "50%"}
        )
    ], style={"padding": "20px", "backgroundColor": "#f8f9fa", "minHeight": "100vh"})

    return layout