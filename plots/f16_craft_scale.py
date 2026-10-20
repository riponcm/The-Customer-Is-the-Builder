"""Figure 16c - how much code is in the suite?"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, apply, save, source_note

STEM = "f16_craft_scale"
OS = ENTITY_COLORS["open_source"]


def make_figure() -> plt.Figure:
    apply()
    t = pd.read_csv(PROCESSED / "16_case_craft_suite_suite_table.csv")
    t = t.sort_values("rs_lines_nonblank", ascending=True).reset_index(drop=True)
    y = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.barh(
        y, t["rs_lines_nonblank"] / 1000, color=OS, alpha=0.85, height=0.62, zorder=3
    )
    ax.scatter(
        t["rust_loc_est_bytes35"] / 1000,
        y,
        marker="D",
        s=22,
        facecolor="none",
        edgecolor=COLORS["ink2"],
        linewidth=1.0,
        zorder=4,
    )
    xmax = max(t["rs_lines_nonblank"].max(), t["rust_loc_est_bytes35"].max()) / 1000
    for r in t.itertuples():
        ax.text(
            max(r.rs_lines_nonblank, r.rust_loc_est_bytes35) / 1000 + xmax * 0.02,
            r.Index,
            f"{r.rs_lines_nonblank / 1000:,.0f}k lines · {int(r.commits):,} commits · {int(r.n_contributors)} contrib.",
            va="center",
            fontsize=6.8,
            color=COLORS["ink2"],
        )
    ax.set_yticks(y)
    ax.set_yticklabels(t["display"], fontsize=8)
    ax.set_xlim(0, xmax * 1.62)
    ax.set_xlabel("Rust lines of code (thousands, non-blank)")
    ax.grid(axis="x", color=COLORS["grid"], lw=0.6)
    ax.grid(axis="y", visible=False)
    tot = t["rs_lines_nonblank"].sum()
    ax.set_title(
        f"About {tot / 1000000.0:.1f} million lines of Rust across the 12 apps in under two weeks",
        loc="left",
        fontsize=9.5,
    )
    ax.scatter(
        [],
        [],
        marker="D",
        s=22,
        facecolor="none",
        edgecolor=COLORS["ink2"],
        label="estimate: language bytes / 35",
    )
    from matplotlib.patches import Patch

    h, l = ax.get_legend_handles_labels()
    ax.legend(
        h + [Patch(color=OS, alpha=0.85)],
        l + ["measured: non-blank .rs lines (clone)"],
        loc="lower right",
        frameon=False,
        fontsize=7,
    )
    fig.subplots_adjust(left=0.13, right=0.98, top=0.92, bottom=0.2)
    source_note(
        fig,
        "Source: shallow git clone of each storytold/<app> default branch (2026-10-12) counted with Python; GitHub /languages API for the estimate. Excludes vendor/target dirs; includes tests.\nLines are volume, not functionality or quality; line counts are inflated by generated code, tests and long files.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
