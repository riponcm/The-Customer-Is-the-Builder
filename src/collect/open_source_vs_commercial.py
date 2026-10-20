"""Module 10 - open-source alternatives vs the commercial products they position against."""

from __future__ import annotations
import math
import re
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from src.fetch import get, github_token
from src.paths import DATA, PROCESSED, RAW

MODULE = "10_open_source_vs_commercial"
RAW_DIR = RAW / MODULE
RAW_DIR.mkdir(parents=True, exist_ok=True)
PRODUCTS_CSV = DATA / "sample" / "products_pilot.csv"


def out(name: str):
    return PROCESSED / f"{MODULE}_{name}.csv"


SEARCH_PAGES = 3
SEARCH_MIN_INTERVAL = 4.5
MIN_STARS = 50
PROXIMITY_CHARS = 40
TOP_K = 3
STAR_PAGE_BUDGET = 40
STAR_PAGE_CAP = 400
PAGEVIEWS_START, PAGEVIEWS_END = ("2016010100", "2026093000")
CHATGPT_DATE = pd.Timestamp("2022-11-30")
AGENT_YEAR_DATE = pd.Timestamp("2025-01-01")
AUTHOR_LOGINS = {"riponcm"}
WIKI_UA = {
    "User-Agent": "software-substitution-research/0.1 (academic research project, University of Utah; Wikimedia pageviews pilot) python-requests"
}
LAUNCH = {
    "Screen Studio": (
        "2022-07-01",
        2022,
        "https://trainn.co/blog/what-is-screen-studio/",
        "founded/started 2022 per secondary profile; month unknown (mid-year used)",
    ),
    "Loom": (
        "2016-06-01",
        2016,
        "https://en.wikipedia.org/wiki/Loom_(company)",
        "Chrome extension released June 2016 (company founded 2015)",
    ),
    "Grammarly": (
        "2009-07-01",
        2009,
        "https://en.wikipedia.org/wiki/Grammarly",
        "initial release 1 July 2009",
    ),
    "QuillBot": (
        "2017-07-01",
        2017,
        "https://en.wikipedia.org/wiki/QuillBot",
        "developed in 2017; month unknown",
    ),
    "Adobe Acrobat": (
        "1993-06-15",
        1993,
        "https://en.wikipedia.org/wiki/Adobe_Acrobat",
        "initial release 15 June 1993",
    ),
    "Smallpdf": (
        "2013-08-01",
        2013,
        "https://en.wikipedia.org/wiki/Smallpdf",
        "founded August 2013",
    ),
    "Adobe Photoshop": (
        "1990-02-19",
        1990,
        "https://en.wikipedia.org/wiki/Adobe_Photoshop",
        "initial release 19 February 1990",
    ),
    "Canva": (
        "2013-08-26",
        2013,
        "https://en.wikipedia.org/wiki/Canva",
        "public launch August 2013 (TechCrunch 26 Aug 2013)",
    ),
    "Notion": (
        "2016-08-01",
        2016,
        "https://en.wikipedia.org/wiki/Notion_(productivity_software)",
        "first released 2016, v1.0 August 2016",
    ),
    "Trello": (
        "2011-09-13",
        2011,
        "https://en.wikipedia.org/wiki/Trello",
        "released 13 September 2011",
    ),
    "Postman": (
        "2012-07-01",
        2012,
        "https://en.wikipedia.org/wiki/Postman_(software)",
        "started 2012 as Chrome app side project; month unknown",
    ),
    "Retool": (
        "2017-07-01",
        2017,
        "https://breakoutstartups.substack.com/p/breakout-startups-16-retool",
        "founded 2017 (YC W17); month unknown",
    ),
}


def products() -> pd.DataFrame:
    return pd.read_csv(PRODUCTS_CSV, dtype=str).fillna("")


def _gh_headers(accept: str = "application/vnd.github+json") -> dict:
    h = {"Accept": accept, "X-GitHub-Api-Version": "2022-11-28"}
    tok = github_token()
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def search_names(product: str, vendor: str) -> list[str]:
    """Product name plus one mechanical alias: when the product name starts with the"""
    names = [product]
    if vendor and product.lower().startswith(vendor.lower() + " "):
        names.append(product[len(vendor) + 1 :])
    return names


def search_query(name: str) -> str:
    return f'"{name} alternative" OR "alternative to {name}" in:name,description,readme'


def discover_candidates(pages: int = SEARCH_PAGES) -> pd.DataFrame:
    rows, meta = ([], [])
    for p in products().itertuples():
        for name in search_names(p.product, p.vendor):
            q = search_query(name)
            for page in range(1, pages + 1):
                body = get(
                    "https://api.github.com/search/repositories",
                    {
                        "q": q,
                        "sort": "stars",
                        "order": "desc",
                        "per_page": 100,
                        "page": page,
                    },
                    namespace="m10_gh_search",
                    headers=_gh_headers(),
                    min_interval=SEARCH_MIN_INTERVAL,
                )
                if page == 1:
                    meta.append(
                        {
                            "product": p.product,
                            "query": q,
                            "total_count": body["total_count"],
                            "incomplete_results": body["incomplete_results"],
                        }
                    )
                for i, it in enumerate(body["items"]):
                    rows.append(
                        {
                            "product": p.product,
                            "category": p.category,
                            "query_name": name,
                            "search_rank": (page - 1) * 100 + i + 1,
                            "repo": it["full_name"],
                            "owner": it["owner"]["login"],
                            "html_url": it["html_url"],
                            "description": (it.get("description") or "").strip(),
                            "homepage": it.get("homepage") or "",
                            "stars": it["stargazers_count"],
                            "forks": it["forks_count"],
                            "created_at": it["created_at"],
                            "pushed_at": it["pushed_at"],
                            "license": (it.get("license") or {}).get("spdx_id") or "",
                            "archived": bool(it["archived"]),
                            "fork": bool(it["fork"]),
                            "language": it.get("language") or "",
                            "topics": ";".join(it.get("topics") or []),
                        }
                    )
                if len(body["items"]) < 100:
                    break
    df = pd.DataFrame(rows)
    df = (
        df.sort_values(["product", "search_rank"])
        .groupby(["product", "repo"], as_index=False)
        .first()
    )
    df["retrieved_by_search"] = True
    pd.DataFrame(meta).to_csv(RAW_DIR / "search_queries.csv", index=False)
    return cross_attribute(df)


def cross_attribute(df: pd.DataFrame) -> pd.DataFrame:
    """A repository retrieved by product A's search whose description positions it as an"""
    prod = products().set_index("product")
    pool = df.drop_duplicates("repo")
    have = set(zip(df["product"], df["repo"]))
    extra = []
    for p in prod.index:
        names = search_names(p, prod.loc[p, "vendor"])
        for r in pool.itertuples(index=False):
            if (p, r.repo) not in have and positions_as_alternative(
                r.description, names
            ):
                d = r._asdict()
                d.update(
                    product=p,
                    category=prod.loc[p, "category"],
                    query_name="",
                    search_rank=np.nan,
                    retrieved_by_search=False,
                )
                extra.append(d)
    return pd.concat([df, pd.DataFrame(extra)], ignore_index=True) if extra else df


LIST_PATTERN = re.compile(
    "\\bawesome\\b|\\bcurated\\b|\\blist of\\b|\\balternatives\\b|\\bdirectory\\b", re.I
)


def _name_regex(name: str) -> str:
    parts = [re.escape(w) for w in name.split()]
    return "\\b" + "[\\s\\-]?".join(parts) + "\\b"


def positions_as_alternative(desc: str, names: list[str]) -> bool:
    """Description names the product and the word 'alternative' within PROXIMITY_CHARS."""
    if not desc:
        return False
    alt = [m.start() for m in re.finditer("\\balternative\\b", desc, re.I)]
    if not alt:
        return False
    for n in names:
        for m in re.finditer(_name_regex(n), desc, re.I):
            if any((abs(m.start() - a) <= PROXIMITY_CHARS for a in alt)):
                return True
    return False


def apply_inclusion_rule(cands: pd.DataFrame) -> pd.DataFrame:
    prod = products().set_index("product")
    df = cands.copy()
    df["rule_positioning"] = [
        positions_as_alternative(d, search_names(p, prod.loc[p, "vendor"]))
        for d, p in zip(df["description"], df["product"])
    ]
    df["rule_not_list"] = ~(
        df["description"].str.contains(LIST_PATTERN)
        | df["repo"].str.split("/").str[1].str.contains(LIST_PATTERN)
    )
    df["rule_not_archived"] = ~df["archived"]
    df["rule_not_fork"] = ~df["fork"]
    df["rule_min_stars"] = df["stars"] >= MIN_STARS
    df["author_conflict_of_interest"] = df["owner"].str.lower().isin(AUTHOR_LOGINS)
    df["included"] = (
        df[
            [
                "rule_positioning",
                "rule_not_list",
                "rule_not_archived",
                "rule_not_fork",
                "rule_min_stars",
            ]
        ].all(axis=1)
        & ~df["author_conflict_of_interest"]
    )
    df["text_match"] = (
        df["rule_positioning"]
        & df["rule_not_list"]
        & df["rule_not_fork"]
        & ~df["author_conflict_of_interest"]
    )
    df = df[~df["author_conflict_of_interest"]].copy()
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_localize(None)
    df["pushed_at"] = pd.to_datetime(df["pushed_at"], utc=True).dt.tz_localize(None)
    df["rank_in_product"] = (
        df[df["included"]]
        .groupby("product")["stars"]
        .rank(ascending=False, method="first")
    )
    df["top_k"] = df["rank_in_product"] <= TOP_K
    vs = df["text_match"] & df["rule_min_stars"]
    df["rank_viability"] = (
        df[vs].groupby("product")["stars"].rank(ascending=False, method="first")
    )
    df["viability_sample"] = df["rank_viability"] <= TOP_K
    return df.sort_values(["product", "stars"], ascending=[True, False])


def _stargazer_page(repo: str, page: int) -> list[dict]:
    return get(
        f"https://api.github.com/repos/{repo}/stargazers",
        {"per_page": 100, "page": int(page)},
        namespace="m10_gh_stargazers",
        headers=_gh_headers("application/vnd.github.star+json"),
        min_interval=0.25,
    )


def star_points(repo: str, total_stars: int) -> pd.DataFrame:
    """(n-th star, starred_at) anchor points."""
    n_pages = max(1, math.ceil(total_stars / 100))
    served = min(n_pages, STAR_PAGE_CAP)
    if served <= STAR_PAGE_BUDGET:
        pages, method = (list(range(1, served + 1)), "all_pages")
    else:
        pages = sorted(
            {int(x) for x in np.linspace(1, served, STAR_PAGE_BUDGET).round()}
        )
        method = (
            "sampled_pages" if n_pages <= STAR_PAGE_CAP else "sampled_pages_capped_40k"
        )
    pts = []
    for pg in pages:
        try:
            items = _stargazer_page(repo, pg)
        except Exception as e:
            print(f"stargazers unavailable for {repo} page {pg}: {e}")
            method = "unavailable"
            break
        if not items:
            continue
        if method == "all_pages":
            for j, it in enumerate(items):
                pts.append(((pg - 1) * 100 + j + 1, it["starred_at"]))
        else:
            pts.append(((pg - 1) * 100 + 1, items[0]["starred_at"]))
            pts.append(((pg - 1) * 100 + len(items), items[-1]["starred_at"]))
    if method == "unavailable":
        pts = []
    df = pd.DataFrame(pts, columns=["n", "starred_at"])
    df["starred_at"] = pd.to_datetime(df["starred_at"], utc=True).dt.tz_localize(None)
    df["repo"], df["method"] = (repo, method)
    return df.sort_values("n")


def monthly_cumulative(
    points: pd.DataFrame, total_stars: int, created: pd.Timestamp, asof: pd.Timestamp
) -> pd.DataFrame:
    p = points.sort_values("starred_at")
    t = p["starred_at"].astype("int64").to_numpy()
    n = p["n"].to_numpy(dtype=float)
    t = np.concatenate([[created.value], t, [asof.value]])
    n = np.concatenate([[0.0], n, [float(total_stars)]])
    n = np.maximum.accumulate(n)
    months = pd.date_range(created.to_period("M").to_timestamp("M"), asof, freq="ME")
    cum = np.interp(months.astype("int64").to_numpy(), t, n)
    return pd.DataFrame({"month": months, "cum_stars": cum.round()})


OSSINSIGHT_DEGRADED = pd.Timestamp("2025-05-23")
OSSINSIGHT_SEVERE = pd.Timestamp("2026-05-01")


def ossinsight_star_history(repo: str) -> tuple[pd.DataFrame, dict]:
    """Monthly cumulative star events from OSS Insight (GH Archive-style public event firehose)."""
    try:
        body = get(
            f"https://api.ossinsight.io/v1/repos/{repo}/stargazers/history",
            {"per": "month"},
            namespace="m10_ossinsight",
            min_interval=1.0,
        )
    except Exception as e:
        print(f"OSS Insight unavailable for {repo}: {e}")
        return (pd.DataFrame(columns=["month", "cum_star_events"]), {})
    rows = body.get("data", {}).get("rows", [])
    df = pd.DataFrame(rows)
    if df.empty:
        return (
            pd.DataFrame(columns=["month", "cum_star_events"]),
            body.get("data_quality", {}),
        )
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp("M")
    df["cum_star_events"] = df["stargazers"].astype(float)
    return (df[["month", "cum_star_events"]], body.get("data_quality", {}))


def _quality(month: pd.Timestamp) -> str:
    start = month.to_period("M").to_timestamp()
    if start >= OSSINSIGHT_SEVERE:
        return "severely_degraded"
    if month >= OSSINSIGHT_DEGRADED:
        return "degraded_lower_bound"
    return "ok"


def star_histories(
    cands: pd.DataFrame, asof: pd.Timestamp
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Monthly cumulative star events per repo (filled over a complete month range) plus a"""
    top = cands[cands["top_k"] | cands["viability_sample"]].drop_duplicates("repo")
    monthly, cov = ([], [])
    for r in top.itertuples():
        h, dq = ossinsight_star_history(r.repo)
        months = pd.date_range(
            r.created_at.to_period("M").to_timestamp("M"), asof, freq="ME"
        )
        if months.empty:
            months = pd.DatetimeIndex([asof.to_period("M").to_timestamp("M")])
        s = (
            h.set_index("month")["cum_star_events"].reindex(months).ffill().fillna(0.0)
            if len(h)
            else pd.Series(np.nan, index=months)
        )
        m = pd.DataFrame({"month": months, "cum_star_events": s.to_numpy()})
        m["repo"] = r.repo
        m["quality"] = [_quality(x) for x in months]
        monthly.append(m)
        pre = m.loc[m["month"] < OSSINSIGHT_DEGRADED, "cum_star_events"]
        cov.append(
            {
                "repo": r.repo,
                "stars_now": int(r.stars),
                "events_total": float(s.iloc[-1]) if len(h) else np.nan,
                "coverage_ratio": (
                    float(s.iloc[-1]) / r.stars if len(h) and r.stars else np.nan
                ),
                "events_before_2025_05": float(pre.iloc[-1]) if len(pre) else 0.0,
                "created_at": r.created_at,
                "ossinsight_status": dq.get("status", ""),
            }
        )
    return (pd.concat(monthly, ignore_index=True), pd.DataFrame(cov))


def exact_star_history_validation(repo: str, asof: pd.Timestamp) -> pd.DataFrame:
    """Exact monthly stars from the stargazers API -- only works for repos the token"""
    stars = get(
        f"https://api.github.com/repos/{repo}",
        namespace="m10_gh_repo",
        headers=_gh_headers(),
    )["stargazers_count"]
    pts = star_points(repo, int(stars))
    if pts.empty:
        return pd.DataFrame()
    created = pd.Timestamp(
        get(
            f"https://api.github.com/repos/{repo}",
            namespace="m10_gh_repo",
            headers=_gh_headers(),
        )["created_at"]
    ).tz_localize(None)
    exact = monthly_cumulative(pts, int(stars), created, asof)
    h, _ = ossinsight_star_history(repo)
    exact = exact.merge(h, on="month", how="left")
    exact["cum_star_events"] = exact["cum_star_events"].ffill().fillna(0.0)
    exact["repo"] = repo
    return exact


def pageviews(title: str) -> pd.DataFrame:
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{title}/monthly/{PAGEVIEWS_START}/{PAGEVIEWS_END}"
    try:
        body = get(url, namespace="m10_pageviews", headers=WIKI_UA, min_interval=0.2)
    except Exception as e:
        print(f"pageviews failed for {title}: {e}")
        return pd.DataFrame(columns=["title", "month", "views"])
    df = pd.DataFrame(body["items"])
    df["month"] = pd.to_datetime(df["timestamp"].str[:8], format="%Y%m%d")
    return df.assign(title=title)[["title", "month", "views"]]


def resolve_wiki_title(title: str) -> dict:
    """Resolve redirects for a pre-specified title and list every redirect (ns 0) that points"""
    b = get(
        "https://en.wikipedia.org/w/api.php",
        {
            "action": "query",
            "titles": title.replace("_", " "),
            "redirects": 1,
            "prop": "redirects",
            "rdlimit": "max",
            "rdnamespace": 0,
            "format": "json",
        },
        namespace="m10_wikiapi",
        headers=WIKI_UA,
        min_interval=0.5,
    )
    q = b["query"]
    pg = list(q["pages"].values())[0]
    target = pg.get("title", title.replace("_", " "))
    return {
        "requested": title,
        "target": target,
        "missing": "missing" in pg,
        "redirects": [r["title"] for r in pg.get("redirects", [])],
    }


def _norm(x: str) -> str:
    return re.sub("[^a-z0-9]", "", x.lower())


def pageviews_redirect_inclusive(title: str, product: str) -> tuple[pd.DataFrame, dict]:
    """Monthly user pageviews summed over the resolved article and all its redirects."""
    info = resolve_wiki_title(title)
    info["product_specific"] = _norm(product) in _norm(info["target"])
    titles = [info["target"]] + info["redirects"]
    parts = [pageviews(t.replace(" ", "_")) for t in titles]
    parts = [x for x in parts if len(x)]
    df = (
        pd.concat(parts).groupby("month", as_index=False)["views"].sum()
        if parts
        else pd.DataFrame(columns=["month", "views"])
    )
    df["title"] = info["target"].replace(" ", "_")
    df["n_titles"] = len(parts)
    info["n_titles_with_data"] = len(parts)
    return (df, info)


def enwiki_total_pageviews() -> pd.DataFrame:
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/en.wikipedia/all-access/user/monthly/{PAGEVIEWS_START}/{PAGEVIEWS_END}"
    body = get(url, namespace="m10_pageviews", headers=WIKI_UA)
    df = pd.DataFrame(body["items"])
    df["month"] = pd.to_datetime(df["timestamp"].str[:8], format="%Y%m%d")
    return df[["month", "views"]].rename(columns={"views": "enwiki_user_views"})


def wikidata_enwiki_for_repos(repos: list[str]) -> pd.DataFrame:
    """Alternatives with a Wikidata item whose P1324 (source code repository URL)"""
    vals = []
    for r in repos:
        for scheme in ("https", "http"):
            for suf in ("", "/", ".git"):
                vals.append(f"<{scheme}://github.com/{r}{suf}>")
    rows = []
    for i in range(0, len(vals), 36):
        q = (
            "SELECT ?item ?repo ?article WHERE { VALUES ?repo { "
            + " ".join(vals[i : i + 36])
            + " } ?item wdt:P1324 ?repo . OPTIONAL { ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . } }"
        )
        body = get(
            "https://query.wikidata.org/sparql",
            {"query": q, "format": "json"},
            namespace="m10_wikidata",
            headers=WIKI_UA,
            min_interval=1.0,
        )
        for b in body["results"]["bindings"]:
            repo_url = b["repo"]["value"]
            m = re.search("github\\.com/([^/]+/[^/]+?)(?:\\.git)?/?$", repo_url)
            rows.append(
                {
                    "repo": m.group(1) if m else repo_url,
                    "wikidata": b["item"]["value"].rsplit("/", 1)[-1],
                    "enwiki_title": b.get("article", {})
                    .get("value", "")
                    .rsplit("/", 1)[-1],
                }
            )
    return pd.DataFrame(
        rows, columns=["repo", "wikidata", "enwiki_title"]
    ).drop_duplicates()


BREW_CASK_ANALYTICS = "https://formulae.brew.sh/api/analytics/cask-install/365d.json"
BREW_FORMULA_ANALYTICS = "https://formulae.brew.sh/api/analytics/install/365d.json"
GENERIC_HOSTS = {
    "github.com",
    "github.io",
    "gitlab.com",
    "",
    "sourceforge.net",
    "vercel.app",
}


def _host(url: str) -> str:
    m = re.match("https?://(?:www\\.)?([^/:]+)", url or "", re.I)
    return m.group(1).lower() if m else ""


def _analytics_counts(body: dict, key: str) -> pd.Series:
    items = body.get("items")
    if items is None:
        items = [x for v in body.get("formulae", {}).values() for x in v]
    s = pd.Series({it[key]: int(str(it["count"]).replace(",", "")) for it in items})
    return s.groupby(level=0).sum()


def homebrew_matches(incl: pd.DataFrame) -> pd.DataFrame:
    """Map included alternatives to Homebrew casks/formulae: package homepage or download URL"""
    casks = get("https://formulae.brew.sh/api/cask.json", namespace="m10_homebrew")
    forms = get("https://formulae.brew.sh/api/formula.json", namespace="m10_homebrew")
    pkgs = []
    for c in casks:
        pkgs.append(("cask", c["token"], c.get("homepage") or "", c.get("url") or ""))
    for f in forms:
        pkgs.append(
            (
                "formula",
                f["name"],
                f.get("homepage") or "",
                ((f.get("urls") or {}).get("stable") or {}).get("url") or "",
            )
        )
    rows = []
    for r in incl.drop_duplicates("repo").itertuples():
        gh = f"github.com/{r.repo}".lower()
        h = _host(r.homepage)
        for kind, name, hp, url in pkgs:
            hit_gh = gh + "/" in hp.lower() + "/" or gh + "/" in url.lower()
            hit_host = (
                h not in GENERIC_HOSTS
                and (not h.endswith("github.io"))
                and (_host(hp) == h)
            )
            if hit_gh or hit_host:
                rows.append(
                    {
                        "repo": r.repo,
                        "kind": kind,
                        "package": name,
                        "match": "github_url" if hit_gh else "homepage_host",
                    }
                )
    return pd.DataFrame(rows, columns=["repo", "kind", "package", "match"])


def homebrew_cross_section(incl: pd.DataFrame) -> pd.DataFrame:
    prod = products()
    cask_body = get(BREW_CASK_ANALYTICS, namespace="m10_homebrew")
    form_body = get(BREW_FORMULA_ANALYTICS, namespace="m10_homebrew")
    cask_n = _analytics_counts(cask_body, "cask")
    form_n = _analytics_counts(form_body, "formula")
    rows = []
    for p in prod.itertuples():
        if p.homebrew_cask:
            rows.append(
                {
                    "product": p.product,
                    "category": p.category,
                    "side": "commercial",
                    "name": p.product,
                    "kind": "cask",
                    "package": p.homebrew_cask,
                    "installs_365d": int(cask_n.get(p.homebrew_cask, 0)),
                    "in_analytics": p.homebrew_cask in cask_n.index,
                }
            )
    matches = homebrew_matches(incl)
    for m in matches.itertuples():
        n = cask_n if m.kind == "cask" else form_n
        for p in incl.loc[incl["repo"] == m.repo, ["product", "category"]].itertuples():
            rows.append(
                {
                    "product": p.product,
                    "category": p.category,
                    "side": "open_source",
                    "name": m.repo,
                    "kind": m.kind,
                    "package": m.package,
                    "installs_365d": int(n.get(m.package, 0)),
                    "in_analytics": m.package in n.index,
                }
            )
    df = pd.DataFrame(rows)
    df["window_start"], df["window_end"] = (
        cask_body["start_date"],
        cask_body["end_date"],
    )
    return df


def wayback_snapshots(url: str) -> pd.DataFrame:
    """Monthly-collapsed Wayback Machine captures of a Homebrew analytics JSON."""
    try:
        body = get(
            "https://web.archive.org/cdx/search/cdx",
            {
                "url": url,
                "output": "json",
                "fl": "timestamp,statuscode,length",
                "collapse": "timestamp:6",
                "filter": "statuscode:200",
            },
            namespace="m10_wayback",
            min_interval=5.0,
            retries=3,
        )
    except Exception as e:
        print(f"Wayback CDX unavailable: {e}")
        return pd.DataFrame(columns=["timestamp", "statuscode", "length"])
    if not body:
        return pd.DataFrame(columns=["timestamp", "statuscode", "length"])
    return pd.DataFrame(body[1:], columns=body[0])


def homebrew_history(
    packages: list[tuple[str, str]], per_year: int = 1
) -> pd.DataFrame:
    """Time series of 365-day installs from archived snapshots (if the archive serves them)."""
    out_rows = []
    for kind, url in (
        ("cask", BREW_CASK_ANALYTICS),
        ("formula", BREW_FORMULA_ANALYTICS),
    ):
        names = [n for k, n in packages if k == kind]
        if not names:
            continue
        snaps = wayback_snapshots(url)
        if snaps.empty:
            continue
        snaps["year"] = snaps["timestamp"].str[:4]
        pick = (
            snaps.groupby("year")
            .apply(
                lambda g: g.iloc[
                    np.linspace(0, len(g) - 1, min(per_year, len(g)))
                    .round()
                    .astype(int)
                ],
                include_groups=False,
            )
            .reset_index(level=0)
        )
        for ts in pick["timestamp"]:
            try:
                body = get(
                    f"https://web.archive.org/web/{ts}id_/{url}",
                    namespace="m10_wayback",
                    min_interval=5.0,
                    retries=3,
                )
            except Exception as e:
                print(f"snapshot {ts} failed: {e}")
                continue
            try:
                counts = _analytics_counts(body, kind if kind == "cask" else "formula")
            except Exception:
                continue
            for n in names:
                out_rows.append(
                    {
                        "snapshot": ts,
                        "window_end": body.get("end_date", ""),
                        "kind": kind,
                        "package": n,
                        "installs_365d": int(counts.get(n, 0)),
                        "present": n in counts.index,
                    }
                )
    return pd.DataFrame(
        out_rows,
        columns=[
            "snapshot",
            "window_end",
            "kind",
            "package",
            "installs_365d",
            "present",
        ],
    )


def _paginate(
    url: str, namespace: str, max_pages: int = 50, params: dict | None = None
) -> list:
    items = []
    for page in range(1, max_pages + 1):
        p = {"per_page": 100, "page": page, **(params or {})}
        body = get(
            url, p, namespace=namespace, headers=_gh_headers(), min_interval=0.25
        )
        if not body:
            break
        items.extend(body)
        if len(body) < 100:
            break
    return items


def _issue_count(repo: str, state: str) -> int:
    body = get(
        "https://api.github.com/search/issues",
        {"q": f"repo:{repo} is:issue is:{state}", "per_page": 1},
        namespace="m10_gh_search",
        headers=_gh_headers(),
        min_interval=SEARCH_MIN_INTERVAL,
    )
    return int(body["total_count"])


def viability_score(
    months_since_push, releases_12m, contributors, closed, open_, archived: bool = False
) -> dict:
    """Score in [0, 100] = 25 x (R + C + B + I), each component in [0, 1]:"""
    R = float(np.clip((24 - months_since_push) / 21, 0, 1)) if not archived else 0.0
    C = min(releases_12m / 12, 1.0)
    B = min(math.log10(1 + contributors) / math.log10(101), 1.0)
    I = closed / (open_ + closed) if open_ + closed else 0.0
    return {
        "comp_recency": R,
        "comp_cadence": C,
        "comp_contributors": B,
        "comp_closure": I,
        "viability_score": 25 * (R + C + B + I),
    }


def viability(cands: pd.DataFrame, asof: pd.Timestamp) -> pd.DataFrame:
    top = cands[cands["viability_sample"]].drop_duplicates("repo")
    rows = []
    for r in top.itertuples():
        rel = _paginate(
            f"https://api.github.com/repos/{r.repo}/releases", "m10_gh_releases"
        )
        rel_dates = pd.to_datetime(
            [x.get("published_at") for x in rel if x.get("published_at")], utc=True
        ).tz_localize(None)
        contrib = _paginate(
            f"https://api.github.com/repos/{r.repo}/contributors",
            "m10_gh_contributors",
            max_pages=10,
        )
        closed, open_ = (_issue_count(r.repo, "closed"), _issue_count(r.repo, "open"))
        months_push = (asof - r.pushed_at).days / 30.44
        rel_12m = int((rel_dates >= asof - pd.Timedelta(days=365)).sum())
        row = {
            "repo": r.repo,
            "product": r.product,
            "category": r.category,
            "stars": r.stars,
            "created_at": r.created_at,
            "pushed_at": r.pushed_at,
            "license": r.license,
            "language": r.language,
            "archived": r.archived,
            "included": r.included,
            "months_active": (r.pushed_at - r.created_at).days / 30.44,
            "months_since_push": months_push,
            "releases_total": len(rel),
            "releases_12m": rel_12m,
            "first_release": rel_dates.min() if len(rel_dates) else pd.NaT,
            "contributors": len(contrib),
            "contributors_capped": len(contrib) >= 1000,
            "issues_open": open_,
            "issues_closed": closed,
            "author_conflict_of_interest": r.author_conflict_of_interest,
        }
        row.update(
            viability_score(
                months_push,
                rel_12m,
                len(contrib),
                closed,
                open_,
                archived=bool(r.archived),
            )
        )
        rows.append(row)
    return pd.DataFrame(rows)


def imitation_lag(cands: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for p in products().itertuples():
        launch_date, launch_year, src, note = LAUNCH[p.product]
        launch = pd.Timestamp(launch_date)
        c = cands[cands["product"] == p.product]
        prim = c[c["text_match"] & c["rule_min_stars"]].sort_values("created_at")
        anyst = c[c["text_match"]].sort_values("created_at")
        row = {
            "product": p.product,
            "category": p.category,
            "launch_date": launch,
            "launch_year": launch_year,
            "launch_source": src,
            "launch_note": note,
        }
        for tag, d in (("", prim), ("_anystars", anyst)):
            if len(d):
                first = d.iloc[0]
                row[f"first_alt_repo{tag}"] = first["repo"]
                row[f"first_alt_created{tag}"] = first["created_at"]
                row[f"lag_years{tag}"] = (first["created_at"] - launch).days / 365.25
            else:
                row[f"first_alt_repo{tag}"], row[f"first_alt_created{tag}"] = (
                    "",
                    pd.NaT,
                )
                row[f"lag_years{tag}"] = np.nan
        row["n_included"] = int(c["included"].sum())
        rows.append(row)
    return pd.DataFrame(rows)


def run_all(wayback: bool = False) -> dict[str, pd.DataFrame]:
    """Run every step; all HTTP is cached under data/cache/m10_*. Set wayback=True to"""
    asof = pd.Timestamp(datetime.now(timezone.utc).date())
    cands = apply_inclusion_rule(discover_candidates())
    cands.to_csv(out("candidates"), index=False)
    incl = cands[cands["included"]].copy()
    monthly, cov = star_histories(cands, asof)
    top = cands[cands["top_k"] | cands["viability_sample"]][
        ["product", "category", "repo", "included", "top_k", "archived", "stars"]
    ]
    monthly = top.merge(monthly, on="repo")
    monthly.to_csv(out("star_history_monthly"), index=False)
    cov.to_csv(out("star_history_coverage"), index=False)
    val = exact_star_history_validation("riponcm/GemType", asof)
    val.to_csv(out("star_history_validation"), index=False)
    prod = products()
    wd = wikidata_enwiki_for_repos(incl["repo"].unique().tolist())
    wd.to_csv(out("alternative_wikidata"), index=False)
    pv, titles = ([], [])
    for p in prod.itertuples():
        if p.wikipedia_title:
            d, info = pageviews_redirect_inclusive(p.wikipedia_title, p.product)
            titles.append(
                {
                    "product": p.product,
                    "side": "commercial",
                    **info,
                    "redirects": ";".join(info["redirects"]),
                }
            )
            pv.append(
                d.assign(
                    product=p.product,
                    category=p.category,
                    side="commercial",
                    entity=p.product,
                    product_specific=info["product_specific"],
                )
            )
    wd_titles = wd.dropna(subset=["enwiki_title"])
    for w in (
        wd_titles[wd_titles["enwiki_title"] != ""]
        .drop_duplicates("enwiki_title")
        .itertuples()
    ):
        for r in incl[incl["repo"] == w.repo].itertuples():
            d, info = pageviews_redirect_inclusive(w.enwiki_title, w.repo.split("/")[1])
            titles.append(
                {
                    "product": r.product,
                    "side": "open_source",
                    **info,
                    "redirects": ";".join(info["redirects"]),
                }
            )
            pv.append(
                d.assign(
                    product=r.product,
                    category=r.category,
                    side="open_source",
                    entity=w.repo,
                    product_specific=True,
                )
            )
    pv = pd.concat(pv, ignore_index=True)
    pv = pv.merge(enwiki_total_pageviews(), on="month", how="left")
    pv.to_csv(out("pageviews_monthly"), index=False)
    pd.DataFrame(titles).to_csv(out("pageviews_titles"), index=False)
    brew = homebrew_cross_section(incl)
    brew.to_csv(out("homebrew_365d"), index=False)
    if wayback or not out("homebrew_history").exists():
        hist = homebrew_history(
            list(
                brew[["kind", "package"]]
                .drop_duplicates()
                .itertuples(index=False, name=None)
            )
        )
        hist.to_csv(out("homebrew_history"), index=False)
    else:
        hist = pd.read_csv(out("homebrew_history"))
    via = viability(cands, asof)
    via.to_csv(out("viability"), index=False)
    lag = imitation_lag(cands)
    lag.to_csv(out("imitation_lag"), index=False)
    return {
        "candidates": cands,
        "star_history": monthly,
        "pageviews": pv,
        "homebrew": brew,
        "homebrew_history": hist,
        "viability": via,
        "lag": lag,
    }
