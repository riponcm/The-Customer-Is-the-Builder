"""Figure 16a - twelve commercial-software "reimplementations" appear in about a week."""

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

STEM = "f16_craft_suite_timeline"
XMIN, XMAX = (pd.Timestamp("2026-09-25"), pd.Timestamp("2026-10-14"))
OS = ENTITY_COLORS["open_source"]


def _size(stars):
    return 8 + 330 * np.asarray(stars, dtype=float) / 50000.0


def load() -> pd.DataFrame:
    t = pd.read_csv(
        PROCESSED / "16_case_craft_suite_suite_table.csv",
        parse_dates=["created_at", "first_commit", "last_commit"],
    )
    hn = pd.read_csv(
        PROCESSED / "16_case_craft_suite_hn_threads.csv", parse_dates=["created_at"]
    )
    return (t, hn)


def make_figure() -> plt.Figure:
    apply()
    t, hn = load()
    t = t.sort_values(["created_at", "stars"], ascending=[True, False]).reset_index(
        drop=True
    )
    t["y"] = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    for r in t.itertuples():
        c0 = r.created_at.tz_localize(None) if r.created_at.tzinfo else r.created_at
        c1 = r.last_commit.tz_localize(None) if r.last_commit.tzinfo else r.last_commit
        ax.plot(
            [c0, c1],
            [r.y, r.y],
            color=OS,
            lw=3.2,
            alpha=0.55,
            solid_capstyle="butt",
            zorder=2,
        )
        ax.scatter(
            [c0],
            [r.y],
            marker="|",
            s=90,
            color=COLORS["ink2"],
            zorder=4,
            linewidths=1.2,
        )
        f0 = (
            r.first_commit.tz_localize(None)
            if r.first_commit.tzinfo
            else r.first_commit
        )
        if c0 - f0 > pd.Timedelta(hours=1):
            ax.plot(
                [f0, c0],
                [r.y, r.y],
                color=COLORS["ink2"],
                lw=0.9,
                ls=(0, (1, 1.5)),
                zorder=3,
            )
            ax.scatter(
                [f0],
                [r.y],
                s=14,
                facecolor=COLORS["surface"],
                edgecolor=COLORS["ink2"],
                linewidth=0.9,
                zorder=4,
            )
        ax.scatter(
            [c1],
            [r.y],
            s=_size([r.stars]),
            color=OS,
            alpha=0.9,
            edgecolor=COLORS["surface"],
            linewidth=0.8,
            zorder=5,
        )
    for r in t.itertuples():
        c1 = r.last_commit.tz_localize(None) if r.last_commit.tzinfo else r.last_commit
        rad = np.sqrt(_size([r.stars])[0] / np.pi) * 1.0
        ax.annotate(
            f"{r.stars / 1000:.1f}k",
            xy=(c1, r.y),
            xytext=(rad + 3, 0),
            textcoords="offset points",
            fontsize=6.8,
            color=COLORS["ink2"],
            va="center",
            ha="left",
        )
    big = hn[hn["points"] >= 100].sort_values("created_at")
    if len(big):
        d = (
            big["created_at"].iloc[0].tz_localize(None)
            if big["created_at"].iloc[0].tzinfo
            else big["created_at"].iloc[0]
        )
        ax.axvline(d, color=COLORS["muted"], lw=0.9, ls=":", zorder=1)
        ax.text(
            d,
            -0.95,
            f"Hacker News thread\n({int(big['points'].iloc[0])} pts, {d.day} {d:%b} {d:%H:%M} UTC)",
            fontsize=6.5,
            color=COLORS["ink2"],
            ha="center",
            va="bottom",
        )
    ax.set_yticks(t["y"])
    ax.set_yticklabels(
        [f"{r.display} → {r.incumbent_product}" for r in t.itertuples()], fontsize=7.4
    )
    ax.set_ylim(len(t) - 0.4, -1.5)
    ax.set_xlim(XMIN, XMAX)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%b %-d" if sys.platform != "win32" else "%b %#d")
    )
    ax.grid(axis="x", color=COLORS["grid"], lw=0.6)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("2026 (UTC)")
    ax.tick_params(axis="x", labelsize=7.5)
    ax.text(
        0.02,
        0.31,
        "marker area = current stars",
        transform=ax.transAxes,
        fontsize=6.8,
        color=COLORS["ink"],
        fontweight="bold",
    )
    for x_, s_, lab in ((0.03, 1000, "1k"), (0.15, 10000, "10k"), (0.27, 50000, "50k")):
        ax.scatter(
            [x_],
            [0.235],
            s=_size([s_])[0],
            color=OS,
            alpha=0.9,
            transform=ax.transAxes,
            clip_on=False,
        )
        ax.text(
            x_ + (0.045 if s_ == 50000 else 0.025),
            0.235,
            lab,
            transform=ax.transAxes,
            fontsize=6.8,
            va="center",
            color=COLORS["ink2"],
        )
    ax.plot(
        [0.02, 0.05],
        [0.16, 0.16],
        color=OS,
        lw=3.2,
        alpha=0.55,
        transform=ax.transAxes,
        solid_capstyle="butt",
    )
    ax.text(
        0.065,
        0.16,
        "creation → latest commit",
        transform=ax.transAxes,
        fontsize=6.8,
        va="center",
        color=COLORS["ink2"],
    )
    ax.scatter(
        [0.035],
        [0.1],
        s=14,
        facecolor=COLORS["surface"],
        edgecolor=COLORS["ink2"],
        linewidth=0.9,
        transform=ax.transAxes,
    )
    ax.text(
        0.065,
        0.1,
        "first commit (history pre-dates the repository)",
        transform=ax.transAxes,
        fontsize=6.8,
        va="center",
        color=COLORS["ink2"],
    )
    fig.subplots_adjust(left=0.3, right=0.97, top=0.92, bottom=0.17)
    source_note(
        fig,
        "Bar: repository creation (tick) to latest commit on the default branch (circle). Source: GitHub REST API (storytold/*), retrieved 2026-10-12 UTC; HN: Algolia API.\nStars are a one-click bookmark, not users; 'clean-room' and 'reimplementation' are the authors' claims. First commits of several repos predate creation (imported history).",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
