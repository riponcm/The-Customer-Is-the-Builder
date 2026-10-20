"""Figure: commits whose message mentions an agent-instruction file, per quarter (log scale)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_FULL, apply, save, source_note

NAME = "f05_instruction_files"
FILES = [
    ("CLAUDE.md", SERIES[1]),
    ("AGENTS.md", SERIES[0]),
    (".cursorrules", SERIES[2]),
]


def make_figure() -> plt.Figure:
    apply()
    d = pd.read_csv(PROCESSED / "ai_attribution_commits_instruction_mentions.csv")
    d["q"] = pd.PeriodIndex(d["quarter"], freq="Q")
    meta = json.loads(
        (PROCESSED / "ai_attribution_commits_meta.json").read_text(encoding="utf-8")
    )
    stock_p = PROCESSED / "ai_attribution_commits_instruction_stock.csv"
    stock = (
        pd.read_csv(stock_p).set_index("file")["total_count"]
        if stock_p.exists()
        else pd.Series(dtype=float)
    )
    quarters = sorted(d["q"].unique())
    xpos = {q: i for i, q in enumerate(quarters)}
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    ends = []
    for f, col in FILES:
        s = d[d["file"] == f].sort_values("q")
        s = s[s["commits"] > 0]
        if s.empty:
            continue
        x = [xpos[q] for q in s["q"]]
        ax.plot(x, s["commits"], color=col, lw=1.6)
        lb = s["lower_bound"].astype(bool)
        ax.plot(
            [xi for xi, b in zip(x, lb) if not b],
            s.loc[~lb, "commits"],
            "o",
            color=col,
            ms=4,
        )
        ax.plot(
            [xi for xi, b in zip(x, lb) if b],
            s.loc[lb, "commits"],
            "o",
            mfc=COLORS["surface"],
            mec=col,
            ms=4,
        )
        ends.append((s["commits"].iloc[-1], x[-1], f))
    ends.sort()
    prev = None
    for v, x, f in ends:
        offset = 14 if prev is not None and v < prev * 2.5 else 0
        prev = v
        ax.annotate(
            f"{f}  {v:,.0f}",
            xy=(x, v),
            xytext=(8, offset),
            textcoords="offset points",
            fontsize=7.5,
            color=COLORS["ink2"],
            va="center",
        )
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_xticks(range(len(quarters)))
    ax.set_xticklabels([f"{q.year}Q{q.quarter}" for q in quarters], fontsize=7.5)
    ax.set_xlim(-0.4, len(quarters) + 1.6)
    ax.spines["bottom"].set_bounds(0, len(quarters) - 1)
    ax.set_ylabel("Commits per quarter mentioning file (log)")
    st = ", ".join((f"{k} {int(v):,}" for k, v in stock.items() if pd.notna(v)))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    source_note(
        fig,
        f"Source: GitHub commit search (/search/commits; literal file name in commit message; committer-date quarterly windows; hollow = lower bound). Retrieved {meta['retrieved_last']}.\nFiles present at retrieval (code search, filename:, no date filter): {st}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
