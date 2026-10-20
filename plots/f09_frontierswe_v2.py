"""Current-model FrontierSWE v2 snapshot on one common evaluation harness."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, apply, save, source_note

NAME = "f09_frontierswe_v2"
P = "agent_capability_cost_"


def make_figure() -> plt.Figure:
    apply()
    meta = json.loads((PROCESSED / f"{P}meta.json").read_text(encoding="utf-8"))
    d = pd.read_csv(PROCESSED / f"{P}frontierswe_v2.csv").sort_values("mean_score_pct")
    fig, ax = plt.subplots(figsize=(7.0, 6.0))
    y = np.arange(len(d))
    ax.hlines(
        y, d["worst_score_pct"], d["best_score_pct"], color=COLORS["context"], lw=2
    )
    ax.scatter(d["mean_score_pct"], y, color=SERIES[0], s=18, zorder=3)
    ax.set_yticks(y, d["model"], fontsize=7.2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 80)
    ax.set_ylim(-0.7, len(d) - 0.3)
    ax.set_xlabel("Mean normalized task score (0 to 100)")
    fig.subplots_adjust(left=0.29, right=0.97, top=0.97, bottom=0.12)
    source_note(
        fig,
        f"Source: Epoch AI FrontierSWE v2 bulk data, common Proximus harness. Dots: mean score; bars: lowest to highest of five runs, not confidence intervals. Retrieved {meta['retrieved_utc']['epoch'][:10]}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
