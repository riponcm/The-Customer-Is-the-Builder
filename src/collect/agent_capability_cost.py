"""Module 09 - AI coding capability and cost trends."""

from __future__ import annotations
import io
import json
import time
import zipfile
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import requests
import yaml
from src.fetch import DEFAULT_UA, _key, get
from src.paths import CACHE, PROCESSED, RAW

NS = "agent_capability_cost"
RAW_DIR = RAW / NS
RAW_DIR.mkdir(parents=True, exist_ok=True)
METR_URL = "https://metr.org/assets/benchmark_results_1_1.yaml"
EPOCH_ZIP_URL = "https://epoch.ai/data/benchmark_data.zip"
EPOCH_FILES = [
    "swe_bench_verified.csv",
    "aider_polyglot_external.csv",
    "metr_time_horizons_external.csv",
    "epoch_capabilities_index/eci_scores.csv",
    "frontierswe_external.csv",
    "README.md",
]
FIT_START = "2023-01-01"
MAX_P50_MIN = 16 * 60
AIDER_THRESHOLDS = [50, 60, 70, 80]
DAYS_PER_YEAR = 365.25
FRONTIERSWE_TRIALS = 5
FIT_CI_PERCENTILES = (2.5, 97.5)


def _download_binary(url: str, dest_name: str, refresh: bool = False) -> bytes:
    """Cached binary GET (same idea as src.fetch.get, which only returns text/JSON)."""
    dest = RAW_DIR / dest_name
    side = RAW_DIR / (dest_name + ".provenance.json")
    if dest.exists() and side.exists() and (not refresh):
        return dest.read_bytes()
    for attempt in range(4):
        r = requests.get(url, headers={"User-Agent": DEFAULT_UA}, timeout=120)
        if r.status_code == 200:
            dest.write_bytes(r.content)
            side.write_text(
                json.dumps(
                    {
                        "url": url,
                        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                        "bytes": len(r.content),
                    }
                ),
                encoding="utf-8",
            )
            return r.content
        time.sleep(2**attempt * 2)
    raise RuntimeError(f"download failed: {url} ({r.status_code})")


def retrieval_dates() -> dict[str, str | None]:
    out = {}
    p = CACHE / NS / f"{_key(METR_URL, None)}.json"
    out["metr"] = (
        json.loads(p.read_text(encoding="utf-8"))["retrieved_utc"]
        if p.exists()
        else None
    )
    side = RAW_DIR / "benchmark_data.zip.provenance.json"
    out["epoch"] = (
        json.loads(side.read_text(encoding="utf-8"))["retrieved_utc"]
        if side.exists()
        else None
    )
    return out


def load_metr() -> tuple[pd.DataFrame, dict]:
    txt = get(METR_URL, namespace=NS, as_json=False)
    (RAW_DIR / "benchmark_results_1_1.yaml").write_text(txt, encoding="utf-8")
    d = yaml.safe_load(txt)
    rows = []
    for key, v in d["results"].items():
        m = v["metrics"]
        rows.append(
            {
                "model_key": key,
                "release_date": pd.Timestamp(v["release_date"]),
                "p50_min": m["p50_horizon_length"]["estimate"],
                "p50_ci_low": m["p50_horizon_length"]["ci_low"],
                "p50_ci_high": m["p50_horizon_length"]["ci_high"],
                "p80_min": m["p80_horizon_length"]["estimate"],
                "average_score": m["average_score"]["estimate"],
                "is_sota": bool(m["is_sota"]),
            }
        )
    df = pd.DataFrame(rows).sort_values("release_date").reset_index(drop=True)
    df["in_fit"] = (
        df["is_sota"]
        & (df["release_date"] >= FIT_START)
        & (df["p50_min"] <= MAX_P50_MIN)
    )
    published = {
        "benchmark": d["benchmark_name"],
        **{
            f"{k}_{kk}": vv
            for k, v in d["doubling_time_in_days"].items()
            for kk, vv in v.items()
        },
    }
    return (df, published)


def load_epoch() -> dict[str, pd.DataFrame]:
    blob = _download_binary(EPOCH_ZIP_URL, "benchmark_data.zip")
    z = zipfile.ZipFile(io.BytesIO(blob))
    out = {}
    for f in EPOCH_FILES:
        raw = z.read(f)
        (RAW_DIR / f"epoch_{f.replace('/', '_')}").write_bytes(raw)
        if f.endswith(".csv"):
            out[f] = pd.read_csv(io.BytesIO(raw))
    return out


def _years(dates: pd.Series) -> np.ndarray:
    return ((dates - pd.Timestamp("2019-01-01")).dt.days / DAYS_PER_YEAR).to_numpy()


def fit_doubling(df: pd.DataFrame, n_boot: int = 10000, seed: int = 20261011) -> dict:
    """OLS of log2(p50 minutes) on release date for models flagged in_fit."""
    import statsmodels.api as sm

    sub = df[df["in_fit"]]
    x = _years(sub["release_date"])
    y = np.log2(sub["p50_min"].to_numpy())
    res = sm.OLS(y, sm.add_constant(x)).fit()
    b = res.params[1]
    lo, hi = res.conf_int(0.05)[1]
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        i = rng.integers(0, len(x), len(x))
        if np.ptp(x[i]) == 0:
            continue
        boots.append(np.polyfit(x[i], y[i], 1)[0])
    blo, bhi = np.percentile(boots, FIT_CI_PERCENTILES)
    return {
        "n": int(len(sub)),
        "start": str(sub["release_date"].min().date()),
        "end": str(sub["release_date"].max().date()),
        "slope_doublings_per_year": b,
        "intercept": res.params[0],
        "r2": res.rsquared,
        "doubling_days": DAYS_PER_YEAR / b,
        "doubling_days_ols_ci_low": DAYS_PER_YEAR / hi,
        "doubling_days_ols_ci_high": DAYS_PER_YEAR / lo,
        "doubling_days_boot_ci_low": DAYS_PER_YEAR / bhi,
        "doubling_days_boot_ci_high": DAYS_PER_YEAR / blo,
    }


def swebench_frontier(sw: pd.DataFrame) -> pd.DataFrame:
    df = sw.rename(
        columns={
            "Model version": "model",
            "mean_score": "score",
            "Release date": "release_date",
            "Organization": "organization",
            "stderr": "stderr",
        }
    )
    df = df[["model", "release_date", "organization", "score", "stderr"]].dropna(
        subset=["release_date", "score"]
    )
    df["release_date"] = pd.to_datetime(df["release_date"])
    df["score_pct"] = df["score"] * 100
    df = df.sort_values(
        ["release_date", "score_pct"], ascending=[True, False]
    ).reset_index(drop=True)
    df["frontier_pct"] = df["score_pct"].cummax()
    df["is_frontier"] = df["score_pct"] >= df["frontier_pct"] - 1e-09
    return df


def general_eci(ec: pd.DataFrame) -> pd.DataFrame:
    """Epoch's general ECI, not a coding horizon or a product reliability score."""
    df = ec.rename(
        columns={
            "Display name": "model",
            "date": "release_date",
            "Organization": "organization",
            "eci": "score",
            "eci_ci_low": "ci_low",
            "eci_ci_high": "ci_high",
        }
    )
    df = df[
        ["model", "release_date", "organization", "score", "ci_low", "ci_high"]
    ].copy()
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df = df.dropna(subset=["model", "release_date", "score"])
    latest_month = df["release_date"].max().to_period("M")
    df["latest_month"] = df["release_date"].dt.to_period("M") == latest_month
    return df.sort_values(["release_date", "model"]).reset_index(drop=True)


def frontierswe_snapshot(fs: pd.DataFrame) -> pd.DataFrame:
    """One common FrontierSWE v2 harness; score is a task reward, not pass rate."""
    df = fs.rename(
        columns={
            "Name": "model",
            "Model version": "model_version",
            "Release date": "release_date",
            "Organization": "organization",
            "Score": "mean_score",
            "Best@5": "best_score",
            "Worst@5": "worst_score",
            "Harness": "harness",
            "Average cost (USD)": "cost_usd",
        }
    )
    df = df[
        [
            "model",
            "model_version",
            "release_date",
            "organization",
            "harness",
            "mean_score",
            "worst_score",
            "best_score",
            "cost_usd",
        ]
    ].copy()
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df = df.dropna(subset=["model", "model_version", "release_date", "mean_score"])
    assert df["harness"].nunique() == 1, "FrontierSWE runs must share a harness"
    for col in ("mean_score", "worst_score", "best_score"):
        df[col + "_pct"] = df[col] * 100
    return df.sort_values("mean_score", ascending=False).reset_index(drop=True)


def aider_cost(ad: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aider Polyglot runs with a usable cost, and cheapest-cost-to-threshold frontier."""
    df = ad.rename(
        columns={
            "Model version": "model",
            "Percent correct": "pct_correct",
            "Release date": "release_date",
            "Cost": "cost_usd",
            "Date of evaluation": "eval_date",
            "Organization": "organization",
            "Edit format": "edit_format",
        }
    )
    df = df[
        [
            "model",
            "organization",
            "release_date",
            "eval_date",
            "pct_correct",
            "cost_usd",
            "edit_format",
        ]
    ]
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["eval_date"] = pd.to_datetime(df["eval_date"], errors="coerce")
    df["date_conflict"] = df["eval_date"] < df["release_date"] - pd.Timedelta(days=7)
    df["usable"] = (
        df["release_date"].notna()
        & df["eval_date"].notna()
        & (df["cost_usd"] > 0)
        & ~df["date_conflict"]
    )
    use = df[df["usable"]].sort_values("release_date")
    rows = []
    months = pd.date_range(
        use["release_date"].min().to_period("M").to_timestamp(),
        use["release_date"].max().to_period("M").to_timestamp(),
        freq="MS",
    )
    for thr in AIDER_THRESHOLDS:
        for m in months:
            end = m + pd.offsets.MonthEnd(0)
            avail = use[(use["release_date"] <= end) & (use["pct_correct"] >= thr)]
            if avail.empty:
                continue
            best = avail.loc[avail["cost_usd"].idxmin()]
            rows.append(
                {
                    "threshold_pct": thr,
                    "month": m,
                    "min_cost_usd": best["cost_usd"],
                    "model": best["model"],
                    "model_pct_correct": best["pct_correct"],
                }
            )
    return (df, pd.DataFrame(rows))


def build(save: bool = True) -> dict:
    metr, published = load_metr()
    ep = load_epoch()
    fit = fit_doubling(metr)
    fit_all = fit_doubling(
        metr.assign(in_fit=metr["is_sota"] & (metr["p50_min"] <= MAX_P50_MIN))
    )
    sw = swebench_frontier(ep["swe_bench_verified.csv"])
    eci = general_eci(ep["epoch_capabilities_index/eci_scores.csv"])
    fs = frontierswe_snapshot(ep["frontierswe_external.csv"])
    ad, ad_frontier = aider_cost(ep["aider_polyglot_external.csv"])
    fits = pd.DataFrame(
        [
            {"fit": "own_ols_sota_from_2023", **fit},
            {"fit": "own_ols_sota_all_years", **fit_all},
        ]
    )
    pub = pd.DataFrame([{"fit": "metr_published", **published}])
    out = {
        "metr": metr,
        "metr_fit": fits,
        "metr_published": pub,
        "swebench": sw,
        "eci": eci,
        "frontierswe": fs,
        "aider": ad,
        "aider_frontier": ad_frontier,
    }
    if save:
        metr.to_csv(PROCESSED / f"{NS}_metr_horizons.csv", index=False)
        fits.to_csv(PROCESSED / f"{NS}_metr_fit.csv", index=False)
        pub.to_csv(PROCESSED / f"{NS}_metr_published_fit.csv", index=False)
        sw.to_csv(PROCESSED / f"{NS}_swebench_verified.csv", index=False)
        eci.to_csv(PROCESSED / f"{NS}_eci_general.csv", index=False)
        fs.to_csv(PROCESSED / f"{NS}_frontierswe_v2.csv", index=False)
        ad.to_csv(PROCESSED / f"{NS}_aider_polyglot.csv", index=False)
        ad_frontier.to_csv(PROCESSED / f"{NS}_aider_cost_frontier.csv", index=False)
        (PROCESSED / f"{NS}_meta.json").write_text(
            json.dumps(
                {
                    "metr_url": METR_URL,
                    "epoch_url": EPOCH_ZIP_URL,
                    "retrieved_utc": retrieval_dates(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return out


def _fmt_minutes(x: float) -> str:
    return f"{x:.0f} minutes" if x < 90 else f"{x / 60:.1f} hours"


def summary_numbers(out: dict) -> dict[str, str]:
    n: dict[str, str] = {}
    pub = out["metr_published"].iloc[0]
    n["CapMetrPubDoublingDays"] = f"{pub['from_2023_on_point_estimate']:.0f}"
    n["CapMetrPubDoublingCiLow"] = f"{pub['from_2023_on_ci_low']:.0f}"
    n["CapMetrPubDoublingCiHigh"] = f"{pub['from_2023_on_ci_high']:.0f}"
    n["CapMetrPubDoublingAllTimeDays"] = (
        f"{pub['all_time_stitched_point_estimate']:.0f}"
    )
    f = out["metr_fit"].set_index("fit").loc["own_ols_sota_from_2023"]
    n["CapMetrFitN"] = str(int(f["n"]))
    n["CapMetrFitDoublingDays"] = f"{f['doubling_days']:.0f}"
    n["CapMetrFitDoublingMonths"] = f"{f['doubling_days'] / 30.44:.1f}"
    n["CapMetrFitBootCiLow"] = f"{f['doubling_days_boot_ci_low']:.0f}"
    n["CapMetrFitBootCiHigh"] = f"{f['doubling_days_boot_ci_high']:.0f}"
    n["CapMetrFitCiPercent"] = f"{FIT_CI_PERCENTILES[1] - FIT_CI_PERCENTILES[0]:g}"
    n["CapMetrFitOlsCiLow"] = f"{f['doubling_days_ols_ci_low']:.0f}"
    n["CapMetrFitOlsCiHigh"] = f"{f['doubling_days_ols_ci_high']:.0f}"
    n["CapMetrFitRsq"] = f"{f['r2']:.2f}"
    n["CapMetrFitGrowthPerYear"] = f"{2 ** f['slope_doublings_per_year']:.1f}"
    fa = out["metr_fit"].set_index("fit").loc["own_ols_sota_all_years"]
    n["CapMetrFitAllYearsDoublingDays"] = f"{fa['doubling_days']:.0f}"
    m = out["metr"]
    top = m.loc[m["p50_min"].idxmax()]
    n["CapMetrTopModel"] = (
        top["model_key"].replace("_inspect", "").replace("_", " ").title()
    )
    n["CapMetrTopPFifty"] = _fmt_minutes(top["p50_min"])
    n["CapMetrTopPFiftyCiLow"] = _fmt_minutes(top["p50_ci_low"])
    n["CapMetrTopPFiftyCiHigh"] = _fmt_minutes(top["p50_ci_high"])
    n["CapMetrTopPEighty"] = _fmt_minutes(top["p80_min"])
    n["CapMetrReliableMaxHours"] = str(MAX_P50_MIN // 60)
    n["CapMetrTopDate"] = top["release_date"].strftime("%B %Y")
    g4 = m[m["model_key"] == "gpt_4"].iloc[0]
    n["CapMetrGptFourPFifty"] = _fmt_minutes(g4["p50_min"])
    n["CapMetrLastRelease"] = m["release_date"].max().strftime("%B %Y")
    sw = out["swebench"]
    n["CapSweFirstDate"] = sw["release_date"].min().strftime("%B %Y")
    n["CapSweLastDate"] = sw["release_date"].max().strftime("%B %Y")
    n["CapSweNumModels"] = str(len(sw))
    n["CapSweFirstFrontier"] = f"{sw['frontier_pct'].iloc[0]:.1f}"
    n["CapSweBest"] = f"{sw['score_pct'].max():.1f}"
    n["CapSweBestModel"] = sw.loc[sw["score_pct"].idxmax(), "model"]
    y25 = sw[sw["release_date"] <= "2025-01-01"]["frontier_pct"]
    n["CapSweFrontierStartTwentyFive"] = f"{y25.iloc[-1]:.1f}" if len(y25) else "n/a"
    y26 = sw[sw["release_date"] <= "2026-01-01"]["frontier_pct"]
    n["CapSweFrontierStartTwentySix"] = f"{y26.iloc[-1]:.1f}"
    eci = out["eci"]
    recent = eci[eci["latest_month"]]
    n["CapEciLatestMonth"] = eci["release_date"].max().strftime("%B %Y")
    n["CapEciRecentN"] = str(len(recent))
    for model, key in (
        ("Claude Opus 5.5", "OpusFiveFive"),
        ("GPT-6 Astra", "GptSixAstra"),
        ("GPT-6.1 Sol", "GptSixOneSol"),
        ("GPT-6 Sol", "GptSixSol"),
    ):
        row = recent.loc[recent["model"] == model]
        if row.empty:
            raise ValueError(f"Expected recent ECI model missing: {model}")
        n[f"CapEci{key}"] = f"{row.iloc[0]['score']:.1f}"
    fs = out["frontierswe"]
    n["CapFrontierSweModelsN"] = str(len(fs))
    n["CapFrontierSweTrials"] = str(FRONTIERSWE_TRIALS)
    n["CapFrontierSweLastDate"] = fs["release_date"].max().strftime("%B %Y")
    n["CapFrontierSweTopModel"] = fs.iloc[0]["model"]
    n["CapFrontierSweTopScore"] = f"{fs.iloc[0]['mean_score_pct']:.1f}"
    fr = out["aider_frontier"]
    ad = out["aider"]
    n["CapAiderNumUsable"] = str(int(ad["usable"].sum()))
    n["CapAiderNumRows"] = str(len(ad))
    for thr, nm in ((50, "Fifty"), (60, "Sixty"), (70, "Seventy"), (80, "Eighty")):
        s = fr[fr["threshold_pct"] == thr].sort_values("month")
        if s.empty:
            continue
        n[f"CapAiderCost{nm}First"] = f"{s['min_cost_usd'].iloc[0]:.2f}"
        n[f"CapAiderCost{nm}FirstMonth"] = s["month"].iloc[0].strftime("%B %Y")
        n[f"CapAiderCost{nm}Last"] = f"{s['min_cost_usd'].iloc[-1]:.2f}"
        n[f"CapAiderCost{nm}LastMonth"] = s["month"].iloc[-1].strftime("%B %Y")
        n[f"CapAiderCost{nm}Fold"] = (
            f"{s['min_cost_usd'].iloc[0] / s['min_cost_usd'].iloc[-1]:.0f}"
        )
    return n


if __name__ == "__main__":
    o = build()
    print(o["metr_fit"].T)
    print(summary_numbers(o))
