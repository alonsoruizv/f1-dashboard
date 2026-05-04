import dash
import dash_bootstrap_components as dbc
from dash import html

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "F1 Dashboard"
server = app.server

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand(
                [
                    html.Span("F1", style={"color": "#e10600", "fontWeight": "900"}),
                    html.Span(" Dashboard", style={"fontWeight": "700"}),
                ],
                href="/",
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
                    dbc.NavItem(dbc.NavLink("Standings Trend", href="/standings", active="exact")),
                    dbc.NavItem(dbc.NavLink("H2H", href="/h2h", active="exact")),
                ],
                navbar=True,
                className="ms-auto",
            ),
        ],
        fluid=True,
    ),
    dark=True,
    className="main-navbar",
)

footer = html.Footer(
    dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    html.Span("Built by ", style={"color": "#555", "fontSize": "0.8rem"}),
                    width="auto",
                    className="pe-0",
                ),
                dbc.Col(
                    html.A(
                        "Alonso Ruiz Velasco",
                        href="https://www.linkedin.com/in/alonsoruizv/",
                        target="_blank",
                        style={"color": "#888", "fontSize": "0.8rem", "textDecoration": "none"},
                    ),
                    width="auto",
                ),
            ],
            align="center",
            className="py-3",
        ),
        fluid=True,
    ),
    style={"borderTop": "1px solid #1e1e1e", "marginTop": "32px"},
)

app.layout = html.Div(
    [
        navbar,
        dbc.Container(dash.page_container, fluid=True, className="page-content"),
        footer,
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
