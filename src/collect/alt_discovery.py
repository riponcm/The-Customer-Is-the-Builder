"""Module 10b: broad, multi-source discovery of alternatives (pilot products)."""

from __future__ import annotations
import pandas as pd
from src.paths import PROCESSED, RAW

SRC = RAW / "alt_discovery"
ERA_BREAKS = {
    "chatgpt": pd.Timestamp("2022-11-30", tz="UTC"),
    "agents": pd.Timestamp("2025-02-24", tz="UTC"),
}
MIN_STARS = 20
NARROW = {
    "Postman": 13,
    "Notion": 11,
    "Loom": 6,
    "Canva": 4,
    "Grammarly": 2,
    "Retool": 3,
    "Screen Studio": 2,
    "Adobe Photoshop": 2,
    "Trello": 2,
    "Adobe Acrobat": 0,
    "Smallpdf": 0,
    "QuillBot": 0,
}
SELF_AUTHORED = {"riponcm/GemType"}


def load() -> pd.DataFrame:
    d = pd.concat(
        [pd.read_csv(p) for p in sorted(SRC.glob("*.csv"))], ignore_index=True
    )
    d["created"] = pd.to_datetime(d["created_at"], utc=True, errors="coerce")
    d["stars"] = pd.to_numeric(d["stars"], errors="coerce")
    d["archived"] = d["archived"].astype("string").str.lower().eq("true")
    d["is_fork"] = d["is_fork"].astype("string").str.lower().eq("true")
    d["self_authored"] = d["repo"].isin(SELF_AUTHORED)
    d["era"] = pd.cut(
        d["created"].map(lambda t: t.value if pd.notna(t) else None).astype("float"),
        [
            -float("inf"),
            ERA_BREAKS["chatgpt"].value,
            ERA_BREAKS["agents"].value,
            float("inf"),
        ],
        labels=["before ChatGPT", "ChatGPT era", "agent era"],
        right=False,
    )
    d["included"] = (
        (d["type"] == "open_source")
        & (d["core_workflow_match"] == "yes")
        & ~d["archived"]
        & ~d["is_fork"]
        & (d["stars"] >= MIN_STARS)
        & d["created"].notna()
        & ~d["self_authored"]
    )
    return d


def build(save: bool = True) -> dict:
    d = load()
    self_authored_excluded = int(d["self_authored"].sum())
    d = d[~d["self_authored"]].copy()
    inc = d[d["included"]]
    by = (
        inc.groupby(["product", "era"], observed=False)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["before ChatGPT", "ChatGPT era", "agent era"])
    )
    by["broad_total"] = by.sum(axis=1)
    paid = (
        d[d["type"].isin(["paid", "freemium", "free_closed"])].groupby("product").size()
    )
    by["paid_or_closed"] = paid.reindex(by.index).fillna(0).astype(int)
    by["candidates"] = d.groupby("product").size().reindex(by.index)
    by["narrow_total"] = pd.Series(NARROW).reindex(by.index).fillna(0).astype(int)
    by["agent_era_share_pct"] = (100 * by["agent era"] / by["broad_total"]).round(0)
    by = by.sort_values("broad_total", ascending=True).reset_index()
    ai = inc["ai_built_evidence"].fillna("").str.strip().ne("")
    meta = {
        "candidates": int(len(d)),
        "included": int(len(inc)),
        "included_agent_era": int((inc["era"] == "agent era").sum()),
        "included_ai_files": int(ai.sum()),
        "included_ai_files_agent_era": int((ai & (inc["era"] == "agent era")).sum()),
        "agent_era_n": int((inc["era"] == "agent era").sum()),
        "paid_or_closed": int(
            d["type"].isin(["paid", "freemium", "free_closed"]).sum()
        ),
        "self_authored_excluded": self_authored_excluded,
    }
    if save:
        by.to_csv(PROCESSED / "alt_discovery_by_product.csv", index=False)
        inc.drop(columns=["era"]).assign(era=inc["era"].astype(str)).to_csv(
            PROCESSED / "alt_discovery_included.csv", index=False
        )
    return {"by_product": by, "included": inc, "meta": meta}


def summary_numbers(out: dict) -> dict[str, str]:
    from src.collect.open_source_vs_commercial import MIN_STARS as NARROW_MIN_STARS

    m, by = (out["meta"], out["by_product"].set_index("product"))
    inc = out["included"]
    n = {
        "AltMinStars": str(MIN_STARS),
        "AltNarrowMinStars": str(NARROW_MIN_STARS),
        "AltCandidates": f"{m['candidates']:,}".replace(",", "{,}"),
        "AltIncluded": f"{m['included']:,}".replace(",", "{,}"),
        "AltIncludedAgentEra": f"{m['included_agent_era']:,}".replace(",", "{,}"),
        "AltAgentEraPct": f"{100 * m['included_agent_era'] / m['included']:.0f}",
        "AltPaidOrClosed": str(m["paid_or_closed"]),
        "AltNarrowTotal": str(int(by["narrow_total"].sum())),
        "AltAiFilesPctAgentEra": f"{100 * m['included_ai_files_agent_era'] / max(m['agent_era_n'], 1):.0f}",
        "AltAiFilesPctBefore": f"{100 * (m['included_ai_files'] - m['included_ai_files_agent_era']) / max(m['included'] - m['agent_era_n'], 1):.0f}",
    }
    for prod, key in (
        ("Screen Studio", "ScreenStudio"),
        ("QuillBot", "Quillbot"),
        ("Adobe Photoshop", "Photoshop"),
        ("Notion", "Notion"),
        ("Smallpdf", "Smallpdf"),
    ):
        if prod in by.index:
            n[f"Alt{key}Broad"] = str(int(by.loc[prod, "broad_total"]))
            n[f"Alt{key}AgentEra"] = str(int(by.loc[prod, "agent era"]))
            n[f"Alt{key}Narrow"] = str(int(by.loc[prod, "narrow_total"]))
    return n


if __name__ == "__main__":
    out = build()
    nums = summary_numbers(out)
    print(out["by_product"].to_string())
    print(out["meta"])
    print(nums)
