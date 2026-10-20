"""Module 05 - documented AI involvement in public commits."""

from __future__ import annotations
import io
import functools
import json
import time
from datetime import datetime, timezone
import pandas as pd
from src import fetch
from src.paths import CACHE, PROCESSED, RAW

MODULE = "ai_attribution_commits"
SEARCH_URL = "https://api.github.com/search/commits"
CODE_URL = "https://api.github.com/search/code"
NAMESPACE = "gh_search_commits"
STAB_NAMESPACE = "gh_search_commits_stability"
RETRY_NAMESPACE = "gh_search_commits_retry"
MIN_INTERVAL = 20.0
CODE_INTERVAL = 6.5
START = "2023-01"
MENTIONS_START = "2024-07"
MAX_SPLIT_DEPTH = 0
SAMPLE_DAYS = (6, 16, 26)
DENSE_FROM, DENSE_DAYS = ("2026-06", (1, 11, 21))
IG_URL = (
    "https://raw.githubusercontent.com/github/innovationgraph/main/data/git_pushes.csv"
)
SERIES_START = {
    "claude_bot": "2025-01",
    "copilot_agent": "2025-01",
    "jules": "2025-01",
    "codex": "2025-01",
    "amp": "2025-01",
    "cursor": "2024-01",
    "devin": "2024-01",
}
REFINE: dict[str, tuple[str, str, int]] = {}
RAW_DIR = RAW / MODULE
RAW_DIR.mkdir(parents=True, exist_ok=True)
SERIES: dict[str, tuple[str, str, str]] = {
    "claude_trailer": (
        '"noreply@anthropic.com"',
        "Claude Code",
        "Co-Authored-By: Claude[ <model>] <noreply@anthropic.com> trailer",
    ),
    "claude_generated": (
        '"Generated with Claude Code"',
        "Claude Code",
        "'Generated with [Claude Code]' line (early commit default; PR default)",
    ),
    "claude_bot": (
        "author:claude[bot]",
        "Claude Code",
        "commits authored by claude[bot] (Claude Code GitHub Action)",
    ),
    "copilot_agent": (
        "author:copilot-swe-agent[bot]",
        "GitHub Copilot",
        "commits authored by Copilot coding agent (copilot-swe-agent[bot])",
    ),
    "copilot_coauthor": (
        '"Co-authored-by: Copilot"',
        "GitHub Copilot",
        "Co-authored-by: Copilot trailer (suggestion/autofix commits, VS Code git.addAICoAuthor)",
    ),
    "cursor": (
        '"cursoragent@cursor.com"',
        "Cursor",
        "Co-authored-by: Cursor <cursoragent@cursor.com> trailer / Cursor Agent author",
    ),
    "aider_trailer": (
        '"aider@aider.chat"',
        "Aider",
        "Co-authored-by: aider (<model>) <aider@aider.chat> trailer (default from v0.85)",
    ),
    "aider_author": (
        "author-name:aider",
        "Aider",
        "author name tagged '(aider)' (default v0.39-v0.84)",
    ),
    "codex": (
        '"noreply@openai.com"',
        "OpenAI Codex",
        "Co-authored-by: Codex <noreply@openai.com> (opt-in / short-lived default)",
    ),
    "jules": (
        "author:google-labs-jules[bot]",
        "Google Jules",
        "commits authored by google-labs-jules[bot]",
    ),
    "devin": (
        "author:devin-ai-integration[bot]",
        "Devin",
        "commits authored by devin-ai-integration[bot]",
    ),
    "amp": (
        '"amp@ampcode.com"',
        "Amp",
        "Co-authored-by: Amp <amp@ampcode.com> trailer",
    ),
}
TOOL_SERIES = {
    "Claude Code": ["claude_trailer", "claude_bot"],
    "GitHub Copilot": ["copilot_agent", "copilot_coauthor"],
    "Cursor": ["cursor"],
    "Aider": ["aider_trailer", "aider_author"],
    "Google Jules": ["jules"],
    "Devin": ["devin"],
    "OpenAI Codex": ["codex"],
    "Amp": ["amp"],
}
INSTRUCTION_FILES = {
    "CLAUDE.md": ('"CLAUDE.md"', "filename:CLAUDE.md"),
    "AGENTS.md": ('"AGENTS.md"', "filename:AGENTS.md"),
    ".cursorrules": ('".cursorrules"', "filename:.cursorrules"),
    "copilot-instructions.md": (
        '"copilot-instructions.md"',
        "filename:copilot-instructions.md path:.github",
    ),
}
MENTION_FILES = ["CLAUDE.md", "AGENTS.md", ".cursorrules"]


@functools.lru_cache(maxsize=1)
def _headers() -> dict:
    tok = fetch.github_token()
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def last_full_month() -> str:
    return str(pd.Period(datetime.now().date(), freq="M") - 1)


def months(start: str = START, end: str | None = None) -> list[pd.Period]:
    return list(pd.period_range(start, end or last_full_month(), freq="M"))


def _q(prefix: str, d0: pd.Timestamp, d1: pd.Timestamp) -> str:
    win = (
        f"committer-date:{d0:%Y-%m-%d}"
        if d0 == d1
        else f"committer-date:{d0:%Y-%m-%d}..{d1:%Y-%m-%d}"
    )
    return f"{prefix} {win}".strip()


def search(
    q: str,
    *,
    url: str = SEARCH_URL,
    namespace: str = NAMESPACE,
    min_interval: float = MIN_INTERVAL,
    refresh: bool = False,
) -> dict:
    for attempt in range(4):
        try:
            body = fetch.get(
                url,
                {"q": q, "per_page": 1},
                namespace=namespace,
                headers=dict(_headers()),
                min_interval=min_interval,
                refresh=refresh,
            )
            break
        except RuntimeError:
            if attempt == 3:
                raise
            time.sleep(90)
    return {
        "total_count": body.get("total_count"),
        "incomplete": bool(body.get("incomplete_results")),
    }


def count_window(
    prefix: str,
    d0: pd.Timestamp,
    d1: pd.Timestamp,
    depth: int = 0,
    max_depth: int | None = None,
) -> dict:
    """Count for [d0, d1]."""
    max_depth = MAX_SPLIT_DEPTH if max_depth is None else max_depth
    q = _q(prefix, d0, d1)
    first = search(q)
    r = first
    if r["incomplete"]:
        r = search(q, namespace=RETRY_NAMESPACE)
    base = {
        "first": first["total_count"],
        "first_incomplete": first["incomplete"],
        "direct": r["total_count"],
        "direct_incomplete": r["incomplete"],
    }
    if not r["incomplete"] or d0 == d1 or depth >= max_depth:
        return {
            "count": best_count(base),
            "n_queries": 1 + int(first["incomplete"]),
            "n_incomplete_leaves": int(r["incomplete"]),
            **base,
        }
    mid = pd.Timestamp((d0 + (d1 - d0) / 2).date())
    a = count_window(prefix, d0, mid, depth + 1, max_depth)
    b = count_window(prefix, mid + pd.Timedelta(days=1), d1, depth + 1, max_depth)
    return {
        "count": a["count"] + b["count"],
        "n_queries": 2 + a["n_queries"] + b["n_queries"],
        "n_incomplete_leaves": a["n_incomplete_leaves"] + b["n_incomplete_leaves"],
        **base,
    }


VALIDATION_CELLS = [("claude_trailer", "2026-05", 2)]


def best_count(row) -> float:
    """Value used for a month cell: the complete count if either attempt was complete,"""
    if "first" not in row or pd.isna(row["first"]):
        return row.get("count")
    if not row.get("first_incomplete", False):
        return row["first"]
    if not row.get("direct_incomplete", False):
        return row["direct"]
    return max(row["first"], row["direct"])


def validate_incomplete(cells=VALIDATION_CELLS) -> pd.DataFrame:
    """For a few cells, compare the accepted month count with a split (down to ~day-level) sum."""
    out = RAW_DIR / "incomplete_validation.csv"
    rows = []
    for k, m, depth in cells:
        p = pd.Period(m, freq="M")
        d0, d1 = (p.start_time.normalize(), p.end_time.normalize())
        acc = count_window(SERIES[k][0], d0, d1, max_depth=0)
        accepted = best_count(acc)
        full = count_window(SERIES[k][0], d0, d1, max_depth=depth)
        rows.append(
            {
                "series": k,
                "month": m,
                "max_depth": depth,
                "first": acc["first"],
                "first_incomplete": acc["first_incomplete"],
                "retry": acc["direct"],
                "retry_incomplete": acc["direct_incomplete"],
                "accepted": accepted,
                "split_sum": full["count"],
                "split_queries": full["n_queries"],
                "split_incomplete_leaves": full["n_incomplete_leaves"],
                "accepted_vs_split_pct": (
                    100 * (accepted - full["count"]) / full["count"]
                    if full["count"]
                    else None
                ),
            }
        )
        print(rows[-1], flush=True)
    df = pd.DataFrame(rows)
    if out.exists():
        old = pd.read_csv(out)
        if "max_depth" in old:
            df = pd.concat([old, df]).drop_duplicates(
                ["series", "month", "max_depth"], keep="last"
            )
    df.to_csv(out, index=False)
    return df


def collect_series(
    keys: list[str] | None = None,
    start: str = START,
    end: str | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    rows = []
    for k in keys or list(SERIES):
        prefix, tool, _ = SERIES[k]
        t0 = time.time()
        ref = REFINE.get(k)
        for p in months(max(start, SERIES_START.get(k, start)), end):
            depth = ref[2] if ref and ref[0] <= str(p) <= ref[1] else None
            try:
                r = count_window(
                    prefix,
                    p.start_time.normalize(),
                    p.end_time.normalize(),
                    max_depth=depth,
                )
            except Exception as exc:
                r = {"count": None, "error": str(exc)[:200]}
            rows.append(
                {
                    "series": k,
                    "tool": tool,
                    "month": str(p),
                    "query_prefix": prefix,
                    **r,
                }
            )
        if verbose:
            print(
                f"[{datetime.now():%H:%M:%S}] {k} done in {time.time() - t0:.0f}s",
                flush=True,
            )
    df = pd.DataFrame(rows)
    if keys is None:
        df.to_csv(RAW_DIR / "commit_search_counts.csv", index=False)
    return df


def collect_instruction_mentions(
    start: str = MENTIONS_START, end: str | None = None
) -> pd.DataFrame:
    rows = []
    for name, (msg_q, _) in INSTRUCTION_FILES.items():
        if name not in MENTION_FILES:
            continue
        last_q = pd.Period(
            pd.Period(end or last_full_month(), freq="M").end_time, freq="Q"
        )
        if pd.Period(end or last_full_month(), freq="M") != pd.Period(
            last_q.end_time, freq="M"
        ):
            last_q -= 1
        for q in pd.period_range(pd.Period(start, freq="Q"), last_q, freq="Q"):
            r = count_window(msg_q, q.start_time.normalize(), q.end_time.normalize())
            rows.append({"file": name, "quarter": str(q), "query_prefix": msg_q, **r})
        print(f"[{datetime.now():%H:%M:%S}] mentions {name} done", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(RAW_DIR / "instruction_file_mentions.csv", index=False)
    return df


def collect_instruction_stock() -> pd.DataFrame:
    """Point-in-time code-search counts (no date filter exists for code search)."""
    rows = []
    for name, (_, code_q) in INSTRUCTION_FILES.items():
        try:
            r = search(
                code_q,
                url=CODE_URL,
                namespace="gh_search_code",
                min_interval=CODE_INTERVAL,
            )
        except Exception as exc:
            r = {"total_count": None, "incomplete": None, "error": str(exc)[:200]}
        path = (
            CACHE
            / "gh_search_code"
            / f"{fetch._key(CODE_URL, {'q': code_q, 'per_page': 1})}.json"
        )
        when = (
            json.loads(path.read_text(encoding="utf-8"))["retrieved_utc"]
            if path.exists()
            else None
        )
        rows.append({"file": name, "query": code_q, **r, "retrieved_utc": when})
    df = pd.DataFrame(rows)
    df.to_csv(RAW_DIR / "instruction_file_stock.csv", index=False)
    return df


def collect_denominator(start: str = START, end: str | None = None) -> pd.DataFrame:
    """All commits in the commit-search index on 3 sampled days per month."""
    rows = []
    for p in months(start, end):
        days = SAMPLE_DAYS + (DENSE_DAYS if str(p) >= DENSE_FROM else ())
        for d in sorted(days):
            day = pd.Timestamp(p.year, p.month, d)
            try:
                r = search(_q("", day, day))
            except Exception:
                r = {"total_count": None, "incomplete": None}
            rows.append(
                {
                    "month": str(p),
                    "date": f"{day:%Y-%m-%d}",
                    "weekday": day.day_name(),
                    "total_count": r["total_count"],
                    "incomplete": r["incomplete"],
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(RAW_DIR / "denominator_daily_sample.csv", index=False)
    return df


def innovation_graph_pushes() -> pd.DataFrame:
    txt = fetch.get(IG_URL, namespace="m05_innovationgraph", as_json=False)
    d = pd.read_csv(io.StringIO(txt))
    d.to_csv(RAW_DIR / "innovationgraph_git_pushes.csv", index=False)
    d = d[d["iso2_code"] != "EU"]
    q = d.groupby(["year", "quarter"], as_index=False).agg(
        git_pushes=("git_pushes", "sum"), n_economies=("iso2_code", "nunique")
    )
    q["quarter_label"] = q["year"].astype(str) + "Q" + q["quarter"].astype(str)
    return q


def stability(n_reps: int = 3, tag: str = "") -> pd.DataFrame:
    """Re-issue a few (complete) queries with the cache bypassed."""
    qs = [
        ('"noreply@anthropic.com"', "2025-03-01", "2025-03-07"),
        ("author:copilot-swe-agent[bot]", "2025-09-01", "2025-09-30"),
        ('"cursoragent@cursor.com"', "2025-09-01", "2025-09-30"),
        ("author-name:aider", "2025-01-01", "2025-01-31"),
        ("", "2025-09-16", "2025-09-16"),
    ]
    rows = []
    for rep in range(n_reps):
        for prefix, a, b in qs:
            q = _q(prefix, pd.Timestamp(a), pd.Timestamp(b))
            r = search(q, namespace=STAB_NAMESPACE, refresh=True)
            rows.append(
                {
                    "query": q,
                    "rep": rep,
                    "tag": tag,
                    **r,
                    "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                }
            )
    df = pd.DataFrame(rows)
    out = RAW_DIR / "stability_runs.csv"
    if out.exists():
        df = pd.concat([pd.read_csv(out), df], ignore_index=True)
    df.to_csv(out, index=False)
    return df


def process() -> dict[str, pd.DataFrame]:
    raw = pd.read_csv(RAW_DIR / "commit_search_counts.csv")
    unsplit = raw["n_queries"].fillna(1) <= 2
    raw.loc[unsplit, "count"] = raw[unsplit].apply(best_count, axis=1)
    raw["lower_bound"] = raw["n_incomplete_leaves"].fillna(0) > 0
    raw.rename(columns={"count": "commits"}).to_csv(
        PROCESSED / f"{MODULE}_series.csv", index=False
    )
    wide = raw.pivot(index="month", columns="series", values="count").sort_index()
    lb = raw.pivot(index="month", columns="series", values="lower_bound").sort_index()
    tool_rows = []
    for tool, keys in TOOL_SERIES.items():
        keys = [k for k in keys if k in wide]
        s = wide[keys].sum(axis=1, min_count=1)
        flag = lb[keys].astype(bool).any(axis=1)
        for m, v in s.items():
            tool_rows.append(
                {"month": m, "tool": tool, "commits": v, "lower_bound": bool(flag[m])}
            )
    tools = pd.DataFrame(tool_rows)
    den = pd.read_csv(RAW_DIR / "denominator_daily_sample.csv")
    dm = den.groupby("month", as_index=False).agg(
        mean_daily=("total_count", "mean"),
        median_daily=("total_count", "median"),
        min_daily=("total_count", "min"),
        max_daily=("total_count", "max"),
        sd_daily=("total_count", "std"),
        n_days=("total_count", "count"),
        n_incomplete=("incomplete", "sum"),
    )
    dm["days_in_month"] = pd.PeriodIndex(dm["month"], freq="M").days_in_month
    dm["est_commits"] = dm["median_daily"] * dm["days_in_month"]
    dm["est_commits_mean_based"] = dm["mean_daily"] * dm["days_in_month"]
    dm["est_commits_se"] = dm["sd_daily"] / dm["n_days"] ** 0.5 * dm["days_in_month"]
    dm.to_csv(PROCESSED / f"{MODULE}_denominator.csv", index=False)
    tools = tools.merge(dm[["month", "est_commits"]], on="month", how="left")
    tools["share_per_10k"] = 10000.0 * tools["commits"] / tools["est_commits"]
    total = tools.groupby("month", as_index=False).agg(
        commits=("commits", lambda x: x.sum(min_count=1)),
        lower_bound=("lower_bound", "any"),
    )
    total = total.merge(
        dm[["month", "est_commits", "est_commits_se"]], on="month", how="left"
    )
    total["share_pct"] = 100 * total["commits"] / total["est_commits"]
    tools.to_csv(PROCESSED / f"{MODULE}_by_tool.csv", index=False)
    total.to_csv(PROCESSED / f"{MODULE}_total.csv", index=False)
    ig = innovation_graph_pushes()
    t = total.copy()
    pm = pd.PeriodIndex(t["month"], freq="M")
    t["year"], t["quarter"] = (pm.year, pm.quarter)
    tq = t.groupby(["year", "quarter"], as_index=False).agg(
        commits=("commits", "sum"),
        est_commits=("est_commits", "sum"),
        n_months=("month", "count"),
    )
    tq = tq[tq["n_months"] == 3].merge(ig, on=["year", "quarter"], how="left")
    tq["ai_commits_per_1k_pushes"] = 1000.0 * tq["commits"] / tq["git_pushes"]
    tq["est_commits_per_push"] = tq["est_commits"] / tq["git_pushes"]
    tq.to_csv(PROCESSED / f"{MODULE}_quarterly.csv", index=False)
    stamps = [
        json.loads(f.read_text(encoding="utf-8"))["retrieved_utc"]
        for f in (CACHE / NAMESPACE).glob("*.json")
    ]
    ret = pd.to_datetime(pd.Series(stamps), utc=True, format="ISO8601")
    meta = {
        "retrieved_first": f"{ret.min():%Y-%m-%d}",
        "retrieved_last": f"{ret.max():%Y-%m-%d}",
        "first_month": str(raw["month"].min()),
        "last_month": str(raw["month"].max()),
        "n_requests_cached": len(stamps),
        "n_cells_with_incomplete_leaves": int(
            (raw["n_incomplete_leaves"].fillna(0) > 0).sum()
        ),
        "n_cells_retried": int((raw["n_queries"].fillna(1) > 1).sum()),
        "ig_last_quarter": str(ig["quarter_label"].iloc[-1]),
    }
    (PROCESSED / f"{MODULE}_meta.json").write_text(
        json.dumps(meta, indent=1), encoding="utf-8"
    )
    out = {
        "meta": meta,
        "series": raw,
        "by_tool": tools,
        "total": total,
        "denominator": dm,
        "quarterly": tq,
    }
    p = RAW_DIR / "instruction_file_mentions.csv"
    if p.exists():
        mm = pd.read_csv(p)
        unsplit = mm["n_queries"].fillna(1) <= 2
        mm.loc[unsplit, "count"] = mm[unsplit].apply(best_count, axis=1)
        mm["lower_bound"] = mm["n_incomplete_leaves"].fillna(0) > 0
        mm.rename(columns={"count": "commits"}).to_csv(
            PROCESSED / f"{MODULE}_instruction_mentions.csv", index=False
        )
        out["mentions"] = mm
    p = RAW_DIR / "instruction_file_stock.csv"
    if p.exists():
        st = pd.read_csv(p)
        st.to_csv(PROCESSED / f"{MODULE}_instruction_stock.csv", index=False)
        out["stock"] = st
    p = RAW_DIR / "stability_runs.csv"
    if p.exists():
        s = pd.read_csv(p)
        g = (
            s.groupby("query")["total_count"]
            .agg(n="count", mean="mean", min="min", max="max", std="std")
            .reset_index()
        )
        g["range_pct"] = 100 * (g["max"] - g["min"]) / g["mean"]
        g.to_csv(PROCESSED / f"{MODULE}_stability.csv", index=False)
        out["stability"] = g
    return out


def collect_all() -> None:
    stability(n_reps=3, tag="start")
    collect_series()
    collect_denominator()
    collect_instruction_mentions()
    collect_instruction_stock()
    validate_incomplete()
    stability(n_reps=3, tag="end")
    process()


if __name__ == "__main__":
    collect_all()
_TOOL_WORD = {
    "Claude Code": "Claude",
    "GitHub Copilot": "Copilot",
    "Cursor": "Cursor",
    "Aider": "Aider",
    "Google Jules": "Jules",
    "Devin": "Devin",
    "OpenAI Codex": "Codex",
    "Amp": "Amp",
}


def _fmt_int(v: float) -> str:
    return f"{v:,.0f}".replace(",", "{,}")


def key_numbers(out: dict) -> dict[str, str]:
    """Return summary values from the processed data."""
    tools, total, den, q = (
        out["by_tool"],
        out["total"],
        out["denominator"],
        out["quarterly"],
    )
    tools = tools.assign(m=pd.PeriodIndex(tools["month"], freq="M"))
    total = total.assign(m=pd.PeriodIndex(total["month"], freq="M")).set_index("m")
    last = total.index.max()
    yago = last - 12
    n = {
        "LastMonth": last.strftime("%B %Y"),
        "FirstMonth": total.index.min().strftime("%B %Y"),
    }
    tl = tools[tools["m"] == last].set_index("tool")["commits"]
    for tool, word in _TOOL_WORD.items():
        if tool in tl:
            n[f"{word}LastMonth"] = _fmt_int(tl[tool])
    n["TotalLastMonth"] = _fmt_int(total.at[last, "commits"])
    n["TotalLastMonthM"] = f"{total.at[last, 'commits'] / 1000000.0:.2f}"
    n["TotalYearAgo"] = _fmt_int(total.at[yago, "commits"])
    n["TotalFoldYoY"] = f"{total.at[last, 'commits'] / total.at[yago, 'commits']:.1f}"
    n["TotalLastTwelveMM"] = (
        f"{total.loc[last - 11:last, 'commits'].sum() / 1000000.0:.1f}"
    )
    n["SharePctLastMonth"] = f"{total.at[last, 'share_pct']:.2f}"
    n["SharePctYearAgo"] = f"{total.at[yago, 'share_pct']:.2f}"
    jan25 = pd.Period("2025-01", freq="M")
    if jan25 in total.index:
        n["SharePctJanTwentyFive"] = f"{total.at[jan25, 'share_pct']:.3f}"
    n["ClaudeShareOfAILastMonth"] = (
        f"{100 * tl.get('Claude Code', 0) / total.at[last, 'commits']:.0f}"
    )
    dd = den.set_index(pd.PeriodIndex(den["month"], freq="M"))
    n["DenomLastMonthM"] = f"{dd.at[last, 'est_commits'] / 1000000.0:.0f}"
    n["DenomYearAgoM"] = f"{dd.at[yago, 'est_commits'] / 1000000.0:.0f}"
    n["DenomGrowthYoY"] = (
        f"{100 * (dd.at[last, 'est_commits'] / dd.at[yago, 'est_commits'] - 1):.0f}"
    )
    n["DenomSampleCVPct"] = f"{100 * (dd['sd_daily'] / dd['mean_daily']).median():.0f}"
    n["DenomDailyMedianLastMonthM"] = f"{dd.at[last, 'median_daily'] / 1000000.0:.1f}"
    n["DenomDailyMedianTwentyFourM"] = (
        f"{dd.loc[dd.index.year == 2024, 'median_daily'].mean() / 1000000.0:.1f}"
    )
    qq = q.dropna(subset=["git_pushes"])
    if len(qq):
        n["IgLastQuarter"] = str(qq["quarter_label"].iloc[-1])
        n["PerKPushesLastQ"] = f"{qq['ai_commits_per_1k_pushes'].iloc[-1]:.1f}"
        n["PerKPushesFirstQ"] = f"{qq['ai_commits_per_1k_pushes'].iloc[0]:.2f}"
        n["IgFirstQuarter"] = str(qq["quarter_label"].iloc[0])
    s = out["series"].pivot(index="month", columns="series", values="count")
    s.index = pd.PeriodIndex(s.index, freq="M")
    n["ClaudeGeneratedRatioLastMonth"] = (
        f"{100 * s.at[last, 'claude_generated'] / s.at[last, 'claude_trailer']:.0f}"
    )
    n["ClaudeTrailerPeakMonth"] = s["claude_trailer"].idxmax().strftime("%B %Y")
    if "mentions" in out:
        mm = out["mentions"].assign(q=lambda d: pd.PeriodIndex(d["quarter"], freq="Q"))
        lq = mm["q"].max()
        n["MentionLastQuarter"] = f"{lq.year}Q{lq.quarter}"
        for f, word in [
            ("CLAUDE.md", "ClaudeMd"),
            ("AGENTS.md", "AgentsMd"),
            (".cursorrules", "Cursorrules"),
        ]:
            sub = mm[mm["file"] == f].set_index("q")["count"]
            if lq in sub.index:
                n[f"Mention{word}LastQ"] = _fmt_int(sub[lq])
            if lq - 4 in sub.index and sub[lq - 4]:
                n[f"Mention{word}FoldYoY"] = f"{sub[lq] / sub[lq - 4]:.1f}"
    if "stock" in out:
        for _, r in out["stock"].iterrows():
            word = {
                "CLAUDE.md": "ClaudeMd",
                "AGENTS.md": "AgentsMd",
                ".cursorrules": "Cursorrules",
                "copilot-instructions.md": "CopilotInstr",
            }[r["file"]]
            if pd.notna(r["total_count"]):
                n[f"Stock{word}"] = _fmt_int(r["total_count"])
    meta = out["meta"]
    n["CellsRetried"] = str(meta["n_cells_retried"])
    n["CellsIncomplete"] = str(meta["n_cells_with_incomplete_leaves"])
    if "stability" in out:
        n["StabMaxRangePct"] = f"{out['stability']['range_pct'].max():.1f}"
    return {"Aic" + k: v for k, v in n.items()}
