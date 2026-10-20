"""Stack Overflow questions per tag, January-September of each year, indexed 2022 = 100 (log scale)."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from src.paths import PROCESSED
from src.style import (
    COLORS,
    ENTITY_COLORS,
    SERIES,
    WIDTH_FULL,
    apply,
    save,
    source_note,
)

NAME = "f07_so_tag_index"
TAG_STYLE = {
    "(all questions)": ("All questions", COLORS["ink"]),
    "python": ("python", ENTITY_COLORS["Python"]),
    "javascript": ("javascript", ENTITY_COLORS["JavaScript"]),
    "rust": ("rust", ENTITY_COLORS["Rust"]),
    "pandas": ("pandas", SERIES[2]),
    "reactjs": ("reactjs", SERIES[4]),
}


def make_figure() -> plt.Figure:
    apply()
    t = pd.read_csv(PROCESSED / "stackoverflow_tags_ytd.csv")
    window = t["window"].dropna().iloc[0]
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    ends = []
    for tag, (label, color) in TAG_STYLE.items():
        d = t[t["tag"] == tag].sort_values("year")
        if d.empty:
            continue
        lw = 2.4 if tag == "(all questions)" else 1.6
        ax.plot(d["year"], d["index_2022"], color=color, lw=lw, marker="o", ms=3)
        ends.append((d["index_2022"].iloc[-1], label, color, d["year"].iloc[-1]))
    import numpy as np

    ends.sort()
    ys = np.log10([e[0] for e in ends])
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + 0.11)
    for (v, label, color, x), y in zip(ends, ys):
        ax.annotate(
            f"{label} ({v:.1f})",
            xy=(x, v),
            xytext=(x + 0.25, 10**y),
            fontsize=7.5,
            color=COLORS["ink2"],
            va="center",
            ha="left",
            arrowprops=dict(arrowstyle="-", color=color, lw=0.6),
        )
    ax.axhline(100, color=COLORS["axis"], lw=0.8)
    ax.axvline(2022.9, color=COLORS["muted"], lw=0.8, ls=":")
    ax.text(
        2022.95,
        260,
        "ChatGPT\n(Nov 2022)",
        fontsize=7.5,
        color=COLORS["ink2"],
        va="top",
    )
    ax.set_yscale("log")
    ax.set_ylim(0.2, 300)
    ax.yaxis.set_major_locator(mticker.FixedLocator([0.3, 1, 3, 10, 30, 100, 300]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.set_xlim(t["year"].min() - 0.3, t["year"].max() + 2.6)
    ax.set_xticks(range(int(t["year"].min()), int(t["year"].max()) + 1))
    ax.spines["bottom"].set_bounds(t["year"].min(), t["year"].max())
    ax.set_ylabel(f"Questions asked {window}, index 2022 = 100 (log)")
    ax.set_title(f"Stack Overflow questions by tag, {window} of each year")
    retrieved = t["retrieved"].iloc[0] if "retrieved" in t else ""
    source_note(
        fig,
        f"Source: Stack Exchange API v2.3, /questions?site=stackoverflow&tagged=<tag> (totals for {window} of each year; excludes deleted questions). Retrieved {retrieved}.",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
