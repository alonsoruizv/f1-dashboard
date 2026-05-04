import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html

from data.api import (
    TEAM_COLORS,
    get_constructor_standings,
    get_driver_standings,
    get_schedule,
)

dash.register_page(__name__, path="/", name="Home")


# ── Helpers ────────────────────────────────────────────────────────────────


def team_dot(team: str) -> html.Span:
    color = TEAM_COLORS.get(team, "#555")
    return html.Span(className="team-dot", style={"backgroundColor": color})


def stat_card(label: str, value: str, subtitle: str = "") -> dbc.Card:
    body_children = [
        html.P(label, className="stat-label"),
        html.P(value, className="stat-value"),
    ]
    if subtitle:
        body_children.append(html.P(subtitle, className="stat-subtitle"))
    return dbc.Card(dbc.CardBody(body_children), className="stat-card")


def driver_table(df: pd.DataFrame) -> html.Div:
    if df.empty:
        return html.P("No data available.", className="text-muted small")

    leader_pts = df.iloc[0]["points"]
    rows = [
        html.Tr(
            [
                html.Td(row["pos"], style={"color": "#555", "fontWeight": "600", "width": "36px"}),
                html.Td(
                    [team_dot(row["team"]), row["driver"]],
                    style={"fontWeight": "500"},
                ),
                html.Td(
                    row["team"],
                    className="d-none d-lg-table-cell",
                    style={"color": "#666", "fontSize": "0.82rem"},
                ),
                html.Td(
                    html.Strong(int(row["points"])),
                    style={"color": "#fff", "textAlign": "right"},
                ),
                html.Td(
                    "—" if row["pos"] == 1 else f"-{int(leader_pts - row['points'])}",
                    style={"color": "#555", "textAlign": "right", "fontSize": "0.82rem"},
                ),
                html.Td(
                    row["wins"],
                    style={"color": "#888", "textAlign": "right"},
                ),
            ]
        )
        for _, row in df.iterrows()
    ]

    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th(""),
                        html.Th("Driver"),
                        html.Th("Team", className="d-none d-lg-table-cell"),
                        html.Th("PTS", style={"textAlign": "right"}),
                        html.Th("GAP", style={"textAlign": "right"}),
                        html.Th("W", style={"textAlign": "right"}),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        className="standings-table",
        hover=True,
        responsive=True,
    )


def constructor_table(df: pd.DataFrame) -> html.Div:
    if df.empty:
        return html.P("No data available.", className="text-muted small")

    leader_pts = df.iloc[0]["points"]
    rows = [
        html.Tr(
            [
                html.Td(row["pos"], style={"color": "#555", "fontWeight": "600", "width": "36px"}),
                html.Td([team_dot(row["team"]), row["team"]], style={"fontWeight": "500"}),
                html.Td(
                    html.Strong(int(row["points"])),
                    style={"color": "#fff", "textAlign": "right"},
                ),
                html.Td(
                    "—" if row["pos"] == 1 else f"-{int(leader_pts - row['points'])}",
                    style={"color": "#555", "textAlign": "right", "fontSize": "0.82rem"},
                ),
                html.Td(row["wins"], style={"color": "#888", "textAlign": "right"}),
            ]
        )
        for _, row in df.iterrows()
    ]

    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th(""),
                        html.Th("Constructor"),
                        html.Th("PTS", style={"textAlign": "right"}),
                        html.Th("GAP", style={"textAlign": "right"}),
                        html.Th("W", style={"textAlign": "right"}),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        className="standings-table",
        hover=True,
        responsive=True,
    )


# ── Layout ─────────────────────────────────────────────────────────────────


def layout():
    drivers = get_driver_standings()
    constructors = get_constructor_standings()
    schedule = get_schedule()

    # Drivers leader card
    if not drivers.empty:
        leader = drivers.iloc[0]
        pts_val = leader["driver"]
        pts_sub = f"{int(leader['points'])} pts · {leader['team']}"
    else:
        pts_val, pts_sub = "—", ""

    # Constructor leader card
    if not constructors.empty:
        con = constructors.iloc[0]
        con_val = con["team"]
        con_sub = f"{int(con['points'])} pts"
    else:
        con_val, con_sub = "—", ""

    # Races card
    if not schedule.empty:
        today = pd.Timestamp.now().normalize()
        done = int((schedule["date"] <= today).sum())
        total = len(schedule)
        pct = round(done / total * 100) if total else 0
        races_val = f"{done} / {total}"
        races_sub = f"{pct}% of season complete"
    else:
        races_val, races_sub = "—", ""

    return html.Div(
        [
            # ── Title
            html.Div(
                html.H1("2025 Formula 1 World Championship", className="page-title"),
                className="mb-4",
            ),
            # ── Stat cards
            dbc.Row(
                [
                    dbc.Col(stat_card("Drivers' Leader", pts_val, pts_sub), md=4, className="mb-3"),
                    dbc.Col(stat_card("Constructors' Leader", con_val, con_sub), md=4, className="mb-3"),
                    dbc.Col(stat_card("Rounds", races_val, races_sub), md=4, className="mb-3"),
                ],
                className="mb-4",
            ),
            # ── Standings tables
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P("Driver Standings", className="section-title"),
                            driver_table(drivers),
                        ],
                        md=7,
                        className="mb-4",
                    ),
                    dbc.Col(
                        [
                            html.P("Constructor Standings", className="section-title"),
                            constructor_table(constructors),
                        ],
                        md=5,
                        className="mb-4",
                    ),
                ]
            ),
        ]
    )
