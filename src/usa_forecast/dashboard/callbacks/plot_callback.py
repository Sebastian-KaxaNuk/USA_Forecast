from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
from src.usa_forecast.plotting.candlestick_plotly import generate_candlestick_with_volume

def register_callback_candlestick_chart(app, mkt_data: dict):
    @app.callback(
        Output('candlestick-chart-container', 'children'),
        Input('submit_candle-button-front', 'n_clicks'),
        Input('toggle-darkmode-button-front', 'n_clicks'),
        State('ticker_candle-dropdown-front', 'value'),
    )
    def display_candlestick_chart(submit_clicks, dark_clicks, selected_ticker):
        if not submit_clicks or not selected_ticker:
            return html.Div("Please select a ticker and press Submit.")

        df = mkt_data.get(selected_ticker)
        if df is None or df.empty:
            return html.Div(f"No data available for {selected_ticker}.")

        required_cols = {'open', 'high', 'low', 'close', 'volume'}
        if not required_cols.issubset(df.columns):
            return html.Div("Data does not contain required OHLC and volume columns.")

        # Evaluar dark mode según cantidad de clics
        dark_mode = (dark_clicks or 0) % 2 == 1

        fig = generate_candlestick_with_volume(df=df, ticker=selected_ticker, dark_mode=dark_mode)

        return dcc.Graph(
            figure=fig,
            config={
                "displaylogo": False,
                "modeBarButtonsToAdd": [
                    "drawline", "drawopenpath", "drawrect", "drawcircle", "eraseshape"
                ],
                "scrollZoom": True
            },
            style={"height": "850px"}
        )