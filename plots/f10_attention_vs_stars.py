"""Figure 10a - commercial attention vs open-source alternative attention, by category."""

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

STEM = "f10_attention_vs_stars"
CATEGORIES = {
    "screen_recording": "Screen recording",
    "writing_assistance": "Writing assistance",
    "pdf_utilities": "PDF utilities",
    "image_editing": "Image editing",
    "productivity": "Productivity",
    "developer_utilities": "Developer utilities",
}
CHATGPT = pd.Timestamp("2022-11-30")
DEGRADED = pd.Timestamp("2025-05-23")
XEND = pd.Timestamp("2026-10-31")
BASE_START, BASE_END = (pd.Timestamp("2023-01-01"), pd.Timestamp("2023-12-31"))
XMIN, XMAX = (pd.Timestamp("2016-01-01"), pd.Timestamp("2029-06-30"))
STYLES = ["-", (0, (3, 1.6))]


def load():
    pv = pd.read_csv(
        PROCESSED / "10_open_source_vs_commercial_pageviews_monthly.csv",
        parse_dates=["month"],
    )
    sh = pd.read_csv(
        PROCESSED / "10_open_source_vs_commercial_star_history_monthly.csv",
        parse_dates=["month"],
    )
    prods = pd.read_csv(
        Path(__file__).resolve().parents[1] / "data" / "sample" / "products_pilot.csv"
    )
    return (pv, sh, prods)


def _pageview_index(pv: pd.DataFrame) -> pd.DataFrame:
    """Product views as a share of all en.wikipedia user views (removes the site-wide decline),"""
    out = []
    use = pv[(pv["side"] == "commercial") & pv["product_specific"].astype(bool)]
    for prod, g in use.groupby("product"):
        g = g.set_index("month").sort_index()
        share = (
            (g["views"] / g["enwiki_user_views"])
            .rolling(3, center=True, min_periods=2)
            .mean()
        )
        base = share.loc[BASE_START:BASE_END]
        if len(base) < 6 or not base.mean() > 0:
            continue
        out.append(
            pd.DataFrame(
                {
                    "product": prod,
                    "month": share.index,
                    "index": 100 * share / base.mean(),
                }
            )
        )
    return pd.concat(out, ignore_index=True)


def _star_index(sh: pd.DataFrame) -> pd.DataFrame:
    """Summed star *events* of the top-3 included alternatives, indexed so that the"""
    top = sh[sh["top_k"].astype(bool)]
    exact = top.drop_duplicates(["product", "repo"]).groupby("product")["stars"].sum()
    agg = top.groupby(["product", "month"], as_index=False)["cum_star_events"].sum()
    out = []
    for prod, g in agg.groupby("product"):
        s = g.set_index("month")["cum_star_events"].sort_index()
        out.append(
            pd.DataFrame(
                {
                    "product": prod,
                    "month": s.index,
                    "index": 100 * s / exact[prod],
                    "latest": exact[prod],
                }
            )
        )
    return pd.concat(out, ignore_index=True)


def _label(ax, x, y, text, color, dy=0):
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(3, dy),
        textcoords="offset points",
        fontsize=6.8,
        color=COLORS["ink2"],
        va="center",
        ha="left",
    )


def _spread(ys, min_gap):
    """Nudge label y-positions apart (data units) so end labels do not collide."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    adj = list(ys)
    for a, b in zip(order, order[1:]):
        if adj[b] - adj[a] < min_gap:
            adj[b] = adj[a] + min_gap
    return adj


def make_figure() -> plt.Figure:
    apply()
    pv, sh, prods = load()
    pvi, sti = (_pageview_index(pv), _star_index(sh))
    fig, axes = plt.subplots(3, 4, figsize=(7.0, 7.6), sharex=True)
    no_wiki, no_alt = ([], [])
    for k, cat in enumerate(CATEGORIES):
        axp, axs = (axes[k // 2, k % 2 * 2], axes[k // 2, k % 2 * 2 + 1])
        plist = prods.loc[prods["category"] == cat, "product"].tolist()
        ends, labels = ([], [])
        for j, prod in enumerate(plist):
            g = pvi[pvi["product"] == prod].dropna()
            if g.empty:
                no_wiki.append(prod)
                continue
            axp.plot(
                g["month"],
                g["index"],
                color=ENTITY_COLORS["commercial"],
                lw=1.4,
                ls=STYLES[j % 2],
            )
            ends.append(np.log10(g["index"].iloc[-1]))
            labels.append((g["month"].iloc[-1], prod))
        axp.set_yscale("log")
        axp.set_ylim(5, 1300)
        axp.set_yticks([10, 30, 100, 300, 1000])
        axp.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
        axp.yaxis.set_minor_locator(mticker.NullLocator())
        axp.axhline(100, color=COLORS["axis"], lw=0.7, zorder=0)
        for (x, t), y in zip(labels, _spread(ends, 0.2)):
            _label(axp, x, 10**y, t, ENTITY_COLORS["commercial"])
        ends, labels = ([], [])
        for j, prod in enumerate(plist):
            g = sti[sti["product"] == prod]
            if g.empty:
                no_alt.append(prod)
                continue
            axs.plot(
                g["month"],
                g["index"],
                color=ENTITY_COLORS["open_source"],
                lw=1.4,
                ls=STYLES[j % 2],
            )
            last = g.iloc[-1]
            axs.plot(
                [last["month"], last["month"]],
                [last["index"], 100],
                color=ENTITY_COLORS["open_source"],
                lw=0.7,
                ls=":",
            )
            axs.plot(
                [last["month"]],
                [100],
                marker="o",
                ms=3.5,
                mfc=COLORS["surface"],
                mec=ENTITY_COLORS["open_source"],
                mew=1.1,
                ls="none",
            )
            ends.append(100 - 30 * len(labels))
            labels.append(
                (last["month"], f"{prod}\n{last['latest'] / 1000:,.1f}k stars")
            )
        for (x, t), y in zip(labels, ends):
            _label(axs, x, y, t, ENTITY_COLORS["open_source"])
        if not labels:
            axs.text(
                0.5,
                0.5,
                "no repository met\nthe inclusion rule",
                transform=axs.transAxes,
                ha="center",
                va="center",
                fontsize=6.8,
                color=COLORS["muted"],
                bbox=dict(facecolor=COLORS["surface"], edgecolor="none", pad=1.5),
            )
        axs.axvspan(DEGRADED, XEND, color=COLORS["grid"], alpha=0.55, lw=0, zorder=0)
        axs.set_ylim(0, 112)
        axs.set_yticks([0, 25, 50, 75, 100])
        axp.set_title(CATEGORIES[cat], fontsize=8.5, loc="left", pad=13)
        axs.set_title(" ", fontsize=8.5, pad=13)
        axp.text(
            0.0,
            1.01,
            "Wikipedia views (share), 2023 = 100",
            transform=axp.transAxes,
            fontsize=6.1,
            color=COLORS["muted"],
            va="bottom",
            ha="left",
        )
        axs.text(
            0.0,
            1.01,
            "Alternatives' stars, today = 100",
            transform=axs.transAxes,
            fontsize=6.1,
            color=COLORS["muted"],
            va="bottom",
            ha="left",
        )
        for ax in (axp, axs):
            ax.axvline(CHATGPT, color=COLORS["muted"], lw=0.7, ls=":", zorder=0)
            ax.set_xlim(XMIN, XMAX)
            ax.tick_params(labelsize=6.5)
            ax.set_xticks(pd.to_datetime(["2016-01-01", "2020-01-01", "2024-01-01"]))
            ax.set_xticklabels(["2016", "'20", "'24"])
    axes[0, 1].annotate(
        "ChatGPT",
        xy=(CHATGPT, 0.02),
        xycoords=("data", "axes fraction"),
        xytext=(-2, 0),
        textcoords="offset points",
        fontsize=6,
        color=COLORS["muted"],
        ha="right",
        va="bottom",
    )
    fig.suptitle(
        "Commercial products' Wikipedia attention vs their open-source alternatives' GitHub stars",
        x=0.01,
        ha="left",
        fontsize=9.5,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.975), h_pad=1.4, w_pad=0.4)
    source_note(
        fig,
        f"Blue: product article views (target + redirects) / all en.wikipedia user views, Wikimedia Pageviews API, 3-month mean, log scale; 2023 = 100.\nNo product-specific article: {', '.join(no_wiki)}. Orange: summed star events of the top-3 included alternatives (OSS Insight), indexed to today's exact GitHub star total = 100\n(hollow dot). Gray band: event data are lower bounds from May 2025. Solid/dashed = first/second product of the category. Stars are attention, not users or paid substitution.\nRetrieved Oct 2026. Pilot of 12 pre-specified products.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
