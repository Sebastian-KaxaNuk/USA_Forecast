from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import exceptions
import numpy as np
from datetime import datetime


def register_callback_market_analysis(app, market_data_dict):
    """
    Registra todos los callbacks para el análisis de mercado
    """

    @app.callback(
        [Output('quick-metrics_output', 'children'),
         Output('store_analysis_results', 'data')],
        [Input('submit-button_analysis', 'n_clicks')],
        [State('ticker-dropdown_analysis', 'value'),
         State('date-picker-range_analysis', 'start_date'),
         State('date-picker-range_analysis', 'end_date'),
         State('analysis-options_checklist', 'value'),
         State('store_market_data', 'data')]
    )
    def run_market_analysis(n_clicks, selected_ticker, start_date, end_date, analysis_options, store_data):
        """Ejecuta el análisis principal del ticker seleccionado"""

        if n_clicks is None or n_clicks == 0:
            raise exceptions.PreventUpdate

        if not selected_ticker or not store_data:
            return html.Div("Please select a ticker and try again.",
                            className="text-danger"), {}

        try:
            # Cargar datos del ticker seleccionado
            df_dict = store_data.get(selected_ticker)
            if df_dict is None:
                return html.Div("No data available for selected ticker.",
                                className="text-danger"), {}

            df = pd.DataFrame(**df_dict)
            df.index = pd.to_datetime(df.index)

            # Filtrar por rango de fechas
            if start_date and end_date:
                df = df.loc[start_date:end_date]

            if df.empty:
                return html.Div("No data available for selected date range.",
                                className="text-danger"), {}

            # Calcular métricas básicas
            current_price = df['close'].iloc[-1] if 'close' in df.columns else df.iloc[-1, 3]
            price_change = ((current_price - df['close'].iloc[0]) / df['close'].iloc[0] * 100) if len(df) > 1 else 0

            # Métricas de trading si están disponibles
            trading_metrics = {}
            if 'Compra_Apartir_de' in df.columns:
                trading_metrics['buy_from'] = df['Compra_Apartir_de'].iloc[-1]
            if 'Precio_Minimo_Que_Puede_Llegar' in df.columns:
                trading_metrics['min_price'] = df['Precio_Minimo_Que_Puede_Llegar'].iloc[-1]
            if 'Vender_Apartir_De' in df.columns:
                trading_metrics['sell_from'] = df['Vender_Apartir_De'].iloc[-1]
            if 'Precio_Maximo_Que_Puede_Llegar' in df.columns:
                trading_metrics['max_price'] = df['Precio_Maximo_Que_Puede_Llegar'].iloc[-1]

            # Volatilidad
            volatility = df['close'].pct_change().std() * np.sqrt(252) * 100 if 'close' in df.columns else 0

            # Crear tarjetas de métricas
            metrics_cards = []

            # Precio actual
            metrics_cards.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"${current_price:.2f}", className="card-title text-primary"),
                            html.P("Current Price", className="card-text small")
                        ])
                    ], className="text-center")
                ], width=6, lg=3)
            )

            # Cambio porcentual
            color = "success" if price_change >= 0 else "danger"
            metrics_cards.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{price_change:+.2f}%", className=f"card-title text-{color}"),
                            html.P("Period Change", className="card-text small")
                        ])
                    ], className="text-center")
                ], width=6, lg=3)
            )

            # Volatilidad
            metrics_cards.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(f"{volatility:.1f}%", className="card-title text-info"),
                            html.P("Annualized Volatility", className="card-text small")
                        ])
                    ], className="text-center")
                ], width=6, lg=3)
            )

            # Rango de trading si disponible
            if trading_metrics:
                range_text = "N/A"
                if 'min_price' in trading_metrics and 'max_price' in trading_metrics:
                    range_text = f"${trading_metrics['min_price']:.2f} - ${trading_metrics['max_price']:.2f}"

                metrics_cards.append(
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6(range_text, className="card-title text-warning"),
                                html.P("Expected Range", className="card-text small")
                            ])
                        ], className="text-center")
                    ], width=6, lg=3)
                )

            quick_metrics = dbc.Row(metrics_cards)

            # Preparar datos para almacenar
            analysis_results = {
                'ticker': selected_ticker,
                'data': df_dict,
                'current_price': current_price,
                'price_change': price_change,
                'volatility': volatility,
                'trading_metrics': trading_metrics,
                'analysis_options': analysis_options or []
            }

            return quick_metrics, analysis_results

        except Exception as e:
            return html.Div(f"Error in analysis: {str(e)}",
                            className="text-danger"), {}

    @app.callback(
        Output('tab-content_analysis', 'children'),
        [Input('analysis-tabs', 'active_tab'),
         Input('store_analysis_results', 'data')]
    )
    def render_tab_content(active_tab, analysis_results):
        """Renderiza el contenido según la tab activa"""

        if not analysis_results:
            return html.Div("Run analysis first to see results.",
                            className="text-muted text-center p-4")

        try:
            # Reconstruir DataFrame
            df_dict = analysis_results['data']
            df = pd.DataFrame(**df_dict)
            df.index = pd.to_datetime(df.index)

            ticker = analysis_results['ticker']

            if active_tab == "price-tab":
                return create_price_analysis_tab(df, ticker, analysis_results)
            elif active_tab == "ohlc-levels-tab":
                return create_ohlc_levels_tab(df, ticker, analysis_results)
            elif active_tab == "trading-metrics-tab":
                return create_trading_metrics_tab(df, ticker, analysis_results)
            elif active_tab == "technical-tab":
                return create_technical_analysis_tab(df, ticker, analysis_results)
            elif active_tab == "volume-tab":
                return create_volume_analysis_tab(df, ticker, analysis_results)
            elif active_tab == "signals-tab":
                return create_signals_analysis_tab(df, ticker, analysis_results)
            elif active_tab == "summary-tab":
                return create_summary_report_tab(df, ticker, analysis_results)
            else:
                return html.Div("Select a tab to view analysis.")

        except Exception as e:
            return html.Div(f"Error rendering tab: {str(e)}", className="text-danger")

    @app.callback(
        [Output('ticker-dropdown_analysis', 'value'),
         Output('analysis-options_checklist', 'value')],
        [Input('reset-button_analysis', 'n_clicks')],
        [State('store_market_data', 'data')]
    )
    def reset_analysis(n_clicks, store_data):
        """Reset del análisis"""
        if n_clicks and n_clicks > 0:
            first_ticker = list(store_data.keys())[0] if store_data else None
            return first_ticker, ["technical", "targets"]
        raise exceptions.PreventUpdate


def create_price_analysis_tab(df, ticker, analysis_results):
    """Crea el contenido del tab de análisis de precios con gráfica de velas profesional"""

    # Crear gráfico de candlestick más robusto
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.6, 0.25, 0.15],
        subplot_titles=['Price Action & Trading Levels', 'Trading Metrics Evolution', 'volume'],
        specs=[[{"secondary_y": False}], [{"secondary_y": True}], [{"secondary_y": False}]]
    )

    # Candlestick chart profesional
    if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        # Determinar colores para velas
        colors = ['green' if close >= open else 'red'
                  for close, open in zip(df['close'], df['open'])]

        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=ticker,
                increasing_line_color='#00C851',
                decreasing_line_color='#FF4444',
                increasing_fillcolor='rgba(0, 200, 81, 0.3)',
                decreasing_fillcolor='rgba(255, 68, 68, 0.3)',
                line=dict(width=1.5)
            ), row=1, col=1
        )

        # Agregar medias móviles
        if len(df) >= 20:
            sma_20 = df['close'].rolling(window=20).mean()
            ema_12 = df['close'].ewm(span=12).mean()

            fig.add_trace(
                go.Scatter(
                    x=df.index, y=sma_20,
                    name='SMA 20',
                    line=dict(color='blue', width=2, dash='dot'),
                    opacity=0.8
                ), row=1, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index, y=ema_12,
                    name='EMA 12',
                    line=dict(color='orange', width=2),
                    opacity=0.8
                ), row=1, col=1
            )

        # Bandas de Bollinger si hay suficientes datos
        if len(df) >= 20:
            sma_20 = df['close'].rolling(window=20).mean()
            std_20 = df['close'].rolling(window=20).std()
            bb_upper = sma_20 + (std_20 * 2)
            bb_lower = sma_20 - (std_20 * 2)

            fig.add_trace(
                go.Scatter(
                    x=df.index, y=bb_upper,
                    name='BB Upper',
                    line=dict(color='gray', width=1, dash='dash'),
                    opacity=0.5
                ), row=1, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index, y=bb_lower,
                    name='BB lower',
                    line=dict(color='gray', width=1, dash='dash'),
                    opacity=0.5,
                    fill='tonexty',
                    fillcolor='rgba(128, 128, 128, 0.1)'
                ), row=1, col=1
            )

    # Gráfico de métricas de trading en serie de tiempo
    trading_cols = ['Compra_Apartir_de', 'Precio_Minimo_Que_Puede_Llegar',
                    'Vender_Apartir_De', 'Precio_Maximo_Que_Puede_Llegar']

    colors_trading = ['#28a745', '#17a2b8', '#dc3545', '#6f42c1']
    line_styles = ['solid', 'dash', 'solid', 'dash']

    for i, col in enumerate(trading_cols):
        if col in df.columns:
            display_name = {
                'Compra_Apartir_de': 'Buy Level',
                'Precio_Minimo_Que_Puede_Llegar': 'Min Target',
                'Vender_Apartir_De': 'Sell Level',
                'Precio_Maximo_Que_Puede_Llegar': 'Max Target'
            }.get(col, col)

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=display_name,
                    line=dict(color=colors_trading[i], width=2.5, dash=line_styles[i]),
                    mode='lines+markers',
                    marker=dict(size=4)
                ), row=2, col=1
            )

    # volume chart con análisis
    if 'volume' in df.columns:
        # volumen con colores según precio
        volume_colors = ['rgba(0, 200, 81, 0.6)' if close >= open else 'rgba(255, 68, 68, 0.6)'
                         for close, open in zip(df['close'], df['open'])]

        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='volume',
                marker_color=volume_colors,
                opacity=0.7
            ), row=3, col=1
        )

        # Media móvil del volumen
        if len(df) >= 20:
            vol_ma = df['volume'].rolling(window=20).mean()
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=vol_ma,
                    name='volume MA 20',
                    line=dict(color='purple', width=2),
                    opacity=0.8
                ), row=3, col=1
            )

    # Configuración profesional del layout
    fig.update_layout(
        title={
            'text': f'{ticker} - Advanced Price Analysis',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black'}
        },
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        template='plotly_white',
        hovermode='x unified'
    )

    # Personalizar ejes
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)',
        showspikes=True,
        spikesnap="cursor",
        spikemode="across"
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)',
        tickformat='.2f'
    )

    # Títulos de ejes
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Trading Levels ($)", row=2, col=1)
    fig.update_yaxes(title_text="volume", row=3, col=1)
    fig.update_xaxes(title_text="Date", row=3, col=1)

    return dcc.Graph(
        figure=fig,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'{ticker}_price_analysis',
                'height': 800,
                'width': 1200,
                'scale': 1
            }
        }
    )


def create_ohlc_levels_tab(df, ticker, analysis_results):
    """Crea el contenido del tab de OHLC + Trading Levels con líneas profesionales"""

    # Verificar columnas necesarias
    ohlc_cols = ['open', 'high', 'low', 'close']
    trading_cols = ['Compra_Apartir_de', 'Precio_Minimo_Que_Puede_Llegar',
                    'Vender_Apartir_De', 'Precio_Maximo_Que_Puede_Llegar']

    available_ohlc = [col for col in ohlc_cols if col in df.columns]
    available_trading = [col for col in trading_cols if col in df.columns]

    if not available_ohlc and not available_trading:
        return html.Div([
            dbc.Alert("No OHLC or trading level data found.", color="warning", className="text-center")
        ])

    # Crear gráfico profesional de líneas - ESTILO MINIMALISTA
    fig = go.Figure()

    # Colores profesionales más suaves
    colors = {
        'open': '#3498db',  # Azul suave
        'high': '#e74c3c',  # Rojo suave
        'low': '#27ae60',  # Verde suave
        'close': '#2c3e50',  # Gris oscuro
        'Compra_Apartir_de': '#9b59b6',  # Púrpura suave
        'Precio_Minimo_Que_Puede_Llegar': '#f39c12',  # Naranja suave
        'Vender_Apartir_De': '#e67e22',  # Naranja rojizo
        'Precio_Maximo_Que_Puede_Llegar': '#34495e'  # Gris azulado
    }

    # Estilos de línea más sutiles
    line_styles = {
        'open': 'solid',
        'high': 'solid',
        'low': 'solid',
        'close': 'solid',
        'Compra_Apartir_de': 'dash',
        'Precio_Minimo_Que_Puede_Llegar': 'dot',
        'Vender_Apartir_De': 'dash',
        'Precio_Maximo_Que_Puede_Llegar': 'dot'
    }

    # Nombres descriptivos
    display_names = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'Compra_Apartir_de': 'Buy Level',
        'Precio_Minimo_Que_Puede_Llegar': 'Min Target',
        'Vender_Apartir_De': 'Sell Level',
        'Precio_Maximo_Que_Puede_Llegar': 'Max Target'
    }

    # Agregar líneas OHLC - LÍNEAS MÁS DELGADAS
    for col in available_ohlc:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[col],
                name=display_names[col],
                line=dict(
                    color=colors[col],
                    width=1.5,  # Más delgada
                    dash=line_styles[col]
                ),
                mode='lines',
                opacity=0.8,  # Más suave
                hovertemplate=f'<b>{display_names[col]}</b><br>' +
                              'Date: %{x}<br>' +
                              'Price: $%{y:.2f}<br>' +
                              '<extra></extra>'
            )
        )

    # Agregar líneas de trading levels - MÁS DELGADAS
    for col in available_trading:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[col],
                name=display_names[col],
                line=dict(
                    color=colors[col],
                    width=1.8,  # Más delgada
                    dash=line_styles[col]
                ),
                mode='lines',
                opacity=0.7,  # Más sutil
                hovertemplate=f'<b>{display_names[col]}</b><br>' +
                              'Date: %{x}<br>' +
                              'Level: $%{y:.2f}<br>' +
                              '<extra></extra>'
            )
        )

    # Configuración minimalista del gráfico
    fig.update_layout(
        title={
            'text': f'{ticker} - OHLC & Trading Levels',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Arial', 'color': '#2c3e50'}
        },
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=500,  # Más compacto
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(t=80, b=60, l=60, r=60)
    )

    # Ejes minimalistas
    fig.update_xaxes(
        showgrid=True,
        gridwidth=0.5,  # Grid más sutil
        gridcolor='rgba(128, 128, 128, 0.1)',
        showline=True,
        linewidth=1,
        linecolor='rgba(128, 128, 128, 0.3)',
        tickfont=dict(size=10)
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=0.5,  # Grid más sutil
        gridcolor='rgba(128, 128, 128, 0.1)',
        tickformat='.2f',
        showline=True,
        linewidth=1,
        linecolor='rgba(128, 128, 128, 0.3)',
        tickfont=dict(size=10)
    )

    # Crear tabla de datos para mostrar los últimos valores
    table_data = []
    latest_date = df.index[-1].strftime('%Y-%m-%d') if len(df) > 0 else 'N/A'

    # Agregar datos OHLC a la tabla
    for col in available_ohlc:
        if not df[col].isna().all():
            current_value = df[col].iloc[-1]
            prev_value = df[col].iloc[-2] if len(df) > 1 else current_value
            change = current_value - prev_value
            change_pct = (change / prev_value * 100) if prev_value != 0 else 0

            table_data.append({
                'Metric': display_names[col],
                'Current Value': f"${current_value:.2f}",
                'Previous Value': f"${prev_value:.2f}",
                'Change ($)': f"{change:+.2f}",
                'Change (%)': f"{change_pct:+.2f}%",
                'Category': 'OHLC Data'
            })

    # Agregar datos de trading levels a la tabla
    for col in available_trading:
        if not df[col].isna().all():
            current_value = df[col].iloc[-1]
            prev_value = df[col].iloc[-2] if len(df) > 1 else current_value
            change = current_value - prev_value
            change_pct = (change / prev_value * 100) if prev_value != 0 else 0

            table_data.append({
                'Metric': display_names[col],
                'Current Value': f"${current_value:.2f}",
                'Previous Value': f"${prev_value:.2f}",
                'Change ($)': f"{change:+.2f}",
                'Change (%)': f"{change_pct:+.2f}%",
                'Category': 'Trading Levels'
            })

    # Crear DataFrame para la tabla resumen
    table_df = pd.DataFrame(table_data)

    # Configurar la tabla resumen
    summary_table = dash_table.DataTable(
        data=table_df.to_dict('records'),
        columns=[
            {"name": "Metric", "id": "Metric", "type": "text"},
            {"name": "Current Value", "id": "Current Value", "type": "text"},
            {"name": "Previous Value", "id": "Previous Value", "type": "text"},
            {"name": "Change ($)", "id": "Change ($)", "type": "text"},
            {"name": "Change (%)", "id": "Change (%)", "type": "text"},
            {"name": "Category", "id": "Category", "type": "text"}
        ],
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        page_size=45,
        style_cell={
            'textAlign': 'center',
            'fontFamily': 'Arial',
            'fontSize': '12px',
            'padding': '8px',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_header={
            'backgroundColor': '#ecf0f1',
            'color': '#2c3e50',
            'fontWeight': 'bold',
            'border': '1px solid #bdc3c7',
            'textAlign': 'center',
            'fontSize': '12px'
        },
        style_data={
            'backgroundColor': 'white',
            'border': '1px solid #ecf0f1',
            'fontSize': '13px'
        },
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Change (%)} contains "+"',
                    'column_id': 'Change (%)'
                },
                'backgroundColor': '#d5f4e6',
                'color': '#27ae60'
            },
            {
                'if': {
                    'filter_query': '{Change (%)} contains "-"',
                    'column_id': 'Change (%)'
                },
                'backgroundColor': '#fadbd8',
                'color': '#e74c3c'
            }
        ]
    )

    # Preparar datos para tabla scrollable de time series
    all_cols = available_ohlc + available_trading
    df_display = df[all_cols].copy()

    # Agregar columna de fecha como string para la tabla
    df_display.insert(0, 'Date', df_display.index.strftime('%Y-%m-%d %H:%M:%S'))

    # Redondear valores numéricos
    for col in all_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].round(2)

    # Preparar columnas para la tabla scrollable
    scrollable_columns = [{"name": "Date", "id": "Date", "type": "text"}]
    for col in all_cols:
        if col in df_display.columns:
            scrollable_columns.append({
                "name": display_names.get(col, col),
                "id": col,
                "type": "numeric",
                "format": {"specifier": ",.2f"}
            })

    # Tabla scrollable de time series
    scrollable_table = dash_table.DataTable(
        data=df_display.to_dict('records'),
        columns=scrollable_columns,
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        page_size=50,
        fixed_columns={"headers": True, "data": 1},  # Fecha fija
        fixed_rows={"headers": True},  # Headers fijos
        style_table={
            'height': '400px',
            'overflowY': 'auto',
            'overflowX': 'auto',
            'border': '1px solid #bdc3c7',
            'width': '100%',
            "minWidth": "100%"  # asegura expansión
        },
        style_cell={
            'textAlign': 'center',
            'fontFamily': 'Arial',
            'fontSize': '11px',
            'padding': '6px',
            'whiteSpace': 'normal',
            'minWidth': '80px',
            'maxWidth': '120px'
        },
        style_header={
            'backgroundColor': '#34495e',
            'color': 'white',
            'fontWeight': 'bold',
            'border': '1px solid #2c3e50',
            'textAlign': 'center',
            'fontSize': '11px',
            'position': 'sticky',
            'top': '0'
        },
        style_data={
            'backgroundColor': 'white',
            'border': '1px solid #ecf0f1',
            'fontSize': '13px'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'Date'},
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'textAlign': 'left',
                "width": "160px",
                'minWidth': '160px',
                'maxWidth': '160px'
            }
        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            }
        ]
    )

    return html.Div([
        # Información de fecha
        html.Div([
            html.H6(f"Last Updated: {latest_date}",
                    className="text-center text-muted mb-3",
                    style={'fontStyle': 'italic', 'fontSize': '14px'})
        ]),

        # Tabla resumen arriba
        html.Div([
            html.H6("Summary - Latest Values", className="mb-2", style={'fontSize': '16px'}),
            summary_table
        ], className="mb-3"),

        html.Hr(style={'margin': '15px 0'}),

        # Gráfico principal
        dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'{ticker}_ohlc_levels',
                    'height': 500,
                    'width': 1200,
                    'scale': 1
                }
            }
        ),

        html.Hr(style={'margin': '15px 0'}),

        # Tabla scrollable de time series
        html.Div([
            html.H6("Historical Data - Time Series", className="mb-2", style={'fontSize': '16px'}),
            html.P("Scroll horizontally and vertically to explore all data. Date column is fixed for reference.",
                   className="text-muted small mb-2"),
            scrollable_table
        ], className="mb-3")
    ])

def create_trading_metrics_tab(df, ticker, analysis_results):
    """Crea el contenido del tab de métricas de trading con gráficos y tablas detalladas"""

    trading_cols = ['Compra_Apartir_de', 'Precio_Minimo_Que_Puede_Llegar',
                    'Vender_Apartir_De', 'Precio_Maximo_Que_Puede_Llegar']

    # Verificar que existan las columnas
    available_cols = [col for col in trading_cols if col in df.columns]

    if not available_cols:
        return html.Div([
            dbc.Alert("Trading metrics columns not found in the dataset.", color="warning", className="text-center")
        ])

    # Crear subplot para gráficos
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=['Trading Levels Evolution', 'Price vs Trading Ranges',
                        'Buy/Sell Spread Analysis', 'Target Ranges Analysis',
                        'Trading Efficiency Metrics', 'Risk-Reward Analysis'],
        specs=[[{"colspan": 2}, None],
               [{"secondary_y": True}, {"secondary_y": True}],
               [{"secondary_y": False}, {"secondary_y": False}]],
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
        row_heights=[0.4, 0.3, 0.3]
    )

    # 1. Gráfico principal de evolución de niveles de trading
    colors_trading = {'Compra_Apartir_de': '#28a745', 'Precio_Minimo_Que_Puede_Llegar': '#17a2b8',
                      'Vender_Apartir_De': '#dc3545', 'Precio_Maximo_Que_Puede_Llegar': '#6f42c1'}

    for col in available_cols:
        display_name = {
            'Compra_Apartir_de': 'Buy Level',
            'Precio_Minimo_Que_Puede_Llegar': 'Min Target',
            'Vender_Apartir_De': 'Sell Level',
            'Precio_Maximo_Que_Puede_Llegar': 'Max Target'
        }.get(col, col)

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[col],
                name=display_name,
                line=dict(color=colors_trading[col], width=3),
                mode='lines+markers',
                marker=dict(size=5, symbol='circle')
            ), row=1, col=1
        )

    # Agregar precio actual si existe
    if 'close' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['close'],
                name='Current Price',
                line=dict(color='black', width=2, dash='dot'),
                opacity=0.8
            ), row=1, col=1
        )

    # 2. Análisis de rangos de trading
    if 'Compra_Apartir_de' in df.columns and 'Vender_Apartir_De' in df.columns:
        buy_sell_spread = df['Vender_Apartir_De'] - df['Compra_Apartir_de']
        spread_pct = (buy_sell_spread / df['Compra_Apartir_de']) * 100

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=buy_sell_spread,
                name='Buy-Sell Spread ($)',
                line=dict(color='orange', width=2),
                yaxis='y2'
            ), row=2, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=spread_pct,
                name='Spread %',
                line=dict(color='red', width=2),
                yaxis='y'
            ), row=2, col=1
        )

    # 3. Análisis de targets
    if 'Precio_Minimo_Que_Puede_Llegar' in df.columns and 'Precio_Maximo_Que_Puede_Llegar' in df.columns:
        target_range = df['Precio_Maximo_Que_Puede_Llegar'] - df['Precio_Minimo_Que_Puede_Llegar']

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=target_range,
                name='Target Range ($)',
                line=dict(color='purple', width=2),
                fill='tonexty' if len(fig.data) > 0 else None,
                fillcolor='rgba(128, 0, 128, 0.1)'
            ), row=2, col=2
        )

        # Punto medio de targets
        target_midpoint = (df['Precio_Maximo_Que_Puede_Llegar'] + df['Precio_Minimo_Que_Puede_Llegar']) / 2
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=target_midpoint,
                name='Target Midpoint',
                line=dict(color='green', width=2, dash='dash')
            ), row=2, col=2
        )

    # 4. Métricas de eficiencia
    if all(col in df.columns for col in ['Compra_Apartir_de', 'Vender_Apartir_De', 'close']):
        # Calcular cuándo el precio está en zona de compra/venta
        in_buy_zone = df['close'] <= df['Compra_Apartir_de']
        in_sell_zone = df['close'] >= df['Vender_Apartir_De']

        # Crear gráfico de barras para eficiencia
        efficiency_data = pd.DataFrame({
            'Date': df.index,
            'Buy_Zone': in_buy_zone.astype(int),
            'Sell_Zone': in_sell_zone.astype(int),
            'Neutral_Zone': (~in_buy_zone & ~in_sell_zone).astype(int)
        })

        fig.add_trace(
            go.Bar(
                x=efficiency_data['Date'],
                y=efficiency_data['Buy_Zone'],
                name='In Buy Zone',
                marker_color='green',
                opacity=0.7
            ), row=3, col=1
        )

        fig.add_trace(
            go.Bar(
                x=efficiency_data['Date'],
                y=efficiency_data['Sell_Zone'],
                name='In Sell Zone',
                marker_color='red',
                opacity=0.7
            ), row=3, col=1
        )

    # 5. Risk-Reward ratio
    if all(col in df.columns for col in available_cols[:4]):
        # Calcular risk-reward basado en rangos
        potential_upside = df['Precio_Maximo_Que_Puede_Llegar'] - df['close'] if 'close' in df.columns else 0
        potential_downside = df['close'] - df['Precio_Minimo_Que_Puede_Llegar'] if 'close' in df.columns else 0

        risk_reward = potential_upside / potential_downside.replace(0, np.nan)

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=risk_reward,
                name='Risk-Reward Ratio',
                line=dict(color='gold', width=3),
                mode='lines+markers'
            ), row=3, col=2
        )

        # Línea de referencia 1:1
        fig.add_hline(y=1, line_dash="dash", line_color="gray",
                      annotation_text="1:1 R/R", row=3, col=2)

    # Configuración del layout
    fig.update_layout(
        title={
            'text': f'{ticker} - Trading Metrics Analysis',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Arial Black'}
        },
        height=900,
        showlegend=True,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Personalizar ejes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.2)')

    # Crear tabla de estadísticas
    stats_data = []
    for col in available_cols:
        if col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                stats_data.append({
                    'Metric': {
                        'Compra_Apartir_de': 'Buy Level',
                        'Precio_Minimo_Que_Puede_Llegar': 'Min Target',
                        'Vender_Apartir_De': 'Sell Level',
                        'Precio_Maximo_Que_Puede_Llegar': 'Max Target'
                    }.get(col, col),
                    'Current': f"${col_data.iloc[-1]:.2f}",
                    'Average': f"${col_data.mean():.2f}",
                    'Min': f"${col_data.min():.2f}",
                    'Max': f"${col_data.max():.2f}",
                    'Std Dev': f"${col_data.std():.2f}",
                    'Trend': '↗️' if col_data.iloc[-1] > col_data.iloc[0] else '↘️' if col_data.iloc[-1] <
                                                                                       col_data.iloc[0] else '→'
                })

    stats_df = pd.DataFrame(stats_data)

    # Crear la tabla con dash_table
    table = dash_table.DataTable(
        data=stats_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in stats_df.columns],
        style_cell={
            'textAlign': 'center',
            'fontFamily': 'Arial',
            'fontSize': '12px',
            'padding': '8px'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'border': '1px solid #dee2e6'
        },
        style_data={
            'backgroundColor': 'white',
            'border': '1px solid #dee2e6'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'Trend'},
                'fontSize': '16px'
            }
        ]
    )

    # Crear análisis adicional
    analysis_cards = []

    # Calcular métricas adicionales
    if 'Compra_Apartir_de' in df.columns and 'Vender_Apartir_De' in df.columns:
        avg_spread = (df['Vender_Apartir_De'] - df['Compra_Apartir_de']).mean()
        avg_spread_pct = ((df['Vender_Apartir_De'] - df['Compra_Apartir_de']) / df['Compra_Apartir_de'] * 100).mean()

        analysis_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Average Trading Range", className="card-title"),
                        html.H3(f"${avg_spread:.2f}", className="text-primary"),
                        html.P(f"({avg_spread_pct:.1f}%)", className="text-muted")
                    ])
                ], className="text-center h-100")
            ], width=6, md=3)
        )

    if 'Precio_Minimo_Que_Puede_Llegar' in df.columns and 'Precio_Maximo_Que_Puede_Llegar' in df.columns:
        avg_target_range = (df['Precio_Maximo_Que_Puede_Llegar'] - df['Precio_Minimo_Que_Puede_Llegar']).mean()

        analysis_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Average Target Range", className="card-title"),
                        html.H3(f"${avg_target_range:.2f}", className="text-success"),
                        html.P("Price Target Spread", className="text-muted")
                    ])
                ], className="text-center h-100")
            ], width=6, md=3)
        )

    # Trading efficiency
    if 'close' in df.columns and 'Compra_Apartir_de' in df.columns and 'Vender_Apartir_De' in df.columns:
        in_range = ((df['close'] >= df['Compra_Apartir_de']) & (df['close'] <= df['Vender_Apartir_De'])).sum()
        total_periods = len(df)
        efficiency = (in_range / total_periods) * 100

        analysis_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Trading Efficiency", className="card-title"),
                        html.H3(f"{efficiency:.1f}%", className="text-info"),
                        html.P("Time in Trading Range", className="text-muted")
                    ])
                ], className="text-center h-100")
            ], width=6, md=3)
        )

    # Volatility of trading levels
    if available_cols:
        level_volatilities = [df[col].std() for col in available_cols if col in df.columns]
        avg_volatility = np.mean(level_volatilities)

        analysis_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Level Volatility", className="card-title"),
                        html.H3(f"${avg_volatility:.2f}", className="text-warning"),
                        html.P("Avg Level Std Dev", className="text-muted")
                    ])
                ], className="text-center h-100")
            ], width=6, md=3)
        )

    return html.Div([
        # Gráficos principales
        dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'{ticker}_trading_metrics',
                    'height': 900,
                    'width': 1400,
                    'scale': 1
                }
            }
        ),

        html.Hr(),

        # Cards de análisis
        html.H5("Key Trading Metrics", className="mb-3"),
        dbc.Row(analysis_cards, className="mb-4"),

        html.Hr(),

        # Tabla de estadísticas
        html.H5("Statistical Summary", className="mb-3"),
        table,

        html.Hr(),

        # Insights adicionales
        html.H5("Trading Insights", className="mb-3"),
        html.Div([
            html.P("📈 Use this analysis to identify optimal entry and exit points based on historical trading levels."),
            html.P("🎯 Monitor the risk-reward ratio to ensure favorable trading conditions."),
            html.P(
                "📊 Track the efficiency metrics to understand how often the price stays within your trading ranges."),
            html.P("⚠️ higher level volatility indicates more dynamic trading conditions requiring closer monitoring.")
        ], className="alert alert-info")
    ])


def create_technical_analysis_tab(df, ticker, analysis_results):
    """Crea el contenido del tab de análisis técnico mejorado"""

    if 'close' not in df.columns:
        return html.Div("Price data (close) not available for technical analysis",
                        className="text-muted text-center p-4")

    # Calcular indicadores técnicos avanzados
    close_prices = df['close'].copy()

    # Moving averages
    df['SMA_10'] = close_prices.rolling(window=10).mean()
    df['SMA_20'] = close_prices.rolling(window=20).mean()
    df['SMA_50'] = close_prices.rolling(window=50).mean()
    df['EMA_12'] = close_prices.ewm(span=12).mean()
    df['EMA_26'] = close_prices.ewm(span=26).mean()

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

    # RSI mejorado
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Bandas de Bollinger
    if len(df) >= 20:
        sma_20 = close_prices.rolling(window=20).mean()
        std_20 = close_prices.rolling(window=20).std()
        df['BB_Upper'] = sma_20 + (std_20 * 2)
        df['BB_lower'] = sma_20 - (std_20 * 2)
        df['BB_Middle'] = sma_20
        df['BB_Width'] = ((df['BB_Upper'] - df['BB_lower']) / df['BB_Middle']) * 100

    # Stochastic Oscillator
    if all(col in df.columns for col in ['high', 'low']):
        lowest_low = df['low'].rolling(window=14).min()
        highest_high = df['high'].rolling(window=14).max()
        df['%K'] = 100 * (close_prices - lowest_low) / (highest_high - lowest_low)
        df['%D'] = df['%K'].rolling(window=3).mean()

    # Crear subplots
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.4, 0.15, 0.15, 0.15, 0.15],
        subplot_titles=[
            'Price & Moving Averages with Bollinger Bands',
            'MACD',
            'RSI',
            'Stochastic Oscillator',
            'volume & BB Width'
        ]
    )

    # 1. Gráfico de precio con medias móviles y Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=df['close'], name='close Price',
                   line=dict(color='black', width=2)), row=1, col=1
    )

    # Moving averages
    colors_ma = ['blue', 'red', 'green', 'orange', 'purple']
    ma_cols = ['SMA_10', 'SMA_20', 'SMA_50', 'EMA_12', 'EMA_26']
    ma_names = ['SMA 10', 'SMA 20', 'SMA 50', 'EMA 12', 'EMA 26']

    for i, (col, name) in enumerate(zip(ma_cols, ma_names)):
        if col in df.columns and not df[col].isna().all():
            fig.add_trace(
                go.Scatter(x=df.index, y=df[col], name=name,
                           line=dict(color=colors_ma[i], width=1.5, dash='dot')),
                row=1, col=1
            )

    # Bollinger Bands
    if all(col in df.columns for col in ['BB_Upper', 'BB_lower', 'BB_Middle']):
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                       line=dict(color='gray', width=1), opacity=0.5),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_lower'], name='BB lower',
                       line=dict(color='gray', width=1), opacity=0.5,
                       fill='tonexty', fillcolor='rgba(128, 128, 128, 0.1)'),
            row=1, col=1
        )

    # 2. MACD
    if all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD'], name='MACD',
                       line=dict(color='blue', width=2)), row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal',
                       line=dict(color='red', width=2)), row=2, col=1
        )

        # Histogram con colores
        colors_hist = ['green' if x >= 0 else 'red' for x in df['MACD_Histogram']]
        fig.add_trace(
            go.Bar(x=df.index, y=df['MACD_Histogram'], name='Histogram',
                   marker_color=colors_hist, opacity=0.6), row=2, col=1
        )

    # 3. RSI
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI',
                       line=dict(color='purple', width=2)), row=3, col=1
        )
        # Líneas de sobrecompra y sobreventa
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                      annotation_text="Overbought", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                      annotation_text="Oversold", row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)

    # 4. Stochastic Oscillator
    if all(col in df.columns for col in ['%K', '%D']):
        fig.add_trace(
            go.Scatter(x=df.index, y=df['%K'], name='%K',
                       line=dict(color='blue', width=2)), row=4, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['%D'], name='%D',
                       line=dict(color='red', width=2)), row=4, col=1
        )
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=4, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=4, col=1)

    # 5. volume y BB Width
    if 'volume' in df.columns:
        fig.add_trace(
            go.Bar(x=df.index, y=df['volume'], name='volume',
                   marker_color='rgba(0,0,255,0.3)', yaxis='y'), row=5, col=1
        )

    if 'BB_Width' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Width'], name='BB Width %',
                       line=dict(color='orange', width=2), yaxis='y2'), row=5, col=1
        )

    # Configuración del layout
    fig.update_layout(
        title={
            'text': f'{ticker} - Comprehensive Technical Analysis',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'family': 'Arial Black'}
        },
        height=1000,
        showlegend=True,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)
        )
    )

    # Personalizar ejes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128, 128, 128, 0.2)')

    # Títulos de ejes específicos
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
    fig.update_yaxes(title_text="Stochastic", row=4, col=1, range=[0, 100])
    fig.update_yaxes(title_text="volume", row=5, col=1)
    fig.update_xaxes(title_text="Date", row=5, col=1)

    # Crear tabla de señales técnicas
    signals_data = []
    current_close = df['close'].iloc[-1] if len(df) > 0 else 0

    # Señales de MA
    if 'SMA_20' in df.columns and not df['SMA_20'].isna().all():
        current_sma20 = df['SMA_20'].iloc[-1]
        ma_signal = "BULLISH" if current_close > current_sma20 else "BEARISH"
        signals_data.append({
            'Indicator': 'SMA 20',
            'Current Value': f"${current_sma20:.2f}",
            'Signal': ma_signal,
            'Strength': 'Medium'
        })

    # Señales de RSI
    if 'RSI' in df.columns and not df['RSI'].isna().all():
        current_rsi = df['RSI'].iloc[-1]
        if current_rsi > 70:
            rsi_signal = "OVERBOUGHT"
            strength = "Strong"
        elif current_rsi < 30:
            rsi_signal = "OVERSOLD"
            strength = "Strong"
        else:
            rsi_signal = "NEUTRAL"
            strength = "Weak"

        signals_data.append({
            'Indicator': 'RSI',
            'Current Value': f"{current_rsi:.1f}",
            'Signal': rsi_signal,
            'Strength': strength
        })

    # Señales de MACD
    if all(col in df.columns for col in ['MACD', 'MACD_Signal']) and not df['MACD'].isna().all():
        current_macd = df['MACD'].iloc[-1]
        current_signal = df['MACD_Signal'].iloc[-1]
        macd_signal = "BULLISH" if current_macd > current_signal else "BEARISH"
        signals_data.append({
            'Indicator': 'MACD',
            'Current Value': f"{current_macd:.4f}",
            'Signal': macd_signal,
            'Strength': 'Medium'
        })

    # Señales de Bollinger Bands
    if all(col in df.columns for col in ['BB_Upper', 'BB_lower']) and not df['BB_Upper'].isna().all():
        current_bb_upper = df['BB_Upper'].iloc[-1]
        current_bb_lower = df['BB_lower'].iloc[-1]

        if current_close > current_bb_upper:
            bb_signal = "OVERBOUGHT"
        elif current_close < current_bb_lower:
            bb_signal = "OVERSOLD"
        else:
            bb_signal = "NORMAL"

        signals_data.append({
            'Indicator': 'Bollinger Bands',
            'Current Value': f"${current_close:.2f}",
            'Signal': bb_signal,
            'Strength': 'Medium'
        })

    # Crear DataFrame para la tabla
    signals_df = pd.DataFrame(signals_data)

    # Tabla de señales
    signals_table = dash_table.DataTable(
        data=signals_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in signals_df.columns],
        style_cell={
            'textAlign': 'center',
            'fontFamily': 'Arial',
            'fontSize': '12px',
            'padding': '10px'
        },
        style_header={
            'backgroundColor': '#343a40',
            'color': 'white',
            'fontWeight': 'bold',
            'border': '1px solid #dee2e6'
        },
        style_data={
            'backgroundColor': 'white',
            'border': '1px solid #dee2e6'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{Signal} = BULLISH', 'column_id': 'Signal'},
                'backgroundColor': '#d4edda',
                'color': '#155724'
            },
            {
                'if': {'filter_query': '{Signal} = BEARISH', 'column_id': 'Signal'},
                'backgroundColor': '#f8d7da',
                'color': '#721c24'
            },
            {
                'if': {'filter_query': '{Signal} = OVERBOUGHT', 'column_id': 'Signal'},
                'backgroundColor': '#fff3cd',
                'color': '#856404'
            },
            {
                'if': {'filter_query': '{Signal} = OVERSOLD', 'column_id': 'Signal'},
                'backgroundColor': '#cce7ff',
                'color': '#004085'
            }
        ]
    )

    return html.Div([
        # Gráfico principal
        dcc.Graph(
            figure=fig,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'{ticker}_technical_analysis',
                    'height': 1000,
                    'width': 1400,
                    'scale': 1
                }
            }
        ),

        html.Hr(),

        # Tabla de señales
        html.H5("Technical Signals Summary", className="mb-3"),
        signals_table,

        html.Hr(),

        # Interpretación de indicadores
        html.H5("Indicator Interpretation", className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.H6("Moving Averages", className="text-primary"),
                html.P("Price above MA = Bullish trend"),
                html.P("Price below MA = Bearish trend"),
            ], width=6, md=3),
            dbc.Col([
                html.H6("RSI", className="text-success"),
                html.P("> 70 = Overbought"),
                html.P("< 30 = Oversold"),
            ], width=6, md=3),
            dbc.Col([
                html.H6("MACD", className="text-info"),
                html.P("MACD > Signal = Bullish"),
                html.P("MACD < Signal = Bearish"),
            ], width=6, md=3),
            dbc.Col([
                html.H6("Bollinger Bands", className="text-warning"),
                html.P("Price > Upper = Overbought"),
                html.P("Price < lower = Oversold"),
            ], width=6, md=3)
        ], className="alert alert-light")
    ])


def create_volume_analysis_tab(df, ticker, analysis_results):
    """Crea el contenido del tab de análisis de volumen"""

    if 'volume' not in df.columns:
        return html.Div("volume data not available", className="text-muted text-center p-4")

    # Análisis de volumen
    avg_volume = df['volume'].rolling(window=20).mean()
    volume_ratio = df['volume'] / avg_volume

    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=['volume Trend', 'volume vs Price',
                                        'volume Ratio', 'volume Distribution'])

    # volume trend
    fig.add_trace(go.Scatter(x=df.index, y=df['volume'], name='volume'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=avg_volume, name='20-day Avg'), row=1, col=1)

    # volume vs Price
    if 'close' in df.columns:
        fig.add_trace(go.Scatter(x=df['volume'], y=df['close'], mode='markers', name='Vol vs Price'), row=1, col=2)

    # volume ratio
    fig.add_trace(go.Bar(x=df.index, y=volume_ratio, name='volume Ratio'), row=2, col=1)

    # volume distribution
    fig.add_trace(go.Histogram(x=df['volume'], name='volume Distribution'), row=2, col=2)

    fig.update_layout(title=f'{ticker} - volume Analysis', height=600)

    return dcc.Graph(figure=fig)


def create_signals_analysis_tab(df, ticker, analysis_results):
    """Crea el contenido del tab de señales de trading"""

    trading_metrics = analysis_results.get('trading_metrics', {})
    current_price = analysis_results.get('current_price', 0)

    signals = []

    # Generar señales basadas en las métricas de trading
    if 'buy_from' in trading_metrics and 'sell_from' in trading_metrics:
        buy_level = trading_metrics['buy_from']
        sell_level = trading_metrics['sell_from']

        if current_price <= buy_level:
            signals.append({
                'Signal': 'BUY',
                'Reason': f'Price at/below buy level (${buy_level:.2f})',
                'Strength': 'Strong',
                'Color': 'success'
            })
        elif current_price >= sell_level:
            signals.append({
                'Signal': 'SELL',
                'Reason': f'Price at/above sell level (${sell_level:.2f})',
                'Strength': 'Strong',
                'Color': 'danger'
            })
        else:
            signals.append({
                'Signal': 'HOLD',
                'Reason': f'Price between levels (${buy_level:.2f} - ${sell_level:.2f})',
                'Strength': 'Neutral',
                'Color': 'warning'
            })

    # RSI signals
    if 'close' in df.columns and len(df) >= 14:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]

        if current_rsi < 30:
            signals.append({
                'Signal': 'BUY',
                'Reason': f'RSI oversold ({current_rsi:.1f})',
                'Strength': 'Moderate',
                'Color': 'success'
            })
        elif current_rsi > 70:
            signals.append({
                'Signal': 'SELL',
                'Reason': f'RSI overbought ({current_rsi:.1f})',
                'Strength': 'Moderate',
                'Color': 'danger'
            })

    # Crear cards para las señales
    signal_cards = []
    for signal in signals:
        signal_cards.append(
            dbc.Col([
                dbc.Alert([
                    html.H4(signal['Signal'], className="alert-heading"),
                    html.P(signal['Reason']),
                    html.Hr(),
                    html.P(f"Strength: {signal['Strength']}", className="mb-0")
                ], color=signal['Color'])
            ], width=12, md=6, lg=4)
        )

    if not signal_cards:
        signal_cards.append(
            dbc.Col([
                dbc.Alert("No clear signals at this time", color="info")
            ], width=12)
        )

    return html.Div([
        html.H4("Trading Signals", className="mb-4"),
        dbc.Row(signal_cards)
    ])


def create_summary_report_tab(df, ticker, analysis_results):
    """Crea el contenido del tab de reporte resumen"""

    current_price = analysis_results.get('current_price', 0)
    price_change = analysis_results.get('price_change', 0)
    volatility = analysis_results.get('volatility', 0)
    trading_metrics = analysis_results.get('trading_metrics', {})

    summary_content = [
        html.H4(f"Analysis Summary for {ticker}", className="mb-4"),

        dbc.Row([
            dbc.Col([
                html.H5("Price Information"),
                html.Ul([
                    html.Li(f"Current Price: ${current_price:.2f}"),
                    html.Li(f"Period Change: {price_change:+.2f}%"),
                    html.Li(f"Annualized Volatility: {volatility:.1f}%"),
                ])
            ], width=6),

            dbc.Col([
                html.H5("Trading Levels"),
                html.Ul([
                    html.Li(f"Buy From: ${trading_metrics.get('buy_from', 'N/A')}"),
                    html.Li(f"Sell From: ${trading_metrics.get('sell_from', 'N/A')}"),
                    html.Li(f"Min Target: ${trading_metrics.get('min_price', 'N/A')}"),
                    html.Li(f"Max Target: ${trading_metrics.get('max_price', 'N/A')}"),
                ])
            ], width=6)
        ]),

        html.Hr(),

        html.H5("Risk Assessment"),
        html.P(f"Based on the current volatility of {volatility:.1f}%, this asset shows " +
               ("high" if volatility > 30 else "moderate" if volatility > 15 else "low") +
               " risk characteristics.")
    ]

    return html.Div(summary_content)