"""Figure: license mix of repositories receiving pushes on GitHub, by license family."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_HALF, apply, save, source_note

NAME = "f02_ig_licenses"
FAMILIES = ["Permissive", "Copyleft", "Other / unidentified", "Public domain"]
COLOR = dict(zip(FAMILIES, SERIES[:4]))


def make_figure() -> plt.Figure:
    apply()
    df = pd.read_csv(
        PROCESSED / "innovation_graph_licenses.csv", parse_dates=["quarter_start"]
    )
    df = df[df["level"] == "family"]
    w = df.pivot(index="quarter_start", columns="family", values="share") * 100
    meta = json.loads(
        (PROCESSED / "innovation_graph_meta.json").read_text(encoding="utf-8")
    )
    fig, ax = plt.subplots(figsize=(WIDTH_HALF[0], 2.8))
    ends = []
    for fam in FAMILIES:
        s = w[fam]
        ax.plot(s.index, s.values, color=COLOR[fam], lw=1.5)
        ax.plot(
            [s.index[-1]],
            [s.values[-1]],
            "o",
            color=COLOR[fam],
            ms=3.5,
            markeredgecolor=COLORS["surface"],
            markeredgewidth=0.8,
        )
        ends.append([s.values[-1], s.values[0], fam, s.index[-1]])
    ends.sort(key=lambda e: e[0])
    ypos = [ends[0][0]]
    for e in ends[1:]:
        ypos.append(max(e[0], ypos[-1] + 9))
    for (last, first, fam, x), y in zip(ends, ypos):
        ax.annotate(
            f"{fam}\n{first:.0f}% → {last:.0f}%",
            xy=(x, y),
            xytext=(6, 0),
            textcoords="offset points",
            fontsize=6.5,
            color=COLORS["ink2"],
            va="center",
        )
    ax.axvline(
        pd.Timestamp("2022-11-30"),
        color=COLORS["muted"],
        lw=0.5,
        ls=(0, (3, 3)),
        zorder=0,
    )
    ax.axvline(
        pd.Timestamp("2025-02-24"),
        color=COLORS["muted"],
        lw=0.5,
        ls=(0, (3, 3)),
        zorder=0,
    )
    ax.set_ylim(0, 75)
    ax.set_xlim(pd.Timestamp("2019-12-01"), pd.Timestamp("2029-06-01"))
    ax.spines["bottom"].set_bounds(
        mdates.date2num(pd.Timestamp("2020-01-01")), mdates.date2num(w.index.max())
    )
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (2020, 2022, 2024, 2026)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylabel("% of licensed-repo pushers")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    source_note(
        fig,
        f"Source: GitHub Innovation Graph, licenses.csv;\nSPDX ids grouped by the authors. Retrieved {meta['retrieved']}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
