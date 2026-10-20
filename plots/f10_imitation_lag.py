"""Figure 10c - imitation lag: years from commercial launch to the first GitHub repository"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, ENTITY_COLORS, apply, save, source_note

STEM = "f10_imitation_lag"
ISOCHRONES = [2010, 2015, 2020, 2023, 2025]
OFFSETS = {
    "Adobe Photoshop": (6, 0),
    "Adobe Acrobat": (6, 0),
    "Grammarly": (6, 0),
    "Trello": (6, 0),
    "Postman": (-6, 0),
    "Canva": (6, -5),
    "Smallpdf": (6, 1),
    "Notion": (-6, 2),
    "Loom": (6, 1),
    "QuillBot": (6, 0),
    "Retool": (6, -4),
    "Screen Studio": (6, 0),
}


def load() -> pd.DataFrame:
    return pd.read_csv(
        PROCESSED / "10_open_source_vs_commercial_imitation_lag.csv",
        parse_dates=["launch_date", "first_alt_created", "first_alt_created_anystars"],
    )


def make_figure() -> plt.Figure:
    apply()
    d = load()
    d["launch_dec"] = (
        d["launch_date"].dt.year + (d["launch_date"].dt.dayofyear - 1) / 365.25
    )
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    xs = np.array([1987, 2025])
    for y in ISOCHRONES:
        ax.plot(xs, y - xs, color=COLORS["context"], lw=0.8, ls="--", zorder=1)
        xl = 1998.5
        ax.text(
            xl,
            y - xl + 0.4,
            str(y),
            fontsize=6.5,
            color=COLORS["muted"],
            rotation=-45,
            transform_rotates_text=True,
            rotation_mode="anchor",
            ha="left",
            va="bottom",
        )
    ax.text(
        1998.2,
        6.0,
        "dashed: year the first\nalternative appeared",
        fontsize=6.3,
        color=COLORS["muted"],
        ha="left",
        va="top",
    )
    ax.axvline(2008.3, color=COLORS["axis"], lw=0.8)
    ax.text(
        2008.5,
        33.5,
        "GitHub opens\n(Apr 2008)",
        fontsize=6.3,
        color=COLORS["muted"],
        va="top",
    )
    c = ENTITY_COLORS["commercial"]
    prim = d.dropna(subset=["lag_years"])
    anyst = d.dropna(subset=["lag_years_anystars"])
    for r in d.itertuples():
        if not np.isnan(r.lag_years) and (not np.isnan(r.lag_years_anystars)):
            ax.plot(
                [r.launch_dec, r.launch_dec],
                [r.lag_years_anystars, r.lag_years],
                color=c,
                lw=0.7,
                alpha=0.5,
                zorder=2,
            )
    ax.scatter(
        anyst["launch_dec"],
        anyst["lag_years_anystars"],
        s=22,
        facecolor=COLORS["surface"],
        edgecolor=c,
        linewidth=1.0,
        zorder=3,
    )
    ax.scatter(prim["launch_dec"], prim["lag_years"], s=34, color=c, zorder=4)
    for r in d.itertuples():
        y = r.lag_years if not np.isnan(r.lag_years) else r.lag_years_anystars
        if np.isnan(y):
            continue
        dx, dy = OFFSETS.get(r.product, (6, 0))
        ax.annotate(
            r.product + ("" if not np.isnan(r.lag_years) else " (any-stars only)"),
            xy=(r.launch_dec, y),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=7,
            color=COLORS["ink2"],
            va="center",
            ha="left" if dx > 0 else "right",
        )
    ax.set_xlim(1987, 2025)
    ax.set_ylim(0, 35)
    ax.set_xlabel("Commercial product launch year")
    ax.set_ylabel("Years until first GitHub alternative")
    ax.set_title(
        "Imitation lag shrinks with launch year, mostly because alternatives cluster after 2020",
        loc="left",
        fontsize=9.5,
    )
    ax.scatter([0.69], [0.93], s=34, color=c, transform=ax.transAxes)
    ax.text(
        0.705,
        0.93,
        "first rule match with >= 50 stars",
        transform=ax.transAxes,
        fontsize=6.8,
        va="center",
        color=COLORS["ink2"],
    )
    ax.scatter(
        [0.69],
        [0.86],
        s=22,
        facecolor=COLORS["surface"],
        edgecolor=c,
        linewidth=1.0,
        transform=ax.transAxes,
    )
    ax.text(
        0.705,
        0.86,
        "first rule match, any stars (top-300 search)",
        transform=ax.transAxes,
        fontsize=6.8,
        va="center",
        color=COLORS["ink2"],
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    source_note(
        fig,
        "Lag = repository created_at minus launch date (sources in data note; mid-year when only the year is known). GitHub-visible lag only: older alternatives hosted elsewhere\n(e.g. GIMP, LibreOffice) or not describing themselves as 'alternative to <product>' are not counted. Retrieved Oct 2026. Pilot of 12 pre-specified products.",
    )
    return fig


def main() -> None:
    fig = make_figure()
    save(fig, STEM)
    plt.close(fig)


if __name__ == "__main__":
    main()
