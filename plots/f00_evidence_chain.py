"""Figure 1: leading indicators (top row) versus lagging indicators (bottom row)."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from src.paths import PROCESSED
from src.style import (
    COLORS,
    ENTITY_COLORS,
    SERIES,
    WIDTH_TALL,
    apply,
    save,
    source_note,
)

NAME = "f00_evidence_chain"
AGENTS = pd.Timestamp("2025-02-24")
LEAD, LAG = (SERIES[0], COLORS["ink2"])


def _mark_agents(ax):
    ax.axvline(AGENTS, color=COLORS["muted"], lw=0.8, ls=":")


def _tag(ax, text, color):
    ax.text(
        0.0,
        1.17,
        text.upper(),
        transform=ax.transAxes,
        fontsize=6.5,
        color=color,
        fontweight="bold",
        va="bottom",
    )


def _years(ax, step=2):
    ax.xaxis.set_major_locator(mdates.YearLocator(step))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def panel_capability(ax):
    d = pd.read_csv(
        PROCESSED / "agent_capability_cost_metr_horizons.csv",
        parse_dates=["release_date"],
    )
    d = d[d.is_sota & (d.release_date >= "2022-01-01")]
    ax.plot(d.release_date, d.p50_min / 60, "o-", color=LEAD, ms=3, lw=1.4)
    ax.set_yscale("log")
    ax.set_yticks([1 / 60, 1, 8])
    ax.set_yticklabels(["1 min", "1 hour", "1 day"])
    ax.minorticks_off()
    _mark_agents(ax)
    _years(ax)
    ax.set_title("A. Task length agents complete")
    _tag(ax, "Leading", LEAD)


def panel_building(ax):
    m = pd.read_csv(PROCESSED / "github_repo_trends_monthly.csv")
    m = m[m.series == "all"].copy()
    m["month"] = pd.to_datetime(m["month"])
    m = m[m.month >= "2018-01-01"].set_index("month")["count"]
    base = m["2019"].mean()
    idx = (m / base * 100).rolling(3).mean()
    ax.plot(idx.index, idx, color=LEAD, lw=1.6)
    _mark_agents(ax)
    _years(ax, 4)
    ax.set_ylabel("Index, 2019 = 100")
    ax.set_title("B. New public GitHub repositories")
    _tag(ax, "Leading", LEAD)


def panel_alternatives(ax):
    r = pd.read_csv(PROCESSED / "github_repo_trends_rates.csv")
    r = r[r.series == "oss_alt"].copy()
    r["month"] = pd.to_datetime(r["month"])
    r = r[r.month >= "2018-01-01"].set_index("month")["rate_per_100k"].rolling(3).mean()
    ax.plot(r.index, r, color=LEAD, lw=1.6)
    _mark_agents(ax)
    _years(ax, 4)
    ax.set_ylim(0, None)
    ax.set_ylabel("Per 100k new repositories")
    ax.set_title('C. "Open source alternative" repos')
    _tag(ax, "Leading", LEAD)


def panel_spending(ax):
    b = pd.read_csv(PROCESSED / "bea_software_investment_annual.csv")
    b = b[(b.measure == "share_of_software_nominal_pct") & (b.year >= 2010)]
    for typ, label, dy in (
        ("prepackaged", "Bought", 6),
        ("own_account", "Built in-house", -12),
    ):
        s = b[b.type == typ]
        ax.plot(s.year, s.value, color=ENTITY_COLORS[typ], lw=1.6)
        ax.annotate(
            label,
            (s.year.iloc[-1], s.value.iloc[-1]),
            xytext=(-2, dy),
            textcoords="offset points",
            fontsize=7,
            color=COLORS["ink2"],
            ha="right",
        )
    ax.axvline(2025.15, color=COLORS["muted"], lw=0.8, ls=":")
    ax.set_ylim(0, 60)
    ax.set_xticks([2010, 2015, 2020, 2025])
    ax.set_ylabel("% of US software investment")
    ax.set_title("D. Who builds firms' software")
    _tag(ax, "Lagging", LAG)


def panel_adoption(ax):
    h = pd.read_csv(
        PROCESSED / "10_open_source_vs_commercial_homebrew_history.csv",
        parse_dates=["window_end"],
    )
    live = pd.read_csv(
        PROCESSED / "10_open_source_vs_commercial_homebrew_365d.csv",
        parse_dates=["window_end"],
    )
    for pkg, side, label, at, off in (
        ("postman", "commercial", "Postman", 0, (4, 8)),
        ("bruno", "open_source", "Bruno (open source)", -1, (-4, -14)),
    ):
        s = pd.concat(
            [
                h[(h.kind == "cask") & (h.package == pkg)][
                    ["window_end", "installs_365d"]
                ],
                live[(live.kind == "cask") & (live.package == pkg)][
                    ["window_end", "installs_365d"]
                ],
            ]
        )
        s = s.sort_values("window_end")
        ax.plot(
            s.window_end,
            s.installs_365d / 1000,
            "o-",
            ms=3,
            lw=1.6,
            color=ENTITY_COLORS[side],
        )
        ax.annotate(
            label,
            (s.window_end.iloc[at], s.installs_365d.iloc[at] / 1000),
            xytext=off,
            textcoords="offset points",
            fontsize=7,
            color=COLORS["ink2"],
            ha="left" if at == 0 else "right",
        )
    _mark_agents(ax)
    _years(ax, 2)
    ax.set_ylim(0, None)
    ax.set_ylabel("Installs per year (thousands)")
    ax.set_title("E. Postman vs Bruno installs")
    _tag(ax, "Lagging", LAG)


def panel_intent(ax):
    import json

    nums = json.loads((PROCESSED / "summary_values.json").read_text(encoding="utf-8"))
    rows = [
        ("Small scripts", nums["SoSurveySmallScripts"]),
        ("Team internal tools", nums["SoSurveyInternalTools"]),
        ("Replacing paid vendors", nums["SoSurveyReplacingVendors"]),
    ]
    labels, vals = zip(*rows)
    y = range(len(rows))[::-1]
    ax.barh(
        list(y), vals, color=[COLORS["context"], COLORS["context"], LAG], height=0.6
    )
    for yi, v in zip(y, vals):
        ax.text(v + 2, yi, f"{v:.0f}%", va="center", fontsize=7, color=COLORS["ink2"])
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("% of in-house builders, 2026")
    ax.set_title("F. Why developers build in-house")
    _tag(ax, "Lagging", LAG)


def make_figure():
    apply()
    fig, axes = plt.subplots(2, 3, figsize=(WIDTH_TALL[0], 5.4))
    for fn, ax in zip(
        (
            panel_capability,
            panel_building,
            panel_alternatives,
            panel_spending,
            panel_adoption,
            panel_intent,
        ),
        axes.flat,
    ):
        fn(ax)
        ax.title.set_fontsize(8.5)
    fig.tight_layout(h_pad=2.2, w_pad=1.2)
    source_note(
        fig,
        "Sources: METR; GitHub search API; BEA NIPA 5.6.5; Homebrew analytics; Stack Overflow Developer Survey 2026. Dotted line: Feb 2025, coding agents arrive. Retrieved 2026-10-12.",
    )
    fig.subplots_adjust(bottom=0.12)
    return fig


def main():
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
