"""Module 04 - public GitHub repository creation trends."""

from __future__ import annotations
import functools
import json
import time
from datetime import date, datetime, timezone
import pandas as pd
from src import fetch
from src.paths import CACHE, PROCESSED, RAW

MODULE = "github_repo_trends"
SEARCH_URL = "https://api.github.com/search/repositories"
NAMESPACE = "gh_search_repos"
STAB_NAMESPACE = "gh_search_repos_stability"
MIN_INTERVAL = 2.2
START = "2012-01"
RAW_DIR = RAW / MODULE
RAW_DIR.mkdir(parents=True, exist_ok=True)
LANGUAGES = ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "C#"]
_ALT_UNION = (
    '"alternative to" OR "open source alternative" OR "self-hosted alternative"'
)
SERIES: dict[str, tuple[str, str, str]] = {
    "all": ("", "base", "All public repositories"),
    "stars1": ("stars:>=1", "base", "Repositories with >=1 star"),
    "stars10": ("stars:>=10", "base", "Repositories with >=10 stars"),
    "alt_union": (
        f"{_ALT_UNION} in:description,readme",
        "alternative",
        "Any alternative phrase",
    ),
    "alt_union_s10": (
        f"{_ALT_UNION} in:description,readme stars:>=10",
        "alternative",
        "Any alternative phrase, >=10 stars",
    ),
    "alt_union_desc": (
        f"{_ALT_UNION} in:description",
        "alternative",
        "Any alternative phrase (description only)",
    ),
    "alt_union_desc_s10": (
        f"{_ALT_UNION} in:description stars:>=10",
        "alternative",
        "Any alternative phrase (description only), >=10 stars",
    ),
    "alt_to": (
        '"alternative to" in:description,readme',
        "alternative",
        '"alternative to"',
    ),
    "alt_to_s10": (
        '"alternative to" in:description,readme stars:>=10',
        "alternative",
        '"alternative to", >=10 stars',
    ),
    "alt_to_desc": (
        '"alternative to" in:description',
        "alternative",
        '"alternative to" (description only)',
    ),
    "oss_alt": (
        '"open source alternative" in:description,readme',
        "alternative",
        '"open source alternative"',
    ),
    "oss_alt_s10": (
        '"open source alternative" in:description,readme stars:>=10',
        "alternative",
        '"open source alternative", >=10 stars',
    ),
    "selfhost_alt": (
        '"self-hosted alternative" in:description,readme',
        "alternative",
        '"self-hosted alternative"',
    ),
    "selfhost_alt_s10": (
        '"self-hosted alternative" in:description,readme stars:>=10',
        "alternative",
        '"self-hosted alternative", >=10 stars',
    ),
    "clone_of": ('"clone of" in:description,readme', "clone", '"clone of"'),
    "clone_of_s10": (
        '"clone of" in:description,readme stars:>=10',
        "clone",
        '"clone of", >=10 stars',
    ),
    "clone_of_desc": (
        '"clone of" in:description',
        "clone",
        '"clone of" (description only)',
    ),
    "oss_clone": (
        '"open source clone" in:description,readme',
        "clone",
        '"open source clone"',
    ),
    "oss_clone_s10": (
        '"open source clone" in:description,readme stars:>=10',
        "clone",
        '"open source clone", >=10 stars',
    ),
}
for _lang in LANGUAGES:
    SERIES[f"lang_{_lang}"] = (f'language:"{_lang}"', "language", _lang)


@functools.lru_cache(maxsize=1)
def _headers() -> dict:
    tok = fetch.github_token()
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def last_full_month(today: date | None = None) -> str:
    today = today or date.today()
    p = pd.Period(today, freq="M") - 1
    return str(p)


def months(start: str = START, end: str | None = None) -> list[pd.Period]:
    end = end or last_full_month()
    return list(pd.period_range(start, end, freq="M"))


def window(p: pd.Period) -> str:
    return f"created:{p.start_time:%Y-%m-%d}..{p.end_time:%Y-%m-%d}"


def build_query(prefix: str, p: pd.Period) -> str:
    return f"{prefix} {window(p)}".strip()


def _cache_time(params: dict, namespace: str = NAMESPACE) -> str | None:
    path = CACHE / namespace / f"{fetch._key(SEARCH_URL, params)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")).get("retrieved_utc")
    return None


def search_count(q: str, *, namespace: str = NAMESPACE, refresh: bool = False) -> dict:
    """total_count for a repository-search query (one request, per_page=1)."""
    params = {"q": q, "per_page": 1}
    body = fetch.get(
        SEARCH_URL,
        params,
        namespace=namespace,
        headers=dict(_headers()),
        min_interval=MIN_INTERVAL,
        refresh=refresh,
    )
    tries = 0
    while body.get("incomplete_results") and tries < 2:
        tries += 1
        body = fetch.get(
            SEARCH_URL,
            params,
            namespace=namespace,
            headers=dict(_headers()),
            min_interval=MIN_INTERVAL,
            refresh=True,
        )
    return {
        "total_count": body.get("total_count"),
        "incomplete_results": bool(body.get("incomplete_results")),
        "retrieved_utc": _cache_time(params, namespace),
    }


def collect(
    series: list[str] | None = None,
    start: str = START,
    end: str | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Query every (series, month) cell; cached, so re-runs are cheap."""
    keys = series or list(SERIES)
    rows = []
    ms = months(start, end)
    for k in keys:
        prefix, group, label = SERIES[k]
        t0 = time.time()
        for p in ms:
            q = build_query(prefix, p)
            try:
                r = search_count(q)
            except Exception as exc:
                r = {
                    "total_count": None,
                    "incomplete_results": None,
                    "retrieved_utc": None,
                    "error": str(exc)[:200],
                }
            rows.append(
                {
                    "series": k,
                    "group": group,
                    "label": label,
                    "month": str(p),
                    "query": q,
                    **r,
                }
            )
        if verbose:
            print(
                f"[{datetime.now():%H:%M:%S}] {k}: {len(ms)} months in {time.time() - t0:.0f}s",
                flush=True,
            )
    df = pd.DataFrame(rows)
    if series is None:
        df.to_csv(RAW_DIR / "search_counts.csv", index=False)
    return df


STABILITY_QUERIES = [
    ("all", "2016-06"),
    ("all", "2023-01"),
    ("all", "2025-06"),
    ("stars10", "2023-01"),
    ("alt_union", "2019-06"),
    ("alt_union", "2023-01"),
    ("alt_union", "2025-06"),
    ("alt_to_s10", "2024-03"),
    ("clone_of", "2023-01"),
    ("lang_Rust", "2024-03"),
]


def stability(n_reps: int = 3, gap_s: float = 0.0, tag: str = "") -> pd.DataFrame:
    """Re-issue a fixed set of queries n_reps times with the cache bypassed."""
    rows = []
    for rep in range(n_reps):
        for k, m in STABILITY_QUERIES:
            q = build_query(SERIES[k][0], pd.Period(m, freq="M"))
            body = fetch.get(
                SEARCH_URL,
                {"q": q, "per_page": 1},
                namespace=STAB_NAMESPACE,
                headers=dict(_headers()),
                min_interval=MIN_INTERVAL,
                refresh=True,
            )
            rows.append(
                {
                    "series": k,
                    "month": m,
                    "query": q,
                    "rep": rep,
                    "tag": tag,
                    "total_count": body.get("total_count"),
                    "incomplete_results": body.get("incomplete_results"),
                    "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                }
            )
        if gap_s and rep < n_reps - 1:
            time.sleep(gap_s)
    df = pd.DataFrame(rows)
    out = RAW_DIR / "stability_runs.csv"
    if out.exists():
        df = pd.concat([pd.read_csv(out), df], ignore_index=True)
    df.to_csv(out, index=False)
    return df


def summarise_stability(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = df if df is not None else pd.read_csv(RAW_DIR / "stability_runs.csv")
    g = df.groupby(["series", "month"])["total_count"]
    out = g.agg(n="count", mean="mean", min="min", max="max", std="std").reset_index()
    out["range_pct"] = 100 * (out["max"] - out["min"]) / out["mean"]
    out["cv_pct"] = 100 * out["std"] / out["mean"]
    main = (
        pd.read_csv(RAW_DIR / "search_counts.csv")
        if (RAW_DIR / "search_counts.csv").exists()
        else None
    )
    if main is not None:
        out = out.merge(
            main[["series", "month", "total_count"]].rename(
                columns={"total_count": "main_value"}
            ),
            on=["series", "month"],
            how="left",
        )
        out["main_dev_pct"] = 100 * (out["main_value"] - out["mean"]) / out["mean"]
    return out


def process(raw: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    """Build tidy processed tables from the raw long table."""
    raw = raw if raw is not None else pd.read_csv(RAW_DIR / "search_counts.csv")
    wide = raw.pivot(index="month", columns="series", values="total_count").sort_index()
    wide.index.name = "month"
    monthly = raw[
        ["month", "series", "group", "label", "total_count", "incomplete_results"]
    ].rename(columns={"total_count": "count"})
    monthly.to_csv(PROCESSED / f"{MODULE}_monthly.csv", index=False)
    rate_rows = []
    for k, (_, group, label) in SERIES.items():
        if group not in ("alternative", "clone") or k not in wide:
            continue
        denom = "stars10" if k.endswith("_s10") else "all"
        r = 100000.0 * wide[k] / wide[denom]
        for m, v in r.items():
            rate_rows.append(
                {
                    "month": m,
                    "series": k,
                    "group": group,
                    "label": label,
                    "denominator": denom,
                    "count": wide.at[m, k],
                    "denominator_count": wide.at[m, denom],
                    "rate_per_100k": v,
                }
            )
    rates = pd.DataFrame(rate_rows)
    rates.to_csv(PROCESSED / f"{MODULE}_rates.csv", index=False)
    lang_rows = []
    for lang in LANGUAGES:
        k = f"lang_{lang}"
        if k not in wide:
            continue
        for m, v in wide[k].items():
            lang_rows.append(
                {
                    "month": m,
                    "language": lang,
                    "count": v,
                    "all_count": wide.at[m, "all"],
                    "share_pct": 100 * v / wide.at[m, "all"],
                }
            )
    langs = pd.DataFrame(lang_rows)
    langs.to_csv(PROCESSED / f"{MODULE}_languages.csv", index=False)
    ret = pd.to_datetime(raw["retrieved_utc"].dropna(), utc=True, format="ISO8601")
    meta = {
        "retrieved_first": f"{ret.min():%Y-%m-%d}",
        "retrieved_last": f"{ret.max():%Y-%m-%d}",
        "first_month": str(wide.index.min()),
        "last_month": str(wide.index.max()),
        "n_cells": int(raw["total_count"].notna().sum()),
        "n_incomplete": int(raw["incomplete_results"].fillna(False).astype(bool).sum()),
    }
    (PROCESSED / f"{MODULE}_meta.json").write_text(
        json.dumps(meta, indent=1), encoding="utf-8"
    )
    out = {
        "monthly": monthly,
        "rates": rates,
        "languages": langs,
        "wide": wide,
        "meta": meta,
    }
    if (RAW_DIR / "stability_runs.csv").exists():
        stab = summarise_stability()
        stab.to_csv(PROCESSED / f"{MODULE}_stability.csv", index=False)
        out["stability"] = stab
    return out


def annual(wide: pd.DataFrame) -> pd.DataFrame:
    """Calendar-year sums (complete years only) for headline numbers."""
    w = wide.copy()
    w.index = pd.PeriodIndex(w.index, freq="M")
    yr = w.groupby(w.index.year).agg(["sum", "count"])
    full = yr.xs("count", axis=1, level=1).min(axis=1) == 12
    return yr.xs("sum", axis=1, level=1)[full]


if __name__ == "__main__":
    stability(n_reps=3, tag="start")
    df = collect()
    stability(n_reps=3, tag="end")
    process(df)
_YW = {
    2012: "Twelve",
    2015: "Fifteen",
    2017: "Seventeen",
    2018: "Eighteen",
    2019: "Nineteen",
    2020: "Twenty",
    2021: "TwentyOne",
    2022: "TwentyTwo",
    2023: "TwentyThree",
    2024: "TwentyFour",
    2025: "TwentyFive",
    2026: "TwentySix",
}


def key_numbers(out: dict) -> dict[str, str]:
    """Return summary values from the processed data."""
    w = out["wide"].copy()
    w.index = pd.PeriodIndex(w.index, freq="M")
    last = w.index.max()
    l12 = w.loc[last - 11 : last]
    p12 = w.loc[last - 23 : last - 12]
    yr = annual(out["wide"])
    rate = out["rates"].pivot(index="month", columns="series", values="rate_per_100k")
    rate.index = pd.PeriodIndex(rate.index, freq="M")
    ry = rate.groupby(rate.index.year).mean()
    r12 = rate.loc[last - 11 : last].mean()

    def rate_l12(k_num, k_den):
        return 100000.0 * l12[k_num].sum() / l12[k_den].sum()

    n = {
        "RepoLastMonth": f"{last.strftime('%B %Y')}",
        "RepoFirstMonth": f"{w.index.min().strftime('%B %Y')}",
        "RepoAllLastTwelveM": f"{l12['all'].sum() / 1000000.0:.1f}",
        "RepoAllPrevTwelveM": f"{p12['all'].sum() / 1000000.0:.1f}",
        "RepoAllGrowthTwelveM": f"{100 * (l12['all'].sum() / p12['all'].sum() - 1):.0f}",
        "RepoStarsTenGrowthTwelveM": f"{100 * (l12['stars10'].sum() / p12['stars10'].sum() - 1):.0f}",
        "RepoStarsOneShareLastTwelveM": f"{100 * l12['stars1'].sum() / l12['all'].sum():.1f}",
    }
    for y in (2019, 2022, 2024, 2025):
        if y in yr.index:
            n[f"RepoAll{_YW[y]}"] = f"{yr.at[y, 'all'] / 1000000.0:.1f}"
            n[f"RepoStarsTen{_YW[y]}"] = f"{yr.at[y, 'stars10'] / 1000.0:.0f}"
            n[f"AltRate{_YW[y]}"] = (
                f"{100000.0 * yr.at[y, 'alt_union'] / yr.at[y, 'all']:.0f}"
            )
            n[f"AltDescRate{_YW[y]}"] = (
                f"{100000.0 * yr.at[y, 'alt_to_desc'] / yr.at[y, 'all']:.1f}"
            )
            n[f"AltSTenRate{_YW[y]}"] = (
                f"{100000.0 * yr.at[y, 'alt_union_s10'] / yr.at[y, 'stars10']:.0f}"
            )
            n[f"CloneRate{_YW[y]}"] = (
                f"{100000.0 * yr.at[y, 'clone_of'] / yr.at[y, 'all']:.0f}"
            )
            n[f"CloneDescRate{_YW[y]}"] = (
                f"{100000.0 * yr.at[y, 'clone_of_desc'] / yr.at[y, 'all']:.1f}"
            )
            n[f"AltCount{_YW[y]}"] = f"{yr.at[y, 'alt_union']:,.0f}".replace(",", "{,}")
    n["AltRateLastTwelveM"] = f"{rate_l12('alt_union', 'all'):.0f}"
    n["AltDescRateLastTwelveM"] = f"{rate_l12('alt_to_desc', 'all'):.1f}"
    n["AltSTenRateLastTwelveM"] = f"{rate_l12('alt_union_s10', 'stars10'):.0f}"
    n["CloneRateLastTwelveM"] = f"{rate_l12('clone_of', 'all'):.0f}"
    n["CloneDescRateLastTwelveM"] = f"{rate_l12('clone_of_desc', 'all'):.1f}"
    n["AltCountLastTwelveM"] = f"{l12['alt_union'].sum():,.0f}".replace(",", "{,}")
    n["AltCountGrowthTwelveM"] = (
        f"{100 * (l12['alt_union'].sum() / p12['alt_union'].sum() - 1):.0f}"
    )
    n["AltRateChangeVsTwentyTwo"] = (
        f"{100 * (rate_l12('alt_union', 'all') / (100000.0 * yr.at[2022, 'alt_union'] / yr.at[2022, 'all']) - 1):.0f}"
    )
    n["AltDescRateChangeVsTwentyTwo"] = (
        f"{100 * (rate_l12('alt_to_desc', 'all') / (100000.0 * yr.at[2022, 'alt_to_desc'] / yr.at[2022, 'all']) - 1):.0f}"
    )
    n["AltSTenRateChangeVsTwentyTwo"] = (
        f"{100 * (rate_l12('alt_union_s10', 'stars10') / (100000.0 * yr.at[2022, 'alt_union_s10'] / yr.at[2022, 'stars10']) - 1):.0f}"
    )

    def yrate(y, k_num, k_den):
        return 100000.0 * yr.at[y, k_num] / yr.at[y, k_den]

    for y in (2017, 2019, 2022, 2024, 2025):
        n[f"AltUDescRate{_YW[y]}"] = f"{yrate(y, 'alt_union_desc', 'all'):.1f}"
    n["AltUDescRateLastTwelveM"] = f"{rate_l12('alt_union_desc', 'all'):.1f}"
    n["AltUDescRateChangeVsTwentyTwo"] = (
        f"{100 * (rate_l12('alt_union_desc', 'all') / yrate(2022, 'alt_union_desc', 'all') - 1):.0f}"
    )
    n["AltUDescCountLastTwelveM"] = f"{l12['alt_union_desc'].sum():,.0f}".replace(
        ",", "{,}"
    )
    n["AltSTenRateSeventeen"] = f"{yrate(2017, 'alt_union_s10', 'stars10'):.0f}"
    n["AltSTenPreTrendPct"] = (
        f"{100 * (yrate(2022, 'alt_union_s10', 'stars10') / yrate(2017, 'alt_union_s10', 'stars10') - 1):.0f}"
    )
    n["AltRatePreTrendPct"] = (
        f"{100 * (yrate(2022, 'alt_union_desc', 'all') / yrate(2017, 'alt_union_desc', 'all') - 1):.0f}"
    )
    for k, word in [("oss_alt", "OssAlt"), ("selfhost_alt", "SelfhostAlt")]:
        n[f"{word}RateTwentyTwo"] = f"{yrate(2022, k, 'all'):.1f}"
        n[f"{word}RateLastTwelveM"] = f"{rate_l12(k, 'all'):.1f}"
        n[f"{word}STenRateTwentyTwo"] = f"{yrate(2022, k + '_s10', 'stars10'):.0f}"
        n[f"{word}STenRateLastTwelveM"] = f"{rate_l12(k + '_s10', 'stars10'):.0f}"
    n["CloneRateChangeVsTwentyTwo"] = (
        f"{100 * (rate_l12('clone_of', 'all') / yrate(2022, 'clone_of', 'all') - 1):.0f}"
    )
    n["CloneDescRateChangeVsTwentyTwo"] = (
        f"{100 * (rate_l12('clone_of_desc', 'all') / yrate(2022, 'clone_of_desc', 'all') - 1):.0f}"
    )
    n["RepoStarsOneGrowthTwelveM"] = (
        f"{100 * (l12['stars1'].sum() / p12['stars1'].sum() - 1):.0f}"
    )
    art = w.loc["2018-01":"2018-10"]
    n["ReadmeArtefactRate"] = (
        f"{100000.0 * art['alt_union'].sum() / art['all'].sum():.0f}"
    )
    langs = out["languages"].copy()
    langs["month"] = pd.PeriodIndex(langs["month"], freq="M")
    for lang, word in [
        ("Python", "Python"),
        ("TypeScript", "TypeScript"),
        ("JavaScript", "JavaScript"),
        ("Java", "Java"),
        ("Rust", "Rust"),
    ]:
        s = langs[langs["language"] == lang].set_index("month")
        n[f"Lang{word}ShareTwentyTwo"] = (
            f"{100 * s.loc[s.index.year == 2022, 'count'].sum() / s.loc[s.index.year == 2022, 'all_count'].sum():.1f}"
        )
        n[f"Lang{word}ShareLastTwelveM"] = (
            f"{100 * s.loc[last - 11:last, 'count'].sum() / s.loc[last - 11:last, 'all_count'].sum():.1f}"
        )
    if "stability" in out:
        st = out["stability"]
        n["StabMaxRangePct"] = f"{st['range_pct'].max():.2f}"
        n["StabMedianRangePct"] = f"{st['range_pct'].median():.2f}"
    _ = r12
    return {"Ght" + k: v for k, v in n.items()}
