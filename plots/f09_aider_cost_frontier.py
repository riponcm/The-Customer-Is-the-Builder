"""Figure: cheapest benchmark-run cost to reach fixed coding-capability thresholds."""

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

NAME = "f09_aider_cost_frontier"
P = "agent_capability_cost_"


def make_figure() -> plt.Figure:
    apply()
    meta = json.loads((PROCESSED / f"{P}meta.json").read_text(encoding="utf-8"))
    fr = pd.read_csv(PROCESSED / f"{P}aider_cost_frontier.csv", parse_dates=["month"])
    ad = pd.read_csv(PROCESSED / f"{P}aider_polyglot.csv", parse_dates=["release_date"])
    ad = ad[ad["usable"]]
    fig, ax = plt.subplots(figsize=(WIDTH_HALF[0] * 1.25, WIDTH_HALF[1] * 1.15))
    ax.plot(
        ad["release_date"],
        ad["cost_usd"],
        "o",
        ms=2.5,
        color=COLORS["context"],
        zorder=1,
    )
    thresholds = sorted(fr["threshold_pct"].unique())
    end = fr["month"].max() + pd.offsets.MonthEnd(0)
    for i, thr in enumerate(thresholds):
        s = fr[fr["threshold_pct"] == thr].sort_values("month")
        x = list(s["month"]) + [end]
        y = list(s["min_cost_usd"]) + [s["min_cost_usd"].iloc[-1]]
        ax.step(x, y, where="post", color=SERIES[i], lw=1.3, zorder=3)
        ax.text(
            end + pd.Timedelta(days=8),
            y[-1] * (1.18 if thr == 70 else 0.85 if thr == 60 else 1.0),
            f"≥{thr}%",
            fontsize=6.8,
            color=SERIES[i],
            va="center",
        )
    ax.set_yscale("log")
    ax.set_yticks([0.3, 1, 3, 10, 30, 100, 300])
    ax.set_yticklabels(["$0.3", "$1", "$3", "$10", "$30", "$100", "$300"])
    ax.minorticks_off()
    ax.set_ylabel("Cheapest cost of full run (USD)")
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.set_xlim(pd.Timestamp("2024-06-15"), end + pd.Timedelta(days=60))
    ax.tick_params(axis="x", labelsize=7)
    fig.subplots_adjust(bottom=0.24, left=0.18)
    source_note(
        fig,
        f"Source: Aider LLM leaderboard via Epoch AI Benchmarking Hub, CC-BY.\nGray: individual runs; overlapping steps share the cheapest model. Retrieved {meta['retrieved_utc']['epoch'][:10]}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
