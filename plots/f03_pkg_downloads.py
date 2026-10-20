"""Figure: registry-wide package downloads per month (log scale, one axis)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import (
    COLORS,
    ENTITY_COLORS,
    SERIES,
    WIDTH_FULL,
    apply,
    save,
    source_note,
)

NAME = "f03_pkg_downloads"
COLOR = {
    "npm": ENTITY_COLORS["JavaScript"],
    "PyPI": ENTITY_COLORS["Python"],
    "Packagist": SERIES[6],
}
START = "2017-01-01"


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(
        PROCESSED / "package_ecosystems_downloads.csv", parse_dates=["month"]
    )
    df = df[df["month"] >= START]
    meta_p = PROCESSED / "package_ecosystems_meta.json"
    retrieved = (
        json.loads(meta_p.read_text(encoding="utf-8"))["retrieved"]
        if meta_p.exists()
        else ""
    )
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    for eco in ["npm", "PyPI", "Packagist"]:
        s = df[df["ecosystem"] == eco].set_index("month")["downloads"] / 1000000000.0
        ax.plot(s.index, s.values, color=COLOR[eco], lw=1.5)
        ax.plot(
            [s.index[-1]],
            [s.values[-1]],
            "o",
            color=COLOR[eco],
            ms=3.5,
            markeredgecolor=COLORS["surface"],
            markeredgewidth=0.8,
        )
        ax.annotate(
            f"{eco} {s.values[-1]:,.0f}B",
            (s.index[-1], s.values[-1]),
            xytext=(5, 0),
            textcoords="offset points",
            fontsize=7.5,
            color=COLORS["ink2"],
            va="center",
        )
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"{v:,.0f}" if v >= 1 else f"{v:g}")
    )
    ax.set_ylabel("Downloads per month (billions, log scale)")
    for x, lab in (
        (pd.Timestamp("2022-11-30"), "ChatGPT"),
        (pd.Timestamp("2025-02-24"), "Coding agents"),
    ):
        ax.axvline(x, color=COLORS["muted"], lw=0.5, ls=(0, (3, 3)), zorder=0)
        ax.text(
            x,
            0.02,
            lab + " ",
            transform=ax.get_xaxis_transform(),
            fontsize=6.5,
            color=COLORS["muted"],
            ha="right",
            va="bottom",
            rotation=90,
        )
    ax.set_xlim(pd.Timestamp(START), df["month"].max() + pd.DateOffset(months=22))
    ax.set_xticks(
        [pd.Timestamp(f"{y}-01-01") for y in range(2017, df["month"].max().year + 1)]
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    source_note(
        fig,
        f"Source: api.npmjs.org/downloads/range (whole registry); PyPI BigQuery download log via ClickHouse playground (pypi.pypi_downloads_per_month);\npackagist.org/statistics. Latest complete month per source; PyPI ends before a mirror ingestion gap (see data notes). Retrieved {retrieved}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
