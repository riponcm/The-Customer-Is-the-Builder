"""Dated backtest of the METR frontier task-horizon trend."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, apply, save, source_note

NAME = "f19_preagent_backtest"
BREAK = pd.Timestamp("2025-02-24")


def make_figure():
    apply()
    data = pd.read_csv(
        PROCESSED / "projections_preagent_backtest.csv", parse_dates=["release_date"]
    )
    p50 = data[data.metric == "p50_min"].sort_values("release_date")
    training = p50[p50.split == "training"]
    holdout = p50[p50.split == "holdout"]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.15))
    ax = axes[0]
    ax.plot(
        p50.release_date,
        p50.predicted_minutes,
        color=SERIES[0],
        lw=1.8,
        label="Trend fitted through 2024",
    )
    ax.scatter(
        training.release_date,
        training.observed_minutes,
        s=21,
        color=COLORS["ink"],
        label="Fit sample",
        zorder=3,
    )
    ax.scatter(
        holdout.release_date,
        holdout.observed_minutes,
        s=26,
        color=SERIES[1],
        label="Later models",
        zorder=3,
    )
    ax.axvline(BREAK, color=COLORS["muted"], ls="--", lw=0.8)
    ax.set_yscale("log")
    ax.set_ylim(2, 2200)
    ax.set_ylabel("50% task horizon (minutes)")
    ax.set_title("A. Earlier trend versus later models")
    ax.legend(loc="upper left", fontsize=7)
    ax = axes[1]
    for metric, color, label in (
        ("p50_min", SERIES[0], "50% success"),
        ("p80_min", SERIES[1], "80% success"),
    ):
        rows = data[(data.metric == metric) & (data.split == "holdout")].sort_values(
            "release_date"
        )
        ax.plot(
            rows.release_date,
            rows.observed_to_predicted,
            "o-",
            ms=3.5,
            color=color,
            label=label,
        )
    ax.axhline(1, color=COLORS["muted"], lw=0.8)
    ax.set_ylim(0, 12)
    ax.set_ylabel("Measured / earlier-trend horizon")
    ax.set_title("B. Later models exceeded the earlier line")
    ax.legend(loc="upper left", fontsize=7)
    for ax in axes:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_xlim(
            pd.Timestamp("2023-01-01") if ax is axes[0] else BREAK,
            pd.Timestamp("2026-07-01"),
        )
    fig.tight_layout(rect=(0, 0.07, 1, 1), w_pad=2.3)
    source_note(
        fig,
        "Source: METR Time Horizon 1.1; pre-agent fit uses frontier models released in 2023-2024, then compares later frontier models. Retrieved 2026-10-12. Selection and task mix may change.",
    )
    return fig


def main():
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
