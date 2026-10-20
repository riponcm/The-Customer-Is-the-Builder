"""Share of Show HN posts that name an AI coding tool in the title, or disclose being built with AI."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_FULL, apply, label_end, save, source_note

NAME = "f06_hn_ai_share"
START = "2020-01-01"
EVENTS = [
    (pd.Timestamp("2022-11-30"), "ChatGPT\n(2022-11-30)"),
    (pd.Timestamp("2025-02-24"), "Claude Code preview,\n'vibe coding' (Feb 2025)"),
]


def make_figure() -> plt.Figure:
    apply()
    m = pd.read_csv(PROCESSED / "hacker_news_monthly.csv")
    m["date"] = pd.PeriodIndex(m["month"], freq="M").to_timestamp()
    m = m[m["date"] >= START]
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    series = [
        (
            "ai_title_mention_share_showhn",
            "Title names an AI\nassistant or coding tool",
            SERIES[0],
        ),
        (
            "ai_built_share_showhn",
            "Title/text says built\nwith AI (vibe coded,\nbuilt with Claude Code...)",
            SERIES[1],
        ),
    ]
    for col, label, color in series:
        y = 100 * m[col]
        ax.plot(m["date"], y, color=color, lw=1.8)
        label_end(ax, m["date"].iloc[-1], y.iloc[-1], label, color)
    for x, label in EVENTS:
        ax.axvline(x, color=COLORS["muted"], lw=0.8, ls=":")
        ax.text(
            x - pd.Timedelta(days=20),
            0.97,
            label,
            transform=ax.get_xaxis_transform(),
            fontsize=7,
            color=COLORS["ink2"],
            ha="right",
            va="top",
        )
    ax.set_ylabel("% of Show HN posts")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylim(0, 100 * m["ai_title_mention_share_showhn"].max() * 1.12)
    ax.set_xlim(
        pd.Timestamp(START) - pd.Timedelta(days=30),
        m["date"].iloc[-1] + pd.Timedelta(days=560),
    )
    ax.spines["bottom"].set_bounds(
        mdates.date2num(pd.Timestamp(START)), mdates.date2num(m["date"].iloc[-1])
    )
    ax.set_xticks(
        [pd.Timestamp(f"{yr}-01-01") for yr in range(2020, m["date"].iloc[-1].year + 1)]
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_title("AI build tools in Show HN posts (monthly share)")
    source_note(
        fig,
        f"Source: Hacker News via Algolia HN Search API; candidates by exact-token search of title + text, classified by regular expressions (src/collect/hacker_news.py).\n'Built with AI' has ~80% precision in a 40-post hand check; disclosure is voluntary, so it is a lower bound. Retrieved {m['retrieved'].iloc[0]}.",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
