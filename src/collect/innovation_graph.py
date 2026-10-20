"""Module 02 - GitHub Innovation Graph (public activity on GitHub, by economy and quarter)."""

from __future__ import annotations
import io
import json
import re
import numpy as np
import pandas as pd
from ..fetch import get
from ..paths import CACHE, PROCESSED, RAW

NS = "innovationgraph"
BASE = "https://raw.githubusercontent.com/github/innovationgraph/main/data/{}.csv"
FILES = [
    "developers",
    "repositories",
    "git_pushes",
    "organizations",
    "languages",
    "licenses",
    "topics",
]
RAW_DIR = RAW / "innovation_graph"
RAW_DIR.mkdir(parents=True, exist_ok=True)
AGGREGATES = {"EU"}
TOP_LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "Go",
    "Rust",
    "C++",
    "C#",
]
PERMISSIVE = {
    "MIT",
    "Apache-2.0",
    "BSD-3-Clause",
    "BSD-2-Clause",
    "ISC",
    "Zlib",
    "BSL-1.0",
    "0BSD",
    "MIT-0",
    "BSD-3-Clause-Clear",
    "Artistic-2.0",
    "UPL-1.0",
    "NCSA",
    "PostgreSQL",
    "BSD-4-Clause",
    "AFL-3.0",
    "MS-PL",
    "ECL-2.0",
    "MulanPSL-2.0",
}
COPYLEFT = {
    "GPL-3.0",
    "GPL-2.0",
    "AGPL-3.0",
    "LGPL-3.0",
    "LGPL-2.1",
    "MPL-2.0",
    "EPL-2.0",
    "EPL-1.0",
    "EUPL-1.2",
    "EUPL-1.1",
    "OSL-3.0",
    "CECILL-2.1",
    "LGPL-2.0",
    "GPL-2.0+",
    "MS-RL",
    "CC-BY-SA-4.0",
    "LPPL-1.3c",
    "ODbL-1.0",
    "OFL-1.1",
}
PUBLIC_DOMAIN = {"Unlicense", "CC0-1.0", "WTFPL"}
AI_TOPIC_RE = re.compile(
    "(?:^|-)(?:ai|llm|llms|gpt|chatgpt|openai|langchain|genai|claude|anthropic|copilot|agent|agents|agentic|mcp|rag|ollama|gemini|deepseek|machine-learning|deep-learning|artificial-intelligence|generative-ai|vibe-coding|cursor|huggingface|transformers|pytorch|tensorflow|llama|mistral|codex|prompt-engineering|large-language-models|neural-network|computer-vision|nlp)(?:$|-)"
)
LLM_TOPIC_RE = re.compile(
    "(?:^|-)(?:llm|llms|gpt|chatgpt|openai|langchain|genai|claude|anthropic|copilot|agent|agents|agentic|mcp|rag|ollama|gemini|deepseek|generative-ai|vibe-coding|cursor|llama|mistral|codex|prompt-engineering|large-language-models)(?:$|-)"
)
NOT_AI = {
    "user-agent",
    "user-agents",
    "useragent",
    "cursor-pagination",
    "cursors",
    "mouse-cursor",
    "custom-cursor",
}


def is_ai_topic(t: str) -> bool:
    return t not in NOT_AI and bool(AI_TOPIC_RE.search(t))


def is_llm_topic(t: str) -> bool:
    return t not in NOT_AI and bool(LLM_TOPIC_RE.search(t))


def _quarter(df: pd.DataFrame) -> pd.Series:
    return pd.PeriodIndex.from_fields(
        year=df["year"], quarter=df["quarter"], freq="Q"
    ).to_timestamp()


def load(name: str) -> pd.DataFrame:
    text = get(BASE.format(name), namespace=NS, as_json=False, min_interval=0.5)
    (RAW_DIR / f"{name}.csv").write_text(text, encoding="utf-8")
    df = pd.read_csv(io.StringIO(text), keep_default_na=False, na_values=[""])
    df["iso2_code"] = df["iso2_code"].astype(str)
    df["quarter_start"] = _quarter(df)
    return df


def retrieval_date() -> str:
    for p in sorted((CACHE / NS).glob("*.json")):
        return json.loads(p.read_text(encoding="utf-8"))["retrieved_utc"][:10]
    return pd.Timestamp.today().date().isoformat()


def _economies(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["iso2_code"].isin(AGGREGATES)]


def balanced_economies(df: pd.DataFrame) -> set[str]:
    """Economies reported in every quarter (removes entry/exit of small economies)."""
    d = _economies(df)
    nq = d["quarter_start"].nunique()
    c = d.groupby("iso2_code")["quarter_start"].nunique()
    return set(c[c == nq].index)


def totals(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for metric in ["developers", "repositories", "git_pushes", "organizations"]:
        d = _economies(frames[metric])
        bal = balanced_economies(frames[metric])
        world = d.groupby("quarter_start")[metric].sum()
        world_bal = d[d["iso2_code"].isin(bal)].groupby("quarter_start")[metric].sum()
        us = d[d["iso2_code"] == "US"].groupby("quarter_start")[metric].sum()
        n_econ = d.groupby("quarter_start")["iso2_code"].nunique()
        for scope, s in (
            ("World", world),
            ("World (balanced panel)", world_bal),
            ("US", us),
        ):
            out = s.rename("value").reset_index()
            out["scope"], out["metric"] = (scope, metric)
            out["index_2020q1"] = 100 * out["value"] / out["value"].iloc[0]
            out["n_economies"] = (
                out["quarter_start"].map(n_econ)
                if scope == "World"
                else len(bal) if scope.startswith("World") else 1
            )
            out["net_change"] = out["value"].diff()
            out["yoy_pct"] = 100 * (out["value"] / out["value"].shift(4) - 1)
            rows.append(out)
    return pd.concat(rows, ignore_index=True)[
        [
            "scope",
            "metric",
            "quarter_start",
            "value",
            "index_2020q1",
            "net_change",
            "yoy_pct",
            "n_economies",
        ]
    ]


def languages(df: pd.DataFrame) -> pd.DataFrame:
    d = _economies(df)
    d = d[d["language_type"] == "programming"]
    tot = (
        d.groupby("quarter_start")["num_pushers"]
        .sum()
        .rename("all_programming_pushers")
    )
    g = (
        d[d["language"].isin(TOP_LANGUAGES)]
        .groupby(["language", "quarter_start"])["num_pushers"]
        .sum()
    )
    out = g.rename("pushers").reset_index().merge(tot.reset_index(), on="quarter_start")
    out["share"] = out["pushers"] / out["all_programming_pushers"]
    out["index_2020q1"] = (
        100 * out["pushers"] / out.groupby("language")["pushers"].transform("first")
    )
    return out.sort_values(["language", "quarter_start"])


def license_family(spdx: str) -> str:
    if spdx in PERMISSIVE:
        return "Permissive"
    if spdx in COPYLEFT or spdx.startswith(
        ("GPL", "LGPL", "AGPL", "EPL", "EUPL", "CECILL")
    ):
        return "Copyleft"
    if spdx in PUBLIC_DOMAIN:
        return "Public domain"
    return "Other / unidentified"


def licenses(df: pd.DataFrame) -> pd.DataFrame:
    d = _economies(df).copy()
    d["family"] = d["spdx_license"].map(license_family)
    g = (
        d.groupby(["family", "quarter_start"])["num_pushers"]
        .sum()
        .rename("pushers")
        .reset_index()
    )
    g["share"] = g["pushers"] / g.groupby("quarter_start")["pushers"].transform("sum")
    top = (
        d.groupby(["spdx_license", "quarter_start"])["num_pushers"]
        .sum()
        .rename("pushers")
        .reset_index()
    )
    top["share"] = top["pushers"] / top.groupby("quarter_start")["pushers"].transform(
        "sum"
    )
    top = top[
        top["spdx_license"].isin(
            ["MIT", "Apache-2.0", "GPL-3.0", "AGPL-3.0", "NOASSERTION", "BSD-3-Clause"]
        )
    ]
    top = top.rename(columns={"spdx_license": "family"})
    top["level"] = "licence"
    g["level"] = "family"
    return pd.concat([g, top], ignore_index=True)


def ai_topics(df: pd.DataFrame) -> pd.DataFrame:
    """Share of topic-pusher counts on AI/ML and LLM/agent topics."""
    d = _economies(df)
    bal = balanced_economies(df)
    d = d[d["iso2_code"].isin(bal)].copy()
    d["is_ai"] = d["topic"].map(is_ai_topic)
    d["is_llm"] = d["topic"].map(is_llm_topic)
    tot = d.groupby("quarter_start")["num_pushers"].sum()
    rows = []
    for grp, mask in (
        ("AI/ML topics (any)", d["is_ai"]),
        ("LLM / agent topics", d["is_llm"]),
    ):
        s = (
            d[mask]
            .groupby("quarter_start")["num_pushers"]
            .sum()
            .reindex(tot.index, fill_value=0)
        )
        rows.append(
            pd.DataFrame(
                {
                    "group": grp,
                    "quarter_start": tot.index,
                    "pushers": s.values,
                    "all_topic_pushers": tot.values,
                    "share": (s / tot).values,
                    "n_economies": len(bal),
                }
            )
        )
    return pd.concat(rows, ignore_index=True)


def ai_topic_list(df: pd.DataFrame) -> pd.DataFrame:
    d = _economies(df)
    d = d[d["topic"].map(is_ai_topic)]
    last = d["quarter_start"].max()
    g = d.groupby(["topic", "quarter_start"])["num_pushers"].sum().unstack()
    return g.sort_values(last, ascending=False)


def run() -> dict[str, pd.DataFrame]:
    frames = {f: load(f) for f in FILES}
    out = {
        "totals": totals(frames),
        "languages": languages(frames["languages"]),
        "licenses": licenses(frames["licenses"]),
        "ai_topics": ai_topics(frames["topics"]),
    }
    for k, v in out.items():
        v.to_csv(PROCESSED / f"innovation_graph_{k}.csv", index=False)
    meta = {
        "retrieved": retrieval_date(),
        "last_quarter": str(frames["developers"]["quarter_start"].max().date()),
        "source": "https://github.com/github/innovationgraph",
    }
    (PROCESSED / "innovation_graph_meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    out["frames"] = frames
    return out


def _qlabel(ts: pd.Timestamp) -> str:
    return f"{ts.year}Q{ts.quarter}"


def key_numbers(out: dict[str, pd.DataFrame]) -> dict[str, str]:
    """Return summary values from the processed data."""
    t, lang, lic, ai = (
        out["totals"],
        out["languages"],
        out["licenses"],
        out["ai_topics"],
    )
    last = t["quarter_start"].max()
    yr_ago = last - pd.DateOffset(years=1)

    def val(scope, metric, q):
        return float(
            t[(t.scope == scope) & (t.metric == metric) & (t.quarter_start == q)][
                "value"
            ].iloc[0]
        )

    def yoy(scope, metric, q):
        return 100 * (
            val(scope, metric, q) / val(scope, metric, q - pd.DateOffset(years=1)) - 1
        )

    w = t[(t.scope == "World") & (t.metric == "git_pushes")].set_index("quarter_start")[
        "value"
    ]
    yoy_w = (100 * (w / w.shift(4) - 1)).dropna()
    pre_mean = yoy_w[
        (yoy_w.index >= "2021-01-01") & (yoy_w.index < "2025-01-01")
    ].mean()
    dev = t[(t.scope == "World") & (t.metric == "developers")].set_index(
        "quarter_start"
    )["net_change"]
    dev_2324 = dev[(dev.index >= "2023-01-01") & (dev.index < "2025-01-01")].mean()
    bal = t[(t.scope == "World (balanced panel)") & (t.metric == "git_pushes")]
    sh = lang.pivot(index="quarter_start", columns="language", values="share") * 100
    fam = (
        lic[lic.level == "family"].pivot(
            index="quarter_start", columns="family", values="share"
        )
        * 100
    )
    a = ai.pivot(index="quarter_start", columns="group", values="share") * 100
    first = sh.index.min()
    n = {
        "IgLastQuarter": _qlabel(last),
        "IgPushesLast": f"{val('World', 'git_pushes', last) / 1000000.0:.0f}",
        "IgPushesYoY": f"{yoy('World', 'git_pushes', last):.0f}",
        "IgPushesYoYPreAgentMean": f"{pre_mean:.0f}",
        "IgPushesIndex": f"{100 * val('World', 'git_pushes', last) / val('World', 'git_pushes', first):.0f}",
        "IgPushesIndexBalanced": f"{bal['index_2020q1'].iloc[-1]:.0f}",
        "IgUSPushesYoY": f"{yoy('US', 'git_pushes', last):.0f}",
        "IgDevelopersLast": f"{val('World', 'developers', last) / 1000000.0:.0f}",
        "IgDevelopersIndex": f"{100 * val('World', 'developers', last) / val('World', 'developers', first):.0f}",
        "IgDevNetAddLast": f"{dev.iloc[-1] / 1000000.0:.1f}",
        "IgDevNetAddTwentyThreeTwentyFour": f"{dev_2324 / 1000000.0:.1f}",
        "IgReposYoY": f"{yoy('World', 'repositories', last):.0f}",
        "IgPythonShareFirst": f"{sh['Python'].iloc[0]:.1f}",
        "IgPythonShareLast": f"{sh['Python'].iloc[-1]:.1f}",
        "IgTypeScriptShareFirst": f"{sh['TypeScript'].iloc[0]:.1f}",
        "IgTypeScriptShareLast": f"{sh['TypeScript'].iloc[-1]:.1f}",
        "IgJavaShareFirst": f"{sh['Java'].iloc[0]:.1f}",
        "IgJavaShareLast": f"{sh['Java'].iloc[-1]:.1f}",
        "IgCSharpShareFirst": f"{sh['C#'].iloc[0]:.1f}",
        "IgCSharpShareLast": f"{sh['C#'].iloc[-1]:.1f}",
        "IgPermissiveShareFirst": f"{fam['Permissive'].iloc[0]:.0f}",
        "IgPermissiveShareLast": f"{fam['Permissive'].iloc[-1]:.0f}",
        "IgCopyleftShareFirst": f"{fam['Copyleft'].iloc[0]:.0f}",
        "IgCopyleftShareLast": f"{fam['Copyleft'].iloc[-1]:.0f}",
        "IgAITopicSharePreChatGPT": f"{a.loc[pd.Timestamp('2022-10-01'), 'AI/ML topics (any)']:.1f}",
        "IgAITopicShareLast": f"{a['AI/ML topics (any)'].iloc[-1]:.1f}",
        "IgLLMTopicShareLast": f"{a['LLM / agent topics'].iloc[-1]:.1f}",
        "IgLLMTopicShareYearAgo": f"{a.loc[yr_ago, 'LLM / agent topics']:.1f}",
        "IgTopicEconomies": str(int(ai["n_economies"].iloc[0])),
    }
    if "frames" in out:
        gp = _economies(out["frames"]["git_pushes"])
        a = gp[gp.quarter_start == last].set_index("iso2_code")["git_pushes"]
        b = gp[gp.quarter_start == yr_ago].set_index("iso2_code")["git_pushes"]
        g = (a / b).dropna() - 1
        n["IgPushEconomiesGrowingPct"] = f"{100 * (g > 0).mean():.0f}"
        n["IgPushEconomiesMedianYoY"] = f"{100 * g.median():.0f}"
        n["IgPushEconomiesN"] = str(len(g))
    return n
    return n
