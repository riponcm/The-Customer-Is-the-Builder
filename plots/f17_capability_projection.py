"""Figure: when would agents handle a work-day / week / month / year of software work?"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_TALL, apply, save, source_note

NAME = "f17_capability_projection"
TODAY = pd.Timestamp("2026-10-12")
REGIME_STYLE = {
    "fast": dict(color=SERIES[0], label="Trend since 2023"),
    "slow": dict(color=SERIES[1], label="Trend since 2019"),
}
Y_TICKS = {
    1: "1 min",
    60: "1 hour",
    8 * 60: "1 work-day",
    40 * 60: "1 work-week",
    167 * 60: "1 work-month",
    2000 * 60: "1 work-year",
}
THRESHOLD_LABEL = {
    "workday": "day",
    "workweek": "week",
    "workmonth": "month",
    "workyear": "year",
}


def _load():
    paths = pd.read_csv(PROCESSED / "projections_paths.csv", parse_dates=["date"])
    cross = pd.read_csv(
        PROCESSED / "projections_crossings.csv",
        parse_dates=["date", "date_p05", "date_p95"],
    )
    pts = pd.read_csv(
        PROCESSED / "agent_capability_cost_metr_horizons.csv",
        parse_dates=["release_date"],
    )
    return (paths, cross, pts[pts["is_sota"]])


def _panel(ax, metric, title, paths, cross, pts):
    start = pd.Timestamp("2022-01-01")
    for regime, st in REGIME_STYLE.items():
        p = paths[
            (paths.metric == metric) & (paths.regime == regime) & (paths.date >= start)
        ]
        future = p[p.date >= pts.release_date.max()]
        ax.fill_between(
            future.date,
            future.minutes_p05,
            future.minutes_p95,
            color=st["color"],
            alpha=0.12,
            lw=0,
        )
        ax.plot(p.date, p.minutes, color=st["color"], lw=1.6, label=st["label"])
        c = cross[(cross.metric == metric) & (cross.regime == regime)]
        for r in c.itertuples():
            if pd.isna(r.date) or r.date > paths.date.max():
                continue
            ax.plot(
                [r.date],
                [r.threshold_minutes],
                "o",
                ms=5,
                color=st["color"],
                markeredgecolor=COLORS["surface"],
                markeredgewidth=1,
                zorder=5,
            )
            if r.threshold in ("workmonth", "workyear") and r.date >= TODAY:
                ax.annotate(
                    r.date.strftime("%b %Y"),
                    (r.date, r.threshold_minutes),
                    xytext=(-5, -16) if regime == "fast" else (5, 10),
                    textcoords="offset points",
                    ha="right" if regime == "fast" else "left",
                    fontsize=6.5,
                    color=COLORS["ink2"],
                )
    obs = pts[pts.release_date >= start]
    ax.plot(
        obs.release_date,
        obs[metric],
        "o",
        ms=4,
        color=COLORS["ink"],
        label="Frontier model (measured)",
        zorder=6,
    )
    for m in Y_TICKS:
        if m >= 8 * 60:
            ax.axhline(m, color=COLORS["grid"], lw=0.8, zorder=0)
    ax.axvline(TODAY, color=COLORS["muted"], lw=0.8)
    ax.text(TODAY, 1.3, " today", fontsize=7, color=COLORS["muted"], va="bottom")
    ax.set_yscale("log")
    ax.set_ylim(1, 400000.0)
    ax.set_yticks(list(Y_TICKS))
    ax.set_yticklabels(list(Y_TICKS.values()))
    ax.minorticks_off()
    ax.grid(False)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(start, pd.Timestamp("2033-06-30"))
    ax.set_title(title)


def make_figure():
    apply()
    paths, cross, pts = _load()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_TALL[0], 3.9), sharey=True)
    _panel(axes[0], "p50_min", "A. Tasks completed with 50% success", paths, cross, pts)
    _panel(axes[1], "p80_min", "B. Tasks completed with 80% success", paths, cross, pts)
    axes[0].set_ylabel("Length of software task\n(time a skilled human needs)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0.07, 1, 0.9))
    source_note(
        fig,
        "Source: METR Time Horizon 1.1 (frontier models); OLS of log2 horizon on release date, shaded = 5-95% bootstrap band. Extrapolation of a benchmark trend, not a forecast. Retrieved 2026-10-12.",
    )
    return fig


def main():
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
