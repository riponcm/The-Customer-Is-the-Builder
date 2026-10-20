"""Figure: attributed public commits and their ratio to GitHub pushes."""

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

NAME = "f05_ai_commit_share"


def make_figure() -> plt.Figure:
    apply()
    tot = pd.read_csv(PROCESSED / "ai_attribution_commits_total.csv")
    tools = pd.read_csv(PROCESSED / "ai_attribution_commits_by_tool.csv")
    q = pd.read_csv(PROCESSED / "ai_attribution_commits_quarterly.csv").dropna(
        subset=["git_pushes"]
    )
    meta = json.loads(
        (PROCESSED / "ai_attribution_commits_meta.json").read_text(encoding="utf-8")
    )
    for df in (tot, tools):
        df["date"] = pd.PeriodIndex(df["month"], freq="M").to_timestamp()
    fig, axes = plt.subplots(
        1, 2, figsize=(WIDTH_FULL[0], 3.4), gridspec_kw={"width_ratios": [1.5, 1]}
    )
    ax = axes[0]
    cl = tools[tools["tool"] == "Claude Code"].set_index("date")
    claude = cl["commits"] / 1000000.0
    total = tot.set_index("date")["commits"] / 1000000.0
    for s, lab, col in [
        (total, "All tracked tools", SERIES[0]),
        (claude, "Claude Code", SERIES[1]),
    ]:
        ax.plot(s.index, s.values, color=col, lw=1.6)
    ends = sorted(
        [
            (total.iloc[-1], "All tracked tools", SERIES[0], total.index[-1]),
            (claude.iloc[-1], "Claude Code", SERIES[1], claude.index[-1]),
        ]
    )
    gap = 0.06 * max(total.max(), 1)
    ypos = [ends[0][0], max(ends[1][0], ends[0][0] + gap)]
    for (v, lab, col, x), y in zip(ends, ypos):
        label_end(ax, x, v, "", col)
        ax.annotate(
            f"{lab} {v:.1f}m",
            xy=(x, y),
            xytext=(5, 0),
            textcoords="offset points",
            fontsize=7.5,
            color=COLORS["ink2"],
            va="center",
        )
    first, last = (tot["date"].min(), tot["date"].max())
    ax.set_xlim(first, last + pd.DateOffset(months=11))
    ax.spines["bottom"].set_bounds(mdates.date2num(first), mdates.date2num(last))
    ax.set_xticks(
        [pd.Timestamp(f"{y}-01-01") for y in range(first.year, last.year + 1)]
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Attributed commits (millions)")
    ax.set_title("A. Monthly public commit counts", fontsize=8.5)
    ax = axes[1]
    x = list(range(len(q)))
    ax.bar(x, q["ai_commits_per_1k_pushes"], color=SERIES[0], width=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [str(int(y)) if qq == 1 else "" for y, qq in zip(q["year"], q["quarter"])],
        fontsize=8,
    )
    for i, v in zip(x, q["ai_commits_per_1k_pushes"]):
        if v >= 1:
            ax.text(
                i,
                v,
                f"{v:.0f}",
                ha="center",
                va="bottom",
                fontsize=6.5,
                color=COLORS["ink2"],
            )
    ax.set_ylabel("AI-attributed commits per 1,000 pushes")
    ax.set_title(
        f"B. Quarterly commits per push\n(through {meta['ig_last_quarter']})",
        fontsize=8.5,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    source_note(
        fig,
        f"Sources: GitHub commit search (tool trailers and bot authors) and GitHub Innovation Graph git_pushes (CC0; economies summed, EU aggregate excluded).\nAttribution is optional; signatures may overlap and some searches are incomplete. Commits per push is not a share. Retrieved {meta['retrieved_last']}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
