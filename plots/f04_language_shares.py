"""Figure: share of new public GitHub repositories by primary language (small multiples)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, WIDTH_TALL, apply, save, source_note

NAME = "f04_language_shares"
ORDER = ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "C#"]
MARKS = [pd.Timestamp("2022-11-30"), pd.Timestamp("2025-02-24")]


def make_figure() -> plt.Figure:
    apply()
    d = pd.read_csv(PROCESSED / "github_repo_trends_languages.csv")
    d["date"] = pd.PeriodIndex(d["month"], freq="M").to_timestamp()
    meta = json.loads(
        (PROCESSED / "github_repo_trends_meta.json").read_text(encoding="utf-8")
    )
    fig, axes = plt.subplots(2, 4, figsize=(WIDTH_TALL[0], 3.9), sharex=True)
    for ax, lang in zip(axes.flat, ORDER):
        s = d[d["language"] == lang].set_index("date")["share_pct"].sort_index()
        sm = s.rolling(3).mean()
        ax.plot(s.index, s.values, color=ENTITY_COLORS[lang], lw=0.6, alpha=0.35)
        ax.plot(sm.index, sm.values, color=ENTITY_COLORS[lang], lw=1.5)
        for x in MARKS:
            ax.axvline(x, color=COLORS["muted"], lw=0.5, ls=(0, (3, 3)), zorder=0)
        ax.set_title(f"{lang}  {sm.iloc[-1]:.1f}%", fontsize=9)
        ax.set_ylim(0, max(s.max() * 1.12, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator(4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("'%y"))
    for ax in axes[:, 0]:
        ax.set_ylabel("% of new repos")
    fig.suptitle(
        "Primary language of new public repositories (share of all repos created per month)",
        x=0.01,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    source_note(
        fig,
        f"Source: GitHub REST search API (/search/repositories, language:X created: monthly windows) ÷ all repos created.\nTitle = latest 3-month mean; 3-month trailing mean (thin = monthly); dashed = ChatGPT, Claude Code. Retrieved {meta['retrieved_last']}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
