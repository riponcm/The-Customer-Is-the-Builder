"""Figure: mean year-over-year growth of new packages per month in three periods (pre, ChatGPT era, agent era)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_FULL, apply, save, source_note

NAME = "f03_pkg_yoy"
ROWS = [
    ("PyPI", "new_packages", "PyPI"),
    ("PyPI", "new_packages_filtered", "PyPI, filtered"),
    ("crates.io", "new_packages", "crates.io"),
    ("crates.io", "new_packages_filtered", "crates.io, filtered"),
    ("RubyGems", "new_packages", "RubyGems"),
    ("RubyGems", "new_packages_filtered", "RubyGems, filtered"),
    ("Packagist", "new_packages", "Packagist (net)"),
]
PERIOD = {
    "pre": (COLORS["muted"], "Jan 2016 – Nov 2022"),
    "chatgpt_era": (SERIES[0], "Dec 2022 – Jan 2025"),
    "agent_era": (SERIES[1], "Feb 2025 – latest"),
}
OFFSETS = {"pre": 0.24, "chatgpt_era": 0.0, "agent_era": -0.24}


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(PROCESSED / "package_ecosystems_yoy.csv")
    meta_p = PROCESSED / "package_ecosystems_meta.json"
    retrieved = (
        json.loads(meta_p.read_text(encoding="utf-8"))["retrieved"]
        if meta_p.exists()
        else ""
    )
    fig, ax = plt.subplots(figsize=(WIDTH_FULL[0], 4.0))
    labels = []
    for i, (eco, metric, lab) in enumerate(ROWS):
        y = len(ROWS) - 1 - i
        labels.append((y, lab))
        for period, dy in OFFSETS.items():
            r = df[
                (df.ecosystem == eco) & (df.metric == metric) & (df.period == period)
            ]
            if r.empty:
                continue
            r = r.iloc[0]
            col = PERIOD[period][0]
            ax.plot(
                [100 * r.lo_pct, 100 * r.hi_pct],
                [y + dy, y + dy],
                color=col,
                lw=1.4,
                solid_capstyle="round",
            )
            ax.plot(
                [100 * r.mean_yoy_pct],
                [y + dy],
                "o",
                color=col,
                ms=5,
                markeredgecolor=COLORS["surface"],
                markeredgewidth=0.8,
                zorder=3,
            )
            ax.annotate(
                f"{100 * r.mean_yoy_pct:+.0f}%",
                (100 * r.hi_pct, y + dy),
                xytext=(4, 0),
                textcoords="offset points",
                fontsize=6.5,
                color=COLORS["ink2"],
                va="center",
            )
    ax.axvline(0, color=COLORS["axis"], lw=0.8, zorder=0)
    ax.set_yticks([y for y, _ in labels])
    ax.set_yticklabels([lab for _, lab in labels])
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("Mean year-over-year change in new packages per month (%)")
    ax.tick_params(axis="y", length=0)
    handles = [
        Line2D([], [], color=PERIOD[p][0], marker="o", lw=1.4, ms=5) for p in PERIOD
    ]
    ax.legend(
        handles,
        [PERIOD[p][1] for p in PERIOD],
        loc="upper center",
        bbox_to_anchor=(0.5, 1.1),
        ncol=3,
        fontsize=7.5,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    source_note(
        fig,
        f"Mean of monthly y/y growth (exp of mean log change); bars: 95% CI (Newey-West s.e.). Sources as Fig. f03_pkg_new_monthly. Retrieved {retrieved}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
