"""Figure: payroll employment in software industries vs total private (Feb 2020 = 100)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_FULL, apply, label_end, save, source_note

NAME = "f08_labor_ces_employment"
START = "2015-01-01"
LINES = [
    ("CES5051320001", "Software publishers", SERIES[0]),
    ("CES6054151101", "Custom computer programming", SERIES[2]),
    ("CES6054151201", "Computer systems design", SERIES[3]),
    ("USPRIV", "Total private", COLORS["ink2"]),
]


def make_figure() -> plt.Figure:
    apply()
    meta = json.loads(
        (PROCESSED / "labor_market_meta.json").read_text(encoding="utf-8")
    )
    d = pd.read_csv(PROCESSED / "labor_market_ces_monthly.csv", parse_dates=["date"])
    d = d[d["date"] >= START]
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    ends = []
    for sid, label, color in LINES:
        s = d[d["series_id"] == sid].set_index("date")["index_feb2020"].sort_index()
        ax.plot(s.index, s.values, color=color, lw=1.4)
        ends.append([s.values[-1], s.index[-1], label, color])
    ends.sort(key=lambda e: e[0])
    ypos = []
    for i, e in enumerate(ends):
        ypos.append(e[0] if i == 0 else max(e[0], ypos[-1] + 4.0))
    for (v, x, label, color), yp in zip(ends, ypos):
        ax.plot(
            [x],
            [v],
            "o",
            color=color,
            markersize=3.5,
            markeredgecolor="white",
            markeredgewidth=0.8,
        )
        ax.text(
            d["date"].max() + pd.Timedelta(days=45),
            yp,
            f"{label}  {v:.0f}",
            fontsize=7.5,
            color=color,
            va="center",
            ha="left",
            clip_on=False,
        )
    ax.axhline(100, color=COLORS["axis"], lw=0.7, zorder=0)
    for x, txt, ha, dx in (
        ("2022-11-30", "ChatGPT", "right", -25),
        ("2025-01-01", "Coding-agent era", "left", 25),
    ):
        x = pd.Timestamp(x)
        ax.axvline(x, color=COLORS["muted"], lw=0.7, ls=(0, (3, 3)), zorder=0)
        ax.text(
            x + pd.Timedelta(days=dx),
            66,
            txt,
            fontsize=6.5,
            color=COLORS["muted"],
            va="bottom",
            ha=ha,
        )
    ax.set_ylim(60, 135)
    ax.set_ylabel("Employment index, Feb 2020 = 100")
    ax.set_title("Payroll employment in software industries")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(pd.Timestamp(START), d["date"].max() + pd.Timedelta(days=20))
    fig.subplots_adjust(right=0.72, bottom=0.14)
    source_note(
        fig,
        f"Source: BLS CES (CES5051320001, CES6054151101, CES6054151201) via BLS API v2; total private via FRED USPRIV. Seasonally adjusted. Data through {meta['ces_last_month'][:7]}. Retrieved {meta['ces_retrieved_utc'][:10]}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
