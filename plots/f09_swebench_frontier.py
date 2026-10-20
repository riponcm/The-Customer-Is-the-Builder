"""Figure: SWE-bench Verified scores (Epoch AI runs) and the best-so-far frontier."""

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

NAME = "f09_swebench_frontier"
P = "agent_capability_cost_"


def make_figure() -> plt.Figure:
    apply()
    meta = json.loads((PROCESSED / f"{P}meta.json").read_text(encoding="utf-8"))
    d = pd.read_csv(
        PROCESSED / f"{P}swebench_verified.csv", parse_dates=["release_date"]
    )
    fig, ax = plt.subplots(figsize=(WIDTH_HALF[0] * 1.25, WIDTH_HALF[1] * 1.15))
    ax.plot(
        d["release_date"],
        d["score_pct"],
        "o",
        ms=3.2,
        color=COLORS["context"],
        zorder=2,
    )
    f = d.groupby("release_date")["frontier_pct"].max()
    ax.step(f.index, f.values, where="post", color=SERIES[0], lw=1.4, zorder=3)
    fr = d[d["is_frontier"]]
    ax.plot(fr["release_date"], fr["score_pct"], "o", ms=3.4, color=SERIES[0], zorder=4)
    first, best = (d.iloc[0], d.loc[d["score_pct"].idxmax()])
    first_label = first["model"].replace("gpt-4o-2024-11-20", "GPT-4o")
    ax.annotate(
        f"{first_label}\n{first['score_pct']:.0f}%",
        (first["release_date"], first["score_pct"]),
        xytext=(2, -12),
        textcoords="offset points",
        fontsize=6.3,
        color=COLORS["ink2"],
        va="top",
    )
    best_label = best["model"].replace("claude-opus-4-7_max", "Claude Opus 4.7 (max)")
    ax.annotate(
        f"{best_label}  {best['score_pct']:.1f}%",
        (best["release_date"], best["score_pct"]),
        xytext=(-4, 7),
        textcoords="offset points",
        fontsize=6.3,
        color=COLORS["ink2"],
        ha="right",
    )
    ax.set_ylim(0, 100)
    ax.set_ylabel("SWE-bench Verified, % resolved")
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    last_release = d["release_date"].max()
    retrieved = d["release_date"].max() + pd.DateOffset(months=6)
    ax.axvspan(
        last_release + pd.Timedelta(days=2),
        retrieved,
        color=COLORS["grid"],
        alpha=0.45,
        linewidth=0,
        zorder=0,
    )
    ax.set_xlim(d["release_date"].min() - pd.Timedelta(days=35), retrieved)
    ax.tick_params(axis="x", labelsize=7)
    fig.subplots_adjust(bottom=0.31, left=0.16)
    fig.text(
        0.99,
        0.12,
        f"Latest model release: {last_release:%b %Y}; later models unmeasured.",
        fontsize=6.2,
        color=COLORS["muted"],
        ha="right",
        va="bottom",
    )
    source_note(
        fig,
        f"Source: Epoch AI Benchmarking Hub (own runs), CC-BY.\nDate = model release; gray = all runs; blue = best observed. Scaffold changed. Retrieved {meta['retrieved_utc']['epoch'][:10]}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
