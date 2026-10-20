"""Figure: composition of US private software investment by type (nominal shares)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import (
    COLORS,
    ENTITY_COLORS,
    WIDTH_FULL,
    apply,
    label_end,
    save,
    source_note,
)

NAME = "f01_bea_software_shares"
LABELS = {
    "prepackaged": "Prepackaged (bought)",
    "custom": "Custom (commissioned)",
    "own_account": "Own-account (built in-house)",
}


def _retrieved() -> str:
    meta = json.loads(
        (PROCESSED / "bea_software_investment_meta.json").read_text(encoding="utf-8")
    )
    return (meta["retrieved_utc"].get("NipaDataA.txt") or "")[:10]


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(PROCESSED / "bea_software_investment_annual.csv")
    sh = df[df["measure"] == "share_of_software_nominal_pct"].pivot_table(
        index="year", columns="type", values="value"
    )
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    for typ in ("prepackaged", "custom", "own_account"):
        s = sh[typ].dropna()
        ax.plot(s.index, s.values, color=ENTITY_COLORS[typ], lw=1.6)
        label_end(
            ax,
            s.index[-1],
            s.values[-1],
            f"{LABELS[typ]}  {s.values[-1]:.0f}%",
            ENTITY_COLORS[typ],
        )
    for x, txt, ha, dx in (
        (2022.9, "ChatGPT\n(Nov 2022)", "right", -0.25),
        (2025.0, "Coding-agent\nera (2025)", "left", 0.3),
    ):
        ax.axvline(x, color=COLORS["muted"], lw=0.7, ls=(0, (3, 3)), zorder=0)
        ax.text(
            x + dx,
            56.5,
            txt,
            fontsize=6.5,
            color=COLORS["muted"],
            ha=ha,
            va="top",
            clip_on=False,
        )
    ax.set_xlim(sh.index.min() - 0.5, sh.index.max() + 0.5)
    ax.set_ylim(0, 57)
    ax.set_ylabel("Share of nominal software investment (%)")
    ax.margins(x=0)
    fig.subplots_adjust(right=0.74, bottom=0.14)
    ax.set_xlim(right=sh.index.max() + 0.6)
    source_note(
        fig,
        f"Source: BEA NIPA Table 5.6.5 (series Y003RC, Y004RC, Y005RC; shares of B985RC), annual. Retrieved {_retrieved()}.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, NAME)


if __name__ == "__main__":
    main()
