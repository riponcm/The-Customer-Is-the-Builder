"""Module 08 - software-developer labour-market signals."""

from __future__ import annotations
import io
import json
import pandas as pd
import requests
from src.fetch import _key, get
from src.paths import CACHE, PROCESSED, RAW

NS = "labor_market"
RAW_DIR = RAW / NS
RAW_DIR.mkdir(parents=True, exist_ok=True)
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"
BLS_API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
SOFTDEV = "IHLIDXUSTPSOFTDEVE"
TOTAL = "IHLIDXUS"
INDEED_CATEGORIES = {
    "IHLIDXUSTPSOFTDEVE": "Software development",
    "IHLIDXUSTPBAFI": "Banking and finance",
    "IHLIDXUSTPITOPHE": "IT operations and helpdesk",
    "IHLIDXUSTPACCO": "Accounting",
    "IHLIDXUSTPELECENGI": "Electrical engineering",
    "IHLIDXUSTPCONS": "Construction",
    "IHLIDXUSTPNURS": "Nursing",
    "IHLIDXUSTPMARK": "Marketing",
    "IHLIDXUSTPCIVIENGI": "Civil engineering",
    "IHLIDXUSTPSCREDE": "Scientific research and development",
    "IHLIDXUSTPINDUENGI": "Industrial engineering",
    "IHLIDXUSTPPRMA": "Production and manufacturing",
    "IHLIDXUSTPHOTO": "Hospitality and tourism",
    "IHLIDXUSTPHUMARESO": "Human resources",
    "IHLIDXUSTPMANA": "Management",
    "IHLIDXUSTPPHSU": "Physicians and surgeons",
    "IHLIDXUSTPRETA": "Retail",
    "IHLIDXUSTPSALE": "Sales",
    "IHLIDXUSTPCUSTSERV": "Customer service",
    "IHLIDXUSTPLEGA": "Legal",
    "IHLIDXUSTPPROJMANA": "Project management",
    "IHLIDXUSTPARCH": "Architecture",
    "IHLIDXUSTPMATH": "Mathematics",
    "IHLIDXUSTPDRIV": "Driving",
    "IHLIDXUSTPFOPRSE": "Food preparation and service",
    "IHLIDXUSTPLOGISUPP": "Logistic support",
    "IHLIDXUSTPVETE": "Veterinary",
    "IHLIDXUSTPDENT": "Dental",
    "IHLIDXUSTPAREN": "Arts and entertainment",
    "IHLIDXUSTPMEDIINFO": "Medical information",
    "IHLIDXUSTPINDEDO": "Information design and documentation",
    "IHLIDXUSTPSEPUSA": "Security and public safety",
    "IHLIDXUSTPTHER": "Therapy",
    "IHLIDXUSTPMECO": "Media and communications",
    "IHLIDXUSTPEDIN": "Education and instruction",
    "IHLIDXUSTPLOST": "Loading and stocking",
    "IHLIDXUSTPCLSA": "Cleaning and sanitation",
    "IHLIDXUSTPMEDITECH": "Medical technician",
    "IHLIDXUSTPPHAR": "Pharmacy",
    "IHLIDXUSTPSPOR": "Sports",
    "IHLIDXUSTPINSU": "Insurance",
    "IHLIDXUSTPBEWE": "Beauty and wellness",
    "IHLIDXUSTPCHIL": "Childcare",
    "IHLIDXUSTPADMIASSI": "Administrative assistance",
    "IHLIDXUSTPINMA": "Installation and maintenance",
    "IHLIDXUSTPCOSOSE": "Community and social service",
    "IHLIDXUSTPPECAHOHE": "Personal care and home health",
    "IHLIDXUSTPMECHENGI": "Mechanical engineering",
    "IHLIDXUSTPCHEMENGI": "Chemical engineering",
    "IHLIDXUSTPAGFO": "Agriculture and forestry",
    "IHLIDXUSTPAVIA": "Aviation",
    "IHLIDXUSTPREES": "Real estate",
}
CES_SERIES = {
    "CES5051320001": "Software publishers (NAICS 5132)",
    "CES6054151101": "Custom computer programming services (NAICS 541511)",
    "CES6054151201": "Computer systems design services (NAICS 541512)",
}
FRED_EMPLOYMENT = {"USPRIV": "Total private (CES0500000001)"}
CES_WINDOWS = [(2000, 2009), (2010, 2019), (2020, 2029)]
EVENTS = {"chatgpt_release": "2022-11-30", "coding_agent_era": "2025-01-01"}


def fred_series(series_id: str) -> pd.DataFrame | None:
    """One FRED series as (date, value); None if FRED does not serve the ID."""
    try:
        txt = get(
            FRED_CSV,
            {"id": series_id},
            namespace=NS,
            as_json=False,
            min_interval=1.0,
            retries=2,
        )
    except (requests.HTTPError, RuntimeError):
        return None
    if not txt.lstrip().startswith("observation_date"):
        return None
    df = pd.read_csv(io.StringIO(txt))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna()


def bls_series(series_id: str) -> pd.DataFrame:
    frames = []
    for start, end in CES_WINDOWS:
        params = {"startyear": str(start), "endyear": str(end)}
        url = BLS_API + series_id
        body = get(url, params, namespace=NS, min_interval=1.5)
        if body.get("status") != "REQUEST_SUCCEEDED":
            (CACHE / NS / f"{_key(url, params)}.json").unlink(missing_ok=True)
            raise RuntimeError(
                f"BLS API refused {series_id} {start}-{end}: {body.get('message')}"
            )
        for s in body["Results"]["series"]:
            for d in s["data"]:
                if not d["period"].startswith("M") or d["period"] == "M13":
                    continue
                frames.append(
                    {
                        "date": pd.Timestamp(int(d["year"]), int(d["period"][1:]), 1),
                        "value": float(d["value"]),
                        "preliminary": any(
                            (f.get("code") == "P" for f in d.get("footnotes", []) if f)
                        ),
                    }
                )
    df = pd.DataFrame(frames).drop_duplicates("date").sort_values("date")
    return df


def retrieved(url: str, params: dict | None) -> str | None:
    p = CACHE / NS / f"{_key(url, params)}.json"
    return (
        json.loads(p.read_text(encoding="utf-8"))["retrieved_utc"]
        if p.exists()
        else None
    )


def build(save: bool = True) -> dict[str, pd.DataFrame]:
    daily, missing = ([], [])
    for sid, name in {TOTAL: "Total postings", **INDEED_CATEGORIES}.items():
        df = fred_series(sid)
        if df is None:
            missing.append(sid)
            continue
        df["series_id"], df["category"] = (sid, name)
        daily.append(df)
    daily = pd.concat(daily, ignore_index=True)
    daily.to_csv(RAW_DIR / "indeed_fred_daily_all.csv", index=False)
    monthly = (
        daily.assign(month=daily["date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["series_id", "category", "month"], as_index=False)["value"]
        .mean()
    )
    last_full = daily["date"].max().to_period("M").to_timestamp()
    if daily["date"].max().day < 25:
        monthly = monthly[monthly["month"] < last_full]
    sd = daily[daily["series_id"].isin([SOFTDEV, TOTAL])].copy()
    ratio = sd.pivot_table(index="date", columns="series_id", values="value").dropna()
    ratio = (ratio[SOFTDEV] / ratio[TOTAL] * 100).rename("value").reset_index()
    ratio["series_id"], ratio["category"] = (
        "SOFTDEV_REL_TOTAL",
        "Software development relative to total (x100)",
    )
    sd = pd.concat([sd, ratio], ignore_index=True)
    ces = []
    for sid, name in CES_SERIES.items():
        df = bls_series(sid)
        df["series_id"], df["industry"] = (sid, name)
        ces.append(df)
    for sid, name in FRED_EMPLOYMENT.items():
        df = fred_series(sid)
        df = df[df["date"] >= "2000-01-01"].copy()
        df["preliminary"] = False
        df["series_id"], df["industry"] = (sid, name)
        ces.append(df)
    ces = pd.concat(ces, ignore_index=True).rename(
        columns={"value": "employment_thousands"}
    )
    ces.to_csv(RAW_DIR / "ces_employment_raw.csv", index=False)
    base = ces[ces["date"] == "2020-02-01"].set_index("series_id")[
        "employment_thousands"
    ]
    ces["index_feb2020"] = (
        ces["employment_thousands"] / ces["series_id"].map(base) * 100
    )
    out = {"indeed_daily": sd, "indeed_monthly": monthly, "ces_monthly": ces}
    if save:
        sd.to_csv(PROCESSED / f"{NS}_indeed_daily.csv", index=False)
        monthly.to_csv(PROCESSED / f"{NS}_indeed_monthly.csv", index=False)
        ces.to_csv(PROCESSED / f"{NS}_ces_monthly.csv", index=False)
        meta = {
            "indeed_source": FRED_CSV,
            "indeed_series": sorted(daily["series_id"].unique().tolist()),
            "indeed_missing_on_fred": missing,
            "indeed_retrieved_utc": retrieved(FRED_CSV, {"id": SOFTDEV}),
            "ces_source": BLS_API,
            "ces_retrieved_utc": retrieved(
                BLS_API + "CES5051320001", {"startyear": "2020", "endyear": "2029"}
            ),
            "indeed_last_date": str(daily["date"].max().date()),
            "ces_last_month": str(
                ces[ces["series_id"] == "CES5051320001"]["date"].max().date()
            ),
        }
        (PROCESSED / f"{NS}_meta.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
    return out


def category_changes(
    monthly: pd.DataFrame, start: str, end: str | None = None
) -> pd.DataFrame:
    """Percent change of each Indeed category between two months (end default: latest)."""
    w = monthly[monthly["series_id"] != TOTAL].pivot_table(
        index="month", columns="category", values="value"
    )
    end_ts = w.index.max() if end is None else pd.Timestamp(end)
    ch = (w.loc[end_ts] / w.loc[pd.Timestamp(start)] - 1) * 100
    return ch.dropna().sort_values()


def summary_numbers(out: dict[str, pd.DataFrame]) -> dict[str, str]:
    d = out["indeed_daily"].pivot_table(
        index="date", columns="series_id", values="value"
    )
    m = out["indeed_monthly"]
    ces = out["ces_monthly"]
    n: dict[str, str] = {}
    last = d.index.max()
    n["LabIndeedLastDate"] = last.strftime("%Y-%m-%d")
    n["LabSoftDevLast"] = f"{d.loc[last, SOFTDEV]:.1f}"
    n["LabTotalPostingsLast"] = f"{d.loc[last, TOTAL]:.1f}"
    pk = d[SOFTDEV].idxmax()
    n["LabSoftDevPeak"] = f"{d[SOFTDEV].max():.1f}"
    n["LabSoftDevPeakDate"] = pk.strftime("%B %Y")
    n["LabSoftDevFromPeakPct"] = (
        f"{(d.loc[last, SOFTDEV] / d[SOFTDEV].max() - 1) * 100:.1f}"
    )
    n["LabSoftDevRelTotalLast"] = f"{d.loc[last, 'SOFTDEV_REL_TOTAL']:.1f}"
    chat = pd.Timestamp(EVENTS["chatgpt_release"])
    n["LabSoftDevAtChatGpt"] = f"{d.loc[chat, SOFTDEV]:.1f}"
    n["LabTotalAtChatGpt"] = f"{d.loc[chat, TOTAL]:.1f}"
    n["LabSoftDevSinceChatGptPct"] = (
        f"{(d.loc[last, SOFTDEV] / d.loc[chat, SOFTDEV] - 1) * 100:.1f}"
    )
    n["LabTotalSinceChatGptPct"] = (
        f"{(d.loc[last, TOTAL] / d.loc[chat, TOTAL] - 1) * 100:.1f}"
    )
    j25 = pd.Timestamp("2025-01-01")
    n["LabSoftDevSinceJanTwentyFivePct"] = (
        f"{(d.loc[last, SOFTDEV] / d.loc[j25, SOFTDEV] - 1) * 100:.1f}"
    )
    n["LabTotalSinceJanTwentyFivePct"] = (
        f"{(d.loc[last, TOTAL] / d.loc[j25, TOTAL] - 1) * 100:.1f}"
    )
    pre = d.loc[chat, SOFTDEV] / d[SOFTDEV].max() - 1
    n["LabSoftDevPeakToChatGptPct"] = f"{pre * 100:.1f}"
    w = m[m["series_id"] != TOTAL].pivot_table(
        index="month", columns="category", values="value"
    )
    lm_ = w.index.max()
    lvl = w.loc[lm_].dropna().sort_values()
    n["LabIndeedLastMonth"] = lm_.strftime("%B %Y")
    n["LabNumCategories"] = str(len(lvl))
    n["LabSoftDevRankLowest"] = str(
        int(list(lvl.index).index("Software development")) + 1
    )
    ch = category_changes(m, "2022-11-01")
    n["LabSoftDevRankChangeSinceChatGpt"] = str(
        int(list(ch.index).index("Software development")) + 1
    )
    n["LabMedianCategoryChangeSinceChatGptPct"] = f"{ch.median():.1f}"
    for sid, nm in (
        ("CES5051320001", "SoftwarePublishers"),
        ("CES6054151101", "CustomProgramming"),
        ("CES6054151201", "SystemsDesign"),
        ("USPRIV", "TotalPrivate"),
    ):
        s = ces[ces["series_id"] == sid].set_index("date")["employment_thousands"]
        n[f"LabEmp{nm}Last"] = f"{s.iloc[-1]:,.1f}"
        n[f"LabEmp{nm}Peak"] = f"{s.max():,.1f}"
        n[f"LabEmp{nm}PeakDate"] = s.idxmax().strftime("%B %Y")
        n[f"LabEmp{nm}FromPeakPct"] = f"{(s.iloc[-1] / s.max() - 1) * 100:.1f}"
        n[f"LabEmp{nm}SinceFebTwentyPct"] = (
            f"{(s.iloc[-1] / s.loc['2020-02-01'] - 1) * 100:.1f}"
        )
        n[f"LabEmp{nm}SinceNovTwentyTwoPct"] = (
            f"{(s.iloc[-1] / s.loc['2022-11-01'] - 1) * 100:.1f}"
        )
    n["LabCesLastMonth"] = (
        ces[ces["series_id"] == "CES5051320001"]["date"].max().strftime("%B %Y")
    )
    return n


if __name__ == "__main__":
    o = build()
    for k, v in o.items():
        print(k, v.shape)
    print(summary_numbers(o))
