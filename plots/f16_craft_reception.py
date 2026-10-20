"""Figure 16d - reception: stars, release-asset downloads, and Hacker News points."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, SERIES, apply, save, source_note

STEM = "f16_craft_reception"
OS = ENTITY_COLORS["open_source"]


def _short(s: str, n: int = 58) -> str:
    s = " ".join(str(s).replace("–", "-").replace("�", "-").split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def make_figure() -> plt.Figure:
    apply()
    t = (
        pd.read_csv(PROCESSED / "16_case_craft_suite_suite_table.csv")
        .sort_values("stars", ascending=True)
        .reset_index(drop=True)
    )
    hn = pd.read_csv(
        PROCESSED / "16_case_craft_suite_hn_raw.csv", parse_dates=["created_at"]
    )
    hn = (
        hn[(hn["kind"] == "story") & hn["name_match"]]
        .drop_duplicates("object_id")
        .sort_values("points", ascending=False)
    )
    hn = hn.head(10).iloc[::-1].reset_index(drop=True)
    fig = plt.figure(figsize=(7.0, 6.2))
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.15, 1.0],
        hspace=0.32,
        wspace=0.08,
        left=0.17,
        right=0.97,
        top=0.9,
        bottom=0.12,
    )
    a = fig.add_subplot(gs[0, 0])
    b = fig.add_subplot(gs[0, 1], sharey=a)
    c = fig.add_subplot(gs[1, :])
    y = np.arange(len(t))
    a.barh(y, t["stars"] / 1000, color=OS, alpha=0.85, height=0.62, zorder=3)
    for yy, v in zip(y, t["stars"]):
        a.text(
            v / 1000 + 0.8,
            yy,
            f"{v / 1000:.1f}k",
            va="center",
            fontsize=6.8,
            color=COLORS["ink2"],
        )
    a.set_yticks(y)
    a.set_yticklabels(t["display"], fontsize=7.8)
    a.set_xlim(0, t["stars"].max() / 1000 * 1.2)
    a.set_title("(a) GitHub stars (thousands)", fontsize=8.5)
    a.grid(axis="x", color=COLORS["grid"], lw=0.6)
    a.grid(axis="y", visible=False)
    b.barh(
        y,
        t["downloads_all_assets"] / 1000,
        color=SERIES[0],
        alpha=0.85,
        height=0.62,
        zorder=3,
    )
    for yy, v in zip(y, t["downloads_all_assets"]):
        b.text(
            v / 1000 + 12,
            yy,
            f"{v / 1000:,.0f}k",
            va="center",
            fontsize=6.8,
            color=COLORS["ink2"],
        )
    b.set_xlim(0, t["downloads_all_assets"].max() / 1000 * 1.25)
    b.set_title("(b) release-asset downloads (thousands)", fontsize=8.5)
    b.tick_params(axis="y", left=False, labelleft=False)
    b.grid(axis="x", color=COLORS["grid"], lw=0.6)
    b.grid(axis="y", visible=False)
    yy = np.arange(len(hn))
    c.barh(yy, hn["points"], color=SERIES[2], alpha=0.9, height=0.62, zorder=3)
    for i, r in hn.iterrows():
        c.text(
            r["points"] + 2,
            i,
            f"{int(r['points'])} pts · {int(r['num_comments'] if not pd.isna(r['num_comments']) else 0)} comment{('' if r['num_comments'] == 1 else 's')} · {r['created_at']:%b} {r['created_at'].day}",
            va="center",
            fontsize=6.5,
            color=COLORS["ink2"],
        )
    c.set_yticks(yy)
    c.set_yticklabels([_short(x) for x in hn["title"]], fontsize=6.6)
    c.set_xlim(0, hn["points"].max() * 1.5)
    c.set_title(
        f"(c) Hacker News stories naming the suite (top {len(hn)} of {int(((pd.read_csv(PROCESSED / '16_case_craft_suite_hn_raw.csv')['kind'] == 'story') & pd.read_csv(PROCESSED / '16_case_craft_suite_hn_raw.csv')['name_match']).sum())}; points)",
        fontsize=8.5,
    )
    c.grid(axis="x", color=COLORS["grid"], lw=0.6)
    c.grid(axis="y", visible=False)
    c.text(
        1.0,
        -0.2,
        "Reddit: scores not collected (automated access blocked)",
        transform=c.transAxes,
        fontsize=6.5,
        color=COLORS["muted"],
        ha="right",
    )
    fig.suptitle(
        f"{t['stars'].sum() / 1000:,.0f}k stars and {t['downloads_all_assets'].sum() / 1000000.0:.1f}M release downloads in under two weeks",
        x=0.01,
        y=0.985,
        ha="left",
        fontsize=9.5,
        fontweight="bold",
    )
    source_note(
        fig,
        "Source: GitHub REST API (stars, release assets) and Hacker News Algolia API, retrieved 2026-10-12 UTC. Stars ≠ users; downloads include auto-updates/metadata and one person can fetch several files.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
