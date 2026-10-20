"""Figure: was the software-postings slump unusual? All Indeed occupational categories."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.paths import PROCESSED
from src.style import COLORS, SERIES, apply, save, source_note

NAME = "f08_labor_indeed_categories"
HIGHLIGHT = "Software development"
RELATED = {
    "IT operations and helpdesk",
    "Mathematics",
    "Information design and documentation",
}


def _changes(m: pd.DataFrame) -> pd.DataFrame:
    w = m[m["series_id"] != "IHLIDXUS"].pivot_table(
        index="month", columns="category", values="value"
    )
    last = w.index.max()
    pre = (w.loc["2022-11-01"] / w.loc["2020-02-01"] - 1) * 100
    post = (w.loc[last] / w.loc["2022-11-01"] - 1) * 100
    out = (
        pd.DataFrame({"pre": pre, "post": post})
        .dropna()
        .sort_values("post", ascending=False)
    )
    out.attrs["last"] = last
    tot = m[m["series_id"] == "IHLIDXUS"].set_index("month")["value"]
    out.attrs["total_pre"] = (tot.loc["2022-11-01"] / tot.loc["2020-02-01"] - 1) * 100
    out.attrs["total_post"] = (tot.loc[last] / tot.loc["2022-11-01"] - 1) * 100
    return out


def make_figure() -> plt.Figure:
    apply()
    meta = json.loads(
        (PROCESSED / "labor_market_meta.json").read_text(encoding="utf-8")
    )
    m = pd.read_csv(
        PROCESSED / "labor_market_indeed_monthly.csv", parse_dates=["month"]
    )
    ch = _changes(m)
    y = range(len(ch))
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 6.4), sharey=True)
    for ax, col, title, tot in (
        (axes[0], "pre", "Feb 2020 to Nov 2022", ch.attrs["total_pre"]),
        (
            axes[1],
            "post",
            f"Nov 2022 to {ch.attrs['last']:%b %Y}",
            ch.attrs["total_post"],
        ),
    ):
        colors = [
            (
                SERIES[0]
                if c == HIGHLIGHT
                else SERIES[1] if c in RELATED else COLORS["context"]
            )
            for c in ch.index
        ]
        ax.barh(list(y), ch[col].values, color=colors, height=0.7)
        ax.axvline(0, color=COLORS["ink2"], lw=0.6)
        ax.axvline(tot, color=COLORS["ink"], lw=0.8, ls=(0, (3, 2)))
        ax.text(
            tot,
            len(ch) - 0.2,
            f" all postings\n {tot:+.0f}%",
            fontsize=6.5,
            color=COLORS["ink"],
            va="bottom",
            ha="left",
        )
        ax.set_title(title, fontsize=9)
        ax.grid(axis="x")
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("% change in postings index")
    axes[0].set_yticks(list(y))
    axes[0].set_yticklabels(ch.index, fontsize=6.3)
    for lab in axes[0].get_yticklabels():
        if lab.get_text() == HIGHLIGHT:
            lab.set_color(SERIES[0])
            lab.set_fontweight("bold")
        elif lab.get_text() in RELATED:
            lab.set_color(SERIES[1])
    axes[0].set_ylim(-0.7, len(ch) + 1.6)
    axes[0].tick_params(axis="y", length=0)
    fig.suptitle(
        "Indeed postings by occupational category (sorted by post-ChatGPT change)",
        x=0.01,
        ha="left",
        fontsize=10,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    source_note(
        fig,
        f"Source: Indeed Hiring Lab via FRED (IHLIDXUSTP* series), monthly means of daily index. Blue: software development; orange: adjacent digital occupations. Retrieved {meta['indeed_retrieved_utc'][:10]}.",
    )
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
