"""Figure: "clone" repositories per 100k new public repositories, monthly."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_FULL, apply, save, source_note

NAME = "f04_clone_rate"
PANELS = [
    (
        "All new repositories",
        [
            ("clone_of", '"clone of"', SERIES[0]),
            ("clone_of_desc", '"clone of" (descr.)', SERIES[1]),
            ("oss_clone", '"open source clone"', SERIES[2]),
        ],
    ),
    (
        "Repositories with ≥10 stars",
        [
            ("clone_of_s10", '"clone of"', SERIES[0]),
            ("oss_clone_s10", '"open source clone"', SERIES[2]),
        ],
    ),
]
MARKS = [
    (pd.Timestamp("2022-11-30"), "ChatGPT"),
    (pd.Timestamp("2025-02-24"), "Claude Code"),
]


def make_figure() -> plt.Figure:
    apply()
    r = pd.read_csv(PROCESSED / "github_repo_trends_rates.csv")
    r["date"] = pd.PeriodIndex(r["month"], freq="M").to_timestamp()
    meta = json.loads(
        (PROCESSED / "github_repo_trends_meta.json").read_text(encoding="utf-8")
    )
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_FULL[0], 3.4))
    first, last = (r["date"].min(), r["date"].max())
    for i, (ax, (title, lines)) in enumerate(zip(axes, PANELS)):
        top, ends = (0.0, [])
        for key, label, color in lines:
            s = r[r["series"] == key].set_index("date")["rate_per_100k"].sort_index()
            sm = s.rolling(3, min_periods=2).mean()
            ax.plot(s.index, s.values, color=color, lw=0.6, alpha=0.3)
            ax.plot(sm.index, sm.values, color=color, lw=1.5)
            top = max(top, s.max())
            ends.append(
                [sm.iloc[-1], sm.index[-1], f"{label} {sm.iloc[-1]:.0f}", color]
            )
        ymax = top * 1.05
        ax.set_ylim(0, ymax)
        ends.sort(key=lambda e: e[0])
        prev = None
        for v, x, text, color in ends:
            y = v if prev is None else max(v, prev + 0.07 * ymax)
            prev = y
            ax.plot([x], [v], "o", color=color, ms=3, mec=COLORS["surface"], mew=0.7)
            ax.annotate(
                text,
                xy=(x, y),
                xytext=(5, 0),
                textcoords="offset points",
                fontsize=6.8,
                color=COLORS["ink2"],
                va="center",
            )
        for x, lab in MARKS:
            ax.axvline(x, color=COLORS["muted"], lw=0.6, ls=(0, (3, 3)), zorder=0)
            if i == 0:
                ax.text(
                    x - pd.Timedelta(days=30),
                    0.97,
                    lab,
                    transform=ax.get_xaxis_transform(),
                    fontsize=6.3,
                    color=COLORS["muted"],
                    ha="right",
                    va="top",
                    rotation=90,
                )
        ax.set_title(title, fontsize=9)
        ax.set_xlim(first, last + pd.DateOffset(months=48))
        ax.spines["bottom"].set_bounds(mdates.date2num(first), mdates.date2num(last))
        ax.set_xticks(
            [pd.Timestamp(f"{y}-01-01") for y in range(2013, last.year + 1, 3)]
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[0].set_ylabel("Repos per 100k new repos")
    axes[1].set_ylabel("Per 100k ≥10-star repos")
    fig.suptitle(
        'Repositories describing themselves as a "clone"',
        x=0.01,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.98))
    source_note(
        fig,
        f"""Source: GitHub REST search API (/search/repositories; "clone of", "open source clone" in:description[,readme]; created: monthly windows).\n3-month trailing mean (thin = monthly); dashed = ChatGPT, Claude Code preview. Deleted repos absent. Retrieved {meta['retrieved_last']}.""",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
