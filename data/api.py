import time
from typing import Any

import pandas as pd
import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
SEASON = "2026"
CACHE_TTL = 300  # 5 minutes

_cache: dict[str, dict[str, Any]] = {}

TEAM_COLORS: dict[str, str] = {
    "Red Bull Racing": "#3671C6",
    "Ferrari": "#E8002D",
    "Mercedes": "#27F4D2",
    "McLaren": "#FF8000",
    "Aston Martin": "#229971",
    "Alpine F1 Team": "#FF87BC",
    "Alpine": "#FF87BC",
    "Williams": "#64C4FF",
    "Haas F1 Team": "#B6BABD",
    "Racing Bulls": "#6692FF",
    "RB F1 Team": "#6692FF",
    "Visa Cash App RB": "#6692FF",
    "Kick Sauber": "#52E252",
    "Sauber": "#52E252",
}

CHART_THEME: dict[str, Any] = dict(
    paper_bgcolor="#1a1a1a",
    plot_bgcolor="#1a1a1a",
    font=dict(color="#e0e0e0", family="Inter, -apple-system, sans-serif", size=12),
    xaxis=dict(gridcolor="#2a2a2a", showline=False, zeroline=False),
    yaxis=dict(gridcolor="#2a2a2a", showline=False, zeroline=False),
    legend=dict(bgcolor="#1a1a1a", bordercolor="#2a2a2a", borderwidth=1),
    margin=dict(l=50, r=30, t=40, b=50),
    hovermode="x unified",
)


def _fetch(url: str) -> dict:
    now = time.time()
    if url in _cache and now - _cache[url]["ts"] < CACHE_TTL:
        return _cache[url]["data"]
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    _cache[url] = {"data": data, "ts": now}
    return data


def get_driver_standings() -> pd.DataFrame:
    try:
        data = _fetch(f"{BASE_URL}/{SEASON}/driverStandings.json")
        lists = data["MRData"]["StandingsTable"]["StandingsLists"]
        if not lists:
            return pd.DataFrame()
        rows = [
            {
                "pos": int(d["position"]),
                "driver": f"{d['Driver']['givenName']} {d['Driver']['familyName']}",
                "code": d["Driver"]["code"],
                "team": d["Constructors"][0]["name"],
                "points": float(d["points"]),
                "wins": int(d["wins"]),
            }
            for d in lists[0]["DriverStandings"]
        ]
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def get_constructor_standings() -> pd.DataFrame:
    try:
        data = _fetch(f"{BASE_URL}/{SEASON}/constructorStandings.json")
        lists = data["MRData"]["StandingsTable"]["StandingsLists"]
        if not lists:
            return pd.DataFrame()
        rows = [
            {
                "pos": int(c["position"]),
                "team": c["Constructor"]["name"],
                "points": float(c["points"]),
                "wins": int(c["wins"]),
            }
            for c in lists[0]["ConstructorStandings"]
        ]
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def get_race_results() -> pd.DataFrame:
    try:
        data = _fetch(f"{BASE_URL}/{SEASON}/results.json?limit=500")
        races = data["MRData"]["RaceTable"]["Races"]
        rows = []
        for race in races:
            for r in race["Results"]:
                pos = r.get("position", "")
                grid = r.get("grid", "")
                rows.append(
                    {
                        "round": int(race["round"]),
                        "race_name": race["raceName"],
                        "driver": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
                        "code": r["Driver"]["code"],
                        "team": r["Constructor"]["name"],
                        "position": int(pos) if pos.isdigit() else None,
                        "points": float(r["points"]),
                        "grid": int(grid) if grid.isdigit() else None,
                        "status": r["status"],
                    }
                )
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def get_qualifying_results() -> pd.DataFrame:
    try:
        data = _fetch(f"{BASE_URL}/{SEASON}/qualifying.json?limit=500")
        races = data["MRData"]["RaceTable"]["Races"]
        rows = []
        for race in races:
            for r in race.get("QualifyingResults", []):
                rows.append(
                    {
                        "round": int(race["round"]),
                        "race_name": race["raceName"],
                        "driver": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
                        "code": r["Driver"]["code"],
                        "team": r["Constructor"]["name"],
                        "position": int(r["position"]),
                    }
                )
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def get_schedule() -> pd.DataFrame:
    try:
        data = _fetch(f"{BASE_URL}/{SEASON}.json")
        races = data["MRData"]["RaceTable"]["Races"]
        rows = [
            {
                "round": int(race["round"]),
                "name": race["raceName"],
                "circuit": race["Circuit"]["circuitName"],
                "country": race["Circuit"]["Location"]["country"],
                "date": pd.to_datetime(race["date"]),
            }
            for race in races
        ]
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def get_standings_progression() -> pd.DataFrame:
    df = get_race_results()
    if df.empty:
        return pd.DataFrame()
    pivot = df.pivot_table(
        index="round",
        columns="code",
        values="points",
        aggfunc="sum",
        fill_value=0,
    )
    return pivot.cumsum()


def get_constructor_progression() -> pd.DataFrame:
    df = get_race_results()
    if df.empty:
        return pd.DataFrame()
    pivot = df.pivot_table(
        index="round",
        columns="team",
        values="points",
        aggfunc="sum",
        fill_value=0,
    )
    return pivot.cumsum()


def get_teams_with_drivers() -> dict[str, list[str]]:
    df = get_race_results()
    if df.empty:
        return {}
    grouped = df.groupby("team")["code"].unique()
    return {team: list(codes) for team, codes in grouped.items()}


def get_driver_team_colors() -> dict[str, str]:
    df = get_driver_standings()
    if df.empty:
        return {}
    return {
        row["code"]: TEAM_COLORS.get(row["team"], "#888888")
        for _, row in df.iterrows()
    }
