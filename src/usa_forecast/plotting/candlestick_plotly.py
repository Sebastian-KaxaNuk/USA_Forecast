import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def generate_candlestick_with_volume(df: pd.DataFrame, ticker: str = "", dark_mode: bool = False) -> go.Figure:
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    volume_colors = [
        "#00FFB3" if c >= o else "#FF5E5E"
        for o, c in zip(df["open"], df["close"])
    ]

    if dark_mode:
        bg_color = "#1a2a3a"  # azul oscuro profesional
        font_color = "#f0f0f0"
        grid_color = "#3e5c76"
        inc_color = "#00FFB3"
        dec_color = "#FF5E5E"
        volume_color = volume_colors
        hover_bgcolor = "rgba(40,40,70,0.9)"
    else:
        bg_color = "white"
        font_color = "black"
        grid_color = "lightgrey"
        inc_color = "#2ECC71"
        dec_color = "#E74C3C"
        volume_color = "rgba(100, 100, 250, 0.3)"
        hover_bgcolor = "rgba(255,255,255,0.85)"

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.75, 0.25],
        # subplot_titles=(f"{ticker} Candlestick Chart", "Volume")
    )

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price",
        increasing_line_color=inc_color,
        decreasing_line_color=dec_color,
        text=[
            f"{d.strftime('%Y-%m-%d')} | Close: ${c:.2f}"
            for d, c in zip(df.index, df["close"])
        ],
        hoverinfo="text"
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df.index,
        y=df["volume"],
        name="Volume",
        marker=dict(color=volume_color),
        hovertemplate="Volume: %{y:,.0f}<extra></extra>",
        showlegend=False
    ), row=2, col=1)

    fig.update_layout(
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=hover_bgcolor,
            font_size=9.5,
            font_family="monospace",
            bordercolor="lightgrey",
            font_color=font_color
        ),
        height=900,
        title={
            'text': f"{ticker} Price & Volume",
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': font_color}
        },
        margin=dict(t=100, b=50, l=60, r=40),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ]),
                x=0,
                y=1.15,
                xanchor='left',
                font=dict(size=12),
                bgcolor="grey" if dark_mode else "lightgrey",
                activecolor="#0d6efd",
                bordercolor="black",
                borderwidth=1
            ),
            type="date",
            rangeslider=dict(visible=False)
        )
    )

    # Ejes
    fig.update_yaxes(title_text="Price", row=1, col=1, showgrid=True, gridcolor=grid_color, griddash="dot")
    fig.update_yaxes(title_text="Volume", row=2, col=1, showgrid=True, gridcolor=grid_color, griddash="dot")
    fig.update_xaxes(showgrid=True, gridcolor=grid_color, griddash="dot")

    return fig
