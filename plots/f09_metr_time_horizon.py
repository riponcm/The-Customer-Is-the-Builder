"""Historical METR horizons and a separate current-model capability view."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, apply, save, source_note

NAME = "f09_metr_time_horizon"
P = "agent_capability_cost_"
TICKS = [
    (1 / 60, "1 s"),
    (0.25, "15 s"),
    (1, "1 min"),
    (4, "4 min"),
    (15, "15 min"),
    (60, "1 h"),
    (240, "4 h"),
    (960, "16 h"),
    (3840, "64 h"),
]


def make_figure() -> plt.Figure:
    apply()
    meta = json.loads((PROCESSED / f"{P}meta.json").read_text(encoding="utf-8"))
    m = pd.read_csv(PROCESSED / f"{P}metr_horizons.csv", parse_dates=["release_date"])
    fit = (
        pd.read_csv(PROCESSED / f"{P}metr_fit.csv")
        .set_index("fit")
        .loc["own_ols_sota_from_2023"]
    )
    eci = pd.read_csv(PROCESSED / f"{P}eci_general.csv")
    recent = eci[eci["latest_month"]].sort_values("score")
    fig, (ax, bx) = plt.subplots(
        2, 1, figsize=(7.0, 7.4), gridspec_kw={"height_ratios": [1, 1.15]}
    )
    for flag, color, face in (
        (False, COLORS["context"], "white"),
        (True, SERIES[0], SERIES[0]),
    ):
        s = m[m["is_sota"] == flag]
        ax.errorbar(
            s["release_date"],
            s["p50_min"],
            yerr=[s["p50_min"] - s["p50_ci_low"], s["p50_ci_high"] - s["p50_min"]],
            fmt="o",
            ms=3.6,
            color=color,
            mfc=face,
            mec=color,
            ecolor=color,
            elinewidth=0.55,
            capsize=0,
            zorder=3 if flag else 2,
        )
    out = m[m["is_sota"] & ~m["in_fit"] & (m["release_date"] >= "2023-01-01")]
    ax.plot(
        out["release_date"],
        out["p50_min"],
        "o",
        ms=4,
        mfc="white",
        mec=SERIES[0],
        zorder=4,
    )
    d = pd.date_range(fit["start"], fit["end"], periods=50)
    x = (d - pd.Timestamp("2019-01-01")).days / 365.25
    ax.plot(
        d,
        2 ** (fit["intercept"] + fit["slope_doublings_per_year"] * x),
        color=SERIES[1],
        lw=1.3,
    )
    ax.text(
        pd.Timestamp("2023-04-01"),
        0.1,
        f"Frontier fit: {fit['doubling_days']:.0f} days per doubling",
        fontsize=7,
        color=SERIES[1],
    )
    ax.set_yscale("log")
    ax.set_yticks([t for t, _ in TICKS])
    ax.set_yticklabels([lab for _, lab in TICKS])
    ax.minorticks_off()
    ax.set_ylim(1 / 60, 4500)
    ax.set_ylabel("50% horizon (human task time)")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    retrieved = m["release_date"].max() + pd.DateOffset(months=6)
    ax.axvspan(
        m["release_date"].max() + pd.Timedelta(days=2),
        retrieved,
        color=COLORS["grid"],
        alpha=0.45,
        linewidth=0,
        zorder=0,
    )
    ax.set_xlim(pd.Timestamp("2018-11-01"), retrieved)
    ax.legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=SERIES[0],
                markeredgecolor=SERIES[0],
                markersize=4,
                label="Frontier at release",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="white",
                markeredgecolor=COLORS["context"],
                markersize=4,
                label="Other measured model",
            ),
        ],
        loc="upper left",
        fontsize=6.5,
        handletextpad=0.2,
    )
    ax.set_title(
        "A. METR software task horizons, models through April 2026",
        loc="left",
        fontsize=9,
    )
    y = np.arange(len(recent))
    bx.errorbar(
        recent["score"],
        y,
        xerr=[recent["score"] - recent["ci_low"], recent["ci_high"] - recent["score"]],
        fmt="o",
        ms=4,
        color=SERIES[0],
        ecolor=SERIES[0],
        elinewidth=0.8,
        capsize=2,
    )
    bx.axvline(150, color=COLORS["muted"], lw=0.8, ls="--")
    bx.text(
        150.3,
        len(recent) - 0.1,
        "GPT-5 reference = 150",
        fontsize=6.4,
        color=COLORS["muted"],
        va="top",
    )
    bx.set_yticks(y, recent["model"], fontsize=7.1)
    bx.tick_params(axis="y", length=0)
    bx.set_xlim(145, 174)
    bx.set_ylim(-0.7, len(recent) - 0.3)
    bx.set_xlabel("Epoch general capability index (different scale)")
    bx.set_title(
        "B. Recent models, September 2026 release cohort", loc="left", fontsize=9
    )
    fig.subplots_adjust(left=0.29, right=0.97, top=0.96, bottom=0.085, hspace=0.45)
    source_note(
        fig,
        f"Sources: METR Time Horizon 1.1 and Epoch AI ECI. Bars: published intervals. Separate tests and units; ECI does not update the METR trend. METR retrieved {meta['retrieved_utc']['metr'][:10]}; Epoch retrieved {meta['retrieved_utc']['epoch'][:10]}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
