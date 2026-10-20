"""Figure 16e - when did the stars arrive? Daily new stars vs the Hacker News threads."""

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

STEM = "f16_craft_star_growth"
OS = ENTITY_COLORS["open_source"]


def daily_gains() -> pd.DataFrame:
    s = pd.read_csv(
        PROCESSED / "16_case_craft_suite_stars_ossinsight.csv", parse_dates=["date"]
    )
    s = s.dropna(subset=["date"])
    days = pd.date_range("2026-09-30", "2026-10-12", freq="D")
    out = {}
    for repo, g in s.groupby("repo"):
        cum = g.set_index("date")["stargazers"].reindex(days).ffill().fillna(0.0)
        out[repo] = cum.diff().fillna(cum)
    return pd.DataFrame(out)


def make_figure() -> plt.Figure:
    apply()
    g = daily_gains()
    hn = pd.read_csv(
        PROCESSED / "16_case_craft_suite_hn_raw.csv", parse_dates=["created_at"]
    )
    hn = (
        hn[(hn["kind"] == "story") & hn["name_match"]]
        .sort_values("points", ascending=False)
        .head(3)
    )
    photo = g["photocraft"]
    rest = g.drop(columns=["photocraft"]).sum(axis=1)
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    x = mdates.date2num(g.index.to_pydatetime())
    ax.bar(x, photo, width=0.9, align="edge", color=OS, label="PhotoCraft", zorder=3)
    ax.bar(
        x,
        rest,
        width=0.9,
        align="edge",
        bottom=photo,
        color=COLORS["context"],
        label="other 11 apps",
        zorder=3,
    )
    ymax = (photo + rest).max()
    for r in hn.sort_values("created_at").itertuples():
        t = r.created_at.tz_convert("UTC").tz_localize(None)
        xv = mdates.date2num(t.to_pydatetime())
        ax.axvline(xv, color=COLORS["ink2"], lw=0.9, ls=":", zorder=4)
        ax.text(
            xv + 0.04,
            ymax * 1.12 - 0.07 * ymax * (0 if r.points >= 150 else 1),
            f"HN {int(r.points)} pts\n{t.day} {t:%b} {t:%H:%M}",
            fontsize=6.4,
            color=COLORS["ink2"],
            va="top",
            ha="left",
        )
    ax.set_ylim(0, ymax * 1.25)
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%b %#d" if sys.platform == "win32" else "%b %-d")
    )
    ax.set_ylabel("new GitHub stars per UTC day")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k" if v else "0")
    )
    ax.grid(axis="x", visible=False)
    peak_day = photo.idxmax()
    ax.set_title(
        f"Attention arrived days after launch: PhotoCraft peaked at {photo.max() / 1000:.1f}k stars on {peak_day.day} {peak_day:%b}",
        loc="left",
        fontsize=9.5,
    )
    ax.legend(loc="upper left", frameon=False, fontsize=7.5, bbox_to_anchor=(0.0, 0.85))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.9, bottom=0.2)
    source_note(
        fig,
        "Source: OSS Insight stargazers/history?per=day (third-party, event-derived, flagged 'degraded' by the provider; its total ends within ~2% of\nGitHub's exact count), HN Algolia API; retrieved 2026-10-12 (12 Oct bar = ~6 h). Stars are attention, not users. Surge and HN threads\ncoincide in time; this does not show the threads caused the stars.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
