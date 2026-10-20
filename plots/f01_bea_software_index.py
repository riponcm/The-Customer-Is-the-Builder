"""Figure: nominal, real and price indexes (2015 = 100) for the three software types."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, apply, save, source_note

NAME = "f01_bea_software_index"
START = 2000
LABELS = {
    "prepackaged": "Prepackaged",
    "custom": "Custom",
    "own_account": "Own-account",
}
PANELS = [
    ("nominal_index_2015", "Nominal spending"),
    ("quantity_index_2015", "Real (Fisher quantity index)"),
    ("price_index_2015", "Price index"),
]


def _retrieved() -> str:
    meta = json.loads(
        (PROCESSED / "bea_software_investment_meta.json").read_text(encoding="utf-8")
    )
    return (meta["retrieved_utc"].get("NipaDataA.txt") or "")[:10]


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(PROCESSED / "bea_software_investment_annual.csv")
    df = df[df["year"] >= START]
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.9), sharex=True)
    for ax, (measure, title) in zip(axes, PANELS):
        w = df[df["measure"] == measure].pivot_table(
            index="year", columns="type", values="value"
        )
        ends = []
        for typ in ("prepackaged", "custom", "own_account"):
            s = w[typ].dropna()
            ls = (
                (0, (2.5, 1.5))
                if measure == "price_index_2015" and typ == "custom"
                else "-"
            )
            ax.plot(
                s.index,
                s.values,
                color=ENTITY_COLORS[typ],
                lw=1.5,
                ls=ls,
                zorder=3 if ls != "-" else 2,
            )
            ends.append([s.values[-1], s.index[-1], typ])
        lo, hi = ax.get_ylim()
        gap = (hi - lo) * 0.07
        ends.sort(key=lambda e: e[0])
        ends[0].append(ends[0][0])
        for i in range(1, len(ends)):
            ends[i].append(max(ends[i][0], ends[i - 1][3] + gap))
        for val, x, typ, ypos in ends:
            ax.text(
                x + 0.6,
                ypos,
                f"{val:.0f}",
                fontsize=6.5,
                color=ENTITY_COLORS[typ],
                va="center",
                ha="left",
            )
        ax.axhline(100, color=COLORS["axis"], lw=0.7, zorder=0)
        for x in (2022.9, 2025.0):
            ax.axvline(x, color=COLORS["muted"], lw=0.6, ls=(0, (3, 3)), zorder=0)
        ax.set_title(title, fontsize=8.5)
        ax.set_xlim(START - 0.5, w.index.max() + 3.2)
        ax.set_xticks([2000, 2010, 2020])
    axes[0].set_ylabel("Index, 2015 = 100")
    handles = [Line2D([], [], color=ENTITY_COLORS[t], lw=1.5) for t in LABELS]
    fig.legend(
        handles,
        list(LABELS.values()),
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.93))
    source_note(
        fig,
        f"Source: BEA NIPA Tables 5.6.5, 5.6.3, 5.6.4 (series Y003-Y005 RC/RA/RG), annual, rebased to 2015 = 100. Retrieved {_retrieved()}.\nVertical dashes: ChatGPT (Nov 2022), coding-agent era (2025). Custom and own-account share one BEA price index.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, NAME)


if __name__ == "__main__":
    main()
