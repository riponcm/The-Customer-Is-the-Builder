"""Monthly new Stack Overflow questions, 2009 to latest, with the ITS counterfactual."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_FULL, apply, save, source_note

NAME = "f07_so_monthly_questions"
CHATGPT = pd.Timestamp("2022-11-30")


def make_figure() -> plt.Figure:
    apply()
    m = pd.read_csv(PROCESSED / "stackoverflow_monthly.csv")
    fit = pd.read_csv(PROCESSED / "stackoverflow_its_fit.csv")
    m["date"] = pd.PeriodIndex(m["month"], freq="M").to_timestamp()
    fit["date"] = pd.PeriodIndex(fit["month"], freq="M").to_timestamp()
    cf = fit[fit["post"] == 1]
    fig, ax = plt.subplots(figsize=WIDTH_FULL)
    ax.plot(m["date"], m["questions"] / 1000.0, color=SERIES[0], lw=1.8)
    ax.plot(
        cf["date"], cf["counterfactual"] / 1000.0, color=COLORS["ink2"], lw=1.2, ls="--"
    )
    ax.axvline(CHATGPT, color=COLORS["muted"], lw=0.8, ls=":")
    ax.text(
        CHATGPT,
        214,
        " ChatGPT\n released\n 2022-11-30",
        fontsize=7.5,
        color=COLORS["ink2"],
        va="top",
        ha="left",
    )
    last = m.iloc[-1]
    ax.annotate(
        f"Actual: {last['questions']:,.0f}\nin {pd.Timestamp(last['date']):%b %Y}",
        xy=(last["date"], last["questions"] / 1000.0),
        xytext=(-6, 26),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=7.5,
        color=COLORS["ink2"],
        arrowprops=dict(arrowstyle="-", color=COLORS["muted"], lw=0.6),
    )
    c_mid = cf.iloc[len(cf) // 3]
    ax.annotate(
        "Pre-trend counterfactual\n(fit: Jan 2017 to Nov 2022)",
        xy=(c_mid["date"], c_mid["counterfactual"] / 1000.0),
        xytext=(0.68, 0.7),
        textcoords="axes fraction",
        ha="left",
        va="bottom",
        fontsize=7.5,
        color=COLORS["ink2"],
        arrowprops=dict(arrowstyle="-", color=COLORS["muted"], lw=0.6),
    )
    peak = m.loc[m["questions"].idxmax()]
    ax.annotate(
        f"Peak {peak['questions'] / 1000.0:,.0f}k\n({pd.Timestamp(peak['date']):%b %Y})",
        xy=(peak["date"], peak["questions"] / 1000.0),
        xytext=(-8, -2),
        textcoords="offset points",
        ha="right",
        va="top",
        fontsize=7.5,
        color=COLORS["ink2"],
    )
    ax.set_ylim(0, 215)
    ax.set_xlim(pd.Timestamp("2008-10-01"), pd.Timestamp("2027-03-01"))
    ax.set_ylabel("New questions per month (thousands)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}k"))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    retrieved = m["retrieved"].iloc[0] if "retrieved" in m else ""
    source_note(
        fig,
        f"Source: Stack Exchange API v2.3, /questions?site=stackoverflow (total per calendar month; excludes deleted questions). Retrieved {retrieved}.",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
