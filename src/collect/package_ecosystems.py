"""Module 03 - growth of open-source package supply and use across ecosystems."""

from __future__ import annotations
import json
import time
import re
from datetime import date, datetime, timezone
from urllib.parse import parse_qs, urlparse
import numpy as np
import pandas as pd
import requests
from ..fetch import _key, get
from ..paths import CACHE, PROCESSED, RAW, TABLES

NS = "package_ecosystems"
RAW_DIR = RAW / "package_ecosystems"
RAW_DIR.mkdir(parents=True, exist_ok=True)
CLICKHOUSE_URL = "https://sql-clickhouse.clickhouse.com/"
CRATES_URL = "https://crates.io/api/v1/crates"
PACKAGIST_URL = "https://packagist.org/statistics"
NPM_DL_URL = "https://api.npmjs.org/downloads/range/{start}:{end}"
START = "2015-01-01"
BREAK = pd.Timestamp("2022-12-01")
AGENT_ERA = pd.Timestamp("2025-02-01")
FILTER_WINDOW_DAYS = 90
ECOSYSTEMS = ["PyPI", "crates.io", "RubyGems", "Packagist", "npm"]


def _provenance(name: str, url: str, extra: dict | None = None) -> None:
    meta = {"source": url, "retrieved_utc": datetime.now(timezone.utc).isoformat()}
    meta.update(extra or {})
    (RAW_DIR / f"{name}.provenance.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )


def retrieval_date(name: str) -> str:
    p = RAW_DIR / f"{name}.provenance.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))["retrieved_utc"][:10]
    return date.today().isoformat()


def clickhouse(sql: str) -> pd.DataFrame:
    """Run a read-only query on the public ClickHouse playground (cached via fetch.get)."""
    body = get(
        CLICKHOUSE_URL,
        params={"user": "demo", "query": sql + " FORMAT JSON"},
        namespace=NS + "_clickhouse",
        min_interval=1.0,
    )
    return pd.DataFrame(body["data"])


def _pypi_first_sql() -> str:
    return f"\nSELECT toStartOfMonth(first_upload) AS month,\n       count() AS new_packages,\n       countIf(n_versions >= 2 AND dateDiff('day', first_upload, second_upload) <= {FILTER_WINDOW_DAYS}) AS new_packages_filtered\nFROM (\n    SELECT name, min(t) AS first_upload, arraySort(groupArray(t)) AS ts, length(ts) AS n_versions,\n           if(n_versions >= 2, ts[2], toDateTime64('2100-01-01 00:00:00', 3)) AS second_upload\n    FROM (\n        SELECT lower(replaceRegexpAll(name, '[-_.]+', '-')) AS name, version, min(upload_time) AS t\n        FROM pypi.projects GROUP BY name, version\n    )\n    GROUP BY name\n)\nGROUP BY month ORDER BY month\n"


def fetch_pypi() -> pd.DataFrame:
    out = RAW_DIR / "pypi_new_monthly.csv"
    if not out.exists():
        df = clickhouse(_pypi_first_sql())
        df.to_csv(out, index=False)
        _provenance(
            "pypi_new_monthly",
            CLICKHOUSE_URL + " table pypi.projects",
            {"query": _pypi_first_sql()},
        )
    df = pd.read_csv(out, parse_dates=["month"])
    df["ecosystem"] = "PyPI"
    return df


def fetch_pypi_versions() -> pd.DataFrame:
    """New releases (distinct project-version pairs) per month, by month of first file upload."""
    out = RAW_DIR / "pypi_versions_monthly.csv"
    if not out.exists():
        sql = "SELECT toStartOfMonth(t) AS month, count() AS new_versions FROM (SELECT lower(replaceRegexpAll(name, '[-_.]+', '-')) AS n, version, min(upload_time) AS t FROM pypi.projects GROUP BY n, version) GROUP BY month ORDER BY month"
        df = clickhouse(sql)
        df.to_csv(out, index=False)
        _provenance(
            "pypi_versions_monthly",
            CLICKHOUSE_URL + " table pypi.projects",
            {"query": sql},
        )
    return pd.read_csv(out, parse_dates=["month"]).assign(ecosystem="PyPI")


SENTINELS = [
    "boto3",
    "certifi",
    "pip",
    "setuptools",
    "requests",
    "urllib3",
    "idna",
    "packaging",
    "charset-normalizer",
    "botocore",
]


def fetch_pypi_downloads() -> pd.DataFrame:
    """Monthly PyPI downloads (all projects) from the BigQuery-log mirror."""
    out = RAW_DIR / "pypi_downloads_monthly.csv"
    sent = RAW_DIR / "pypi_downloads_sentinels.csv"
    if not out.exists():
        sql = "SELECT month, sum(count) AS downloads FROM pypi.pypi_downloads_per_month GROUP BY month ORDER BY month"
        df = clickhouse(sql)
        df.to_csv(out, index=False)
        _provenance(
            "pypi_downloads_monthly",
            CLICKHOUSE_URL + " table pypi.pypi_downloads_per_month",
            {"query": sql},
        )
    if not sent.exists():
        names = ", ".join((f"'{x}'" for x in SENTINELS))
        sql = f"SELECT month, project, sum(count) AS downloads FROM pypi.pypi_downloads_per_month WHERE project IN ({names}) GROUP BY month, project ORDER BY month"
        clickhouse(sql).to_csv(sent, index=False)
    df = pd.read_csv(out, parse_dates=["month"])
    s = pd.read_csv(sent, parse_dates=["month"]).pivot(
        index="month", columns="project", values="downloads"
    )
    s = s.reindex(columns=SENTINELS).fillna(0)
    ratio = (s / s.shift(1)).median(axis=1)
    bad = (ratio < 0.75) & (s.index >= "2019-01-01")
    first_bad = s.index[bad].min() if bad.any() else None
    df = df[df["month"] >= "2018-08-01"]
    if first_bad is not None:
        df = df[df["month"] < first_bad]
    df["ecosystem"] = "PyPI"
    return df


def fetch_rubygems() -> pd.DataFrame:
    out = RAW_DIR / "rubygems_new_monthly.csv"
    if not out.exists():
        sql = "SELECT toStartOfMonth(created_at) AS month, count() AS new_packages, countIf(indexed = 't') AS new_packages_filtered FROM rubygems.rubygems GROUP BY month ORDER BY month"
        df = clickhouse(sql)
        df.to_csv(out, index=False)
        _provenance(
            "rubygems_new_monthly",
            CLICKHOUSE_URL + " table rubygems.rubygems",
            {"query": sql},
        )
    df = pd.read_csv(out, parse_dates=["month"])
    df["ecosystem"] = "RubyGems"
    return df


def fetch_crates(max_pages: int = 10000) -> pd.DataFrame:
    """All current crates with created_at via the seek-paginated API."""
    out = RAW_DIR / "crates_created.csv.gz"
    if out.exists():
        return pd.read_csv(out, parse_dates=["created_at"])
    ckpt = RAW_DIR / "crates_checkpoint.json"
    state = (
        json.loads(ckpt.read_text())
        if ckpt.exists()
        else {"seek": None, "rows": [], "pages": 0}
    )
    ns = NS + "_crates_pages"
    while state["pages"] < max_pages:
        params = {"sort": "new", "per_page": 100}
        if state["seek"]:
            params["seek"] = state["seek"]
        for attempt in range(6):
            try:
                body = get(CRATES_URL, params=params, namespace=ns, min_interval=1.05)
                break
            except requests.exceptions.RequestException:
                if attempt == 5:
                    ckpt.write_text(json.dumps(state))
                    raise
                time.sleep(10 * 2**attempt)
        (CACHE / ns / f"{_key(CRATES_URL, params)}.json").unlink(missing_ok=True)
        for c in body["crates"]:
            state["rows"].append(
                [c["name"], c["created_at"], c.get("num_versions"), c.get("downloads")]
            )
        state["pages"] += 1
        nxt = (body.get("meta") or {}).get("next_page")
        if not nxt or not body["crates"]:
            state["seek"] = None
            break
        state["seek"] = parse_qs(urlparse(nxt).query)["seek"][0]
        if state["pages"] % 50 == 0:
            ckpt.write_text(json.dumps(state))
            print(
                f"crates.io: {state['pages']} pages, {len(state['rows'])} crates, last {state['rows'][-1][1]}",
                flush=True,
            )
    df = pd.DataFrame(
        state["rows"], columns=["name", "created_at", "num_versions", "downloads"]
    )
    df = df.drop_duplicates("name")
    df.to_csv(out, index=False, compression="gzip")
    _provenance(
        "crates_created",
        CRATES_URL + "?sort=new&per_page=100 (seek pagination)",
        {"n_crates": int(len(df)), "pages": state["pages"]},
    )
    ckpt.unlink(missing_ok=True)
    return pd.read_csv(out, parse_dates=["created_at"])


def crates_monthly() -> pd.DataFrame:
    df = fetch_crates()
    df["month"] = (
        df["created_at"].dt.tz_localize(None).dt.to_period("M").dt.to_timestamp()
    )
    g = df.groupby("month").agg(
        new_packages=("name", "size"),
        new_packages_filtered=("num_versions", lambda s: int((s >= 2).sum())),
    )
    g = g.reset_index()
    g["ecosystem"] = "crates.io"
    return g


def _packagist_series() -> dict[str, pd.DataFrame]:
    html = get(PACKAGIST_URL, namespace=NS + "_packagist", as_json=False)
    charts = re.findall('data-labels="([^"]+)"\\s+data-values="([^"]+)"', html)
    out = {}
    for labels, values in charts:
        labs = labels.split(",")
        for series in values.split("|"):
            name, _, vals = series.partition(":")
            nums = [float(v) if v else np.nan for v in vals.split(",")]
            if len(nums) == len(labs):
                out[name.strip()] = pd.DataFrame({"label": labs, "value": nums})
    return out


def fetch_packagist() -> tuple[pd.DataFrame, pd.DataFrame]:
    s = _packagist_series()
    out = RAW_DIR / "packagist_statistics.json"
    out.write_text(
        json.dumps({k: v.to_dict("list") for k, v in s.items()}), encoding="utf-8"
    )
    _provenance("packagist_statistics", PACKAGIST_URL, {"series": list(s)})
    pk_key = next((k for k in s if k.lower().startswith("packages")))
    pk = s[pk_key].rename(columns={"value": "cum_packages"})
    pk["month"] = pd.to_datetime(pk["label"] + "-01")
    pk["new_packages"] = pk["cum_packages"].diff()
    vk = next((k for k in s if k.lower().startswith("versions")))
    pk["new_versions"] = s[vk]["value"].diff().values
    pk["ecosystem"] = "Packagist"
    inst_key = [k for k in s if k.lower().startswith("installs")]
    dl = pd.DataFrame()
    for k in inst_key:
        d = s[k]
        if d["label"].str.len().max() == 7:
            dl = d.rename(columns={"value": "downloads"})
            dl["month"] = pd.to_datetime(dl["label"] + "-01")
            dl["ecosystem"] = "Packagist"
    return (
        pk[["ecosystem", "month", "new_packages", "cum_packages", "new_versions"]],
        dl[["ecosystem", "month", "downloads"]],
    )


def fetch_npm_downloads(start: str = "2015-01-10") -> pd.DataFrame:
    """Whole-registry daily downloads; API serves at most 18 months per call."""
    today = pd.Timestamp.today().normalize()
    s = pd.Timestamp(start)
    frames = []
    while s < today:
        e = min(s + pd.DateOffset(days=540), today - pd.Timedelta(days=1))
        url = NPM_DL_URL.format(start=s.date(), end=e.date())
        body = get(url, namespace=NS + "_npm", min_interval=1.0)
        frames.append(pd.DataFrame(body["downloads"]))
        s = e + pd.Timedelta(days=1)
    df = pd.concat(frames).drop_duplicates("day")
    df["day"] = pd.to_datetime(df["day"])
    df.to_csv(RAW_DIR / "npm_registry_daily_downloads.csv", index=False)
    _provenance(
        "npm_registry_daily_downloads",
        "https://api.npmjs.org/downloads/range/<start>:<end>",
    )
    return df


def npm_monthly() -> pd.DataFrame:
    """Monthly registry downloads. Days reported as 0 are API gaps (not true zeros):"""
    d = fetch_npm_downloads()
    d["downloads"] = d["downloads"].where(d["downloads"] > 0)
    d["month"] = d["day"].dt.to_period("M").dt.to_timestamp()
    g = (
        d.groupby("month")
        .agg(
            mean_day=("downloads", "mean"),
            valid_days=("downloads", "count"),
            days=("day", "nunique"),
        )
        .reset_index()
    )
    g["days_in_month"] = g["month"].dt.days_in_month
    g = g[(g["valid_days"] >= 20) & (g["days"] == g["days_in_month"])]
    g["downloads"] = g["mean_day"] * g["days_in_month"]
    g["imputed_days"] = g["days_in_month"] - g["valid_days"]
    g["ecosystem"] = "npm"
    return g[["ecosystem", "month", "downloads", "imputed_days"]]


def build_new_monthly() -> pd.DataFrame:
    frames = [
        fetch_pypi().merge(
            fetch_pypi_versions(), on=["month", "ecosystem"], how="left"
        ),
        crates_monthly(),
        fetch_rubygems(),
    ]
    pk, _ = fetch_packagist()
    frames.append(pk)
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(["ecosystem", "month"])
    df["cum_packages"] = df["cum_packages"].where(
        df["ecosystem"] == "Packagist", df.groupby("ecosystem")["new_packages"].cumsum()
    )
    this_month = pd.Timestamp.today().to_period("M").to_timestamp()
    df = df[df["month"] < this_month]
    cutoff = this_month - pd.DateOffset(days=FILTER_WINDOW_DAYS + 31)
    cens = (df["month"] > cutoff) & df["ecosystem"].isin(["PyPI", "crates.io"])
    df.loc[cens, "new_packages_filtered"] = np.nan
    df = df[df["month"] >= pd.Timestamp("2010-01-01")]
    return df[
        [
            "ecosystem",
            "month",
            "new_packages",
            "new_packages_filtered",
            "cum_packages",
            "new_versions",
        ]
    ]


def build_downloads() -> pd.DataFrame:
    _, pk_dl = fetch_packagist()
    py = fetch_pypi_downloads()
    this_month = pd.Timestamp.today().to_period("M").to_timestamp()
    df = pd.concat(
        [npm_monthly(), py[["ecosystem", "month", "downloads"]], pk_dl],
        ignore_index=True,
    )
    df = df[df["month"] < this_month].sort_values(["ecosystem", "month"])
    return df


def cagr(df: pd.DataFrame, col: str = "new_packages") -> pd.DataFrame:
    """Annual growth of the yearly flow of new packages: 2017->2022 vs 2022->last 12 months."""
    rows = []
    for eco, d in df.groupby("ecosystem"):
        d = d.set_index("month")[col].dropna()
        if d.empty:
            continue
        last = d.index.max()
        ann = {y: d[str(y)].sum() for y in range(2015, 2026) if len(d[str(y)]) == 12}
        ttm = d[last - pd.DateOffset(months=11) : last].sum()
        yrs_post = (
            last - pd.DateOffset(months=5, days=14) - pd.Timestamp("2022-07-01")
        ).days / 365.25
        pre = (
            (ann[2022] / ann[2017]) ** (1 / 5) - 1
            if 2017 in ann and 2022 in ann
            else np.nan
        )
        post = (ttm / ann[2022]) ** (1 / yrs_post) - 1 if 2022 in ann else np.nan
        rows.append(
            {
                "ecosystem": eco,
                "metric": col,
                "flow_2017": ann.get(2017),
                "flow_2022": ann.get(2022),
                "flow_ttm": ttm,
                "ttm_end": last.date(),
                "cagr_2017_2022": pre,
                "cagr_2022_ttm": post,
            }
        )
    return pd.DataFrame(rows)


def yoy_intervals(df: pd.DataFrame, col: str = "new_packages") -> pd.DataFrame:
    """Mean monthly year-over-year growth (log points): pre (2016-01..2022-11), post (2022-12..last),"""
    import statsmodels.api as sm

    rows = []
    for eco, d in df.groupby("ecosystem"):
        s = d.set_index("month")[col].dropna()
        s = s[s > 0]
        yoy = np.log(s).diff(12).dropna()
        for period, mask in (
            ("pre", (yoy.index >= "2016-01-01") & (yoy.index < BREAK)),
            ("post", yoy.index >= BREAK),
            ("chatgpt_era", (yoy.index >= BREAK) & (yoy.index < AGENT_ERA)),
            ("agent_era", yoy.index >= AGENT_ERA),
        ):
            x = yoy[mask].to_numpy()
            if len(x) < 12:
                continue
            m = sm.OLS(x, np.ones(len(x))).fit(
                cov_type="HAC", cov_kwds={"maxlags": min(11, len(x) - 2)}
            )
            mu, se = (float(m.params[0]), float(m.bse[0]))
            lo, hi = (mu - 1.96 * se, mu + 1.96 * se)
            rows.append(
                {
                    "ecosystem": eco,
                    "metric": col,
                    "period": period,
                    "n_months": len(x),
                    "mean_yoy_log": mu,
                    "se": se,
                    "lo": lo,
                    "hi": hi,
                    "mean_yoy_pct": np.expm1(mu),
                    "lo_pct": np.expm1(lo),
                    "hi_pct": np.expm1(hi),
                }
            )
    return pd.DataFrame(rows)


def _tidx(m):
    if isinstance(m, pd.Timestamp):
        return (m.year - 2016) * 12 + m.month - 1
    return (m.dt.year - 2016) * 12 + m.dt.month - 1


def its(
    df: pd.DataFrame,
    col: str = "new_packages",
    start: str = "2016-01-01",
    maxlags: int = 12,
    agent_break: bool = False,
) -> pd.DataFrame:
    """Segmented regression (interrupted time series) of log monthly counts:"""
    import statsmodels.formula.api as smf

    rows = []
    for eco, d in df.groupby("ecosystem"):
        d = d[d["month"] >= start].dropna(subset=[col])
        d = d[d[col] > 0].copy()
        if len(d) < 48:
            continue
        d["y"] = np.log(d[col])
        d["t"] = _tidx(d["month"])
        d["post"] = (d["month"] >= BREAK).astype(int)
        d["t_post"] = d["post"] * (d["t"] - _tidx(BREAK))
        d["agent"] = (d["month"] >= AGENT_ERA).astype(int)
        d["t_agent"] = d["agent"] * (d["t"] - _tidx(AGENT_ERA))
        d["moy"] = d["month"].dt.month.astype(str)
        terms = ["t", "post", "t_post"] + (["agent", "t_agent"] if agent_break else [])
        m = smf.ols("y ~ " + " + ".join(terms) + " + C(moy)", data=d).fit(
            cov_type="HAC", cov_kwds={"maxlags": maxlags}
        )
        for term in terms:
            rows.append(
                {
                    "ecosystem": eco,
                    "metric": col,
                    "spec": "agent" if agent_break else "chatgpt",
                    "term": term,
                    "coef": m.params[term],
                    "se": m.bse[term],
                    "p": m.pvalues[term],
                    "n": int(m.nobs),
                    "start": d["month"].min().date(),
                    "end": d["month"].max().date(),
                    "r2": m.rsquared,
                }
            )
    return pd.DataFrame(rows)


ITS_ROWS = [
    ("PyPI", "new_packages", "new packages"),
    ("PyPI", "new_packages_filtered", "filtered"),
    ("crates.io", "new_packages", "new packages"),
    ("crates.io", "new_packages_filtered", "filtered"),
    ("RubyGems", "new_packages", "new packages"),
    ("RubyGems", "new_packages_filtered", "filtered"),
    ("Packagist", "new_packages", "net additions"),
    ("npm", "downloads", "downloads"),
    ("PyPI", "downloads", "downloads"),
    ("Packagist", "downloads", "installs"),
]
NAME = {
    "PyPI": "Pypi",
    "crates.io": "Crates",
    "RubyGems": "Rubygems",
    "Packagist": "Packagist",
    "npm": "Npm",
}
SUF = {
    "new_packages": "",
    "new_packages_filtered": "Filtered",
    "downloads": "Downloads",
}


def _thousands(x: float) -> str:
    return f"{x:,.0f}".replace(",", "{,}")


def key_numbers(res: dict[str, pd.DataFrame]) -> dict[str, str]:
    cg, yoy, it, new, dl = (
        res["cagr"],
        res["yoy"],
        res["its"],
        res["new"],
        res["downloads"],
    )
    n: dict[str, str] = {
        "PkgLastMonth": new["month"].max().strftime("%B %Y"),
        "PkgChatgptBreak": BREAK.strftime("%B %Y"),
        "PkgAgentBreak": AGENT_ERA.strftime("%B %Y"),
        "PkgFilterWindowDays": str(FILTER_WINDOW_DAYS),
    }
    for _, r in cg.iterrows():
        suf = SUF[r.metric]
        if pd.notna(r.cagr_2017_2022):
            n[f"Pkg{NAME[r.ecosystem]}{suf}CagrPre"] = f"{100 * r.cagr_2017_2022:.0f}"
        if pd.notna(r.cagr_2022_ttm):
            n[f"Pkg{NAME[r.ecosystem]}{suf}CagrPost"] = f"{100 * r.cagr_2022_ttm:.0f}"
        if suf == "" and pd.notna(r.flow_ttm):
            n[f"Pkg{NAME[r.ecosystem]}NewTTM"] = _thousands(r.flow_ttm)
            if pd.notna(r.flow_2022):
                n[f"Pkg{NAME[r.ecosystem]}NewTwentyTwentyTwo"] = _thousands(r.flow_2022)
    for _, r in yoy.iterrows():
        per = {
            "pre": "Pre",
            "post": "Post",
            "chatgpt_era": "ChatEra",
            "agent_era": "AgentEra",
        }[r.period]
        n[f"Pkg{NAME[r.ecosystem]}{SUF[r.metric]}YoY{per}"] = (
            f"{100 * r.mean_yoy_pct:.0f}"
        )
    for _, r in it.iterrows():
        if r.spec == "chatgpt":
            term = {"t": "Trend", "post": "Level", "t_post": "Slope"}[r.term]
            key = f"Pkg{NAME[r.ecosystem]}{SUF[r.metric]}Its{term}"
        elif r.term in ("agent", "t_agent"):
            term = {"agent": "Level", "t_agent": "Slope"}[r.term]
            key = f"Pkg{NAME[r.ecosystem]}{SUF[r.metric]}Agent{term}"
        else:
            continue
        scale = 100 if r.term in ("post", "agent") else 1200
        n[key] = f"{scale * r.coef:.1f}"
        n[key + "P"] = f"{r.p:.3f}"
    last = new["month"].max()
    cur = (new["month"] >= f"{last.year}-01-01") & (new["month"] <= last)
    prev = (new["month"] >= f"{last.year - 1}-01-01") & (
        new["month"] <= last - pd.DateOffset(years=1)
    )
    for eco in ["PyPI", "crates.io", "RubyGems", "Packagist"]:
        e = new["ecosystem"] == eco
        for col, lab in (("new_packages", "New"), ("new_versions", "Versions")):
            a, b = (new.loc[e & cur, col].sum(), new.loc[e & prev, col].sum())
            if b > 0 and a > 0:
                n[f"Pkg{NAME[eco]}{lab}YtdGrowth"] = f"{100 * (a / b - 1):.0f}"
    for eco in ["npm", "PyPI", "Packagist"]:
        s = dl[dl.ecosystem == eco].set_index("month")["downloads"]
        last = s.index.max()
        if last - pd.DateOffset(years=1) in s.index:
            n[f"Pkg{NAME[eco]}DownloadsYoY"] = (
                f"{100 * (s[last] / s[last - pd.DateOffset(years=1)] - 1):.0f}"
            )
        n[f"Pkg{NAME[eco]}DownloadsLast"] = _thousands(s[last] / 1000000000.0)
        n[f"Pkg{NAME[eco]}DownloadsLastMonth"] = last.strftime("%B %Y")
    return n


def run() -> dict[str, pd.DataFrame]:
    new = build_new_monthly()
    new.to_csv(PROCESSED / "package_ecosystems_new_monthly.csv", index=False)
    dl = build_downloads()
    dl.to_csv(PROCESSED / "package_ecosystems_downloads.csv", index=False)
    growth = pd.concat(
        [cagr(new), cagr(new, "new_packages_filtered")], ignore_index=True
    )
    growth.to_csv(PROCESSED / "package_ecosystems_cagr.csv", index=False)
    yoy = pd.concat(
        [yoy_intervals(new), yoy_intervals(new, "new_packages_filtered")],
        ignore_index=True,
    )
    yoy.to_csv(PROCESSED / "package_ecosystems_yoy.csv", index=False)
    dl_w = dl.rename(columns={"downloads": "count"})
    its_df = pd.concat(
        [
            its(new, c, agent_break=a)
            for c in ("new_packages", "new_packages_filtered")
            for a in (False, True)
        ]
        + [
            its(dl_w, "count", start="2017-01-01", agent_break=a).assign(
                metric="downloads"
            )
            for a in (False, True)
        ],
        ignore_index=True,
    )
    its_df.to_csv(PROCESSED / "package_ecosystems_its.csv", index=False)
    meta = {
        "retrieved": min(
            (
                retrieval_date(x)
                for x in (
                    "pypi_new_monthly",
                    "rubygems_new_monthly",
                    "crates_created",
                    "packagist_statistics",
                    "npm_registry_daily_downloads",
                )
            )
        ),
        "last_month": str(new["month"].max().date()),
    }
    (PROCESSED / "package_ecosystems_meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    return {"new": new, "downloads": dl, "cagr": growth, "yoy": yoy, "its": its_df}
