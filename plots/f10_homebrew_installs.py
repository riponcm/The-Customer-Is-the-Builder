"""Figure 10e - Homebrew 365-day installs: commercial cask vs rule-included open-source alternatives."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, apply, save, source_note

STEM = "f10_homebrew_installs"
PANELS = ["Postman", "Notion", "Loom", "Adobe Photoshop"]
STYLES = ["-", (0, (3, 1.6))]
DISPLAY_NAMES = {
    "adobe-creative-cloud": "Creative Cloud",
    "robbietilton-compositor": "Compositor",
}


def load() -> pd.DataFrame:
    cur = pd.read_csv(PROCESSED / "10_open_source_vs_commercial_homebrew_365d.csv")
    hist = pd.read_csv(PROCESSED / "10_open_source_vs_commercial_homebrew_history.csv")
    pk = cur[cur["kind"] == "cask"].drop_duplicates(["product", "package"])[
        ["product", "side", "name", "package"]
    ]
    h = hist[(hist["kind"] == "cask") & hist["present"]][
        ["package", "window_end", "installs_365d"]
    ]
    c = cur[(cur["kind"] == "cask") & cur["in_analytics"]][
        ["package", "window_end", "installs_365d"]
    ]
    pts = pd.concat([h, c.drop_duplicates()], ignore_index=True)
    pts["window_end"] = pd.to_datetime(pts["window_end"])
    return pk.merge(pts, on="package").sort_values("window_end")


def make_figure() -> plt.Figure:
    apply()
    d = load()
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.8), sharex=True)
    for ax, prod in zip(axes.ravel(), PANELS):
        g = d[d["product"] == prod]
        ends = []
        for side in ("commercial", "open_source"):
            for j, (pkg, s) in enumerate(
                g[g["side"] == side].groupby("package", sort=False)
            ):
                ax.plot(
                    s["window_end"],
                    s["installs_365d"],
                    color=ENTITY_COLORS[side],
                    lw=1.5,
                    ls=STYLES[j % 2],
                    marker="o",
                    ms=3.2,
                )
                last = s.iloc[-1]
                ends.append((last["window_end"], last["installs_365d"], pkg, side))
        ends.sort(key=lambda e: e[1])
        ly = [np.log10(max(e[1], 1)) for e in ends]
        for i in range(1, len(ly)):
            ly[i] = max(ly[i], ly[i - 1] + 0.45)
        for (x, y, pkg, side), yy in zip(ends, ly):
            name = DISPLAY_NAMES.get(pkg, pkg)
            ax.annotate(
                f"{name} {y / 1000:,.1f}k" if y >= 1000 else f"{name} {y:,.0f}",
                xy=(x, 10**yy),
                xytext=(5, 0),
                textcoords="offset points",
                fontsize=6.6,
                color=ENTITY_COLORS[side],
                va="center",
            )
        ax.set_yscale("log")
        ax.set_ylim(1, 400000)
        ax.set_yticks([1, 10, 100, 1000, 10000, 100000])
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(
                lambda v, _: f"{v / 1000:g}k" if v >= 1000 else f"{v:g}"
            )
        )
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.set_title(prod, loc="left", fontsize=8.5)
        ax.set_xlim(pd.Timestamp("2019-01-01"), pd.Timestamp("2028-06-30"))
        ax.set_xticks(pd.to_datetime([f"{y}-01-01" for y in (2020, 2022, 2024, 2026)]))
        ax.set_xticklabels(["2020", "2022", "2024", "2026"])
        ax.tick_params(labelsize=7)
        ax.axvline(
            pd.Timestamp("2022-11-30"), color=COLORS["muted"], lw=0.7, ls=":", zorder=0
        )
    for ax in axes[:, 0]:
        ax.set_ylabel("Installs, trailing 365 days", fontsize=7.5)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    source_note(
        fig,
        "Homebrew cask-install analytics (formulae.brew.sh), live file Oct 2026 plus Wayback Machine captures (only years the archive served intact). Opt-in macOS Homebrew users only;\nadobe-creative-cloud stands in for Photoshop. Installs are not paid seats or active users. Dotted line: ChatGPT. Pilot of 12 pre-specified products.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
