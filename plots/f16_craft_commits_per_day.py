"""Figure 16b - commits per day across the Craft suite, with the AI-attributed share."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, apply, save, source_note

STEM = "f16_craft_commits_per_day"
AI = ENTITY_COLORS["open_source"]
APPS = [
    "photocraft",
    "filmcraft",
    "lightcraft",
    "pdfcraft",
    "vectorcraft",
    "effectcraft",
    "designcraft",
    "wordcraft",
    "gridcraft",
    "deckcraft",
    "cadcraft",
    "soundcraft",
]


def load():
    c = pd.read_csv(
        PROCESSED / "16_case_craft_suite_commits.csv",
        usecols=["repo", "author_date", "ai_any"],
        parse_dates=["author_date"],
    )
    t = pd.read_csv(PROCESSED / "16_case_craft_suite_suite_table.csv")
    return (c[c["repo"].isin(APPS)], t)


def make_figure() -> plt.Figure:
    apply()
    c, t = load()
    c["date"] = (
        c["author_date"].dt.tz_convert("UTC").dt.tz_localize(None).dt.normalize()
    )
    days = pd.date_range(c["date"].min(), c["date"].max(), freq="D")
    order = t.sort_values("created_at")["repo"].tolist()
    disp = t.set_index("repo")["display"].to_dict()
    fig, axes = plt.subplots(3, 4, figsize=(7.0, 5.4), sharex=True)
    for ax, repo in zip(axes.ravel(), order):
        g = c[c["repo"] == repo]
        tot = g.groupby("date").size().reindex(days, fill_value=0)
        ai = g[g["ai_any"]].groupby("date").size().reindex(days, fill_value=0)
        ax.bar(days, ai, color=AI, width=0.85, label="AI-attributed", zorder=3)
        ax.bar(
            days,
            tot - ai,
            bottom=ai,
            color=COLORS["context"],
            width=0.85,
            label="other",
            zorder=3,
        )
        share = 100 * g["ai_any"].mean()
        ax.set_title(f"{disp[repo]}", fontsize=8, loc="left", pad=8)
        ax.text(
            0.0,
            1.0,
            f"{len(g):,} commits · {share:.0f}% AI · peak {int(tot.max())}/day",
            transform=ax.transAxes,
            fontsize=5.8,
            color=COLORS["ink2"],
            va="bottom",
        )
        ax.set_ylim(0, tot.max() * 1.08)
        ax.tick_params(axis="y", labelsize=6.5)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%b %#d" if sys.platform == "win32" else "%b %-d")
        )
        ax.tick_params(axis="x", labelsize=6.3)
        ax.grid(axis="y", color=COLORS["grid"], lw=0.5)
        ax.grid(axis="x", visible=False)
    for ax in axes.ravel()[len(order) :]:
        ax.set_visible(False)
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=AI),
        plt.Rectangle((0, 0), 1, 1, color=COLORS["context"]),
    ]
    fig.legend(
        handles,
        ["with AI co-author trailer / AI account", "no AI attribution visible"],
        loc="upper left",
        ncol=2,
        fontsize=7,
        frameon=False,
        bbox_to_anchor=(0.01, 0.965),
    )
    fig.supylabel(
        "commits per day (UTC); y-scale differs by panel",
        fontsize=7.5,
        color=COLORS["ink2"],
        x=0.0,
    )
    fig.tight_layout(rect=(0.0, 0.035, 1, 0.94), h_pad=1.6)
    source_note(
        fig,
        "Source: GitHub REST /commits (default branch) for storytold/*, history up to 2026-10-12T06:06Z. Squash-merged PRs count as one commit, so this is merged work, not agent turns.\nAI flag = Co-authored-by trailer from an AI vendor or an AI author account; a lower bound on AI involvement.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
