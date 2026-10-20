"""Figure: new packages per month by ecosystem (small multiples, one y-axis per panel)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import (
    COLORS,
    ENTITY_COLORS,
    SERIES,
    WIDTH_TALL,
    apply,
    save,
    source_note,
)

NAME = "f03_pkg_new_monthly"
ECOS = ["PyPI", "crates.io", "RubyGems", "Packagist"]
COLOR = {
    "PyPI": ENTITY_COLORS["Python"],
    "crates.io": ENTITY_COLORS["Rust"],
    "RubyGems": SERIES[7],
    "Packagist": SERIES[6],
    "npm": ENTITY_COLORS["JavaScript"],
}
FILTER_LABEL = {
    "PyPI": "2nd release ≤ 90 days",
    "crates.io": "≥ 2 versions",
    "RubyGems": "not fully yanked",
    "Packagist": None,
}
START = "2015-01-01"


def _retrieved() -> str:
    p = PROCESSED / "package_ecosystems_meta.json"
    return json.loads(p.read_text(encoding="utf-8"))["retrieved"] if p.exists() else ""


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(
        PROCESSED / "package_ecosystems_new_monthly.csv", parse_dates=["month"]
    )
    df = df[df["month"] >= START]
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH_TALL[0], 4.6), sharex=True)
    for ax, eco in zip(axes.flat, ECOS):
        d = df[df["ecosystem"] == eco].set_index("month")
        c = COLOR[eco]
        k = 1000.0
        ax.plot(d.index, d["new_packages"] / k, color=c, lw=0.5, alpha=0.45)
        roll = d["new_packages"].rolling(12).mean() / k
        ax.plot(roll.index, roll.values, color=c, lw=1.6)
        if d["new_packages_filtered"].notna().any():
            rf = d["new_packages_filtered"].rolling(12).mean() / k
            ax.plot(rf.index, rf.values, color=c, lw=1.1, ls=(0, (3, 1.5)))
        for x in (pd.Timestamp("2022-11-30"), pd.Timestamp("2025-02-24")):
            ax.axvline(x, color=COLORS["muted"], lw=0.5, ls=(0, (3, 3)), zorder=0)
        title = eco + ("  (net additions)" if eco == "Packagist" else "")
        ax.set_title(title, fontsize=8.5)
        ax.set_ylim(0, None)
        ax.set_ylabel("New packages / month (k)" if eco in ("PyPI", "RubyGems") else "")
        lab = FILTER_LABEL[eco]
        if lab:
            ax.text(
                0.02,
                0.96,
                f"dashed: {lab}",
                transform=ax.transAxes,
                fontsize=6.5,
                color=COLORS["ink2"],
                va="top",
            )
    axes[0, 0].text(
        pd.Timestamp("2022-11-30"),
        axes[0, 0].get_ylim()[1] * 0.98,
        "ChatGPT ",
        fontsize=6,
        color=COLORS["muted"],
        ha="right",
        va="top",
        rotation=90,
    )
    axes[0, 0].text(
        pd.Timestamp("2025-02-24"),
        axes[0, 0].get_ylim()[1] * 0.98,
        "Agents ",
        fontsize=6,
        color=COLORS["muted"],
        ha="right",
        va="top",
        rotation=90,
    )
    handles = [
        Line2D([], [], color=COLORS["ink2"], lw=0.5, alpha=0.6),
        Line2D([], [], color=COLORS["ink2"], lw=1.6),
        Line2D([], [], color=COLORS["ink2"], lw=1.1, ls=(0, (3, 1.5))),
    ]
    fig.legend(
        handles,
        ["Monthly", "12-month mean", "12-month mean, filtered"],
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.01),
        fontsize=7.5,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.95), h_pad=1.2)
    source_note(
        fig,
        f"Source: PyPI & RubyGems via ClickHouse public playground (mirrors of PyPI BigQuery metadata and the RubyGems.org dump); crates.io API; packagist.org/statistics. Retrieved {_retrieved()}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
