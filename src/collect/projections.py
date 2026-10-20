"""Module 17: capability projections (the paper's warning timeline)."""

from __future__ import annotations
import json
import numpy as np
import pandas as pd
from src.paths import PROCESSED

DAYS_PER_YEAR = 365.25
ORIGIN = pd.Timestamp("2019-01-01")
FAST_START = pd.Timestamp("2023-01-01")
MAX_FIT_HOURS = 16
SEED = 20261012
N_BOOT = 10000
THRESHOLDS = {
    "workday": 8 * 60,
    "workweek": 40 * 60,
    "workmonth": 167 * 60,
    "workyear": 2000 * 60,
}
CHECKPOINT_YEARS = {"early": 2028, "middle": 2031, "long": 2036}
REGIMES = {"fast": "Frontier trend since 2023", "slow": "Frontier trend since 2019"}
HORIZON_END = pd.Timestamp("2032-12-31")


def _years(dates: pd.Series) -> np.ndarray:
    return ((pd.to_datetime(dates) - ORIGIN).dt.days / DAYS_PER_YEAR).to_numpy()


def _to_date(years: float) -> pd.Timestamp | None:
    if not np.isfinite(years):
        return None
    ts = ORIGIN + pd.Timedelta(days=float(years) * DAYS_PER_YEAR)
    return ts if ts <= pd.Timestamp("2100-01-01") else None


def load_points() -> pd.DataFrame:
    df = pd.read_csv(
        PROCESSED / "agent_capability_cost_metr_horizons.csv",
        parse_dates=["release_date"],
    )
    return df


def regime_rows(df: pd.DataFrame, regime: str) -> pd.DataFrame:
    if regime == "fast":
        return df[df["in_fit"]]
    return df[df["is_sota"] & (df["p50_min"] <= MAX_FIT_HOURS * 60)]


def bootstrap(df: pd.DataFrame, col: str) -> np.ndarray:
    """Return (N_BOOT, 2) array of [slope, intercept] for log2(col) ~ years."""
    x = _years(df["release_date"])
    y = np.log2(df[col].to_numpy())
    rng = np.random.default_rng(SEED)
    out = []
    while len(out) < N_BOOT:
        i = rng.integers(0, len(x), len(x))
        if np.ptp(x[i]) == 0:
            continue
        out.append(np.polyfit(x[i], y[i], 1))
    return np.array(out)


def build(save: bool = True) -> dict:
    pts = load_points()
    grid = pd.date_range("2019-01-01", HORIZON_END, freq="MS")
    gx = _years(pd.Series(grid))
    paths, crossings = ([], [])
    for metric in ("p50_min", "p80_min"):
        for regime in REGIMES:
            rows = regime_rows(pts, regime)
            coefs = bootstrap(rows, metric)
            point = np.polyfit(
                _years(rows["release_date"]), np.log2(rows[metric].to_numpy()), 1
            )
            sims = coefs[:, :1] * gx[None, :] + coefs[:, 1:]
            paths.append(
                pd.DataFrame(
                    {
                        "date": grid,
                        "metric": metric,
                        "regime": regime,
                        "minutes": 2 ** (point[0] * gx + point[1]),
                        "minutes_p05": 2 ** np.percentile(sims, 5, axis=0),
                        "minutes_p95": 2 ** np.percentile(sims, 95, axis=0),
                    }
                )
            )
            for name, minutes in THRESHOLDS.items():
                target = np.log2(minutes)
                t_point = (target - point[1]) / point[0]
                t_boot = (target - coefs[:, 1]) / coefs[:, 0]
                t_boot = t_boot[coefs[:, 0] > 0]
                lo, hi = np.percentile(t_boot, [5, 95])
                crossings.append(
                    {
                        "metric": metric,
                        "regime": regime,
                        "threshold": name,
                        "threshold_minutes": minutes,
                        "date": _to_date(t_point),
                        "date_p05": _to_date(lo),
                        "date_p95": _to_date(hi),
                        "doubling_days": DAYS_PER_YEAR / point[0],
                        "n_models": len(rows),
                    }
                )
    paths = pd.concat(paths, ignore_index=True)
    crossings = pd.DataFrame(crossings)
    training = pts[
        pts["is_sota"]
        & (pts["release_date"] >= FAST_START)
        & (pts["release_date"] < pd.Timestamp("2025-02-24"))
    ].copy()
    test = pts[
        pts["is_sota"] & (pts["release_date"] >= pd.Timestamp("2025-02-24"))
    ].copy()
    backtest_parts = []
    for metric in ("p50_min", "p80_min"):
        coef = np.polyfit(
            _years(training["release_date"]), np.log2(training[metric]), 1
        )
        for split, rows in (("training", training), ("holdout", test)):
            part = rows[["model_key", "release_date", metric]].copy()
            part = part.rename(columns={metric: "observed_minutes"})
            part["metric"] = metric
            part["split"] = split
            part["predicted_minutes"] = 2 ** np.polyval(
                coef, _years(part["release_date"])
            )
            part["observed_to_predicted"] = (
                part.observed_minutes / part.predicted_minutes
            )
            backtest_parts.append(part)
    backtest = pd.concat(backtest_parts, ignore_index=True)
    meta = {
        "source": "Module 09 processed METR Time Horizon 1.1 data (agent_capability_cost_metr_horizons.csv)",
        "method": "OLS of log2(horizon minutes) on release date; model-level bootstrap (10,000) of slope+intercept; 5-95% bands",
        "thresholds_minutes": THRESHOLDS,
        "latest_observation": str(pts["release_date"].max().date()),
        "caveat": "Extrapolation of a measured benchmark trend, not a forecast. METR horizon = human time of tasks an agent completes at the stated success rate on METR's task suite; not autonomous job duration.",
    }
    if save:
        paths.to_csv(PROCESSED / "projections_paths.csv", index=False)
        crossings.to_csv(PROCESSED / "projections_crossings.csv", index=False)
        backtest.to_csv(PROCESSED / "projections_preagent_backtest.csv", index=False)
        (PROCESSED / "projections_meta.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
    return {
        "points": pts,
        "paths": paths,
        "crossings": crossings,
        "backtest": backtest,
        "meta": meta,
    }


def _fmt(ts) -> str:
    return (
        "beyond 2100"
        if ts is None or pd.isna(ts)
        else pd.Timestamp(ts).strftime("%b %Y")
    )


def summary_numbers(out: dict) -> dict[str, str]:
    """Return summary values from the processed data."""
    names = {"p50_min": "Fifty", "p80_min": "Eighty", "fast": "Fast", "slow": "Slow"}
    nums = {}
    nums.update(
        {
            "ProjSuccessFifty": "50",
            "ProjSuccessEighty": "80",
            "ProjFastStartYear": str(FAST_START.year),
            "ProjSlowStartYear": str(ORIGIN.year),
            "ProjMaxFitHours": str(MAX_FIT_HOURS),
            "ProjBootstrapSamples": f"{N_BOOT:,}".replace(",", "{,}"),
            "ProjBandLowPercentile": "5",
            "ProjBandHighPercentile": "95",
        }
    )
    for threshold, minutes in THRESHOLDS.items():
        nums[f"Proj{threshold.capitalize()}Hours"] = f"{minutes // 60:,}".replace(
            ",", "{,}"
        )
    for r in out["crossings"].itertuples():
        stem = f"Proj{names[r.metric]}{names[r.regime]}{r.threshold.capitalize()}"
        nums[stem + "Date"] = _fmt(r.date)
        nums[stem + "Low"] = _fmt(r.date_p05)
        nums[stem + "High"] = _fmt(r.date_p95)
    for regime in REGIMES:
        c = out["crossings"]
        d = c[(c.metric == "p50_min") & (c.regime == regime)]["doubling_days"].iloc[0]
        nums[f"ProjDoublingDays{names[regime]}"] = f"{d:.0f}"
    for label, year in CHECKPOINT_YEARS.items():
        nums[f"ProjCheckpoint{label.capitalize()}Year"] = str(year)
    holdout = out["backtest"]
    holdout = holdout[(holdout.metric == "p50_min") & (holdout.split == "holdout")]
    nums["ProjBacktestN"] = str(len(holdout))
    nums["ProjBacktestAboveN"] = str((holdout.observed_to_predicted > 1).sum())
    nums["ProjBacktestMedianRatio"] = f"{holdout.observed_to_predicted.median():.1f}"
    return nums
