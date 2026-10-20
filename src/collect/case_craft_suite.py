"""Module 16 - case study: the ArtCraft "Craft" suite (GitHub org `storytold`)."""

from __future__ import annotations
import base64
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from src.fetch import _key, get, github_token
from src.paths import CACHE, DATA, PROCESSED, RAW

MODULE = "16_case_craft_suite"
RAW_DIR = RAW / MODULE
RAW_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR = DATA / "sample"
OWNER = "storytold"
API = "https://api.github.com"
NS = "m16_gh"
NS_SEARCH = "m16_search"
REST_INTERVAL = 0.8
SEARCH_INTERVAL = 6.5
SNAPSHOT_CSV = PROCESSED / "case_craft_suite_snapshots.csv"
BYTES_PER_LINE = 35
COMMIT_SAMPLE = 50
SEED = 16
APPS = {
    "photocraft": "PhotoCraft",
    "filmcraft": "FilmCraft",
    "lightcraft": "LightCraft",
    "pdfcraft": "PdfCraft",
    "vectorcraft": "VectorCraft",
    "effectcraft": "EffectCraft",
    "designcraft": "DesignCraft",
    "wordcraft": "WordCraft",
    "gridcraft": "GridCraft",
    "deckcraft": "DeckCraft",
    "cadcraft": "CADCraft",
    "soundcraft": "SoundCraft",
}
SUPPORT = [
    "craft-launcher",
    "craft-libs",
    "craft-fonts",
    "craft-repo-status-app",
    "craft-common-actions",
    "photocraft-corpus",
]
LEGACY = ["artcraft", "artcraftx", "artcraft-services"]
ALL_REPOS = list(APPS) + SUPPORT + LEGACY
COMMIT_REPOS = list(APPS) + SUPPORT
CLONE_REPOS = list(APPS)
KEY_REPOS = ["photocraft", "pdfcraft", "wordcraft"]
AI_DOMAINS = {
    "anthropic.com": "claude",
    "openai.com": "codex",
    "cursor.com": "cursor",
    "google.com": "gemini",
    "opencode.ai": "other_agent",
    "z.ai": "other_agent",
    "meta.com": "other_agent",
    "deepseek.com": "other_agent",
    "qwen.ai": "other_agent",
    "codebuff.com": "other_agent",
    "x.ai": "other_agent",
    "moonshot.ai": "other_agent",
    "mistral.ai": "other_agent",
    "windsurf.com": "other_agent",
    "cognition.ai": "other_agent",
}
AGENT_NAME_RX = re.compile(
    "^(claude|copilot|codex|cursor|gemini|devin|jules|aider|kimi|opencode|chatgpt)\\b",
    re.I,
)
AGENT_NAME_FLAG = {
    "claude": "claude",
    "copilot": "copilot",
    "codex": "codex",
    "chatgpt": "codex",
    "cursor": "cursor",
    "gemini": "gemini",
    "aider": "aider",
}
AI_PATTERNS = {
    "claude": "generated (?:with|by)[^\\n]*claude|claude\\.ai/code",
    "codex": "generated (?:with|by)[^\\n]*codex",
    "copilot": "generated (?:with|by)[^\\n]*copilot|copilot-swe-agent",
    "cursor": "generated (?:with|by)[^\\n]*cursor",
    "aider": "(?:^|\\n)\\s*aider:|\\(aider\\)",
    "gemini": "generated (?:with|by)[^\\n]*gemini|gemini-cli",
}
AI_RX = {k: re.compile(v, re.I) for k, v in AI_PATTERNS.items()}
AI_FLAGS = ["claude", "codex", "copilot", "cursor", "aider", "gemini", "other_agent"]
AI_LOGIN_RX = re.compile(
    "^(claude|copilot|cursoragent|codex|devin-ai-integration\\[bot\\]|copilot-swe-agent\\[bot\\]|google-labs-jules\\[bot\\]|chatgpt-codex-connector\\[bot\\])$",
    re.I,
)
COAUTH_RX = re.compile("^co-authored-by:\\s*(.+?)\\s*<([^>]*)>\\s*$", re.I | re.M)
EMAIL_RX = re.compile("[\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)+")
PR_RX = re.compile("\\(#(\\d+)\\)\\s*$")


def classify_trailers(msg: str) -> tuple[dict, list[str], int, int]:
    """-> (flags by AI family, AI model names, n AI co-authors, n human co-authors)."""
    flags = {k: False for k in AI_FLAGS}
    models, n_ai, n_h = ([], 0, 0)
    for name, email in COAUTH_RX.findall(msg):
        dom = email.split("@")[-1].lower()
        fam = AI_DOMAINS.get(dom)
        if fam is None and dom.endswith("users.noreply.github.com"):
            m = AGENT_NAME_RX.match(name.strip())
            if m:
                fam = AGENT_NAME_FLAG.get(m.group(1).lower(), "other_agent")
        if (
            fam is None
            and dom in ("storyteller.dev",)
            and AGENT_NAME_RX.match(name.strip())
        ):
            fam = "other_agent"
        if fam:
            flags[fam] = True
            models.append(name.strip())
            n_ai += 1
        else:
            n_h += 1
    return (flags, models, n_ai, n_h)


def out(name: str) -> Path:
    return PROCESSED / f"{MODULE}_{name}.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def asof() -> pd.Timestamp:
    """Fixed collection instant: commits are fetched with until=ASOF so every run sees one snapshot."""
    p = RAW_DIR / "asof_utc.txt"
    if not p.exists():
        p.write_text(now_utc(), encoding="utf-8")
    return pd.Timestamp(p.read_text(encoding="utf-8").strip())


def gh_headers() -> dict:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    tok = github_token()
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def gh(
    path: str,
    params: dict | None = None,
    *,
    refresh: bool = False,
    interval: float = REST_INTERVAL,
    namespace: str = NS,
    retries: int = 5,
):
    url = path if path.startswith("http") else f"{API}/{path.lstrip('/')}"
    return get(
        url,
        params,
        namespace=namespace,
        headers=gh_headers(),
        min_interval=interval,
        refresh=refresh,
        retries=retries,
    )


def retrieved_at(path: str, params: dict | None = None, namespace: str = NS) -> str:
    """Retrieval timestamp recorded by src.fetch for a cached call ('' if not cached)."""
    url = path if path.startswith("http") else f"{API}/{path.lstrip('/')}"
    f = CACHE / namespace / f"{_key(url, params)}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8")).get("retrieved_utc", "")
    return ""


def paginate(
    path: str,
    params: dict | None = None,
    *,
    key: str | None = None,
    per_page: int = 100,
    max_pages: int = 500,
    refresh: bool = False,
    interval: float = REST_INTERVAL,
) -> list:
    """Follow ?page=N until a short/empty page. `key` selects the list inside a dict body."""
    rows: list = []
    for page in range(1, max_pages + 1):
        p = dict(params or {})
        p.update({"per_page": per_page, "page": page})
        try:
            body = gh(path, p, refresh=refresh, interval=interval)
        except Exception as e:
            print(f"  paginate {path} p{page}: {type(e).__name__}: {str(e)[:80]}")
            break
        items = body.get(key, []) if key and isinstance(body, dict) else body
        if not items:
            break
        rows.extend(items)
        if len(items) < per_page:
            break
    return rows


def pseud(login: str | None) -> str:
    """Short irreversible-in-practice hash of a login (privacy: issue authors are not stored in clear)."""
    return hashlib.sha256(f"m16:{login}".encode()).hexdigest()[:10] if login else ""


def _rmtree(path: Path) -> None:

    def onerr(func, p, _):
        os.chmod(p, stat.S_IWRITE)
        func(p)

    shutil.rmtree(path, onerror=onerr)


def collect_repos() -> pd.DataFrame:
    rows = []
    for name in ALL_REPOS:
        r = gh(f"repos/{OWNER}/{name}")
        langs = gh(f"repos/{OWNER}/{name}/languages")
        contrib = paginate(
            f"repos/{OWNER}/{name}/contributors", {"anon": "0"}, max_pages=20
        )
        rel = paginate(f"repos/{OWNER}/{name}/releases")
        downloads = sum(
            (a.get("download_count", 0) for x in rel for a in x.get("assets", []))
        )
        total_b = sum(langs.values()) or 1
        contribs = sorted((c["contributions"] for c in contrib), reverse=True)
        tot_c = sum(contribs) or 1
        rows.append(
            {
                "repo": name,
                "display": APPS.get(name, name),
                "group": (
                    "app"
                    if name in APPS
                    else "support" if name in SUPPORT else "legacy"
                ),
                "description": r.get("description") or "",
                "created_at": r["created_at"],
                "pushed_at": r["pushed_at"],
                "stars": r["stargazers_count"],
                "forks": r["forks_count"],
                "watchers_subscribers": r.get("subscribers_count", np.nan),
                "open_issues_and_prs": r["open_issues_count"],
                "license": (r.get("license") or {}).get("spdx_id", ""),
                "size_kb": r["size"],
                "default_branch": r["default_branch"],
                "homepage": r.get("homepage") or "",
                "topics": ";".join(r.get("topics", [])),
                "language_main": r.get("language") or "",
                "rust_bytes": langs.get("Rust", 0),
                "total_bytes": sum(langs.values()),
                "rust_share": langs.get("Rust", 0) / total_b,
                "languages_json": json.dumps(langs),
                "n_contributors": len(contrib),
                "n_contributors_ge10": int(sum((c >= 10 for c in contribs))),
                "top_contributor_share": contribs[0] / tot_c if contribs else np.nan,
                "top5_contributor_share": (
                    sum(contribs[:5]) / tot_c if contribs else np.nan
                ),
                "contributor_commit_total": tot_c if contribs else 0,
                "n_releases": len(rel),
                "release_downloads": downloads,
                "first_release_at": min(
                    (x["published_at"] for x in rel if x.get("published_at")),
                    default="",
                ),
                "retrieved_utc": retrieved_at(f"repos/{OWNER}/{name}"),
            }
        )
        (
            pd.DataFrame(contrib)[["login", "type", "contributions"]]
            .assign(repo=name)
            .to_csv(RAW_DIR / f"contributors_{name}.csv", index=False)
            if contrib
            else None
        )
    df = pd.DataFrame(rows)
    df["rust_loc_est_bytes35"] = (df["rust_bytes"] / BYTES_PER_LINE).round()
    df.to_csv(out("repos"), index=False)
    return df


def parse_commit(repo: str, c: dict) -> dict:
    msg = c["commit"]["message"] or ""
    first = msg.split("\n", 1)[0]
    flags, models, n_ai, n_h = classify_trailers(msg)
    for k, rx in AI_RX.items():
        flags[k] = flags[k] or bool(rx.search(msg))
    a_login = (c.get("author") or {}).get("login") or ""
    c_login = (c.get("committer") or {}).get("login") or ""
    ai_login = bool(AI_LOGIN_RX.match(a_login))
    pr = PR_RX.search(first)
    return {
        "repo": repo,
        "sha": c["sha"],
        "author_date": c["commit"]["author"]["date"],
        "committer_date": c["commit"]["committer"]["date"],
        "author_login": a_login,
        "committer_login": c_login,
        "author_type": (c.get("author") or {}).get("type", ""),
        "first_line": EMAIL_RX.sub("<email>", first)[:200],
        "msg_len": len(msg),
        "n_parents": len(c.get("parents", [])),
        "pr_number": int(pr.group(1)) if pr else np.nan,
        "via_web_flow": c_login == "web-flow",
        **{f"ai_{k}": v for k, v in flags.items()},
        "ai_author_login": ai_login,
        "ai_trailer": n_ai > 0,
        "ai_any": any(flags.values()) or ai_login,
        "ai_models": ";".join(sorted(set(models))),
        "n_coauthors_ai": n_ai,
        "n_coauthors_human": n_h,
    }


def collect_commits() -> pd.DataFrame:
    until = asof().strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for repo in COMMIT_REPOS:
        raw = paginate(f"repos/{OWNER}/{repo}/commits", {"until": until})
        rows.extend((parse_commit(repo, c) for c in raw))
        print(f"  commits {repo}: {len(raw)}")
    df = pd.DataFrame(rows)
    df["author_date"] = pd.to_datetime(df["author_date"], utc=True)
    df["committer_date"] = pd.to_datetime(df["committer_date"], utc=True)
    df = df.drop_duplicates(["repo", "sha"]).sort_values(["repo", "author_date"])
    df.to_csv(out("commits"), index=False)
    return df


def commit_daily(commits: pd.DataFrame) -> pd.DataFrame:
    c = commits.copy()
    c["date"] = c["author_date"].dt.tz_convert("UTC").dt.date
    d = (
        c.groupby(["repo", "date"])
        .agg(
            commits=("sha", "size"),
            ai_any=("ai_any", "sum"),
            ai_claude=("ai_claude", "sum"),
            authors=("author_login", "nunique"),
        )
        .reset_index()
    )
    d.to_csv(out("commits_daily"), index=False)
    return d


def commit_summary(commits: pd.DataFrame, repos: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for repo, g in commits.groupby("repo"):
        t = g["author_date"].dt.tz_convert("UTC")
        first, last = (t.min(), t.max())
        span_days = max((last - first).total_seconds() / 86400, 1e-09)
        cal_days = (last.normalize() - first.normalize()).days + 1
        hours = t.dt.floor("h").nunique()
        per_day = g.groupby(t.dt.date).size()
        feat = g[g["pr_number"].notna()]
        rows.append(
            {
                "repo": repo,
                "n_commits": len(g),
                "first_commit": first,
                "last_commit": last,
                "calendar_days": cal_days,
                "active_days": per_day.size,
                "commits_per_calendar_day": len(g) / cal_days,
                "max_commits_in_a_day": int(per_day.max()),
                "active_hours_utc": int(hours),
                "hours_in_span": int(np.ceil(span_days * 24)),
                "share_hours_active": hours / max(np.ceil(span_days * 24), 1),
                "n_authors": g["author_login"].replace("", np.nan).nunique(),
                "top_author_share": g["author_login"]
                .replace("", np.nan)
                .value_counts(normalize=True)
                .iloc[0],
                "share_via_web_flow": g["via_web_flow"].mean(),
                "share_with_pr_number": g["pr_number"].notna().mean(),
                "n_ai_any": int(g["ai_any"].sum()),
                "share_ai_any": g["ai_any"].mean(),
                "n_ai_claude": int(g["ai_claude"].sum()),
                "share_ai_claude": g["ai_claude"].mean(),
                "n_ai_codex": int(g["ai_codex"].sum()),
                "n_ai_copilot": int(g["ai_copilot"].sum()),
                "n_ai_cursor": int(g["ai_cursor"].sum()),
                "n_ai_aider": int(g["ai_aider"].sum()),
                "n_ai_gemini": int(g["ai_gemini"].sum()),
                "n_ai_other_agent": int(g["ai_other_agent"].sum()),
                "n_ai_author_login": int(g["ai_author_login"].sum()),
                "n_ai_trailer": int(g["ai_trailer"].sum()),
                "n_commits_multi_vendor": int(
                    (g[[f"ai_{k}" for k in AI_FLAGS]].sum(axis=1) > 1).sum()
                ),
                "ai_models": ";".join(
                    (
                        f"{m}={n}"
                        for m, n in g["ai_models"]
                        .str.split(";")
                        .explode()
                        .replace("", np.nan)
                        .dropna()
                        .value_counts()
                        .items()
                    )
                ),
            }
        )
    s = pd.DataFrame(rows)
    s.to_csv(out("commit_summary"), index=False)
    return s


def collect_commit_sizes(commits: pd.DataFrame, n: int = COMMIT_SAMPLE) -> pd.DataFrame:
    rows = []
    for repo in APPS:
        g = commits[commits["repo"] == repo]
        samp = g.sample(n=min(n, len(g)), random_state=SEED)
        for r in samp.itertuples():
            try:
                d = gh(f"repos/{OWNER}/{repo}/commits/{r.sha}")
            except Exception as e:
                print(f"  size {repo} {r.sha[:7]}: {e}")
                continue
            st = d.get("stats", {})
            rows.append(
                {
                    "repo": repo,
                    "sha": r.sha,
                    "additions": st.get("additions"),
                    "deletions": st.get("deletions"),
                    "total": st.get("total"),
                    "files_changed": (
                        len(d.get("files", []))
                        if d.get("files") is not None
                        else np.nan
                    ),
                    "files_truncated": len(d.get("files", [])) >= 300,
                    "ai_any": r.ai_any,
                    "n_parents": r.n_parents,
                }
            )
        print(f"  sizes {repo}: {sum((1 for x in rows if x['repo'] == repo))}")
    df = pd.DataFrame(rows)
    df.to_csv(out("commit_sizes"), index=False)
    return df


def code_frequency(repo: str) -> dict:
    """Weekly additions/deletions for the whole default branch (cheap cross-check on LOC churn)."""
    try:
        w = gh(f"repos/{OWNER}/{repo}/stats/code_frequency", interval=3.0, retries=6)
    except Exception:
        return {}
    if not isinstance(w, list) or not w:
        return {}
    return {
        "additions_total": sum((x[1] for x in w)),
        "deletions_total": -sum((x[2] for x in w)),
    }


INSTR_RX = re.compile(
    "(^|/)(claude\\.md|agents\\.md|gemini\\.md|codex\\.md|\\.cursorrules|copilot-instructions\\.md)$|^\\.(claude|cursor|codex|agents)/|^\\.github/(instructions|agents|prompts)/",
    re.I,
)
KEYWORDS = [
    "claude",
    "agent",
    "codex",
    "cursor",
    "llm",
    "ai-",
    "clean-room",
    "clean room",
    "reverse engineer",
    "decompil",
    "leaked",
    "proprietary",
    "adobe",
    "microsoft",
    "test",
    "clippy",
    "no unsafe",
    "pure rust",
    "do not copy",
    "spec",
    "pull request",
    "commit",
]


def collect_instruction_files() -> pd.DataFrame:
    rows = []
    for repo in ALL_REPOS:
        try:
            tree = gh(f"repos/{OWNER}/{repo}/git/trees/HEAD", {"recursive": "1"})
        except Exception as e:
            print(f"  tree {repo}: {e}")
            continue
        paths = [
            x
            for x in tree["tree"]
            if x["type"] == "blob" and INSTR_RX.search(x["path"])
        ]
        n_rs = sum(
            (
                1
                for x in tree["tree"]
                if x["type"] == "blob" and x["path"].endswith(".rs")
            )
        )
        rows.append(
            {
                "repo": repo,
                "path": "<tree>",
                "bytes": np.nan,
                "lines": np.nan,
                "tree_truncated": tree.get("truncated", False),
                "n_rs_files_tree": n_rs,
                "n_agent_config_files": len(paths),
            }
        )
        for x in sorted(paths, key=lambda z: (z["path"].count("/"), z["path"]))[:12]:
            try:
                body = gh(f"repos/{OWNER}/{repo}/contents/{x['path']}")
                text = (
                    base64.b64decode(body["content"]).decode("utf-8", errors="replace")
                    if body.get("content")
                    else ""
                )
            except Exception as e:
                print(f"  content {repo}/{x['path']}: {e}")
                continue
            d = RAW_DIR / "instruction_files" / repo
            d.mkdir(parents=True, exist_ok=True)
            (d / x["path"].replace("/", "__")).write_text(text, encoding="utf-8")
            low = text.lower()
            rows.append(
                {
                    "repo": repo,
                    "path": x["path"],
                    "bytes": x.get("size"),
                    "lines": text.count("\n") + 1,
                    "tree_truncated": False,
                    "n_rs_files_tree": np.nan,
                    "n_agent_config_files": np.nan,
                    **{
                        f"kw_{k.strip('-').replace(' ', '_')}": low.count(k)
                        for k in KEYWORDS
                    },
                    "retrieved_utc": retrieved_at(
                        f"repos/{OWNER}/{repo}/contents/{x['path']}"
                    ),
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(out("instruction_files"), index=False)
    return df


READY_RX = re.compile(
    "ready[- ]for[- ]real[- ]work[^|\\n]*?(?:[|*~ ]+)(?:~|about )?(\\d{1,3})\\s?%", re.I
)
STAGE_RX = re.compile("\\*\\*Stage:\\s*([A-Za-z -]+?)\\*\\*")
TARGET_RX = re.compile("\\*\\*Target:\\*\\*\\s*([^\\n]+)")
REVIEWED_RX = re.compile("Last reviewed:\\*\\*\\s*(\\d{4}-\\d{2}-\\d{2})")


def _file(repo: str, path: str) -> str | None:
    try:
        body = gh(f"repos/{OWNER}/{repo}/contents/{path}")
    except Exception:
        return None
    return (
        base64.b64decode(body["content"]).decode("utf-8", errors="replace")
        if body.get("content")
        else None
    )


def collect_selfreport() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Authors' own claims: ROADMAP.md stage / target product / 'ready for real work' %, and the"""
    road, mod = ([], [])
    d = RAW_DIR / "roadmaps"
    d.mkdir(exist_ok=True)
    for repo in APPS:
        t = _file(repo, "ROADMAP.md")
        if t is None:
            road.append({"repo": repo, "roadmap_found": False})
            continue
        (d / f"{repo}_ROADMAP.md").write_text(t, encoding="utf-8")
        head = t[:6000]
        rd = READY_RX.findall(head)
        st = STAGE_RX.search(head)
        tg = TARGET_RX.search(head)
        rv = REVIEWED_RX.findall(head)
        road.append(
            {
                "repo": repo,
                "roadmap_found": True,
                "stage": st.group(1).strip() if st else "",
                "target_product": (tg.group(1).strip() if tg else "")[:120],
                "ready_for_real_work_pct_claimed": int(rd[0]) if rd else np.nan,
                "last_reviewed": rv[0] if rv else "",
                "retrieved_utc": retrieved_at(
                    f"repos/{OWNER}/{repo}/contents/ROADMAP.md"
                ),
            }
        )
        raw = _file(repo, "contributors/contributors.json")
        if raw:
            j = json.loads(raw)
            (d / f"{repo}_contributors.json").write_text(raw, encoding="utf-8")
            for m_ in j.get("models", []):
                mod.append(
                    {
                        "repo": repo,
                        "json_head_date": j.get("head_date"),
                        "json_commits": j.get("commits"),
                        "model_id": m_["id"],
                        "company": m_["company"],
                        "model": m_["model"],
                        "version": m_.get("version", ""),
                        "commits": m_["commits"],
                        "lines_added": m_["lines_added"],
                        "lines_deleted": m_["lines_deleted"],
                        "json_total_lines_added": sum(
                            (c["lines_added"] for c in j.get("contributors", []))
                        ),
                    }
                )
    r = pd.DataFrame(road)
    r.to_csv(out("selfreport_roadmap"), index=False)
    m = pd.DataFrame(mod)
    m.to_csv(out("selfreport_models"), index=False)
    return (r, m)


def collect_readme_claims() -> pd.DataFrame:
    """How each README / GitHub description words the 'clean-room' and AI claims (counts only)."""
    rows = []
    d = RAW_DIR / "readmes"
    d.mkdir(exist_ok=True)
    repos = pd.read_csv(out("repos")).set_index("repo")
    for repo in APPS:
        t = _file(repo, "README.md") or ""
        (d / f"{repo}_README.md").write_text(t, encoding="utf-8")
        low = t.lower()
        desc = str(repos.loc[repo, "description"])
        rows.append(
            {
                "repo": repo,
                "readme_chars": len(t),
                "readme_cleanroom_mentions": len(re.findall("clean[- ]room", low)),
                "desc_says_cleanroom": bool(re.search("clean[- ]room", desc, re.I)),
                "readme_alpha_mentions": len(re.findall("alpha", low)),
                "readme_anthropic_mentions": len(
                    re.findall("anthropic|claude (?:code|opus|sonnet)|opus 5", low)
                ),
                "readme_agent_mentions": len(re.findall("\\bagents?\\b", low)),
                "readme_not_affiliated": bool(
                    re.search("not (affiliated|endorsed|associated)|trademark", low)
                ),
                "retrieved_utc": retrieved_at(
                    f"repos/{OWNER}/{repo}/contents/README.md"
                ),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(out("readme_claims"), index=False)
    return df


def _site_lines(url: str) -> tuple[list[str], str]:
    import html as _html

    t = get(url, namespace="m16_site", as_json=False, min_interval=2.0)
    ts = retrieved_at(url, namespace="m16_site")
    t = re.sub("<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = _html.unescape(re.sub("<[^>]+>", "\n", t))
    return ([ln.strip() for ln in t.split("\n") if ln.strip()], ts)


def collect_site() -> pd.DataFrame:
    """The ArtCraft site's own claims per app: tagline, maturity label, platforms (getartcraft.com/apps)."""
    url = "https://getartcraft.com/apps"
    lines, ts = _site_lines(url)
    (RAW_DIR / "site_apps_text.txt").write_text("\n".join(lines), encoding="utf-8")
    rows, i = ([], 0)
    while i < len(lines):
        if (
            re.fullmatch("\\d{2}", lines[i])
            and i + 5 < len(lines)
            and (lines[i + 3].lower() == "craft")
        ):
            cat, pre, tag = (lines[i + 1], lines[i + 2], lines[i + 4])
            j, mat, plats = (i + 5, "", [])
            while (
                j < len(lines)
                and (not re.fullmatch("\\d{2}", lines[j]))
                and (lines[j] != "Next up")
            ):
                if lines[j] in (
                    "Early alpha",
                    "In development",
                    "Alpha",
                    "Beta",
                    "Pre-alpha",
                    "Stable",
                    "Coming soon",
                ):
                    mat = lines[j]
                if lines[j] in ("macOS", "Windows", "Linux", "Web"):
                    plats.append(lines[j])
                j += 1
            rows.append(
                {
                    "repo": f"{pre}craft".lower(),
                    "site_name": f"{pre}Craft",
                    "site_category": cat,
                    "site_tagline": tag,
                    "site_maturity_label": mat,
                    "site_platforms": ";".join(plats),
                    "source_url": url,
                    "retrieved_utc": ts,
                }
            )
            i = j
        else:
            i += 1
    df = pd.DataFrame(rows)
    df.to_csv(out("site_claims"), index=False)
    return df


SKIP_DIRS = {".git", "target", "node_modules", "vendor", "third_party"}


def count_clone(root: Path) -> dict:
    n_files = n_nb = n_code = n_test = n_md = n_cargo = 0
    for p in root.rglob("*"):
        if not p.is_file() or any(
            (part in SKIP_DIRS for part in p.relative_to(root).parts)
        ):
            continue
        suf = p.suffix.lower()
        if suf == ".rs":
            n_files += 1
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            nb = [ln for ln in lines if ln.strip()]
            n_nb += len(nb)
            n_code += sum((1 for ln in nb if not ln.lstrip().startswith("//")))
            n_test += sum(
                (
                    1
                    for ln in nb
                    if ln.strip() in ("#[test]", "#[tokio::test]")
                    or ln.strip().startswith("#[test")
                )
            )
        elif suf == ".md":
            try:
                n_md += sum(
                    (
                        1
                        for ln in p.read_text(
                            encoding="utf-8", errors="replace"
                        ).splitlines()
                        if ln.strip()
                    )
                )
            except OSError:
                pass
        if p.name == "Cargo.toml":
            n_cargo += 1
    return {
        "rs_files": n_files,
        "rs_lines_nonblank": n_nb,
        "rs_lines_noncomment": n_code,
        "test_fns": n_test,
        "md_lines_nonblank": n_md,
        "cargo_tomls": n_cargo,
    }


def collect_loc(
    repos_df: pd.DataFrame, names: list[str] = CLONE_REPOS, keep: bool = False
) -> pd.DataFrame:
    base = RAW_DIR / "clones"
    base.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in names:
        dest = base / name
        if dest.exists():
            _rmtree(dest)
        t0 = time.time()
        cp = subprocess.run(
            [
                "git",
                "-c",
                "core.longpaths=true",
                "clone",
                "--depth",
                "1",
                "--quiet",
                f"https://github.com/{OWNER}/{name}.git",
                str(dest),
            ],
            capture_output=True,
            text=True,
            timeout=1500,
        )
        if cp.returncode != 0:
            print(f"  clone {name} failed: {cp.stderr[:200]}")
            continue
        head = subprocess.run(
            ["git", "-C", str(dest), "log", "-1", "--format=%H|%cI"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        stats = count_clone(dest)
        rb = int(repos_df.loc[repos_df["repo"] == name, "rust_bytes"].iloc[0])
        rows.append(
            {
                "repo": name,
                "head_sha": head.split("|")[0],
                "head_commit_date": head.split("|")[-1],
                "cloned_utc": now_utc(),
                **stats,
                "rust_bytes_api": rb,
                "bytes_per_nonblank_line": (
                    rb / stats["rs_lines_nonblank"]
                    if stats["rs_lines_nonblank"]
                    else np.nan
                ),
                "key_repo": name in KEY_REPOS,
                **code_frequency(name),
            }
        )
        print(
            f"  clone {name}: {stats['rs_lines_nonblank']:,} non-blank .rs lines in {time.time() - t0:.0f}s"
        )
        if not keep:
            _rmtree(dest)
    df = pd.DataFrame(rows)
    df.to_csv(out("loc"), index=False)
    if not keep and base.exists() and (not any(base.iterdir())):
        base.rmdir()
    return df


def collect_ci(n_pages: int = 2) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Most recent n_pages*100 workflow runs per repo + all releases/assets (download_count)."""
    runs, rels = ([], [])
    for repo in ALL_REPOS:
        total = None
        got = []
        for page in range(1, n_pages + 1):
            try:
                body = gh(
                    f"repos/{OWNER}/{repo}/actions/runs",
                    {"per_page": 100, "page": page},
                )
            except Exception as e:
                print(f"  runs {repo}: {e}")
                break
            total = body.get("total_count", total)
            got.extend(body.get("workflow_runs", []))
            if len(body.get("workflow_runs", [])) < 100:
                break
        for x in got:
            runs.append(
                {
                    "repo": repo,
                    "run_id": x["id"],
                    "workflow": x["name"],
                    "event": x["event"],
                    "status": x["status"],
                    "conclusion": x["conclusion"] or "",
                    "head_branch": x.get("head_branch") or "",
                    "created_at": x["created_at"],
                    "total_count_repo": total,
                }
            )
        for x in paginate(f"repos/{OWNER}/{repo}/releases"):
            for a in x.get("assets", []) or [
                {"name": "", "download_count": 0, "size": 0, "content_type": ""}
            ]:
                rels.append(
                    {
                        "repo": repo,
                        "tag": x["tag_name"],
                        "published_at": x.get("published_at"),
                        "prerelease": x["prerelease"],
                        "draft": x["draft"],
                        "asset": a["name"],
                        "asset_size": a.get("size"),
                        "download_count": a.get("download_count", 0),
                        "content_type": a.get("content_type", ""),
                    }
                )
    r = pd.DataFrame(runs)
    r.to_csv(out("ci_runs"), index=False)
    a = pd.DataFrame(rels)
    a.to_csv(out("release_assets"), index=False)
    return (r, a)


def collect_ci_exact(repos: list[str] | None = None) -> pd.DataFrame:
    """Exact workflow-run counts per repo x UTC day x conclusion (+ push-only), from `total_count`."""
    repos = repos or list(APPS) + ["craft-launcher"]
    created = pd.read_csv(out("repos")).set_index("repo")["created_at"]
    end = asof().normalize()
    rows = []
    for repo in repos:
        day = max(
            pd.Timestamp(created[repo]).normalize(),
            pd.Timestamp("2026-09-29", tz="UTC"),
        )
        while day <= end:
            rng = f"{day:%Y-%m-%d}..{day:%Y-%m-%d}"
            for event in ("any", "push"):
                for status in ("success", "failure", "cancelled"):
                    if event == "push" and status == "cancelled":
                        continue
                    params = {"per_page": 1, "status": status, "created": rng}
                    if event == "push":
                        params["event"] = "push"
                    try:
                        body = gh(f"repos/{OWNER}/{repo}/actions/runs", params)
                        n = body.get("total_count", 0)
                    except Exception as e:
                        print(f"  ci_exact {repo} {rng} {status}: {str(e)[:60]}")
                        n = np.nan
                    rows.append(
                        {
                            "repo": repo,
                            "date": f"{day:%Y-%m-%d}",
                            "event_filter": event,
                            "conclusion": status,
                            "n_runs": n,
                            "at_cap": n == 2500,
                        }
                    )
            day += pd.Timedelta(days=1)
        print(f"  ci_exact {repo} done")
    df = pd.DataFrame(rows)
    df.to_csv(out("ci_daily"), index=False)
    return df


def ci_summary(runs: pd.DataFrame, assets: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for repo in ALL_REPOS:
        g = runs[runs["repo"] == repo] if len(runs) else runs
        done = g[g["conclusion"].isin(["success", "failure"])] if len(g) else g
        main = done[done["event"] == "push"] if len(done) else done
        a = assets[assets["repo"] == repo] if len(assets) else assets
        binar = (
            a[
                ~a["asset"].str.contains(
                    "\\.(?:zsync|sha256|sha512|sig|json|yml|yaml|txt|blockmap)$|SHA256SUMS",
                    case=False,
                    regex=True,
                )
            ]
            if len(a)
            else a
        )
        rows.append(
            {
                "repo": repo,
                "runs_sampled": len(g),
                "runs_total_repo": g["total_count_repo"].max() if len(g) else np.nan,
                "completed_pass_fail": len(done),
                "ci_pass_pct": (
                    100 * (done["conclusion"] == "success").mean()
                    if len(done)
                    else np.nan
                ),
                "push_runs": len(main),
                "push_pass_pct": (
                    100 * (main["conclusion"] == "success").mean()
                    if len(main)
                    else np.nan
                ),
                "runs_first": g["created_at"].min() if len(g) else "",
                "runs_last": g["created_at"].max() if len(g) else "",
                "n_releases": a["tag"].nunique() if len(a) else 0,
                "n_assets": len(a),
                "downloads_all_assets": int(a["download_count"].sum()) if len(a) else 0,
                "downloads_binaries": (
                    int(binar["download_count"].sum()) if len(binar) else 0
                ),
                "n_binaries": len(binar),
            }
        )
    s = pd.DataFrame(rows)
    s.to_csv(out("ci_release_summary"), index=False)
    return s


def collect_issues() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for repo in list(APPS) + ["craft-launcher", "craft-libs"]:
        items = paginate(
            f"repos/{OWNER}/{repo}/issues",
            {"state": "all", "sort": "created", "direction": "asc"},
        )
        for x in items:
            rows.append(
                {
                    "repo": repo,
                    "number": x["number"],
                    "is_pr": "pull_request" in x,
                    "state": x["state"],
                    "created_at": x["created_at"],
                    "closed_at": x.get("closed_at") or "",
                    "merged": bool((x.get("pull_request") or {}).get("merged_at")),
                    "comments": x.get("comments", 0),
                    "reactions": (x.get("reactions") or {}).get("total_count", 0),
                    "author": pseud((x.get("user") or {}).get("login")),
                    "author_type": (x.get("user") or {}).get("type", ""),
                    "author_association": x.get("author_association", ""),
                    "labels": ";".join((l["name"] for l in x.get("labels", []))),
                    "title": EMAIL_RX.sub("<email>", x["title"])[:200],
                }
            )
        print(f"  issues {repo}: {len(items)}")
    df = pd.DataFrame(rows)
    df.to_csv(out("issues"), index=False)
    ext = {"NONE", "FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER", "CONTRIBUTOR"}
    srows = []
    for repo, g in df.groupby("repo"):
        iss = g[~g["is_pr"]]
        pr = g[g["is_pr"]]
        non_member = iss[
            iss["author_association"].isin(ext) & (iss["author_type"] != "Bot")
        ]
        pr_non_member = pr[
            pr["author_association"].isin(ext) & (pr["author_type"] != "Bot")
        ]
        srows.append(
            {
                "repo": repo,
                "n_issues": len(iss),
                "n_prs": len(pr),
                "issues_open": int((iss["state"] == "open").sum()),
                "issues_closed": int((iss["state"] == "closed").sum()),
                "issue_reporters_distinct": iss["author"].nunique(),
                "issue_reporters_non_member": non_member["author"].nunique(),
                "share_issues_by_non_member": (
                    len(non_member) / len(iss) if len(iss) else np.nan
                ),
                "pr_authors_distinct": pr["author"].nunique(),
                "pr_authors_non_member": pr_non_member["author"].nunique(),
                "prs_merged": int(pr["merged"].sum()),
                "prs_merged_by_non_member": int(pr_non_member["merged"].sum()),
                "bug_labelled_issues": int(
                    iss["labels"].str.contains("bug", case=False).sum()
                ),
                "median_hours_to_close_issue": (
                    float(
                        np.median(
                            (
                                pd.to_datetime(
                                    iss.loc[iss["closed_at"] != "", "closed_at"]
                                )
                                - pd.to_datetime(
                                    iss.loc[iss["closed_at"] != "", "created_at"]
                                )
                            ).dt.total_seconds()
                            / 3600
                        )
                    )
                    if (iss["closed_at"] != "").any()
                    else np.nan
                ),
            }
        )
    s = pd.DataFrame(srows)
    s.to_csv(out("issue_summary"), index=False)
    return (df, s)


BUGLIKE_RX = re.compile(
    "^\\[?bug|crash|panic|freez|hang|broken|fails?\x08|failure|error|doesn.?t|does not|cannot|can.?t |wrong|glitch|\\blag(?:gy|s|ging)?\\b",
    re.I,
)


def top_issues(df: pd.DataFrame, k: int = 8) -> pd.DataFrame:
    """Most-discussed issues (not PRs) per app: public titles = user evidence of real use (bug reports, requests)"""
    d = df[~df["is_pr"]].copy()
    d["bug_like_title"] = d["title"].str.contains(BUGLIKE_RX)
    d["engagement"] = d["comments"] + d["reactions"]
    d = (
        d.sort_values(["repo", "engagement"], ascending=[True, False])
        .groupby("repo")
        .head(k)
    )
    d[
        [
            "repo",
            "number",
            "title",
            "comments",
            "reactions",
            "state",
            "created_at",
            "author_association",
            "bug_like_title",
        ]
    ].to_csv(out("top_issues"), index=False)
    return d


def collect_forks() -> pd.DataFrame:
    rows = []
    for repo in APPS:
        items = paginate(
            f"repos/{OWNER}/{repo}/forks", {"sort": "oldest"}, max_pages=400
        )
        rows.extend(
            (
                {
                    "repo": repo,
                    "fork_created_at": x["created_at"],
                    "owner_type": x["owner"]["type"],
                }
                for x in items
            )
        )
        print(f"  forks {repo}: {len(items)}")
    df = pd.DataFrame(rows)
    df.to_csv(out("forks"), index=False)
    return df


def ossinsight_stars(
    repo: str, per: str = "day", start: str = "2026-09-25"
) -> tuple[pd.DataFrame, dict]:
    """Star events from OSS Insight. The GitHub stargazer listing is admin-only since 2026-07, so"""
    url = f"https://api.ossinsight.io/v1/repos/{OWNER}/{repo}/stargazers/history"
    for p in ({"per": per, "from": start}, {"per": per}, {"per": "month"}):
        try:
            body = get(url, p, namespace="m16_ossinsight", min_interval=2.0, retries=2)
        except Exception as e:
            print(f"  OSS Insight {repo} {p}: {str(e)[:80]}")
            continue
        rows = body.get("data", {}).get("rows", [])
        if rows:
            df = pd.DataFrame(rows)
            return (
                df,
                {
                    "params": p,
                    "data_quality": body.get("data_quality", {}),
                    "per": p.get("per"),
                },
            )
    return (pd.DataFrame(), {})


def collect_stars(repos_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for repo in APPS:
        df, meta = ossinsight_stars(repo)
        stars_now = int(repos_df.loc[repos_df["repo"] == repo, "stars"].iloc[0])
        if df.empty:
            rows.append(
                {
                    "repo": repo,
                    "date": "",
                    "stargazers": np.nan,
                    "per": "",
                    "stars_now": stars_now,
                    "status": "unavailable",
                }
            )
            continue
        dcol = "date" if "date" in df else df.columns[0]
        for r in df.itertuples():
            rows.append(
                {
                    "repo": repo,
                    "date": getattr(r, dcol),
                    "stargazers": float(r.stargazers),
                    "per": meta["per"],
                    "stars_now": stars_now,
                    "status": (meta["data_quality"] or {}).get("status", ""),
                }
            )
    out_df = pd.DataFrame(rows)
    out_df.to_csv(out("stars_ossinsight"), index=False)
    return out_df


def snapshot(repos: list[str] | None = None) -> pd.DataFrame:
    """Append current stars/forks/watchers/issues/release-downloads per repo with a UTC timestamp to"""
    ts = now_utc()
    rows = []
    for name in repos or list(APPS) + SUPPORT + LEGACY:
        r = gh(f"repos/{OWNER}/{name}", refresh=True)
        rel = []
        for page in range(1, 20):
            chunk = gh(
                f"repos/{OWNER}/{name}/releases",
                {"per_page": 100, "page": page},
                refresh=True,
            )
            rel.extend(chunk)
            if len(chunk) < 100:
                break
        rows.append(
            {
                "snapshot_utc": ts,
                "repo": name,
                "stars": r["stargazers_count"],
                "forks": r["forks_count"],
                "watchers_subscribers": r.get("subscribers_count", ""),
                "open_issues_and_prs": r["open_issues_count"],
                "n_releases": len(rel),
                "release_downloads": sum(
                    (
                        a.get("download_count", 0)
                        for x in rel
                        for a in x.get("assets", [])
                    )
                ),
                "pushed_at": r["pushed_at"],
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(SNAPSHOT_CSV, mode="a", header=not SNAPSHOT_CSV.exists(), index=False)
    return df


HN_START = pd.Timestamp("2026-09-25", tz="UTC")
HN_QUERIES = [
    "photocraft",
    "artcraft",
    "storytold",
    "getartcraft",
    "filmcraft",
    "lightcraft",
    "pdfcraft",
    "vectorcraft",
    "effectcraft",
    "designcraft",
    "wordcraft rust",
    "gridcraft",
    "deckcraft",
    "cadcraft",
    "soundcraft rust",
    "craft apps rust",
    "clean-room photoshop",
    "pure rust photoshop",
    "rust photoshop",
    "open source photoshop rust",
]
NAME_RX = re.compile(
    "storytold|getartcraft|artcraft|photocraft|filmcraft|lightcraft|pdfcraft|vectorcraft|effectcraft|designcraft|wordcraft|gridcraft|deckcraft|cadcraft|soundcraft|craft apps",
    re.I,
)


def collect_hn() -> pd.DataFrame:
    rows = []
    seen = set()
    for q in HN_QUERIES:
        for tag in ("story", "comment"):
            try:
                body = get(
                    "https://hn.algolia.com/api/v1/search_by_date",
                    {
                        "query": q,
                        "tags": tag,
                        "hitsPerPage": 100,
                        "numericFilters": f"created_at_i>{int(HN_START.timestamp())}",
                    },
                    namespace=NS_SEARCH,
                    min_interval=1.0,
                )
            except Exception as e:
                print(f"  HN {q}/{tag}: {e}")
                continue
            for h in body.get("hits", []):
                oid = h["objectID"]
                if oid in seen:
                    continue
                seen.add(oid)
                text = " ".join(
                    (
                        str(h.get(k) or "")
                        for k in (
                            "title",
                            "url",
                            "story_title",
                            "story_url",
                            "comment_text",
                        )
                    )
                )
                rows.append(
                    {
                        "object_id": oid,
                        "kind": tag,
                        "query": q,
                        "created_at": h["created_at"],
                        "title": h.get("title") or h.get("story_title") or "",
                        "url": h.get("url") or h.get("story_url") or "",
                        "points": h.get("points"),
                        "num_comments": h.get("num_comments"),
                        "story_id": h.get("story_id") or oid,
                        "comment_snippet": (
                            re.sub("<[^>]+>", " ", h.get("comment_text") or "")[:240]
                            if tag == "comment"
                            else ""
                        ),
                        "name_match": bool(NAME_RX.search(text)),
                        "hn_url": f"https://news.ycombinator.com/item?id={oid}",
                        "retrieved_utc": now_utc(),
                    }
                )
    df = pd.DataFrame(rows)
    df.to_csv(out("hn_raw"), index=False)
    return df


THEMES = {
    "quality_complaint": "\\b(lag|laggy|slow|broken|buggy|bugs?|crash\\w*|unusable|janky|glitch\\w*|doesn'?t work|not working|half[- ]baked)\\b",
    "ai_process": "vibe|slop|ai[- ]generated|ai[- ]written|\\bllm\\b|claude|opus|written by (an )?ai",
    "legal_cleanroom": "clean[- ]?room|copyright|trade dress|lawsuit|\\bsue[ds]?\\b|\\blegal|patent|infring|licen[sc]",
    "named_alternative": "affinity|krita|gimp|inkscape|darktable|libreoffice|onlyoffice|blender|davinci|kdenlive|photopea|ardour|openshot",
    "positive": "impressive|amazing|awesome|nice work|great work|congrat|\\bwow\\b|love (this|it)|cool project|well done",
    "price_adobe": "subscription|cancell?ation fee|too expensive|overpriced|\\bprice",
}
THEME_RX = {k: re.compile(v, re.I) for k, v in THEMES.items()}


def _walk(node: dict, depth: int = 0):
    yield (node, depth)
    for ch in node.get("children", []) or []:
        yield from _walk(ch, depth + 1)


def collect_hn_threads(
    hn: pd.DataFrame, min_points: int = 10, min_comments: int = 10
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Full comment trees (Algolia /items/{id}) for the larger name-matching stories: comment counts,"""
    st = hn[
        (hn["kind"] == "story")
        & hn["name_match"]
        & ((hn["points"] >= min_points) | (hn["num_comments"] >= min_comments))
    ]
    rows, trows = ([], [])
    for r in st.drop_duplicates("object_id").itertuples():
        try:
            tree = get(
                f"https://hn.algolia.com/api/v1/items/{r.object_id}",
                namespace=NS_SEARCH,
                min_interval=1.0,
            )
        except Exception as e:
            print(f"  HN item {r.object_id}: {e}")
            continue
        com = [(n, d) for n, d in _walk(tree) if n.get("text") and n is not tree]
        texts = [re.sub("<[^>]+>", " ", n["text"]) for n, _ in com]
        op = tree.get("author")
        rows.append(
            {
                "object_id": r.object_id,
                "title": tree.get("title"),
                "url": tree.get("url"),
                "created_at": tree.get("created_at"),
                "points": tree.get("points"),
                "n_comments_tree": len(com),
                "max_depth": max((d for _, d in com), default=0),
                "distinct_commenters": len({n.get("author") for n, _ in com}),
                "submitter_comments": sum((1 for n, _ in com if n.get("author") == op)),
                "retrieved_utc": retrieved_at(
                    f"https://hn.algolia.com/api/v1/items/{r.object_id}",
                    namespace=NS_SEARCH,
                ),
                **{
                    f"share_{k}": (
                        sum((bool(rx.search(t)) for t in texts)) / len(texts)
                        if texts
                        else np.nan
                    )
                    for k, rx in THEME_RX.items()
                },
                **{
                    f"n_{k}": sum((bool(rx.search(t)) for t in texts))
                    for k, rx in THEME_RX.items()
                },
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(out("hn_threads"), index=False)
    return (df, st)


REDDIT_UA = {
    "User-Agent": "software-substitution-research/0.1 (academic research; contact via GitHub)"
}
SUBREDDITS = [
    "rust",
    "programming",
    "opensource",
    "photoshop",
    "linux",
    "ClaudeAI",
    "singularity",
    "technology",
    "ArtificialInteligence",
    "LocalLLaMA",
]


def collect_reddit() -> pd.DataFrame:
    log, rows = ([], [])
    jobs = [
        ("all", q)
        for q in (
            "photocraft",
            "artcraft storytold",
            "getartcraft",
            "filmcraft pdfcraft",
            "wordcraft rust clean-room",
        )
    ]
    jobs += [(s, "photocraft OR artcraft OR storytold") for s in SUBREDDITS]
    for sub, q in jobs:
        url = (
            "https://www.reddit.com/search.json"
            if sub == "all"
            else f"https://www.reddit.com/r/{sub}/search.json"
        )
        params = {"q": q, "sort": "new", "limit": 100, "t": "month"}
        if sub != "all":
            params["restrict_sr"] = 1
        try:
            body = get(
                url,
                params,
                namespace="m16_reddit",
                headers=REDDIT_UA,
                min_interval=3.0,
                retries=1,
            )
            log.append({"subreddit": sub, "query": q, "status": "ok"})
        except Exception as e:
            log.append(
                {"subreddit": sub, "query": q, "status": f"blocked/err: {str(e)[:60]}"}
            )
            continue
        for ch in body.get("data", {}).get("children", []):
            d = ch["data"]
            rows.append(
                {
                    "subreddit": d["subreddit"],
                    "title": d["title"],
                    "score": d["score"],
                    "num_comments": d["num_comments"],
                    "upvote_ratio": d.get("upvote_ratio"),
                    "created_utc": datetime.fromtimestamp(
                        d["created_utc"], timezone.utc
                    ).isoformat(),
                    "url": "https://www.reddit.com" + d["permalink"],
                    "query": q,
                }
            )
    pd.DataFrame(log).to_csv(RAW_DIR / "reddit_access_log.csv", index=False)
    df = (
        pd.DataFrame(rows).drop_duplicates("url")
        if rows
        else pd.DataFrame(
            columns=[
                "subreddit",
                "title",
                "score",
                "num_comments",
                "upvote_ratio",
                "created_utc",
                "url",
                "query",
            ]
        )
    )
    df.to_csv(out("reddit_raw"), index=False)
    return df


def ci_rates() -> pd.DataFrame:
    """CI pass % from exact daily counts (success / (success + failure)); all events and push-only."""
    f = out("ci_daily")
    if not f.exists():
        return pd.DataFrame(columns=["repo"])
    d = pd.read_csv(f)
    rows = []
    for repo, g in d.groupby("repo"):

        def tot(ev, st):
            return g[(g["event_filter"] == ev) & (g["conclusion"] == st)][
                "n_runs"
            ].sum()

        s_all, f_all, c_all = (
            tot("any", "success"),
            tot("any", "failure"),
            tot("any", "cancelled"),
        )
        s_p, f_p = (tot("push", "success"), tot("push", "failure"))
        rows.append(
            {
                "repo": repo,
                "ci_success": int(s_all),
                "ci_failure": int(f_all),
                "ci_cancelled": int(c_all),
                "ci_pass_pct_all": (
                    100 * s_all / (s_all + f_all) if s_all + f_all else np.nan
                ),
                "ci_push_success": int(s_p),
                "ci_push_failure": int(f_p),
                "ci_pass_pct_push": 100 * s_p / (s_p + f_p) if s_p + f_p else np.nan,
                "ci_any_cell_at_cap": bool(g["at_cap"].any()),
            }
        )
    return pd.DataFrame(rows)


def build_suite_table() -> pd.DataFrame:
    repos = pd.read_csv(out("repos"), parse_dates=["created_at", "pushed_at"])
    repos = repos[repos["repo"].isin(APPS)]
    inc = pd.read_csv(SAMPLE_DIR / "16_craft_incumbents.csv")
    cs = pd.read_csv(out("commit_summary"), parse_dates=["first_commit", "last_commit"])
    loc = pd.read_csv(out("loc"))
    site = pd.read_csv(out("site_claims"))
    road = pd.read_csv(out("selfreport_roadmap"))
    cis = pd.read_csv(out("ci_release_summary"))
    t = repos[
        [
            "repo",
            "display",
            "created_at",
            "pushed_at",
            "stars",
            "forks",
            "license",
            "n_contributors",
            "rust_bytes",
            "rust_loc_est_bytes35",
            "n_releases",
            "release_downloads",
            "description",
        ]
    ].copy()
    t = t.merge(
        inc[
            [
                "repo",
                "incumbent_product",
                "incumbent_vendor",
                "plan_priced",
                "price_usd_per_year",
                "bundle_id",
                "verification",
            ]
        ].rename(columns={"verification": "price_verification"}),
        on="repo",
        how="left",
    )
    t = t.merge(
        cs[
            [
                "repo",
                "n_commits",
                "first_commit",
                "last_commit",
                "commits_per_calendar_day",
                "calendar_days",
                "share_ai_any",
                "share_ai_claude",
                "n_ai_any" if "n_ai_any" in cs else "n_commits",
            ]
        ].rename(columns={"n_commits": "commits"}),
        on="repo",
        how="left",
    )
    t = t.merge(
        loc[
            [
                "repo",
                "rs_files",
                "rs_lines_nonblank",
                "rs_lines_noncomment",
                "test_fns",
                "bytes_per_nonblank_line",
            ]
        ],
        on="repo",
        how="left",
    )
    t = t.merge(
        site[["repo", "site_maturity_label", "site_tagline"]], on="repo", how="left"
    )
    t = t.merge(
        road[
            ["repo", "stage", "target_product", "ready_for_real_work_pct_claimed"]
        ].rename(columns={"stage": "roadmap_stage"}),
        on="repo",
        how="left",
    )
    t = t.merge(
        cis[
            [
                "repo",
                "downloads_all_assets",
                "downloads_binaries",
                "ci_pass_pct",
                "runs_total_repo",
            ]
        ].rename(columns={"ci_pass_pct": "ci_pass_pct_recent200"}),
        on="repo",
        how="left",
    )
    r = ci_rates()
    if len(r):
        t = t.merge(r, on="repo", how="left")
    t["ai_any_pct"] = 100 * t["share_ai_any"]
    t["ai_claude_pct"] = 100 * t["share_ai_claude"]
    t = t.sort_values("created_at", kind="stable").reset_index(drop=True)
    t.to_csv(out("suite_table"), index=False)
    return t


def bundle_annual_price() -> dict:
    b = pd.read_csv(SAMPLE_DIR / "16_craft_bundles.csv")
    return {"total": float(b["price_usd_per_year"].sum()), "rows": b}


def run_all(
    *, loc: bool = True, sizes: bool = True, forks: bool = True, social: bool = True
) -> dict:
    asof()
    res = {}
    res["repos"] = collect_repos()
    res["commits"] = collect_commits()
    res["daily"] = commit_daily(res["commits"])
    res["commit_summary"] = commit_summary(res["commits"], res["repos"])
    if sizes:
        res["sizes"] = collect_commit_sizes(res["commits"])
    res["instr"] = collect_instruction_files()
    res["road"], res["models"] = collect_selfreport()
    res["site"] = collect_site()
    res["readme"] = collect_readme_claims()
    if loc:
        res["loc"] = collect_loc(res["repos"])
    res["ci_runs"], res["assets"] = collect_ci()
    res["ci_summary"] = ci_summary(res["ci_runs"], res["assets"])
    res["ci_daily"] = collect_ci_exact()
    res["issues"], res["issue_summary"] = collect_issues()
    res["top_issues"] = top_issues(res["issues"])
    if forks:
        res["forks"] = collect_forks()
    res["stars"] = collect_stars(res["repos"])
    if social:
        res["hn"] = collect_hn()
        res["hn_threads"], _ = collect_hn_threads(res["hn"])
        res["reddit"] = collect_reddit()
    res["snapshot"] = snapshot()
    res["suite_table"] = build_suite_table()
    return res
