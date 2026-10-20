"""Archive and process separate app-building and organizational survey sources."""

from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
import pandas as pd
from bs4 import BeautifulSoup
from src.fetch import _key, get
from src.paths import CACHE, PROCESSED, RAW, ROOT

NS = "customer_building_evidence"
VALS_URL = "https://www.vals.ai/benchmarks/vibe-code"
SURVEY_URL = (
    "https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai"
)
MODEL_SAMPLE = (
    "Claude Sonnet 5.5",
    "Claude Haiku 5.5",
    "Claude Opus 5.5",
    "Claude Fable 5.1",
    "GPT-6 Astra",
    "GPT-6.1 Sol",
    "Gemini 4 Argon",
    "Grok 4.7",
    "DeepSeek V4.1 Flash 1017",
)


def snapshot(name: str, url: str, refresh: bool) -> tuple[str, dict]:
    folder = RAW / NS
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / f"{name}.html"
    side = folder / f"{name}.provenance.json"
    if not dest.exists() and (folder / f"{name}.txt").exists():
        dest = folder / f"{name}.txt"
    if dest.exists() and side.exists() and (not refresh):
        body = dest.read_text(encoding="utf-8")
        meta = json.loads(side.read_text(encoding="utf-8"))
        if hashlib.sha256(body.encode()).hexdigest() != meta["sha256"]:
            raise ValueError(f"Snapshot checksum changed: {dest}")
        return (body, meta)
    body = get(url, namespace=NS, as_json=False, refresh=refresh, retries=2)
    cached = json.loads(
        (CACHE / NS / f"{_key(url, None)}.json").read_text(encoding="utf-8")
    )
    meta = {
        "url": url,
        "retrieved_utc": cached["retrieved_utc"],
        "sha256": hashlib.sha256(body.encode()).hexdigest(),
    }
    dest.write_text(body, encoding="utf-8")
    side.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return (body, meta)


def match(pattern: str, text: str) -> re.Match:
    result = re.search(pattern, text, flags=re.I)
    if result is None:
        raise ValueError(f"Source format changed; cannot verify {pattern!r}")
    return result


def process_vals(body: str, provenance: dict) -> tuple[pd.DataFrame, dict]:
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text(" ", strip=True)
    updated = pd.Timestamp(
        match("Updated\\s+(\\d{1,2}/\\d{1,2}/\\d{4})", text).group(1)
    )
    version = match("Version\\s+(\\d+\\.\\d+)", text).group(1)
    threshold = int(
        match("at least\\s+(\\d+)%\\s+of the substeps succeed", text).group(1)
    )
    limit = match("up to\\s+(\\d+)\\s+hours or\\s+(\\d+)\\s+turns", text)
    rows = []
    for tr in soup.select("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.select("td, th")]
        if len(cells) < 4 or not re.fullmatch("\\d+(?:\\.\\d+)?%", cells[3]):
            continue
        rows.append(
            {
                "rank": int(cells[0]),
                "model": cells[1],
                "harness": cells[2],
                "score_pct": float(cells[3].rstrip("%")),
                "source_url": VALS_URL,
                "source_updated": updated.strftime("%Y-%m-%d"),
                "version": version,
                "retrieved_utc": provenance["retrieved_utc"],
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ValueError("No Vibe Code Bench table found; inspect archived HTML")
    selected = frame[
        frame.model.isin(MODEL_SAMPLE) & frame.harness.eq("OpenHands")
    ].copy()
    if len(selected) != len(MODEL_SAMPLE) or selected.model.duplicated().any():
        raise ValueError("Selected model coverage is incomplete or ambiguous")
    if not selected.score_pct.between(0, 100).all():
        raise ValueError("Invalid percentage")
    selected.sort_values("score_pct", ascending=False, inplace=True)
    frame.to_csv(PROCESSED / "customer_building_vcb_all.csv", index=False)
    selected.to_csv(PROCESSED / "customer_building_vcb_selected.csv", index=False)
    return (
        selected,
        {
            "source_updated": updated.strftime("%Y-%m-%d"),
            "version": version,
            "substep_pass_pct": threshold,
            "limit_hours": int(limit.group(1)),
            "limit_turns": int(limit.group(2)),
            "rows": len(frame),
            **provenance,
        },
    )


def process_survey(body: str, provenance: dict) -> dict:
    soup = BeautifulSoup(body, "html.parser")
    text = soup.get_text(" ", strip=True)
    claim = match(
        "Nearly one-third of respondents \\((\\d+) percent\\) report that their organizations have decided against purchasing at least one software product or feature because they were able to build the functionality in-house using agentic coding tools\\.",
        text,
    )
    sample = match(
        "garnered responses from ([\\d,]+) participants in (\\d+) nations", text
    )
    field = match("in the field from (\\w+ \\d+) to (\\w+ \\d+), (\\d{4})", text)
    if "weighted by the contribution of each respondent" not in text:
        raise ValueError("Survey weighting documentation not found")
    record = {
        "measure": "respondents reporting at least one foregone software product or feature purchase",
        "reported_pct": int(claim.group(1)),
        "sample_n": int(sample.group(1).replace(",", "")),
        "nations_n": int(sample.group(2)),
        "field_start": f"{field.group(1)}, {field.group(3)}",
        "field_end": f"{field.group(2)}, {field.group(3)}",
        "year": field.group(3),
        "weighting": "respondent nation contribution to global GDP",
        "claim_text": claim.group(0),
        "source_url": SURVEY_URL,
        "retrieved_utc": provenance["retrieved_utc"],
    }
    pd.DataFrame([record]).to_csv(
        PROCESSED / "customer_building_survey.csv", index=False
    )
    return record


def build(refresh: bool = False) -> None:
    vals_html, vals_prov = snapshot("vals_vibe_code", VALS_URL, refresh)
    selected, vals = process_vals(vals_html, vals_prov)
    survey_html, survey_prov = snapshot("mckinsey_state_ai", SURVEY_URL, refresh)
    survey = process_survey(survey_html, survey_prov)
    nums = {
        "BuildSurveyForegonePct": str(survey["reported_pct"]),
        "BuildSurveyN": f"{survey['sample_n']:,}",
        "BuildSurveyNations": str(survey["nations_n"]),
        "BuildSurveyFieldStart": survey["field_start"],
        "BuildSurveyFieldEnd": survey["field_end"],
        "BuildSurveyYear": survey["year"],
        "VcbSelectedN": str(len(selected)),
        "VcbVersion": vals["version"],
        "VcbSubstepPassPct": str(vals["substep_pass_pct"]),
        "VcbLimitHours": str(vals["limit_hours"]),
        "VcbLimitTurns": f"{vals['limit_turns']:,}",
        "VcbTopScore": f"{selected.iloc[0].score_pct:.2f}",
        "VcbLowSelectedScore": f"{selected.iloc[-1].score_pct:.2f}",
        "VcbSnapshotDate": pd.Timestamp(vals["source_updated"]).strftime("%B %d, %Y"),
    }
    meta = {
        "vals": vals,
        "survey": survey_prov,
        "model_sample": MODEL_SAMPLE,
        "processed_utc": datetime.now(timezone.utc).isoformat(),
    }
    (PROCESSED / "customer_building_evidence_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"VCB: {len(selected)} selected / {vals['rows']} archived rows; survey: {survey['reported_pct']}%"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    build(parser.parse_args().refresh)
