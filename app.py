import base64

import dash
import dash_bootstrap_components as dbc
from dash import html

_LI_ICON = "data:image/svg+xml;base64," + base64.b64encode(
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0A66C2">'
    b'<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0'
    b"-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 "
    b"3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 "
    b"01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452z"
    b"M22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451"
    b'C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
).decode()

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
                        [
                            html.Img(
                                src=_LI_ICON,
                                style={"width": "14px", "height": "14px", "marginRight": "6px", "verticalAlign": "middle"},
                            ),
                            "Alonso Ruiz Velasco",
                        ],
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
