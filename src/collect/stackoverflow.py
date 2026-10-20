"""Module 07 -- Stack Overflow question volume (Stack Exchange API v2.3)."""

from __future__ import annotations
import time
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
from src.fetch import get
from src.paths import PROCESSED

API = "https://api.stackexchange.com/2.3/questions"
NS = "stackoverflow"
FILTER = "!9n30I5fDgPX4"
START = "2009-01"
TAGS = ["python", "javascript", "reactjs", "pandas", "rust"]
TAG_YEARS = list(range(2016, 2027))
QUOTA_RESERVE = 3
CHATGPT = pd.Timestamp("2022-11-30")
BREAK_MONTH = "2022-12"


class QuotaExhausted(RuntimeError):
    pass


_state = {"quota_remaining": None}


def last_full_month(today: datetime | None = None) -> pd.Period:
    today = today or datetime.now(timezone.utc)
    return pd.Period(today.strftime("%Y-%m"), "M") - 1


def _ts(t: pd.Timestamp) -> int:
    return int(t.tz_localize("UTC").timestamp())


def total(fromdate: int, todate: int, tagged: str | None = None) -> int:
    """Questions created in [fromdate, todate] (both inclusive, UTC seconds)."""
    q = _state["quota_remaining"]
    if q is not None and q <= QUOTA_RESERVE:
        raise QuotaExhausted(f"quota_remaining={q}")
    params = {
        "site": "stackoverflow",
        "fromdate": fromdate,
        "todate": todate,
        "filter": FILTER,
    }
    if tagged:
        params["tagged"] = tagged
    try:
        body = get(API, params, namespace=NS, min_interval=0.6)
    except requests.HTTPError as err:
        raise QuotaExhausted(str(err)) from err
    if "quota_remaining" in body:
        _state["quota_remaining"] = body["quota_remaining"]
    if body.get("backoff"):
        time.sleep(int(body["backoff"]) + 1)
    if "total" not in body:
        raise RuntimeError(f"unexpected response {body}")
    return int(body["total"])


def collect_monthly(end: pd.Period | None = None) -> pd.DataFrame:
    end = end or last_full_month()
    rows = []
    for p in pd.period_range(START, end, freq="M"):
        s = _ts(p.start_time)
        e = _ts((p + 1).start_time) - 1
        try:
            rows.append({"month": str(p), "questions": total(s, e)})
        except QuotaExhausted as err:
            print(f"stopped at {p}: {err}")
            break
    return pd.DataFrame(rows)


def collect_tags(end: pd.Period | None = None, tags: list[str] = TAGS) -> pd.DataFrame:
    """Per-tag questions asked from 1 January to the end of month `end.month`, each year."""
    end = end or last_full_month()
    last_m = end.month
    rows = []
    for tag in tags:
        for y in TAG_YEARS:
            if y > end.year:
                continue
            s = _ts(pd.Timestamp(f"{y}-01-01"))
            e = _ts((pd.Period(f"{y}-{last_m:02d}", "M") + 1).start_time) - 1
            try:
                n = total(s, e, tagged=tag)
            except QuotaExhausted as err:
                print(f"stopped at {tag} {y}: {err}")
                return pd.DataFrame(rows)
            rows.append(
                {
                    "tag": tag,
                    "year": y,
                    "window": f"Jan-{pd.Timestamp(2000, last_m, 1):%b}",
                    "questions": n,
                }
            )
    return pd.DataFrame(rows)


def its(
    monthly: pd.DataFrame,
    start: str = "2017-01",
    end: str | None = None,
    break_month: str = BREAK_MONTH,
    seasonal: bool = True,
    hac_lags: int = 12,
    drop: tuple[str, str] | None = None,
):
    """Segmented regression of log monthly questions with level + slope change."""
    df = monthly.copy()
    df["month"] = pd.PeriodIndex(df["month"], freq="M")
    df = df[df["month"] >= pd.Period(start, "M")]
    if end:
        df = df[df["month"] <= pd.Period(end, "M")]
    if drop:
        df = df[
            (df["month"] < pd.Period(drop[0], "M"))
            | (df["month"] > pd.Period(drop[1], "M"))
        ]
    t0 = pd.Period(break_month, "M")
    df["t"] = [(m - pd.Period(start, "M")).n for m in df["month"]]
    tb = (t0 - pd.Period(start, "M")).n
    df["post"] = (df["month"] >= t0).astype(int)
    df["t_post"] = (df["t"] - tb).clip(lower=0) * df["post"]
    X = df[["t", "post", "t_post"]].astype(float)
    if seasonal:
        moy = pd.get_dummies(df["month"].dt.month, prefix="m", drop_first=True).astype(
            float
        )
        X = pd.concat([X, moy], axis=1)
    X = sm.add_constant(X)
    y = np.log(df["questions"].astype(float))
    res = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})
    df["fitted"] = np.exp(res.fittedvalues)
    Xcf = X.copy()
    Xcf["post"] = 0.0
    Xcf["t_post"] = 0.0
    df["counterfactual"] = np.exp(res.predict(Xcf))
    return (res, df)


SURVEY_NS = "stackoverflow_survey"
SURVEY_HTML = [
    (
        2023,
        "https://survey.stackoverflow.co/2023/",
        "AI tools in the development process 70% of all respondents",
        ["Yes", "No, but I plan to soon", "No, and I don't plan to"],
        "Do you currently use AI tools in your development process?",
    ),
    (
        2024,
        "https://survey.stackoverflow.co/2024/ai",
        "Do you currently use AI tools in your development process?",
        ["Yes", "No, but I plan to soon", "No, and I don't plan to"],
        "Do you currently use AI tools in your development process?",
    ),
]
SURVEY_2025 = "https://survey.stackoverflow.co/2025/ai"
SURVEY_2026_JSON = {
    "BuildTool": "https://survey.stackoverflow.co/2026/technology/data/build-tool",
    "SOChange": "https://survey.stackoverflow.co/2026/community/data/so-change",
}
SURVEY_2026_AI = "https://survey.stackoverflow.co/2026/ai/data"


def _page_text(url: str) -> str:
    import html as _html
    import re as _re

    t = get(url, namespace=SURVEY_NS, as_json=False, min_interval=2.0)
    t = _re.sub("<script.*?</script>|<style.*?</style>", " ", t, flags=_re.S)
    t = _re.sub("<[^>]+>", " ", t)
    return _re.sub("\\s+", " ", _html.unescape(t)).replace("’", "'")


def _pct_after(text: str, label: str, start: int) -> float:
    import re as _re

    m = _re.compile(_re.escape(label) + "\\s+(\\d{1,3}(?:\\.\\d+)?)%").search(
        text, start
    )
    if not m:
        raise ValueError(f"{label!r} not found after {start}")
    return float(m.group(1))


def collect_survey() -> pd.DataFrame:
    """AI-use figures exactly as printed on the survey result pages (All Respondents tab)."""
    import json as _json
    import re as _re

    rows = []
    for year, url, anchor, labels, question in SURVEY_HTML:
        text = _page_text(url)
        i = text.find(anchor)
        m_n = _re.compile("([\\d,]+) responses Yes ").search(text, i) or _re.compile(
            "Responses: ([\\d,]+) \\("
        ).search(text, i)
        n = (
            int(m_n.group(1).replace(",", ""))
            if m_n and m_n.start() - i < 2000
            else None
        )
        for lab in labels:
            rows.append(
                {
                    "year": year,
                    "item": "AISelect",
                    "question": question,
                    "response": lab,
                    "demographic": "All respondents",
                    "pct": _pct_after(text, lab, i),
                    "n": n,
                    "url": url,
                }
            )
    raw = get(SURVEY_2025, namespace=SURVEY_NS, as_json=False, min_interval=2.0)
    j = raw.find("AISelect:{qid:")
    blk = raw[j : j + 3000]
    n = int(_re.search("total_respondents:(\\d+)", blk).group(1))
    for resp, pct in _re.findall(
        'response:"([^"]+)",frequency:\\d+,percent:([\\d.]+)', blk.split("]")[0]
    ):
        rows.append(
            {
                "year": 2025,
                "item": "AISelect",
                "question": "Do you currently use AI tools in your development process?",
                "response": resp.replace("\\u2019", "'"),
                "demographic": "All respondents",
                "pct": round(100 * float(pct), 2),
                "n": n,
                "url": SURVEY_2025,
            }
        )
    text = _page_text(SURVEY_2026_AI)
    anchor = "Do you currently use AI tools or AI agents in your role at work?"
    i = text.find(anchor)
    n = int(
        _re.search("All Respondents · n = ([\\d,]+)", text[i:])
        .group(1)
        .replace(",", "")
    )
    k = text.find("Respondents Percent", i)
    for lab in [
        "AI coding assistants or coding agents",
        "General-purpose AI chat tools",
        "AI agents or automated workflows",
        "Internal AI tools built by my company",
        "I don't use AI tools",
    ]:
        m = _re.search(_re.escape(lab) + " [\\d,]+ (\\d+(?:\\.\\d+)?)%", text[k:])
        rows.append(
            {
                "year": 2026,
                "item": "AIUse2026",
                "question": anchor,
                "response": lab,
                "demographic": "All respondents",
                "pct": float(m.group(1)),
                "n": n,
                "url": SURVEY_2026_AI,
            }
        )
    for item, url in SURVEY_2026_JSON.items():
        text = _page_text(url)
        k = text.find('{ "question"')
        obj, _ = _json.JSONDecoder().raw_decode(text[k:])
        for d in obj["data"]:
            rows.append(
                {
                    "year": 2026,
                    "item": obj["dataId"],
                    "question": obj["asked"],
                    "response": d["response"],
                    "demographic": obj["demographic"]["name"],
                    "pct": round(100 * d["pct"], 2),
                    "n": obj["demographic"]["n"],
                    "url": url,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(PROCESSED / "stackoverflow_survey_ai.csv", index=False)
    return df


ITS_SPECS = [
    ("Main: 2017-01 to latest, break 2022-12", {}),
    ("Longer pre-period: from 2015-01", {"start": "2015-01"}),
    ("Excluding COVID months 2020-03 to 2021-06", {"drop": ("2020-03", "2021-06")}),
    ("No month-of-year effects", {"seasonal": False}),
    (
        "Placebo: break 2021-06, data to 2022-10",
        {"end": "2022-10", "break_month": "2021-06"},
    ),
]


def its_table(monthly: pd.DataFrame) -> pd.DataFrame:
    """Coefficients of each ITS spec, transformed to percentages."""
    rows = []
    for label, kw in ITS_SPECS:
        res, d = its(monthly, **kw)
        ci = res.conf_int()
        pct = lambda b: 100 * (np.exp(b) - 1)
        rows.append(
            {
                "spec": label,
                "pre_trend_pct_month": pct(res.params["t"]),
                "pre_trend_se": 100 * res.bse["t"],
                "pre_trend_p": res.pvalues["t"],
                "level_change_pct": pct(res.params["post"]),
                "level_change_se": 100 * res.bse["post"],
                "level_change_p": res.pvalues["post"],
                "slope_change_pct_month": pct(res.params["t_post"]),
                "slope_change_se": 100 * res.bse["t_post"],
                "slope_change_p": res.pvalues["t_post"],
                "slope_change_lo": pct(ci.loc["t_post", 0]),
                "slope_change_hi": pct(ci.loc["t_post", 1]),
                "gap_last_pct": 100
                * (d["questions"].iloc[-1] / d["counterfactual"].iloc[-1] - 1),
                "last_month": str(d["month"].iloc[-1]),
                "n_months": int(res.nobs),
                "r2": res.rsquared,
            }
        )
    return pd.DataFrame(rows)


def _stars(p: float) -> str:
    return "^{***}" if p < 0.01 else "^{**}" if p < 0.05 else "^{*}" if p < 0.1 else ""


def retrieval_date(namespace: str = NS) -> str:
    """Latest retrieval date (UTC) recorded in the HTTP cache for a namespace."""
    import json as _json
    from src.paths import CACHE

    dates = [
        _json.loads(p.read_text(encoding="utf-8"))["retrieved_utc"][:10]
        for p in (CACHE / namespace).glob("*.json")
    ]
    return max(dates) if dates else ""


def build(end: pd.Period | None = None) -> dict[str, pd.DataFrame]:
    end = end or last_full_month()
    monthly = collect_monthly(end)
    monthly["retrieved"] = retrieval_date()
    monthly.to_csv(PROCESSED / "stackoverflow_monthly.csv", index=False)
    tags = collect_tags(end)
    mm = monthly.assign(p=pd.PeriodIndex(monthly["month"], freq="M"))
    mm = mm[mm["p"].dt.month <= end.month]
    allq = (
        mm.groupby(mm["p"].dt.year)["questions"]
        .sum()
        .loc[TAG_YEARS[0] :]
        .rename_axis("year")
        .reset_index()
        .assign(tag="(all questions)")
    )
    allq["window"] = tags["window"].iloc[0] if not tags.empty else ""
    tags = pd.concat(
        [tags, allq[["tag", "year", "window", "questions"]]], ignore_index=True
    )
    base = tags[tags["year"] == 2022].set_index("tag")["questions"]
    tags["index_2022"] = 100 * tags["questions"] / tags["tag"].map(base)
    tags["retrieved"] = monthly["retrieved"].iloc[0]
    tags.to_csv(PROCESSED / "stackoverflow_tags_ytd.csv", index=False)
    print("quota_remaining:", _state["quota_remaining"])
    survey = collect_survey()
    survey["retrieved"] = retrieval_date(SURVEY_NS)
    survey.to_csv(PROCESSED / "stackoverflow_survey_ai.csv", index=False)
    tab = its_table(monthly)
    tab.to_csv(PROCESSED / "stackoverflow_its.csv", index=False)
    _, fit = its(monthly)
    fit = fit[["month", "questions", "fitted", "counterfactual", "post"]].assign(
        month=lambda d: d["month"].astype(str)
    )
    fit.to_csv(PROCESSED / "stackoverflow_its_fit.csv", index=False)
    return {
        "monthly": monthly,
        "tags": tags,
        "survey": survey,
        "its": tab,
        "its_fit": fit,
    }


def load() -> dict[str, pd.DataFrame]:
    out = {
        "monthly": pd.read_csv(PROCESSED / "stackoverflow_monthly.csv"),
        "tags": pd.read_csv(PROCESSED / "stackoverflow_tags_ytd.csv"),
    }
    for k in ("survey_ai", "its", "its_fit"):
        out[k] = pd.read_csv(PROCESSED / f"stackoverflow_{k}.csv")
    return out


if __name__ == "__main__":
    out = build()
    print(out["monthly"].tail(), out["tags"].tail())


def key_numbers(out: dict[str, pd.DataFrame]) -> dict[str, str]:
    m = out["monthly"].copy()
    m["p"] = pd.PeriodIndex(m["month"], freq="M")
    tags, survey, tab = (out["tags"], out["survey_ai"], out["its"].set_index("spec"))
    main = tab.iloc[0]
    plac = tab.loc[[s for s in tab.index if s.startswith("Placebo")][0]]
    base = m[
        (m["p"] >= pd.Period("2022-01", "M")) & (m["p"] <= pd.Period("2022-10", "M"))
    ]["questions"].mean()
    last3 = m.tail(3)["questions"].mean()
    peak = m.loc[m["questions"].idxmax()]
    last = m.iloc[-1]
    idx = tags.pivot(index="year", columns="tag", values="index_2022")
    last_year = int(idx.index.max())
    window = tags["window"].dropna().iloc[0]

    def sv(item, resp, year=None):
        d = survey[(survey["item"] == item) & (survey["response"] == resp)]
        if year is not None:
            d = d[d["year"] == year]
        return float(d["pct"].iloc[0])

    use25 = survey[(survey["year"] == 2025) & survey["response"].str.startswith("Yes")][
        "pct"
    ].sum()
    f0, f1 = (lambda v: f"{v:,.0f}", lambda v: f"{v:.1f}")
    nums = {
        "SoFirstMonth": str(m["month"].iloc[0]),
        "SoLastMonth": str(last["month"]),
        "SoLastMonthQuestions": f0(last["questions"]),
        "SoPeakQuestions": f0(peak["questions"]),
        "SoPeakMonth": str(peak["month"]),
        "SoBaselineTwentyTwoMonthly": f0(base),
        "SoLastThreeMonthsMean": f0(last3),
        "SoDeclineVsBaselinePct": f1(100 * (1 - last3 / base)),
        "SoDeclineFromPeakPct": f1(100 * (1 - last["questions"] / peak["questions"])),
        "SoWindow": window,
        "SoYtdIndexLastYear": f1(idx.loc[last_year, "(all questions)"]),
        "SoYtdDeclineVsTwentyTwoPct": f1(100 - idx.loc[last_year, "(all questions)"]),
        "SoPreChatGPTDeclinePct": f1(
            100 * (1 - 100 / idx.loc[2017, "(all questions)"])
        ),
        "SoIdxPython": f1(idx.loc[last_year, "python"]),
        "SoIdxJavascript": f1(idx.loc[last_year, "javascript"]),
        "SoIdxReactjs": f1(idx.loc[last_year, "reactjs"]),
        "SoIdxPandas": f1(idx.loc[last_year, "pandas"]),
        "SoIdxRust": f1(idx.loc[last_year, "rust"]),
        "SoItsPreTrendPctMonth": f"{main['pre_trend_pct_month']:.2f}",
        "SoItsPreTrendPctYear": f1(
            100 * ((1 + main["pre_trend_pct_month"] / 100) ** 12 - 1)
        ),
        "SoItsLevelPct": f1(main["level_change_pct"]),
        "SoItsLevelP": f"{main['level_change_p']:.2f}",
        "SoItsSlopePctMonth": f"{main['slope_change_pct_month']:.2f}",
        "SoItsSlopeLo": f"{main['slope_change_lo']:.2f}",
        "SoItsSlopeHi": f"{main['slope_change_hi']:.2f}",
        "SoItsGapPct": f1(main["gap_last_pct"]),
        "SoItsMonths": str(int(main["n_months"])),
        "SoPlaceboSlopePctMonth": f"{plac['slope_change_pct_month']:.2f}",
        "SoPlaceboSlopeP": f"{plac['slope_change_p']:.3f}",
        "SoPlaceboLevelPct": f1(plac["level_change_pct"]),
        "SoSurveyUseTwentyThree": f1(sv("AISelect", "Yes", 2023)),
        "SoSurveyUseTwentyFour": f1(sv("AISelect", "Yes", 2024)),
        "SoSurveyUseTwentyFive": f1(use25),
        "SoSurveyDailyTwentyFive": f1(
            sv("AISelect", "Yes, I use AI tools daily", 2025)
        ),
        "SoSurveyUseTwentySix": f1(100 - sv("AIUse2026", "I don't use AI tools")),
        "SoSurveyCodingAgentsTwentySix": f1(
            sv("AIUse2026", "AI coding assistants or coding agents")
        ),
        "SoSurveyReplacingVendors": f1(sv("BuildTool", "Replacing paid vendors")),
        "SoSurveyInternalTools": f1(sv("BuildTool", "Team-level internal tools")),
        "SoSurveySmallScripts": f1(sv("BuildTool", "Small scripts/automations")),
        "SoSurveyBuildN": f0(survey[survey["item"] == "BuildTool"]["n"].iloc[0]),
        "SoSurveyVisitLess": f1(sv("SOChange", "Visit less for simple questions")),
        "SoSurveyAskFewer": f1(sv("SOChange", "Ask fewer questions")),
        "SoSurveyNoChange": f1(sv("SOChange", "No change")),
        "SoSurveyChangeN": f0(survey[survey["item"] == "SOChange"]["n"].iloc[0]),
    }
    return nums
