"""Regenerate the package ITS break-date sensitivity table from processed data."""

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/package_ecosystems_new_monthly.csv"
SERIES = (
    ("PyPI", "new_packages_filtered", "PyPI screened"),
    ("crates.io", "new_packages_filtered", "crates.io screened"),
    ("RubyGems", "new_packages_filtered", "RubyGems screened"),
    ("Packagist", "new_packages", "Packagist net additions"),
)
BREAKS = pd.date_range("2024-08-01", "2025-08-01", freq="MS")
EVENT = pd.Timestamp("2025-02-01")
CHATGPT = pd.Timestamp("2022-12-01")


def month_index(s: pd.Series | pd.Timestamp):
    if isinstance(s, pd.Timestamp):
        return (s.year - 2016) * 12 + s.month - 1
    return (s.dt.year - 2016) * 12 + s.dt.month - 1


def calculate() -> pd.DataFrame:
    raw = pd.read_csv(SOURCE, parse_dates=["month"])
    rows = []
    for ecosystem, column, label in SERIES:
        d = raw[(raw.ecosystem == ecosystem) & (raw.month >= "2016-01-01")].copy()
        d = d.dropna(subset=[column])
        d = d[d[column] > 0]
        d["y"] = np.log(d[column])
        d["t"] = month_index(d.month)
        d["post"] = (d.month >= CHATGPT).astype(int)
        d["t_post"] = d.post * (d.t - month_index(CHATGPT))
        d["moy"] = d.month.dt.month.astype(str)
        fits = []
        for break_date in BREAKS:
            d["agent"] = (d.month >= break_date).astype(int)
            d["t_agent"] = d.agent * (d.t - month_index(break_date))
            fit = smf.ols(
                "y ~ t + post + t_post + agent + t_agent + C(moy)", data=d
            ).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
            fits.append(
                (
                    break_date,
                    fit.params["t_agent"] * 1200,
                    fit.aic,
                    fit.pvalues["t_agent"],
                )
            )
        event = next((row for row in fits if row[0] == EVENT))
        rows.append(
            {
                "label": label,
                "feb_slope": event[1],
                "min_slope": min((row[1] for row in fits)),
                "max_slope": max((row[1] for row in fits)),
                "min_aic_date": min(fits, key=lambda row: row[2])[0],
                "feb_p": event[3],
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    result = calculate()
    destination = ROOT / "output/tables/package_break_sensitivity.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(destination, index=False)
    print(result.to_string(index=False))
