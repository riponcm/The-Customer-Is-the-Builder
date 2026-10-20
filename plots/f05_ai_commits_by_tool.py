"""Figure: public commits carrying a default AI-tool attribution, per month, by tool (small multiples, log scale)."""

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
from src.style import COLORS, SERIES, WIDTH_TALL, apply, save, source_note

NAME = "f05_ai_commits_by_tool"
TOOLS = [
    "Claude Code",
    "GitHub Copilot",
    "Cursor",
    "Aider",
    "Google Jules",
    "Devin",
    "OpenAI Codex",
    "Amp",
]
COLOR = dict(zip(TOOLS, SERIES))
CC_PREVIEW = pd.Timestamp("2025-02-24")


def _fmt(v: float) -> str:
    return (
        f"{v / 1000000.0:.1f}M"
        if v >= 1000000.0
        else f"{v / 1000.0:.0f}k" if v >= 1000.0 else f"{v:.0f}"
    )


def make_figure() -> plt.Figure:
    apply()
    d = pd.read_csv(PROCESSED / "ai_attribution_commits_by_tool.csv")
    d["date"] = pd.PeriodIndex(d["month"], freq="M").to_timestamp()
    d["commits"] = d["commits"].where(d["commits"] >= 1)
    meta = json.loads(
        (PROCESSED / "ai_attribution_commits_meta.json").read_text(encoding="utf-8")
    )
    first, last = (d["date"].min(), d["date"].max())
    fig, axes = plt.subplots(
        2, 4, figsize=(WIDTH_TALL[0], 4.3), sharex=True, sharey=True
    )
    for ax, tool in zip(axes.flat, TOOLS):
        for other in TOOLS:
            if other == tool:
                continue
            o = d[d["tool"] == other].set_index("date")["commits"]
            ax.plot(o.index, o.values, color=COLORS["grid"], lw=0.8, zorder=1)
        s = d[d["tool"] == tool].set_index("date").sort_index()
        ax.plot(s.index, s["commits"], color=COLOR[tool], lw=1.6, zorder=3)
        lb = s[s["lower_bound"].astype(bool) & (s["commits"] >= 1000)]
        ax.plot(
            lb.index,
            lb["commits"],
            "o",
            ms=3.2,
            mfc=COLORS["surface"],
            mec=COLOR[tool],
            mew=0.9,
            zorder=4,
        )
        ax.axvline(CC_PREVIEW, color=COLORS["muted"], lw=0.5, ls=(0, (3, 3)), zorder=0)
        lastv = s["commits"].dropna()
        ax.set_title(
            f"{tool}  {_fmt(lastv.iloc[-1])}" if len(lastv) else tool, fontsize=8.5
        )
        ax.set_yscale("log")
        ax.set_ylim(1, 50000000.0)
        ax.yaxis.set_major_locator(mticker.LogLocator(base=10, numticks=10))
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(
                lambda v, _: {
                    1: "1",
                    100.0: "100",
                    10000.0: "10k",
                    1000000.0: "1M",
                }.get(v, "")
            )
        )
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xlim(first - pd.DateOffset(days=15), last + pd.DateOffset(days=15))
        ax.set_xticks(
            [pd.Timestamp(f"{y}-01-01") for y in range(first.year, last.year + 1)]
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("'%y"))
    for ax in axes[:, 0]:
        ax.set_ylabel("Commits / month")
    fig.suptitle(
        "Public commits with a default AI-tool attribution, by tool (lower bound; title = latest month)",
        x=0.01,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    source_note(
        fig,
        f"Source: GitHub REST commit search (/search/commits, total_count; committer-date monthly windows; default branches of public repos). Trailers / bot authors per tool in data notes;\nusers can disable or strip them. Hollow = incomplete search result, >=1k (lower bound). Dashed = Claude Code preview (2025-02-24). Retrieved {meta['retrieved_last']}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
