import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from data.api import (
    CHART_THEME,
    TEAM_COLORS,
    get_constructor_progression,
    get_driver_standings,
    get_driver_team_colors,
    get_standings_progression,
)

dash.register_page(__name__, path="/standings", name="Standings Trend")


def layout():
    driver_df = get_driver_standings()

    driver_options = (
        [
            {"label": f"{r['code']}  ·  {r['team']}", "value": r["code"]}
            for _, r in driver_df.iterrows()
        ]
        if not driver_df.empty
        else []
    )
    default_drivers = [d["value"] for d in driver_options[:10]]

    return html.Div(
        [
            html.Div(
                html.H1("Championship Standings", className="page-title"),
                className="mb-4",
            ),
            # ── Controls
            dbc.Row(
                [
                    dbc.Col(
                        dbc.RadioItems(
                            id="standings-type",
                            options=[
                                {"label": "Drivers", "value": "drivers"},
                                {"label": "Constructors", "value": "constructors"},
                            ],
                            value="drivers",
                            inline=True,
                            inputClassName="me-1",
                            labelClassName="me-4",
                        ),
                        width="auto",
                    )
                ],
                className="mb-3",
            ),
            # ── Driver filter (hidden for constructor view)
            html.Div(
                dcc.Dropdown(
                    id="driver-select",
                    options=driver_options,
                    value=default_drivers,
                    multi=True,
                    placeholder="Select drivers…",
                    style={"fontSize": "0.85rem"},
                ),
                id="driver-filter",
                className="mb-4",
            ),
            # ── Chart
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(
                        id="standings-chart",
                        config={"displayModeBar": False},
                        style={"height": "480px"},
                    )
                ),
                className="chart-card",
            ),
        ]
    )


# ── Callbacks ──────────────────────────────────────────────────────────────


@callback(
    Output("driver-filter", "style"),
    Input("standings-type", "value"),
)
def toggle_filter(view: str):
    return {"display": "none"} if view == "constructors" else {}


@callback(
    Output("standings-chart", "figure"),
    Input("standings-type", "value"),
    Input("driver-select", "value"),
)
def update_chart(view: str, selected_drivers: list[str]):
    fig = go.Figure()
    fig.update_layout(**CHART_THEME)

    if view == "drivers":
        progression = get_standings_progression()
        if progression.empty:
            return _empty_fig("No race data yet")

        colors = get_driver_team_colors()
        drivers = selected_drivers or list(progression.columns[:10])

        for code in drivers:
            if code not in progression.columns:
                continue
            fig.add_trace(
                go.Scatter(
                    x=progression.index,
                    y=progression[code],
                    mode="lines+markers",
                    name=code,
                    line=dict(color=colors.get(code, "#888"), width=2),
                    marker=dict(size=5),
                    hovertemplate=f"<b>{code}</b>: %{{y}} pts<extra></extra>",
                )
            )

        fig.update_layout(
            xaxis_title="Round",
            yaxis_title="Points",
            xaxis=dict(**CHART_THEME["xaxis"], dtick=1),
        )

    else:
        progression = get_constructor_progression()
        if progression.empty:
            return _empty_fig("No race data yet")

        for team in progression.columns:
            fig.add_trace(
                go.Scatter(
                    x=progression.index,
                    y=progression[team],
                    mode="lines+markers",
                    name=team,
                    line=dict(color=TEAM_COLORS.get(team, "#888"), width=2),
                    marker=dict(size=5),
                    hovertemplate=f"<b>{team}</b>: %{{y}} pts<extra></extra>",
                )
            )

        fig.update_layout(
            xaxis_title="Round",
            yaxis_title="Points",
            xaxis=dict(**CHART_THEME["xaxis"], dtick=1),
        )

    return fig


def _empty_fig(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        **CHART_THEME,
        annotations=[
            dict(
                text=msg,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(color="#555", size=16),
            )
        ],
    )
    return fig
