"""Figure: share of GitHub topic-pushers on AI/ML and on LLM/agent topics (balanced panel)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_HALF, apply, save, source_note

NAME = "f02_ig_ai_topics"
GROUPS = [
    ("AI/ML topics (any)", SERIES[0], "AI / ML (any)"),
    ("LLM / agent topics", SERIES[1], "LLM / agent"),
]


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(
        PROCESSED / "innovation_graph_ai_topics.csv", parse_dates=["quarter_start"]
    )
    meta = json.loads(
        (PROCESSED / "innovation_graph_meta.json").read_text(encoding="utf-8")
    )
    n_econ = int(df["n_economies"].iloc[0])
    fig, ax = plt.subplots(figsize=(WIDTH_HALF[0], 2.8))
    for grp, col, lab in GROUPS:
        s = df[df["group"] == grp].set_index("quarter_start")["share"] * 100
        ax.plot(s.index, s.values, color=col, lw=1.5)
        ax.plot(
            [s.index[-1]],
            [s.values[-1]],
            "o",
            color=col,
            ms=3.5,
            markeredgecolor=COLORS["surface"],
            markeredgewidth=0.8,
        )
        ax.annotate(
            f"{lab}\n{s.values[-1]:.1f}%",
            (s.index[-1], s.values[-1]),
            xytext=(5, 0),
            textcoords="offset points",
            fontsize=6.5,
            color=COLORS["ink2"],
            va="center",
        )
    for x, lab in (
        (pd.Timestamp("2022-11-30"), "ChatGPT"),
        (pd.Timestamp("2025-02-24"), "Coding agents"),
    ):
        ax.axvline(x, color=COLORS["muted"], lw=0.5, ls=(0, (3, 3)), zorder=0)
        ax.text(
            x,
            0.98,
            lab,
            transform=ax.get_xaxis_transform(),
            fontsize=6,
            color=COLORS["muted"],
            ha="right",
            va="top",
            rotation=90,
        )
    ax.set_ylim(0, None)
    ax.set_xlim(pd.Timestamp("2019-12-01"), pd.Timestamp("2028-04-01"))
    ax.spines["bottom"].set_bounds(
        mdates.date2num(pd.Timestamp("2020-01-01")),
        mdates.date2num(df["quarter_start"].max()),
    )
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (2020, 2022, 2024, 2026)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylabel("% of topic-pushers")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    source_note(
        fig,
        f"Source: GitHub Innovation Graph, topics.csv; {n_econ} economies present\nin all quarters; keyword match on topic names. Retrieved {meta['retrieved']}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
