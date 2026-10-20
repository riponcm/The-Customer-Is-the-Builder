"""Module 06 -- Hacker News (Show HN) via the public Algolia HN Search API."""

from __future__ import annotations
import html
import re
from datetime import datetime, timezone
import pandas as pd
from src.fetch import get
from src.paths import PROCESSED, RAW

API = "https://hn.algolia.com/api/v1/search_by_date"
NS = "hacker_news"
MIN_INTERVAL = 0.45
START = "2012-01"
RAW_DIR = RAW / "hacker_news"
RAW_DIR.mkdir(parents=True, exist_ok=True)
STRICT = {"typoTolerance": "false", "queryType": "prefixNone", "advancedSyntax": "true"}
COUNT_SERIES = {
    "showhn_all": {"tags": "show_hn"},
    "story_all": {"tags": "story"},
    "showhn_alt_word": {"tags": "show_hn", "query": "alternative"},
    "showhn_alt_to": {"tags": "show_hn", "query": '"alternative to"'},
    "showhn_oss_alt": {"tags": "show_hn", "query": '"open source alternative"'},
    "story_alt_to": {"tags": "story", "query": '"alternative to"'},
}
AI_QUERIES = [
    "claude",
    "cursor",
    "copilot",
    "codex",
    "vibe",
    '"built with ai"',
    "lovable",
    "bolt",
    "v0",
    "replit",
    "chatgpt",
    "windsurf",
]
AI_TITLE_TERMS = {
    "Claude": "\\bclaude\\b",
    "Claude Code": "\\bclaude[ -]code\\b",
    "Cursor": "\\bcursor\\b",
    "Copilot": "\\bcopilot\\b",
    "Codex": "\\bcodex\\b",
    "ChatGPT": "\\bchat-?gpt\\b",
    "Vibe coding": "\\bvibe[- ]?cod(?:ed|ing|er|e)\\b",
    "Built with AI": "\\bbuilt (?:with|using) ai\\b",
    "Lovable": "\\blovable(?:\\.dev)?\\b",
    "Bolt.new": "\\bbolt\\.new\\b",
    "v0 (Vercel)": "\\bv0\\.dev\\b|\\bv0 by vercel\\b|\\bvercel'?s v0\\b",
    "Replit": "\\breplit\\b",
    "Windsurf": "\\bwindsurf\\b",
}
AI_TITLE_RE = re.compile("|".join((f"(?:{p})" for p in AI_TITLE_TERMS.values())), re.I)
_TOOLS = "(?:an? )?(?:ai|llms?|claude(?:[ -]code)?|cursor|(?:github )?copilot|codex|chat-?gpt|gpt-?[345o][\\w.]*|lovable|bolt(?:\\.new)?|v0(?:\\.dev)?|replit(?: agent)?|windsurf|gemini|sonnet|opus|o[13](?:-mini)?)"
AI_BUILT_RE = re.compile(
    "\\bvibe[- ]?cod(?:ed|ing)\\b|\\b(?:built|made|created|wrote|written|coded|developed|programmed)\\b[^.!?\\n]{0,40}?\\b(?:with|using|by|via)\\s+(?:the help of\\s+|help from\\s+)?"
    + _TOOLS
    + "\\b",
    re.I,
)
EVENTS = {"ChatGPT": "2022-11-30", "Claude Code preview": "2025-02-24"}


def last_full_month(today: datetime | None = None) -> pd.Period:
    today = today or datetime.now(timezone.utc)
    return pd.Period(today.strftime("%Y-%m"), "M") - 1


def months(start: str = START, end: pd.Period | None = None) -> pd.PeriodIndex:
    return pd.period_range(start, end or last_full_month(), freq="M")


def _bounds(p: pd.Period) -> tuple[int, int]:
    s = int(p.start_time.tz_localize("UTC").timestamp())
    e = int((p + 1).start_time.tz_localize("UTC").timestamp())
    return (s, e)


def _nf(s: int, e: int) -> str:
    return f"created_at_i>={s},created_at_i<{e}"


def count(s: int, e: int, tags: str, query: str | None = None) -> int:
    params = {"tags": tags, "numericFilters": _nf(s, e), "hitsPerPage": 0}
    if query:
        params.update(STRICT, query=query, restrictSearchableAttributes="title")
    body = get(API, params, namespace=NS, min_interval=MIN_INTERVAL)
    if not body.get("exhaustive", {}).get(
        "nbHits", body.get("exhaustiveNbHits", False)
    ):
        if e - s < 3600:
            raise RuntimeError(f"non-exhaustive nbHits for {params}")
        mid = (s + e) // 2
        return count(s, mid, tags, query) + count(mid, e, tags, query)
    return int(body["nbHits"])


def fetch_hits(
    s: int, e: int, query: str, tags: str = "show_hn", attrs: str = "title,story_text"
) -> list[dict]:
    """All hits for a query in [s, e). Splits the window if > 1000 hits."""
    params = {
        "tags": tags,
        "numericFilters": _nf(s, e),
        "query": query,
        "restrictSearchableAttributes": attrs,
        "hitsPerPage": 1000,
        "attributesToRetrieve": "objectID,title,url,story_text,created_at_i,points,num_comments,author",
        **STRICT,
    }
    body = get(API, params, namespace=NS, min_interval=MIN_INTERVAL)
    if body["nbHits"] > len(body["hits"]):
        mid = (s + e) // 2
        return fetch_hits(s, mid, query, tags, attrs) + fetch_hits(
            mid, e, query, tags, attrs
        )
    return [
        {
            k: h.get(k)
            for k in (
                "objectID",
                "title",
                "url",
                "story_text",
                "created_at_i",
                "points",
                "num_comments",
                "author",
            )
        }
        for h in body["hits"]
    ]


def _clean_text(t: str | None) -> str:
    if not t:
        return ""
    t = re.sub("<[^>]+>", " ", t)
    return html.unescape(t)


def collect_counts(end: pd.Period | None = None, verbose: bool = False) -> pd.DataFrame:
    rows = []
    for p in months(end=end):
        s, e = _bounds(p)
        row = {"month": str(p)}
        for name, spec in COUNT_SERIES.items():
            row[name] = count(s, e, spec["tags"], spec.get("query"))
        rows.append(row)
        if verbose and p.month == 12:
            print(p, row)
    return pd.DataFrame(rows)


def collect_ai_candidates(end: pd.Period | None = None) -> pd.DataFrame:
    recs = []
    for p in months(end=end):
        s, e = _bounds(p)
        for q in AI_QUERIES:
            for h in fetch_hits(s, e, q):
                h["query"] = q
                recs.append(h)
    df = pd.DataFrame(recs)
    df = df.groupby("objectID", as_index=False).agg(
        {
            **{c: "first" for c in df.columns if c not in ("objectID", "query")},
            "query": lambda x: ";".join(sorted(set(x))),
        }
    )
    return df


def collect_alternative_hits(
    n_months: int = 24, end: pd.Period | None = None
) -> pd.DataFrame:
    end = end or last_full_month()
    recs = []
    for p in pd.period_range(end - (n_months - 1), end, freq="M"):
        s, e = _bounds(p)
        recs += fetch_hits(s, e, "alternative", attrs="title")
    return pd.DataFrame(recs)


def classify_ai(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["title"] = df["title"].fillna("").map(html.unescape)
    text = df["story_text"].map(_clean_text)
    df["ai_title_mention"] = df["title"].str.contains(AI_TITLE_RE)
    df["ai_built"] = df["title"].str.contains(AI_BUILT_RE) | text.str.contains(
        AI_BUILT_RE
    )
    df["ai_built_title"] = df["title"].str.contains(AI_BUILT_RE)
    for term, pat in AI_TITLE_TERMS.items():
        df["t_" + term] = df["title"].str.contains(pat, flags=re.I, regex=True)
    df["created"] = pd.to_datetime(df["created_at_i"], unit="s", utc=True)
    df["month"] = df["created"].dt.strftime("%Y-%m")
    df["has_text"] = text.str.strip().ne("")
    return df


def retrieval_date(namespace: str = NS) -> str:
    """Latest retrieval date (UTC) recorded in the HTTP cache for this module."""
    import json
    from src.paths import CACHE

    dates = [
        json.loads(p.read_text(encoding="utf-8"))["retrieved_utc"][:10]
        for p in (CACHE / namespace).glob("*.json")
    ]
    return max(dates) if dates else ""


def hn_url(oid: str) -> str:
    return f"https://news.ycombinator.com/item?id={oid}"


def build(
    end: pd.Period | None = None, verbose: bool = False
) -> dict[str, pd.DataFrame]:
    """Run all collection and write data/processed/hacker_news_*.csv."""
    end = end or last_full_month()
    counts = collect_counts(end, verbose=verbose)
    cand = classify_ai(collect_ai_candidates(end))
    cand.drop(columns=["story_text"]).to_parquet(
        RAW_DIR / "ai_candidates.parquet", index=False
    )
    agg = (
        cand.groupby("month")
        .agg(
            ai_title_mention=("ai_title_mention", "sum"),
            ai_built=("ai_built", "sum"),
            ai_built_title=("ai_built_title", "sum"),
            ai_candidates=("objectID", "size"),
        )
        .reset_index()
    )
    monthly = counts.merge(agg, on="month", how="left").fillna(0)
    for c in ("ai_title_mention", "ai_built", "ai_built_title", "ai_candidates"):
        monthly[c] = monthly[c].astype(int)
    for c in (
        "showhn_alt_word",
        "showhn_alt_to",
        "showhn_oss_alt",
        "ai_title_mention",
        "ai_built",
        "ai_built_title",
    ):
        monthly[f"{c}_share_showhn"] = monthly[c] / monthly["showhn_all"]
    monthly["story_alt_to_share_story"] = monthly["story_alt_to"] / monthly["story_all"]
    monthly["showhn_share_story"] = monthly["showhn_all"] / monthly["story_all"]
    monthly["retrieved"] = retrieval_date()
    monthly.to_csv(PROCESSED / "hacker_news_monthly.csv", index=False)
    term_cols = [c for c in cand.columns if c.startswith("t_")]
    terms = (
        cand.groupby("month")[term_cols]
        .sum()
        .reindex([str(m) for m in months(end=end)], fill_value=0)
        .rename(columns=lambda c: c[2:])
        .reset_index()
        .rename(columns={"index": "month"})
        .melt(id_vars="month", var_name="term", value_name="n_titles")
    )
    terms.to_csv(PROCESSED / "hacker_news_ai_terms_monthly.csv", index=False)
    first = str(end - 23)
    alt = classify_ai(collect_alternative_hits(24, end))
    alt["match"] = "alternative"
    ai_recent = cand[
        (cand["month"] >= first) & (cand["ai_title_mention"] | cand["ai_built"])
    ].copy()
    ai_recent["match"] = ai_recent.apply(
        lambda r: "ai_built" if r["ai_built"] else "ai_title_mention", axis=1
    )
    sample = pd.concat([alt, ai_recent], ignore_index=True)
    sample = sample.groupby("objectID", as_index=False).agg(
        month=("month", "first"),
        created=("created", "first"),
        title=("title", "first"),
        url=("url", "first"),
        points=("points", "first"),
        num_comments=("num_comments", "first"),
        match=("match", lambda x: ";".join(sorted(set(x)))),
        ai_built=("ai_built", "max"),
        ai_title_mention=("ai_title_mention", "max"),
    )
    sample["hn_url"] = sample["objectID"].map(hn_url)
    sample["alt_to_phrase"] = sample["title"].str.contains(
        "\\balternative to\\b", case=False
    )
    sample = sample.sort_values("created").reset_index(drop=True)
    sample.drop(columns=["created"]).to_csv(
        PROCESSED / "hacker_news_sample_titles.csv", index=False
    )
    return {"monthly": monthly, "terms": terms, "sample": sample, "candidates": cand}


def load() -> dict[str, pd.DataFrame]:
    return {
        "monthly": pd.read_csv(PROCESSED / "hacker_news_monthly.csv"),
        "terms": pd.read_csv(PROCESSED / "hacker_news_ai_terms_monthly.csv"),
        "sample": pd.read_csv(PROCESSED / "hacker_news_sample_titles.csv"),
    }


if __name__ == "__main__":
    out = build(verbose=True)
    print(out["monthly"].tail())


def key_numbers(
    monthly: pd.DataFrame,
    sample: pd.DataFrame | None = None,
    validation: pd.DataFrame | None = None,
) -> dict[str, str]:
    m = monthly.copy()
    m["p"] = pd.PeriodIndex(m["month"], freq="M")
    pre = m[
        (m["p"] >= pd.Period("2022-01", "M")) & (m["p"] <= pd.Period("2022-10", "M"))
    ]
    y22 = m[m["p"].dt.year == 2022]
    pre19 = m[
        (m["p"] >= pd.Period("2019-01", "M")) & (m["p"] <= pd.Period("2021-12", "M"))
    ]
    last = m.tail(12)
    pk = m.loc[m["showhn_all"].idxmax()]
    post23 = m[
        (m["p"] >= pd.Period("2022-12", "M")) & (m["p"] <= pd.Period("2023-12", "M"))
    ]
    pk_ai = post23.loc[post23["ai_title_mention_share_showhn"].idxmax()]

    def share(d, num, den="showhn_all", scale=100):
        return scale * d[num].sum() / d[den].sum()

    f0, f1, f2 = (lambda v: f"{v:,.0f}", lambda v: f"{v:.1f}", lambda v: f"{v:.2f}")
    ai_month = last["ai_built"].mean()
    extra = last["showhn_all"].mean() - pre["showhn_all"].mean()
    nums = {
        "HnFirstMonth": str(m["month"].iloc[0]),
        "HnLastMonth": str(m["month"].iloc[-1]),
        "HnLastTwelveFrom": str(last["month"].iloc[0]),
        "HnShowPreMean": f0(pre["showhn_all"].mean()),
        "HnShowLastTwelveMean": f0(last["showhn_all"].mean()),
        "HnShowGrowthPct": f0(
            100 * (last["showhn_all"].mean() / pre["showhn_all"].mean() - 1)
        ),
        "HnShowPeak": f0(pk["showhn_all"]),
        "HnShowPeakMonth": str(pk["month"]),
        "HnStoriesPreMean": f0(pre["story_all"].mean()),
        "HnStoriesLastTwelveMean": f0(last["story_all"].mean()),
        "HnStoriesGrowthPct": f1(
            100 * (last["story_all"].mean() / pre["story_all"].mean() - 1)
        ),
        "HnShowShareStoriesPre": f1(share(pre, "showhn_all", "story_all")),
        "HnShowShareStoriesLastTwelve": f1(share(last, "showhn_all", "story_all")),
        "HnAltShareNineteenTwentyOne": f2(share(pre19, "showhn_alt_word")),
        "HnAltShareTwentyTwo": f2(share(y22, "showhn_alt_word")),
        "HnAltShareLastTwelve": f2(share(last, "showhn_alt_word")),
        "HnAltToShareTwentyTwo": f2(share(y22, "showhn_alt_to")),
        "HnAltToShareLastTwelve": f2(share(last, "showhn_alt_to")),
        "HnOssAltShareTwentyTwo": f2(share(y22, "showhn_oss_alt")),
        "HnOssAltShareLastTwelve": f2(share(last, "showhn_oss_alt")),
        "HnAltCountTwentyTwo": f0(y22["showhn_alt_word"].sum()),
        "HnAltCountLastTwelve": f0(last["showhn_alt_word"].sum()),
        "HnStoryAltToPerTenKTwentyTwo": f1(
            share(y22, "story_alt_to", "story_all", 10000.0)
        ),
        "HnStoryAltToPerTenKLastTwelve": f1(
            share(last, "story_alt_to", "story_all", 10000.0)
        ),
        "HnStoryAltToPerTenKNineteenTwentyOne": f1(
            share(pre19, "story_alt_to", "story_all", 10000.0)
        ),
        "HnAiTitleSharePreTwentyOne": f2(
            share(m[m["p"] < pd.Period("2021-01", "M")], "ai_title_mention")
        ),
        "HnAiTitleShareChatGPTPeak": f1(100 * pk_ai["ai_title_mention_share_showhn"]),
        "HnAiTitleShareChatGPTPeakMonth": str(pk_ai["month"]),
        "HnAiTitleShareTwentyFour": f1(
            share(m[m["p"].dt.year == 2024], "ai_title_mention")
        ),
        "HnAiTitleShareLastTwelve": f1(share(last, "ai_title_mention")),
        "HnAiBuiltShareTwentyFour": f2(share(m[m["p"].dt.year == 2024], "ai_built")),
        "HnAiBuiltShareLastTwelve": f2(share(last, "ai_built")),
        "HnAiBuiltCountLastTwelve": f0(last["ai_built"].sum()),
        "HnAiBuiltMonthlyLastTwelve": f0(ai_month),
        "HnExtraShowPerMonth": f0(extra),
        "HnAiBuiltShareOfExtraPct": f0(100 * ai_month / extra),
    }
    if sample is not None:
        nums["HnSampleTitles"] = f0(len(sample))
        nums["HnSampleAltTitles"] = f0(
            sample["match"].str.contains("alternative").sum()
        )
    if validation is not None:
        nums["HnAiBuiltPrecisionPct"] = f0(
            100 * validation["label_built_with_ai"].mean()
        )
        nums["HnAiBuiltValidationN"] = f0(len(validation))
    return nums
