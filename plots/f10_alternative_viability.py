"""Figure 10d - are the alternatives viable projects?"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, apply, save, source_note

STEM = "f10_alternative_viability"
CHATGPT = pd.Timestamp("2022-11-30")
Y2025 = pd.Timestamp("2025-01-01")
COHORTS = ["before ChatGPT", "Dec 2022-2024", "2025-2026"]
COHORT_COLORS = {
    "before ChatGPT": "#f7c2a8",
    "Dec 2022-2024": "#f1925f",
    "2025-2026": "#eb6834",
}
LABEL_OFFSETS = {
    "AppFlowy": (-5, 0),
    "hoppscotch": (4, 5),
    "Toola": (-5, 0),
    "Avnac-Studio": (4, 5),
    "OpenDesign": (4, -5),
    "react-video-editor": (4, 2),
}


def load() -> pd.DataFrame:
    v = pd.read_csv(
        PROCESSED / "10_open_source_vs_commercial_viability.csv",
        parse_dates=["created_at", "pushed_at"],
    )
    v["cohort"] = np.select(
        [v["created_at"] < CHATGPT, v["created_at"] < Y2025], COHORTS[:2], COHORTS[2]
    )
    return v


def make_figure() -> plt.Figure:
    apply()
    v = load()
    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(7.0, 3.9), gridspec_kw={"width_ratios": [2.1, 1]}
    )
    for coh in COHORTS:
        g = v[v["cohort"] == coh]
        live, arch = (g[~g["archived"]], g[g["archived"]])
        ax.scatter(
            live["months_active"].clip(lower=0.5),
            live["stars"],
            s=34,
            color=COHORT_COLORS[coh],
            edgecolor=COLORS["ink2"],
            linewidth=0.4,
            zorder=3,
            label=coh,
        )
        ax.scatter(
            arch["months_active"].clip(lower=0.5),
            arch["stars"],
            s=48,
            marker="X",
            color=COHORT_COLORS[coh],
            edgecolor=COLORS["ink"],
            linewidth=0.6,
            zorder=4,
        )
    for r in v.itertuples():
        name = r.repo.split("/")[1]
        dx, dy = LABEL_OFFSETS.get(name, (4, 0))
        ax.annotate(
            name + (" (archived)" if r.archived else ""),
            xy=(max(r.months_active, 0.5), r.stars),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=5.8,
            color=COLORS["ink2"],
            va="center",
            ha="left" if dx > 0 else "right",
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.4, 400)
    ax.set_ylim(30, 200000)
    for a in (ax.xaxis, ax.yaxis):
        a.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"{x:,.0f}" if x >= 1 else f"{x:g}")
        )
        a.set_minor_locator(mticker.NullLocator())
    ax.set_xticks([1, 3, 12, 36, 120])
    ax.set_yticks([100, 1000, 10000, 100000])
    ax.set_xlabel("Months active (creation to last push, log)")
    ax.set_ylabel("GitHub stars (log)")
    ax.grid(axis="x", color=COLORS["grid"], lw=0.6)
    ax.set_title("Stars vs time active", loc="left", fontsize=9)
    ax.legend(
        loc="upper left",
        fontsize=6.8,
        handletextpad=0.2,
        title="created",
        title_fontsize=6.8,
    )
    rng = np.random.default_rng(10)
    for i, coh in enumerate(COHORTS):
        g = v[v["cohort"] == coh]
        x = i + rng.uniform(-0.18, 0.18, len(g))
        ax2.scatter(
            x,
            g["viability_score"],
            s=26,
            color=COHORT_COLORS[coh],
            edgecolor=COLORS["ink2"],
            linewidth=0.4,
            zorder=3,
        )
        if len(g):
            med = g["viability_score"].median()
            ax2.plot(
                [i - 0.3, i + 0.3], [med, med], color=COLORS["ink"], lw=1.4, zorder=4
            )
            ax2.text(
                i + 0.32,
                med,
                f"{med:.0f}",
                fontsize=6.8,
                color=COLORS["ink"],
                va="center",
            )
            ax2.text(
                i, -9, f"n={len(g)}", fontsize=6.5, color=COLORS["muted"], ha="center"
            )
    ax2.set_xticks(range(len(COHORTS)))
    ax2.set_xticklabels(
        ["before\nChatGPT", "Dec 2022-\n2024", "2025-\n2026"], fontsize=7
    )
    ax2.set_ylim(-14, 105)
    ax2.set_yticks([0, 25, 50, 75, 100])
    ax2.set_xlim(-0.5, 2.7)
    ax2.set_ylabel("Viability score (0-100)")
    ax2.set_title("Viability by cohort (bar = median)", loc="left", fontsize=9)
    fig.suptitle(
        "Older alternatives hold most stars; young ones are active but thinly staffed",
        x=0.01,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    source_note(
        fig,
        "Viability sample: top-3 rule-matching alternatives per product (>= 50 stars, archived kept; a repository matching two products is shown once). Score = 25 x (recency + release cadence\n+ contributor base + issue closure), see data note. GitHub REST API, retrieved Oct 2026. Stars are attention, not users. Pilot of 12 pre-specified products.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
