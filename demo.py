import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

def create_navbar(pathname):
    def style_for(link_path):
        if pathname == link_path:
            return {
                "background-color": "#0d6efd",
                "color": "white",
                "border-radius": "0.5rem",
                "font-weight": "bold",
                "padding": "8px"
            }
        return {}

    return dbc.Navbar(
        dbc.Container([
            dbc.Nav([
                dbc.NavLink("Page 1", href="/page-1", style=style_for("/page-1")),
                dbc.NavLink("Page 2", href="/page-2", style=style_for("/page-2")),
            ])
        ]),
        color="light",
        dark=False,
    )

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id="navbar-container"),
    html.Div(id="page-content")
])

@app.callback(
    Output("navbar-container", "children"),
    Input("url", "pathname")
)
def update_navbar(pathname):
    print(f"[DEBUG] Pathname: {pathname}")
    if pathname is None or pathname == "/":
        pathname = "/page-1"
    return create_navbar(pathname)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def update_page(pathname):
    if pathname == "/page-1":
        return html.H3("Estás en la Página 1")
    elif pathname == "/page-2":
        return html.H3("Estás en la Página 2")
    else:
        return html.H3("404 Página no encontrada")

if __name__ == "__main__":
    app.run(debug=True)
