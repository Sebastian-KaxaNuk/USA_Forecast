import dash_bootstrap_components as dbc
import dash_html_components as html

def build_navbar(pathname: str) -> dbc.Navbar:
    def style(path):
        return {
            "backgroundColor": "#0d6efd",
            "color": "white",
            "borderRadius": "0.5rem",
            "fontWeight": "bold",
            "fontSize": "16px",
            "padding": "8px"
        } if pathname == path else {
            "color": "black",
            "fontWeight": "bold",
            "fontSize": "16px",
            "padding": "8px"
        }

    return dbc.Navbar(
        [
            dbc.Row(
                [
                    dbc.Col(html.Img(src="assets/image.jpg", height="32px", style={"marginLeft": "8px"}), width=2),
                ],
                align="center",
                justify="start"
            ),
            dbc.NavbarToggler(id="navbar-toggler", style={"color": "red"}),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Heatmap", href="/heatmap_analysis-page", style=style("/heatmap_analysis-page"))),
                        dbc.NavItem(dbc.NavLink("Target Price Table", href="/target_price-page", style=style("/target_price-page"))),
                        dbc.NavItem(dbc.NavLink("Final Data Historical", href="/final_data_historical-page", style=style("/final_data_historical-page"))),
                    ],
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
        color="light",
        dark=False,
    )
