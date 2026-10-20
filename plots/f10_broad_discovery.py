"""Figure: open-source alternatives per product under the broad rule, by creation era,"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_FULL, apply, save, source_note

NAME = "f10_broad_discovery"
ERAS = [
    ("before ChatGPT", COLORS["context"]),
    ("ChatGPT era", SERIES[0]),
    ("agent era", SERIES[1]),
]
ERA_LABEL = {
    "before ChatGPT": "Before Dec 2022",
    "ChatGPT era": "Dec 2022 to Feb 2025",
    "agent era": "Since Feb 2025",
}


def make_figure():
    apply()
    d = pd.read_csv(PROCESSED / "alt_discovery_by_product.csv")
    fig, ax = plt.subplots(figsize=(WIDTH_FULL[0], 3.9))
    y = range(len(d))
    left = pd.Series(0, index=d.index, dtype=float)
    for era, color in ERAS:
        ax.barh(
            list(y),
            d[era],
            left=left,
            color=color,
            height=0.62,
            label=ERA_LABEL[era],
            edgecolor=COLORS["surface"],
            linewidth=1,
        )
        left += d[era]
    ax.plot(
        d["narrow_total"],
        list(y),
        "|",
        ms=11,
        mew=2,
        color=COLORS["ink"],
        label="Narrow rule (names the product)",
    )
    for yi, r in zip(y, d.itertuples()):
        ax.text(
            r.broad_total + 2,
            yi,
            f"{r.broad_total}",
            va="center",
            fontsize=7,
            color=COLORS["ink2"],
        )
    ax.set_yticks(list(y))
    ax.set_yticklabels(d["product"])
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("Screened open-source candidates (broad rule)")
    ax.legend(loc="lower right", ncol=1, fontsize=7)
    fig.tight_layout()
    source_note(
        fig,
        "Broad rule: six discovery strategies; screened for core workflow, not archived, not a fork, >= 20 stars; author-owned repo excluded. Workflow match partly heuristic (upper bound). Retrieved 2026-10-12.",
    )
    fig.subplots_adjust(bottom=0.2)
    return fig


def main():
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
