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
                    dbc.NavItem(dbc.NavLink("Target Price Table", href="/target_price-page", style={"color": "black", "fontWeight": "bold", "fontSize": "16px"})),  # Adjusted font-weight and font-size
                    dbc.NavItem(dbc.NavLink("Heatmap Visualization", href="/heatmap_analysis-page", style={"color": "black", "fontWeight": "bold", "fontSize": "16px"})),  # Adjusted font-weight and font-size
                    dbc.NavItem(dbc.NavLink("Final Data Historical", href="/final_data_historical-page", style={"color": "black", "fontWeight": "bold", "fontSize": "16px"})),  # Adjusted font-weight and font-size
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
