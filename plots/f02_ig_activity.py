"""Figure: GitHub developers, repositories and git pushes, World and US, 2020Q1 = 100."""

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

NAME = "f02_ig_activity"
METRICS = [
    ("git_pushes", "Git pushes"),
    ("developers", "Developers"),
    ("repositories", "Repositories"),
]
COLOR = {"git_pushes": SERIES[0], "developers": SERIES[1], "repositories": SERIES[2]}
MARKS = [
    (pd.Timestamp("2022-11-30"), "ChatGPT"),
    (pd.Timestamp("2025-02-24"), "Coding agents"),
]


def _meta() -> dict:
    return json.loads(
        (PROCESSED / "innovation_graph_meta.json").read_text(encoding="utf-8")
    )


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(
        PROCESSED / "innovation_graph_totals.csv", parse_dates=["quarter_start"]
    )
    fig, axes = plt.subplots(1, 2, figsize=WIDTH_FULL, sharey=True)
    for ax, scope in zip(axes, ["World", "US"]):
        d = df[df["scope"] == scope]
        ends = []
        for m, lab in METRICS:
            s = d[d["metric"] == m].set_index("quarter_start")["index_2020q1"]
            ax.plot(s.index, s.values, color=COLOR[m], lw=1.5)
            ends.append([s.values[-1], s.index[-1], lab, m])
        ends.sort(key=lambda e: e[0])
        gap = 18
        ypos = [ends[0][0]]
        for e in ends[1:]:
            ypos.append(max(e[0], ypos[-1] + gap))
        for (v, x, lab, m), y in zip(ends, ypos):
            label_end(ax, x, v, "", COLOR[m])
            ax.annotate(
                f"{lab} {v:.0f}",
                xy=(x, y),
                xytext=(6, 0),
                textcoords="offset points",
                fontsize=7,
                color=COLORS["ink2"],
                va="center",
            )
        ax.axhline(100, color=COLORS["axis"], lw=0.7, zorder=0)
        for x, lab in MARKS:
            ax.axvline(x, color=COLORS["muted"], lw=0.6, ls=(0, (3, 3)), zorder=0)
            ax.text(
                x,
                0.98,
                lab,
                transform=ax.get_xaxis_transform(),
                fontsize=6.5,
                color=COLORS["muted"],
                ha="right",
                va="top",
                rotation=90,
            )
        ax.set_title(
            "World (sum of economies)" if scope == "World" else "United States",
            fontsize=9,
        )
        ax.set_xlim(pd.Timestamp("2019-11-01"), pd.Timestamp("2028-03-01"))
        ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (2020, 2022, 2024, 2026)])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.spines["bottom"].set_bounds(
            mdates.date2num(pd.Timestamp("2020-01-01")),
            mdates.date2num(d["quarter_start"].max()),
        )
    axes[0].set_ylabel("Index, 2020Q1 = 100")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    meta = _meta()
    source_note(
        fig,
        f"Source: GitHub Innovation Graph (github.com/github/innovationgraph, CC0), quarterly, public activity; economies with <100 developers suppressed; EU aggregate excluded. Retrieved {meta['retrieved']}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
