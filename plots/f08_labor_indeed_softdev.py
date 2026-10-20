"""Figure: Indeed software-development job postings vs all postings (Feb 1 2020 = 100)."""

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

NAME = "f08_labor_indeed_softdev"
LINES = [
    ("IHLIDXUSTPSOFTDEVE", "Software development", SERIES[0]),
    ("IHLIDXUS", "All job postings", COLORS["ink2"]),
]
EVENTS = [("2022-11-30", "ChatGPT"), ("2025-01-01", "Coding-agent era")]


def make_figure() -> plt.Figure:
    apply()
    meta = json.loads(
        (PROCESSED / "labor_market_meta.json").read_text(encoding="utf-8")
    )
    d = pd.read_csv(PROCESSED / "labor_market_indeed_daily.csv", parse_dates=["date"])
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    for sid, label, color in LINES:
        s = d[d["series_id"] == sid].set_index("date")["value"].sort_index()
        ax.plot(s.index, s.values, color=color, lw=1.4)
        label_end(ax, s.index[-1], s.values[-1], f"{label}  {s.values[-1]:.0f}", color)
    ax.axhline(100, color=COLORS["axis"], lw=0.7, zorder=0)
    for x, txt in EVENTS:
        x = pd.Timestamp(x)
        ax.axvline(x, color=COLORS["muted"], lw=0.7, ls=(0, (3, 3)), zorder=0)
        ax.text(
            x + pd.Timedelta(days=20),
            238,
            txt,
            fontsize=6.5,
            color=COLORS["muted"],
            va="top",
        )
    ax.set_ylim(0, 245)
    ax.set_ylabel("Index, 1 Feb 2020 = 100")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(pd.Timestamp("2020-01-15"), d["date"].max() + pd.Timedelta(days=10))
    fig.subplots_adjust(right=0.77, bottom=0.14)
    source_note(
        fig,
        f"Source: Indeed Hiring Lab via FRED (IHLIDXUSTPSOFTDEVE, IHLIDXUS); seasonally adjusted, 7-day trailing average. Data through {meta['indeed_last_date']}. Retrieved {meta['indeed_retrieved_utc'][:10]}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
