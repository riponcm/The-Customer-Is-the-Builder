"""Show HN posts per month and as a share of all Hacker News stories, 2012 to latest."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_TALL, apply, save, source_note

NAME = "f06_hn_showhn_volume"
EVENTS = [
    (pd.Timestamp("2022-11-30"), "ChatGPT\n(2022-11-30)", 0.97),
    (
        pd.Timestamp("2025-02-24"),
        "Claude Code preview,\n'vibe coding' (Feb 2025)",
        0.72,
    ),
]


def _events(ax) -> None:
    for x, label, y_frac in EVENTS:
        ax.axvline(x, color=COLORS["muted"], lw=0.8, ls=":")
        ax.text(
            x - pd.Timedelta(days=25),
            y_frac,
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
    fig, axes = plt.subplots(
        2, 1, figsize=WIDTH_TALL, sharex=True, height_ratios=[1.25, 1]
    )
    ax = axes[0]
    ax.plot(m["date"], m["showhn_all"], color=SERIES[0], lw=1.6)
    ax.set_ylabel("Show HN posts per month")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_ylim(0, m["showhn_all"].max() * 1.12)
    _events(ax)
    pre = m[(m["date"] >= "2022-01-01") & (m["date"] < "2022-11-01")][
        "showhn_all"
    ].mean()
    ax.axhline(pre, color=COLORS["context"], lw=0.8)
    ax.text(
        pd.Timestamp("2012-02-01"),
        1500,
        f"Gray line: Jan-Oct 2022 mean ({pre:,.0f}/month)",
        fontsize=7,
        color=COLORS["ink2"],
        va="bottom",
    )
    pk = m.loc[m["showhn_all"].idxmax()]
    ax.annotate(
        f"{pk['showhn_all']:,.0f}\n({pd.Timestamp(pk['date']):%b %Y})",
        xy=(pk["date"], pk["showhn_all"]),
        xytext=(6, -4),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=7.5,
        color=COLORS["ink2"],
    )
    ax.set_title("A. Show HN posts per month")
    ax = axes[1]
    ax.plot(m["date"], 100 * m["showhn_share_story"], color=SERIES[0], lw=1.6)
    ax.set_ylabel("% of all stories")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylim(0, 100 * m["showhn_share_story"].max() * 1.15)
    ax.set_title("B. Show HN as a share of all Hacker News stories")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    source_note(
        fig,
        f"Source: Hacker News via Algolia HN Search API (hn.algolia.com/api/v1/search_by_date, tags=show_hn and tags=story; nbHits per calendar month, UTC). Retrieved {m['retrieved'].iloc[0]}.",
    )
    fig.tight_layout(rect=(0, 0.025, 1, 1))
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
