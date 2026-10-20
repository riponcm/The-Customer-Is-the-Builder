"""Figure: share of GitHub pushers by programming language, 2020Q1-latest (small multiples)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, apply, save, source_note

NAME = "f02_ig_languages"
ORDER = ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "C#"]


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(
        PROCESSED / "innovation_graph_languages.csv", parse_dates=["quarter_start"]
    )
    w = (
        df.pivot(index="quarter_start", columns="language", values="share").sort_index()
        * 100
    )
    meta = json.loads(
        (PROCESSED / "innovation_graph_meta.json").read_text(encoding="utf-8")
    )
    fig, axes = plt.subplots(2, 4, figsize=(6.5, 4.6), sharex=True, sharey=True)
    for ax, lang in zip(axes.flat, ORDER):
        s = w[lang]
        ax.plot(s.index, s.values, color=ENTITY_COLORS[lang], lw=1.6, zorder=3)
        first, last = (s.iloc[0], s.iloc[-1])
        ax.plot(
            [s.index[0], s.index[-1]],
            [first, last],
            "o",
            color=ENTITY_COLORS[lang],
            ms=3,
            zorder=4,
            markeredgecolor=COLORS["surface"],
            markeredgewidth=0.8,
        )
        change = last - first
        change_label = "0.0" if abs(change) < 0.05 else f"{change:+.1f}"
        ax.text(
            0.03,
            0.95,
            f"Change: {change_label} pp",
            transform=ax.transAxes,
            fontsize=7.5,
            va="top",
            color=COLORS["ink2"],
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.6},
        )
        ax.annotate(
            f"{first:.1f}",
            (s.index[0], first),
            xytext=(0, 6),
            textcoords="offset points",
            fontsize=7.5,
            color=COLORS["ink2"],
            ha="left",
        )
        ax.annotate(
            f"{last:.1f}",
            (s.index[-1], last),
            xytext=(0, 6),
            textcoords="offset points",
            fontsize=7.5,
            color=COLORS["ink2"],
            ha="right",
        )
        ax.axvline(
            pd.Timestamp("2022-11-30"),
            color=COLORS["muted"],
            lw=0.5,
            ls=(0, (3, 3)),
            zorder=0,
        )
        ax.axvline(
            pd.Timestamp("2025-02-24"),
            color=COLORS["muted"],
            lw=0.5,
            ls=(0, (3, 3)),
            zorder=0,
        )
        ax.set_title(lang, fontsize=9)
        ax.tick_params(labelsize=8)
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("'%y"))
        ax.set_ylim(0, 23)
        ax.set_yticks([0, 5, 10, 15, 20])
    for ax in axes[:, 0]:
        ax.set_ylabel("% of language-pushers", fontsize=9)
    period = f"{w.index[0].to_period('Q')} to {w.index[-1].to_period('Q')}"
    source_note(
        fig,
        f"Source: GitHub Innovation Graph, languages.csv. Public repository activity; economy cells below 100 suppressed. Last accessed {meta['retrieved']}.\nShare of summed language-pusher counts; developers may count in multiple languages. pp = percentage points, {period} (computed before rounding).\nDashed lines: ChatGPT (Nov 2022) and coding-agent era (Feb 2025). Labels: first and latest share (%).",
    )
    fig.tight_layout(rect=(0.015, 0.14, 0.985, 0.99), h_pad=1.7, w_pad=0.9)
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
