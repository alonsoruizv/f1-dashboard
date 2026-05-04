import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from data.api import (
    CHART_THEME,
    TEAM_COLORS,
    get_qualifying_results,
    get_race_results,
    get_teams_with_drivers,
)

dash.register_page(__name__, path="/h2h", name="H2H")


# ── Helpers ────────────────────────────────────────────────────────────────


def _h2h_stat_card(
    label: str,
    d1: str,
    d2: str,
    val1: int,
    val2: int,
    team_color: str,
) -> dbc.Card:
    winner_color = team_color
    loser_color = "#444"

    c1 = winner_color if val1 >= val2 else loser_color
    c2 = winner_color if val2 >= val1 else loser_color

    total = val1 + val2
    pct1 = (val1 / total * 100) if total else 50
    pct2 = 100 - pct1

    return dbc.Card(
        dbc.CardBody(
            [
                html.P(label, className="stat-label text-center"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(d1, className="driver-code text-center", style={"color": c1}),
                                html.Div(val1, className="h2h-score text-center"),
                            ]
                        ),
                        dbc.Col(
                            html.Div("vs", className="text-center mt-2", style={"color": "#444", "fontSize": "0.8rem"}),
                            width="auto",
                            className="px-0",
                        ),
                        dbc.Col(
                            [
                                html.Div(d2, className="driver-code text-center", style={"color": c2}),
                                html.Div(val2, className="h2h-score text-center"),
                            ]
                        ),
                    ],
                    align="center",
                    className="my-2",
                ),
                # Proportional bar
                html.Div(
                    [
                        html.Div(
                            style={
                                "width": f"{pct1:.1f}%",
                                "backgroundColor": team_color,
                                "height": "100%",
                            }
                        ),
                        html.Div(
                            style={
                                "width": f"{pct2:.1f}%",
                                "backgroundColor": "#2a2a2a",
                                "height": "100%",
                            }
                        ),
                    ],
                    className="h2h-bar-wrap",
                ),
            ]
        ),
        className="h2h-card",
    )


def _positions_chart(
    d1: str,
    d2: str,
    d1_pos: dict,
    d2_pos: dict,
    team_color: str,
) -> go.Figure:
    rounds = sorted(set(d1_pos) | set(d2_pos))

    _base = {k: v for k, v in CHART_THEME.items() if k not in ("yaxis", "xaxis", "hovermode")}
    fig = go.Figure()
    fig.update_layout(
        **_base,
        yaxis=dict(**CHART_THEME["yaxis"], autorange="reversed", title="Finishing Position", dtick=5),
        xaxis=dict(**CHART_THEME["xaxis"], title="Round", dtick=1),
        title="Race Positions",
        hovermode="x unified",
    )

    fig.add_trace(
        go.Scatter(
            x=rounds,
            y=[d1_pos.get(r) for r in rounds],
            mode="lines+markers",
            name=d1,
            line=dict(color=team_color, width=2),
            marker=dict(size=7),
            connectgaps=False,
            hovertemplate=f"<b>{d1}</b>: P%{{y}}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=rounds,
            y=[d2_pos.get(r) for r in rounds],
            mode="lines+markers",
            name=d2,
            line=dict(color="#fff", width=2, dash="dot"),
            marker=dict(size=7, color="#fff"),
            connectgaps=False,
            hovertemplate=f"<b>{d2}</b>: P%{{y}}<extra></extra>",
        )
    )
    return fig


def _quali_chart(
    d1: str,
    d2: str,
    d1_q: dict,
    d2_q: dict,
    team_color: str,
) -> go.Figure:
    rounds = sorted(set(d1_q) & set(d2_q))
    if not rounds:
        return None

    _base = {k: v for k, v in CHART_THEME.items() if k not in ("yaxis", "xaxis", "hovermode")}
    fig = go.Figure()
    fig.update_layout(
        **_base,
        yaxis=dict(**CHART_THEME["yaxis"], autorange="reversed", title="Qualifying Position"),
        xaxis=dict(**CHART_THEME["xaxis"], title="Round", dtick=1),
        title="Qualifying Positions",
        hovermode="x unified",
    )
    fig.add_trace(
        go.Scatter(
            x=rounds,
            y=[d1_q.get(r) for r in rounds],
            mode="lines+markers",
            name=d1,
            line=dict(color=team_color, width=2),
            marker=dict(size=7),
            hovertemplate=f"<b>{d1}</b>: P%{{y}}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=rounds,
            y=[d2_q.get(r) for r in rounds],
            mode="lines+markers",
            name=d2,
            line=dict(color="#fff", width=2, dash="dot"),
            marker=dict(size=7, color="#fff"),
            hovertemplate=f"<b>{d2}</b>: P%{{y}}<extra></extra>",
        )
    )
    return fig


# ── Layout ─────────────────────────────────────────────────────────────────


def layout():
    teams = get_teams_with_drivers()
    options = [{"label": t, "value": t} for t in sorted(teams)]
    default = options[0]["value"] if options else None

    return html.Div(
        [
            html.Div(
                html.H1("Teammate Head to Head", className="page-title"),
                className="mb-4",
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        id="team-select",
                        options=options,
                        value=default,
                        clearable=False,
                        style={"fontSize": "0.85rem"},
                    ),
                    md=4,
                ),
                className="mb-4",
            ),
            html.Div(id="h2h-content"),
        ]
    )


# ── Callback ───────────────────────────────────────────────────────────────


@callback(
    Output("h2h-content", "children"),
    Input("team-select", "value"),
)
def update_h2h(team: str):
    if not team:
        return html.P("Select a team above.", className="text-muted")

    race_df = get_race_results()
    quali_df = get_qualifying_results()

    if race_df.empty:
        return html.P("No race data available yet.", className="text-muted")

    team_races = race_df[race_df["team"] == team]
    # Pick the two drivers with the most races for this team
    top_drivers = team_races["code"].value_counts().index[:2].tolist()

    if len(top_drivers) < 2:
        return html.P("Need at least two drivers to compare.", className="text-muted")

    d1, d2 = top_drivers[0], top_drivers[1]
    team_color = TEAM_COLORS.get(team, "#e10600")

    # ── Race data
    d1_races = team_races[team_races["code"] == d1].set_index("round")
    d2_races = team_races[team_races["code"] == d2].set_index("round")

    d1_pos = {r: d1_races.loc[r, "position"] for r in d1_races.index}
    d2_pos = {r: d2_races.loc[r, "position"] for r in d2_races.index}

    common = [
        r
        for r in set(d1_pos) & set(d2_pos)
        if d1_pos[r] is not None and d2_pos[r] is not None
    ]
    d1_race_wins = sum(1 for r in common if d1_pos[r] < d2_pos[r])
    d2_race_wins = len(common) - d1_race_wins

    # ── Points
    d1_pts = int(d1_races["points"].sum())
    d2_pts = int(d2_races["points"].sum())

    # ── Qualifying
    d1_q: dict = {}
    d2_q: dict = {}
    d1_quali_wins = d2_quali_wins = 0

    if not quali_df.empty:
        team_quali = quali_df[quali_df["team"] == team]
        d1_q = {
            r: pos
            for r, pos in team_quali[team_quali["code"] == d1]
            .set_index("round")["position"]
            .items()
        }
        d2_q = {
            r: pos
            for r, pos in team_quali[team_quali["code"] == d2]
            .set_index("round")["position"]
            .items()
        }
        common_q = set(d1_q) & set(d2_q)
        d1_quali_wins = sum(1 for r in common_q if d1_q[r] < d2_q[r])
        d2_quali_wins = len(common_q) - d1_quali_wins

    # ── Avg finish position
    d1_avg = round(sum(v for v in d1_pos.values() if v) / max(len([v for v in d1_pos.values() if v]), 1), 1)
    d2_avg = round(sum(v for v in d2_pos.values() if v) / max(len([v for v in d2_pos.values() if v]), 1), 1)
    # For avg position, lower is better — invert comparison
    d1_avg_inv = int(d2_avg * 10)
    d2_avg_inv = int(d1_avg * 10)

    # ── Build charts
    race_fig = _positions_chart(d1, d2, d1_pos, d2_pos, team_color)
    quali_fig = _quali_chart(d1, d2, d1_q, d2_q, team_color)

    chart_cols = (
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=race_fig, config={"displayModeBar": False}, style={"height": "380px"})),
                    className="chart-card",
                ),
                md=6,
                className="mb-4",
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=quali_fig, config={"displayModeBar": False}, style={"height": "380px"})),
                    className="chart-card",
                ),
                md=6,
                className="mb-4",
            ),
        ]
        if quali_fig
        else [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(dcc.Graph(figure=race_fig, config={"displayModeBar": False}, style={"height": "380px"})),
                    className="chart-card",
                ),
                md=12,
                className="mb-4",
            )
        ]
    )

    return html.Div(
        [
            # ── Stat summary cards
            dbc.Row(
                [
                    dbc.Col(
                        _h2h_stat_card("Points", d1, d2, d1_pts, d2_pts, team_color),
                        md=3, xs=6, className="mb-3",
                    ),
                    dbc.Col(
                        _h2h_stat_card("Race H2H", d1, d2, d1_race_wins, d2_race_wins, team_color),
                        md=3, xs=6, className="mb-3",
                    ),
                    dbc.Col(
                        _h2h_stat_card("Qualifying H2H", d1, d2, d1_quali_wins, d2_quali_wins, team_color),
                        md=3, xs=6, className="mb-3",
                    ),
                    dbc.Col(
                        _h2h_stat_card(
                            "Avg Finish (lower=better)",
                            d1, d2, d1_avg_inv, d2_avg_inv, team_color,
                        ),
                        md=3, xs=6, className="mb-3",
                    ),
                ],
                className="mb-2",
            ),
            # ── Avg position labels (human-readable)
            dbc.Row(
                dbc.Col(
                    html.P(
                        f"Average finish — {d1}: P{d1_avg}  ·  {d2}: P{d2_avg}",
                        className="text-muted small mb-4",
                    )
                )
            ),
            # ── Charts
            dbc.Row(chart_cols),
        ]
    )
