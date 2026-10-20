"""Figure: public GitHub repositories created per month, indexed (2019 average = 100), log scale."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_FULL, apply, save, source_note

NAME = "f04_repo_creation"
LINES = [
    ("all", "All public repos", SERIES[0]),
    ("stars1", "≥1 star", SERIES[1]),
    ("stars10", "≥10 stars", SERIES[2]),
]
MARKS = [
    (pd.Timestamp("2022-11-30"), "ChatGPT"),
    (pd.Timestamp("2025-02-24"), "Claude Code / Codex"),
]


def load() -> pd.DataFrame:
    d = pd.read_csv(PROCESSED / "github_repo_trends_monthly.csv")
    w = d.pivot(index="month", columns="series", values="count")
    w.index = pd.PeriodIndex(w.index, freq="M").to_timestamp()
    return w


def make_figure() -> plt.Figure:
    apply()
    w = load()
    meta = json.loads(
        (PROCESSED / "github_repo_trends_meta.json").read_text(encoding="utf-8")
    )
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    base = w[w.index.year == 2019].mean()
    last = w.index.max()
    for key, label, color in LINES:
        s = 100 * w[key] / base[key]
        ax.plot(s.index, s.values, color=color, lw=1.4)
        ax.annotate(
            f"{label}  {s.iloc[-1]:.0f}",
            xy=(last, s.iloc[-1]),
            xytext=(5, 0),
            textcoords="offset points",
            fontsize=7.5,
            color=COLORS["ink2"],
            va="center",
        )
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(mticker.FixedLocator([10, 25, 50, 100, 200, 400, 800]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.axhline(100, color=COLORS["axis"], lw=0.7, zorder=0)
    ax.axvspan(
        last - pd.DateOffset(months=11),
        last + pd.DateOffset(days=20),
        color=COLORS["grid"],
        alpha=0.45,
        lw=0,
        zorder=0,
    )
    ax.text(
        last - pd.DateOffset(months=11),
        0.02,
        " star counts\n still accruing",
        transform=ax.get_xaxis_transform(),
        fontsize=6.5,
        color=COLORS["muted"],
        va="bottom",
        ha="left",
    )
    for x, lab in MARKS:
        ax.axvline(x, color=COLORS["muted"], lw=0.6, ls=(0, (3, 3)), zorder=0)
        ax.text(
            x - pd.Timedelta(days=25),
            0.03,
            lab,
            transform=ax.get_xaxis_transform(),
            fontsize=6.5,
            color=COLORS["muted"],
            ha="right",
            va="bottom",
            rotation=90,
        )
    ax.set_ylabel("Repos created per month\n(index, 2019 average = 100, log scale)")
    ax.set_xlim(w.index.min(), last + pd.DateOffset(months=30))
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in range(2012, last.year + 1, 2)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.spines["bottom"].set_bounds(
        mdates.date2num(w.index.min()), mdates.date2num(last)
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    source_note(
        fig,
        f"Source: GitHub REST search API (/search/repositories, total_count, created: monthly windows; forks excluded; deleted/private repos absent). Retrieved {meta['retrieved_last']}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
