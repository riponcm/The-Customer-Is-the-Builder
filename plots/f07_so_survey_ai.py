"""Stack Overflow Developer Survey: AI-tool use 2023-2026, AI's effect on SO use, and what in-house builders build."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import pandas as pd
from src.paths import PROCESSED
from src.style import COLORS, SERIES, WIDTH_TALL, apply, save, source_note

NAME = "f07_so_survey_ai"


def usage_by_year(s: pd.DataFrame) -> pd.DataFrame:
    """Share currently using AI tools: 'Yes' (2023-24), sum of 'Yes, ...' (2025), 100 - non-users (2026)."""
    a = s[s["item"] == "AISelect"]
    rows = []
    for y, d in a.groupby("year"):
        use = d[d["response"].str.startswith("Yes")]["pct"].sum()
        plan = d[d["response"].str.startswith("No, but")]["pct"].sum()
        rows.append({"year": y, "using": use, "planning": plan})
    b = s[(s["item"] == "AIUse2026") & (s["response"] == "I don't use AI tools")]
    if not b.empty:
        rows.append(
            {"year": 2026, "using": 100 - b["pct"].iloc[0], "planning": float("nan")}
        )
    return pd.DataFrame(rows)


def _hbar(ax, d: pd.DataFrame, color: str, highlight: str | None = None) -> None:
    d = d.sort_values("pct")
    colors = [
        SERIES[1] if highlight and r == highlight else color for r in d["response"]
    ]
    ax.barh(d["label"], d["pct"], color=colors, height=0.62)
    for y, v in enumerate(d["pct"]):
        ax.text(
            v + 1.2, y, f"{v:.1f}%", va="center", fontsize=7.5, color=COLORS["ink2"]
        )
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.tick_params(axis="y", length=0, labelsize=7.5)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100%"])


SHORT = {
    "Visit less for simple questions": "Visit less for simple questions",
    "Ask fewer questions": "Ask fewer questions",
    "Contribute less": "Contribute less",
    "No change": "No change",
    "Visit more for verification (for example, source attribution)": "Visit more to verify AI output",
    "Other": "Other",
    "Ask more advanced questions": "Ask more advanced questions",
    "Visit SO more because AI-generated answers lead you there": "Visit more, led by AI answers",
    "Contribute more": "Contribute more",
}


def make_figure() -> plt.Figure:
    apply()
    s = pd.read_csv(PROCESSED / "stackoverflow_survey_ai.csv")
    fig = plt.figure(figsize=WIDTH_TALL)
    gs = fig.add_gridspec(
        2, 2, width_ratios=[0.8, 1.2], height_ratios=[1, 1.15], hspace=0.55, wspace=0.75
    )
    ax = fig.add_subplot(gs[0, 0])
    u = usage_by_year(s)
    colors = [SERIES[0] if y < 2026 else COLORS["context"] for y in u["year"]]
    ax.bar(u["year"].astype(str), u["using"], color=colors, width=0.62)
    for i, v in enumerate(u["using"]):
        ax.text(i, v + 2, f"{v:.1f}%", ha="center", fontsize=7.5, color=COLORS["ink2"])
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0", "25", "50", "75", "100%"])
    ax.set_title("A. Respondents using AI tools", fontsize=9)
    ax.text(3, 6, "new\nquestion*", ha="center", fontsize=6.5, color=COLORS["ink"])
    ax = fig.add_subplot(gs[0, 1])
    b = s[s["item"] == "BuildTool"].copy()
    b["label"] = b["response"]
    _hbar(ax, b, SERIES[0], highlight="Replacing paid vendors")
    n = int(b["n"].iloc[0])
    ax.set_title(f"B. Building in-house software, 2026 (n = {n:,})", fontsize=9)
    ax = fig.add_subplot(gs[1, :])
    c = s[s["item"] == "SOChange"].copy()
    c["label"] = c["response"].map(SHORT).fillna(c["response"])
    _hbar(ax, c, SERIES[0])
    n = int(c["n"].iloc[0])
    ax.set_title(
        f'C. "How has AI changed your Stack Overflow usage?" 2026 (n = {n:,}, select all)',
        fontsize=9,
    )
    retrieved = s["retrieved"].iloc[0] if "retrieved" in s else ""
    source_note(
        fig,
        f"Source: Stack Overflow Developer Survey 2023-2026 result pages (survey.stackoverflow.co), All Respondents; opt-in samples. *2023-25: 'Do you currently use AI tools in your development process?'\n(2025 sums the three 'Yes' options); 2026: 100% minus 'I don't use AI tools' in a multi-select about AI tools at work. Retrieved {retrieved}.",
    )
    fig.subplots_adjust(left=0.2, right=0.97, top=0.93, bottom=0.12)
    return fig


def main() -> None:
    save(make_figure(), NAME)


if __name__ == "__main__":
    main()
