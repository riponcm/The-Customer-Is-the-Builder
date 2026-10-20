"""Selected current models on a common application-building evaluation harness."""

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

NAME = "f20_vibe_code_bench"


def make_figure() -> plt.Figure:
    apply()
    frame = pd.read_csv(PROCESSED / "customer_building_vcb_selected.csv").sort_values(
        "score_pct"
    )
    meta = json.loads(
        (PROCESSED / "customer_building_evidence_meta.json").read_text(encoding="utf-8")
    )["vals"]
    fig, ax = plt.subplots(figsize=(7.0, 3.7))
    y = np.arange(len(frame))
    ax.hlines(y, 0, frame.score_pct, color=COLORS["grid"], lw=1.8)
    ax.scatter(frame.score_pct, y, s=30, color=SERIES[0], zorder=3)
    for yi, value in zip(y, frame.score_pct):
        ax.text(
            value + 1.2,
            yi,
            f"{value:.2f}",
            va="center",
            fontsize=8,
            color=COLORS["ink2"],
        )
    labels = frame.model.str.replace(
        "DeepSeek V4.1 Flash 1017", "DeepSeek V4.1 Flash (1017)", regex=False
    )
    ax.set_yticks(y, labels, fontsize=8)
    ax.set_xlim(0, 103)
    ax.set_xticks(np.arange(0, 101, 20))
    ax.set_ylim(-0.6, len(frame) - 0.4)
    ax.set_xlabel("Mean functional UI-test score (%)")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.tick_params(axis="y", length=0)
    fig.subplots_adjust(left=0.29, right=0.97, top=0.98, bottom=0.2)
    source_note(
        fig,
        f"Source: Vals AI Vibe Code Bench v{meta['version']}; selected models, OpenHands harness.\nScores average application test results, not complete-application success rates. Last accessed {meta['retrieved_utc'][:10]}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
