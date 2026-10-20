"""Figure 10b - when were the open-source alternatives created?"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, apply, save, source_note

STEM = "f10_alternative_timeline"
XMIN, XMAX = (pd.Timestamp("2008-01-01"), pd.Timestamp("2027-01-01"))
CHATGPT = pd.Timestamp("2022-11-30")
YEAR2025 = pd.Timestamp("2025-01-01")
CATEGORY_ORDER = [
    "screen_recording",
    "writing_assistance",
    "pdf_utilities",
    "image_editing",
    "productivity",
    "developer_utilities",
]


def load():
    c = pd.read_csv(
        PROCESSED / "10_open_source_vs_commercial_candidates.csv",
        parse_dates=["created_at"],
    )
    lag = pd.read_csv(
        PROCESSED / "10_open_source_vs_commercial_imitation_lag.csv",
        parse_dates=["launch_date"],
    )
    return (c, lag)


def _size(stars):
    return 6 + 260 * np.sqrt(np.asarray(stars, dtype=float) / 80000)


def make_figure() -> plt.Figure:
    apply()
    c, lag = load()
    lag["cat_rank"] = lag["category"].map({k: i for i, k in enumerate(CATEGORY_ORDER)})
    order = lag.sort_values(["cat_rank"], kind="stable")["product"].tolist()
    ypos = {p: i for i, p in enumerate(order)}
    pts = c[c["text_match"] & c["rule_min_stars"]].copy()
    pts["y"] = pts["product"].map(ypos)
    fig, ax = plt.subplots(figsize=(7.0, 5.2))
    oc = ENTITY_COLORS["open_source"]
    inc = pts[~pts["archived"]]
    arc = pts[pts["archived"]]
    ax.scatter(
        inc["created_at"],
        inc["y"],
        s=_size(inc["stars"]),
        color=oc,
        alpha=0.55,
        edgecolor=COLORS["surface"],
        linewidth=0.5,
        zorder=3,
    )
    ax.scatter(
        arc["created_at"],
        arc["y"],
        s=_size(arc["stars"]),
        facecolor="none",
        edgecolor=oc,
        linewidth=1.0,
        zorder=3,
    )
    for p, g in pts.groupby("product"):
        top = g.sort_values("stars").iloc[-1]
        late = top["created_at"] > pd.Timestamp("2025-06-01")
        if top["stars"] >= 1000:
            ax.annotate(
                f"{top['repo'].split('/')[1]} ({top['stars'] / 1000:.0f}k)",
                xy=(top["created_at"], top["y"]),
                xytext=(4 if late else 0, 7.5),
                textcoords="offset points",
                fontsize=6.3,
                color=COLORS["ink2"],
                ha="right" if late else "center",
                va="bottom",
            )
    for r in lag.itertuples():
        y = ypos[r.product]
        if r.launch_date >= XMIN:
            ax.scatter(
                [r.launch_date],
                [y],
                marker="D",
                s=22,
                color=ENTITY_COLORS["commercial"],
                zorder=4,
            )
        else:
            ax.annotate(
                f"launched {r.launch_year} ←",
                xy=(XMIN, y),
                xytext=(3, 0),
                textcoords="offset points",
                fontsize=6.3,
                color=ENTITY_COLORS["commercial"],
                va="center",
                ha="left",
            )
    for d, t, align in (
        (CHATGPT, "ChatGPT\n(Nov 2022)", "right"),
        (YEAR2025, "2025: agentic\ncoding tools", "left"),
    ):
        ax.axvline(d, color=COLORS["muted"], lw=0.8, ls=":", zorder=1)
        ax.text(d, -2.6, t, fontsize=6.5, color=COLORS["ink2"], ha=align, va="top")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=7.5)
    ax.set_ylim(len(order) - 0.5, -2.9)
    ax.set_xlim(XMIN, XMAX)
    ax.grid(axis="x", color=COLORS["grid"], lw=0.6)
    ax.grid(axis="y", visible=False)
    cats = lag.set_index("product").loc[order, "category"].tolist()
    for i in range(1, len(order)):
        if cats[i] != cats[i - 1]:
            ax.axhline(i - 0.5, color=COLORS["axis"], lw=0.5)
    kx = 0.77
    fig.text(
        kx,
        0.8,
        "Alternative repository",
        fontsize=7,
        color=COLORS["ink"],
        fontweight="bold",
    )
    for s_, lab, yy in (
        (100, "100 stars", 0.74),
        (1000, "1k stars", 0.685),
        (10000, "10k stars", 0.605),
        (50000, "50k stars", 0.49),
    ):
        fig.add_artist(
            plt.Line2D(
                [kx + 0.02],
                [yy],
                marker="o",
                ls="none",
                color=oc,
                alpha=0.55,
                markersize=np.sqrt(_size([s_])[0]),
                transform=fig.transFigure,
            )
        )
        fig.text(kx + 0.06, yy, lab, fontsize=6.8, va="center", color=COLORS["ink2"])
    fig.add_artist(
        plt.Line2D(
            [kx + 0.02],
            [0.39],
            marker="o",
            ls="none",
            mfc="none",
            mec=oc,
            mew=1.0,
            markersize=7,
            transform=fig.transFigure,
        )
    )
    fig.text(
        kx + 0.06, 0.39, "archived", fontsize=6.8, va="center", color=COLORS["ink2"]
    )
    fig.add_artist(
        plt.Line2D(
            [kx + 0.02],
            [0.33],
            marker="D",
            ls="none",
            color=ENTITY_COLORS["commercial"],
            markersize=4.5,
            transform=fig.transFigure,
        )
    )
    fig.text(
        kx + 0.06,
        0.33,
        "commercial launch",
        fontsize=6.8,
        va="center",
        color=COLORS["ink2"],
    )
    n_post = int((pts.drop_duplicates("repo")["created_at"] >= CHATGPT).sum())
    n_all = int(pts["repo"].nunique())
    ax.set_xlabel("Repository creation date")
    fig.subplots_adjust(left=0.15, right=0.82, top=0.93, bottom=0.17)
    source_note(
        fig,
        "Dots: GitHub repositories whose description positions them as an alternative to the product (rule in data note), >= 50 stars; area ~ current stars.\nSurvivorship: only repositories still on GitHub in Oct 2026 can appear. Stars are attention, not users. Pilot of 12 pre-specified products.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
