# F1 Dashboard

Keeping track of the F1 season because checking the standings on my phone wasn't doing it for me anymore.

Built with Python + Dash. 100% vibe coded — I picked the stack, Claude wrote the code, I told it when things looked wrong.

## What's in it

- **Season page** — standings at a glance, drivers and constructors
- **Standings** — points over the season as a chart, so you can actually see how the championship is moving
- **H2H** — pick any team and compare teammates head to head. Points, race results, qualifying, average finish

## Run it

```bash
git clone https://github.com/alonsoruizv/f1-dashboard.git
cd f1-dashboard

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open [http://127.0.0.1:8050](http://127.0.0.1:8050)

## Stack

- [Dash](https://dash.plotly.com/) + Plotly for the charts
- [Jolpica API](https://api.jolpi.ca/) for the data (free Ergast replacement)
- Deployed on [Render](https://render.com)

---

Built with [Claude Code](https://claude.ai/code)
