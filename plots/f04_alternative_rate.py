"""Figure: "alternative" repositories per 100k new public repositories, monthly (2x2 panels)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_TALL, apply, save, source_note

NAME = "f04_alternative_rate"
PANELS = [
    (
        "A. Any phrase\n(description only)",
        [("alt_union_desc", "Any phrase", SERIES[0])],
        None,
    ),
    (
        "B. Substitute phrases\n(description or README)",
        [
            ("oss_alt", "Open source alt.", SERIES[2]),
            ("selfhost_alt", "Self-hosted alt.", SERIES[3]),
        ],
        None,
    ),
    (
        "C. Star-filtered repositories",
        [
            ("alt_union_s10", "Any phrase", SERIES[0]),
            ("oss_alt_s10", "Open source alt.", SERIES[2]),
            ("selfhost_alt_s10", "Self-hosted alt.", SERIES[3]),
        ],
        None,
    ),
    (
        "D. Any phrase\n(description or README)",
        [("alt_union", "Any phrase", SERIES[0])],
        260,
    ),
]
MARKS = [
    (pd.Timestamp("2022-11-30"), "ChatGPT"),
    (pd.Timestamp("2025-02-24"), "Claude Code"),
]


def _labels(ax, ends, span):
    """Separate two-line end labels by at least 15% of the y-span."""
    ends.sort(key=lambda e: e[0])
    prev = None
    for v, x, text, color in ends:
        y = v if prev is None else max(v, prev + 0.15 * span)
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


def make_figure() -> plt.Figure:
    apply()
    r = pd.read_csv(PROCESSED / "github_repo_trends_rates.csv")
    r["date"] = pd.PeriodIndex(r["month"], freq="M").to_timestamp()
    meta = json.loads(
        (PROCESSED / "github_repo_trends_meta.json").read_text(encoding="utf-8")
    )
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH_TALL[0], 5.0))
    first, last = (r["date"].min(), r["date"].max())
    for i, (ax, (title, lines, clip)) in enumerate(zip(axes.flat, PANELS)):
        top, ends = (0.0, [])
        for key, label, color in lines:
            s = r[r["series"] == key].set_index("date")["rate_per_100k"].sort_index()
            if s.notna().sum() == 0:
                continue
            sm = s.rolling(3, min_periods=2).mean()
            ax.plot(s.index, s.values, color=color, lw=0.6, alpha=0.3)
            ax.plot(sm.index, sm.values, color=color, lw=1.5)
            top = max(top, s.max())
            ends.append(
                [
                    sm.iloc[-1],
                    sm.index[-1],
                    (
                        f"{label}\n{sm.iloc[-1]:.0f}"
                        if sm.iloc[-1] >= 20
                        else f"{label}\n{sm.iloc[-1]:.1f}"
                    ),
                    color,
                ]
            )
        ymax = clip if clip else top * 1.08
        ax.set_ylim(0, ymax)
        _labels(ax, ends, ymax)
        if clip and top > clip:
            s = r[r["series"] == lines[0][0]].set_index("date")["rate_per_100k"]
            pk = s.idxmax()
            ax.annotate(
                f"README-index\nartifact, 2018\n(peak {s.max():,.0f})",
                xy=(pk, clip * 0.97),
                xytext=(0.43, 0.96),
                textcoords="axes fraction",
                fontsize=6.3,
                color=COLORS["muted"],
                va="top",
                arrowprops={"arrowstyle": "-", "color": COLORS["muted"], "lw": 0.6},
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
        ax.set_title(title, fontsize=8.5)
        ax.set_xlim(first, last + pd.DateOffset(months=40))
        ax.spines["bottom"].set_bounds(mdates.date2num(first), mdates.date2num(last))
        ax.set_xticks(
            [pd.Timestamp(f"{y}-01-01") for y in range(2013, last.year + 1, 6)]
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[0, 0].set_ylabel("Repos per 100k new repos")
    axes[1, 0].set_ylabel("Per 100k starred repos")
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    source_note(
        fig,
        f"""Source: GitHub REST search API (/search/repositories; "alternative to" OR "open source alternative" OR "self-hosted alternative"; in:description[,readme]; created: monthly windows).\n3-month trailing mean (thin = monthly); dashed = ChatGPT (2022-11-30), Claude Code preview (2025-02-24). Deleted repos absent. Retrieved {meta['retrieved_last']}.""",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
