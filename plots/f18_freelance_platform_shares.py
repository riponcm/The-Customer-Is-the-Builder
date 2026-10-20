"""Freelance platform share prices with the broad US equity market as context."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, apply, label_end, save, source_note

NAME = "f18_freelance_platform_shares"
COLORS_BY_TICKER = {"UPWK": SERIES[0], "FVRR": SERIES[1], "SPY": COLORS["context"]}


def make_figure():
    apply()
    prices = pd.read_csv(
        PROCESSED / "freelance_platforms_prices.csv", parse_dates=["month"]
    )
    wide = prices.pivot(index="month", columns="ticker", values="adjusted_close_usd")
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.45))
    panels = [
        (axes[0], pd.Timestamp("2021-01-01"), "A. Since January 2021", True),
        (axes[1], pd.Timestamp("2025-02-01"), "B. Since coding agents arrived", False),
    ]
    for ax, base, title, use_log in panels:
        subset = wide.loc[base:]
        indexed = 100 * subset / subset.iloc[0]
        for ticker in ("SPY", "UPWK", "FVRR"):
            color = COLORS_BY_TICKER[ticker]
            ax.plot(
                indexed.index,
                indexed[ticker],
                color=color,
                lw=1.9,
                zorder=2 if ticker != "SPY" else 1,
            )
            label_end(
                ax, indexed.index[-1], indexed[ticker].iloc[-1], ticker, color, dx=3
            )
        ax.axhline(100, lw=0.7, color=COLORS["grid"])
        if base.year == 2021:
            ax.axvline(
                pd.Timestamp("2025-02-01"), lw=0.8, ls="--", color=COLORS["muted"]
            )
        if use_log:
            ax.set_yscale("log")
            ax.set_yticks([5, 10, 20, 50, 100, 200])
            ax.set_yticklabels(["5", "10", "20", "50", "100", "200"])
            ax.minorticks_off()
        else:
            ax.set_ylim(0, 155)
        ax.set_xlim(indexed.index[0], indexed.index[-1] + pd.Timedelta(days=110))
        ax.xaxis.set_major_locator(mdates.YearLocator(1 if use_log else 1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_title(title)
        ax.set_ylabel(
            "Adjusted close, start = 100"
            if use_log
            else "Adjusted close, Feb 2025 = 100"
        )
    fig.tight_layout(rect=(0, 0.065, 1, 1), w_pad=2.0)
    source_note(
        fig,
        "Source: Yahoo Finance chart endpoint, monthly adjusted closes through Sep 2026; SPY is market context. Retrieved 2026-10-13. Shares are not a measure of demand or AI's effect.",
    )
    return fig


def main():
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
