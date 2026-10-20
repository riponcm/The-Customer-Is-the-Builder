"""Share of Show HN posts (and of all stories) whose title pitches an 'alternative', 2012 to latest."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_TALL, apply, label_end, save, source_note

NAME = "f06_hn_alternative_share"
EVENTS = [
    (pd.Timestamp("2022-11-30"), "ChatGPT"),
    (pd.Timestamp("2025-02-24"), "Claude Code\npreview"),
]
W = 12


def _events(ax) -> None:
    for x, label in EVENTS:
        ax.axvline(x, color=COLORS["muted"], lw=0.8, ls=":")
        ax.text(
            x - pd.Timedelta(days=25),
            0.97,
            label,
            transform=ax.get_xaxis_transform(),
            fontsize=7,
            color=COLORS["ink2"],
            ha="right",
            va="top",
        )


def make_figure() -> plt.Figure:
    apply()
    m = pd.read_csv(PROCESSED / "hacker_news_monthly.csv")
    m["date"] = pd.PeriodIndex(m["month"], freq="M").to_timestamp()
    r = m.set_index("date").rolling(W).sum(numeric_only=True)
    r = r[r.index >= m["date"].iloc[W - 1]]
    fig, axes = plt.subplots(2, 1, figsize=WIDTH_TALL, sharex=True)
    ax = axes[0]
    lines = [
        ("showhn_alt_word", '"alternative(s)"', SERIES[0]),
        ("showhn_alt_to", '"alternative to"', SERIES[1]),
        ("showhn_oss_alt", '"open source alternative"', SERIES[2]),
    ]
    for col, label, color in lines:
        y = 100 * r[col] / r["showhn_all"]
        ax.plot(y.index, y, color=color, lw=1.8)
        label_end(ax, y.index[-1], y.iloc[-1], label, color)
    ax.set_ylabel("% of Show HN posts")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
    ax.set_ylim(0, 100 * (r["showhn_alt_word"] / r["showhn_all"]).max() * 1.3)
    _events(ax)
    ax.set_title(f"A. Show HN titles containing ... (trailing {W}-month share)")
    ax = axes[1]
    y = 10000.0 * r["story_alt_to"] / r["story_all"]
    ax.plot(y.index, y, color=SERIES[1], lw=1.8)
    label_end(ax, y.index[-1], y.iloc[-1], '"alternative to"', SERIES[1])
    ax.set_ylabel("Per 10,000 stories")
    ax.set_ylim(0, y.max() * 1.3)
    _events(ax)
    ax.set_title(
        f'B. All stories with "alternative to" in the title (trailing {W}-month rate)'
    )
    ax.set_xticks(
        [
            pd.Timestamp(f"{yr}-01-01")
            for yr in range(2014, m["date"].iloc[-1].year + 1, 2)
        ]
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(None, m["date"].iloc[-1] + pd.Timedelta(days=1000))
    for a in axes:
        a.spines["bottom"].set_bounds(
            mdates.date2num(r.index[0]), mdates.date2num(m["date"].iloc[-1])
        )
    source_note(
        fig,
        f"Source: Hacker News via Algolia HN Search API; title-only exact-token search (typoTolerance=false, queryType=prefixNone, quoted phrases). Retrieved {m['retrieved'].iloc[0]}.",
    )
    fig.tight_layout(rect=(0, 0.025, 1, 1))
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
