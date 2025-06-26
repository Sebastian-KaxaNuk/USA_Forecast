# navigation.py
import dash_bootstrap_components as dbc
import dash_html_components as html

#%%

navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(html.Img(src="assets/image.jpg", height="32px", style={"marginLeft": "8px"}), width=2),  # Added marginLeft style directly
            ],
            align="center",
            justify="start"
        ),
        dbc.NavbarToggler(id="navbar-toggler", style={"color": "red"}),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Stock Overview", href="/actuals-page", style={"color": "black", "fontWeight": "bold", "fontSize": "16px"})),  # Adjusted font-weight and font-size
                    dbc.NavItem(dbc.NavLink("Decil Analysis", href="/decil-analysis", style={"color": "black", "fontWeight": "bold", "fontSize": "16px"})),  # Adjusted font-weight and font-size
                    dbc.NavItem(dbc.NavLink("Sector Analysis", href="/sector-page", style={"color": "black", "fontWeight": "bold", "fontSize": "16px"})),  # Adjusted font-weight and font-size
                    dbc.NavItem(dbc.NavLink("Portfolio Analysis", href="/portfolio-page", style={"color": "black", "fontWeight": "bold", "fontSize": "16px"})),  # Adjusted font-weight and font-size
                    # dbc.DropdownMenu(
                    #     children=[
                    #         dbc.DropdownMenuItem("Our Community", href="", style={"color": "red"}),
                    #     ],
                    #     nav=True,
                    #     in_navbar=True,
                    #     label="More",
                    #     style={"color": "red"},
                    # ),
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
