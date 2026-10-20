"""Module 01 - BEA private fixed investment in software, by type."""

from __future__ import annotations
import io
import json
import pandas as pd
from src.fetch import get
from src.paths import CACHE, PROCESSED, RAW

NS = "bea_software_investment"
BASE_URL = "https://apps.bea.gov/national/Release/TXT/"
RAW_DIR = RAW / NS
RAW_DIR.mkdir(parents=True, exist_ok=True)
TYPES = {
    "B985": ("software_total", 2),
    "Y003": ("prepackaged", 3),
    "Y004": ("custom", 4),
    "Y005": ("own_account", 5),
}
MEASURES = {
    "RC": "nominal_musd",
    "RX": "real_chained_musd",
    "RA": "quantity_index",
    "RG": "price_index",
}
MEASURE_TABLE = {"RC": "T50605", "RX": "T50606", "RA": "T50603", "RG": "T50604"}
CONTEXT = {
    "Y001RC": "ipp_total_nominal_musd",
    "A008RC": "nonres_fixed_investment_nominal_musd",
    "A191RC": "gdp_nominal_musd",
}
EVENTS = {"chatgpt_release": "2022-11-30", "coding_agent_era": "2025-01-01"}


def _fetch_text(name: str) -> str:
    return get(BASE_URL + name, namespace=NS, as_json=False, min_interval=2.0)


def retrieved_utc(name: str) -> str | None:
    """Retrieval timestamp recorded by src.fetch for a cached BEA file."""
    from src.fetch import _key

    p = CACHE / NS / f"{_key(BASE_URL + name, None)}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))["retrieved_utc"]
    return None


def series_register() -> pd.DataFrame:
    txt = _fetch_text("SeriesRegister.txt")
    df = pd.read_csv(io.StringIO(txt.lstrip("%")))
    return df


def series_codes() -> dict[str, tuple[str, str]]:
    """Return {series_code: (type, measure)} and verify against SeriesRegister."""
    reg = series_register().set_index("SeriesCode")
    out: dict[str, tuple[str, str]] = {}
    for stem, (typ, line) in TYPES.items():
        for suf, measure in MEASURES.items():
            code = stem + suf
            if code not in reg.index:
                raise KeyError(f"{code} missing from BEA SeriesRegister")
            tid = f"{MEASURE_TABLE[suf]}:{line}"
            if tid not in str(reg.loc[code, "TableId:LineNo"]).split("|"):
                raise ValueError(
                    f"{code} no longer maps to {tid}: {reg.loc[code, 'TableId:LineNo']}"
                )
            out[code] = (typ, measure)
    for code, measure in CONTEXT.items():
        if code not in reg.index:
            raise KeyError(f"{code} missing from BEA SeriesRegister")
        out[code] = ("context", measure)
    return out


def _load(freq: str, codes: dict[str, tuple[str, str]]) -> pd.DataFrame:
    name = {"A": "NipaDataA.txt", "Q": "NipaDataQ.txt"}[freq]
    txt = _fetch_text(name)
    keep = []
    wanted = tuple((c + "," for c in codes))
    for line in txt.splitlines():
        if line.startswith(wanted):
            keep.append(line)
    df = pd.read_csv(
        io.StringIO("SeriesCode,Period,Value\n" + "\n".join(keep)), thousands=","
    )
    df.to_csv(RAW_DIR / f"nipa_software_subset_{freq}.csv", index=False)
    df["type"] = df["SeriesCode"].map(lambda c: codes[c][0])
    df["measure"] = df["SeriesCode"].map(lambda c: codes[c][1])
    df = df.rename(
        columns={"SeriesCode": "series_code", "Period": "period", "Value": "value"}
    )
    if freq == "A":
        df["year"] = df["period"].astype(int)
        df["date"] = pd.to_datetime(df["year"].astype(str) + "-07-01")
    else:
        p = pd.PeriodIndex(df["period"].str.replace("Q", "-Q"), freq="Q")
        df["year"] = p.year
        df["quarter"] = p.quarter
        df["date"] = p.to_timestamp(how="start") + pd.Timedelta(days=45)
    return df


def _add_derived(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Shares of nominal software investment and 2015=100 rebased indexes."""
    nom = df[df["measure"] == "nominal_musd"].pivot_table(
        index=keys, columns="type", values="value"
    )
    shares = []
    for typ in ("prepackaged", "custom", "own_account"):
        if typ not in nom.columns:
            continue
        s = (nom[typ] / nom["software_total"] * 100).rename("value").reset_index()
        s["type"], s["measure"], s["series_code"] = (
            typ,
            "share_of_software_nominal_pct",
            "derived",
        )
        shares.append(s)
    ctx = df[df["type"] == "context"].pivot_table(
        index=keys, columns="measure", values="value"
    )
    for denom, label in (
        ("gdp_nominal_musd", "software_share_of_gdp_pct"),
        ("nonres_fixed_investment_nominal_musd", "software_share_of_nonres_pfi_pct"),
    ):
        s = (nom["software_total"] / ctx[denom] * 100).rename("value").reset_index()
        s["type"], s["measure"], s["series_code"] = ("software_total", label, "derived")
        shares.append(s)
    base = []
    rebased = {
        "nominal_musd": "nominal_index_2015",
        "quantity_index": "quantity_index_2015",
        "price_index": "price_index_2015",
    }
    for measure in rebased:
        sub = df[(df["measure"] == measure) & (df["type"] != "context")].copy()
        b = sub[sub["year"] == 2015].groupby("type")["value"].mean()
        sub["value"] = sub["value"] / sub["type"].map(b) * 100
        sub["measure"] = rebased[measure]
        sub["series_code"] = sub["series_code"] + ":rebased"
        base.append(sub)
    out = pd.concat([df] + shares + base, ignore_index=True)
    return out


def build(save: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    codes = series_codes()
    pd.DataFrame(
        [(c, t, m) for c, (t, m) in codes.items()],
        columns=["series_code", "type", "measure"],
    ).to_csv(RAW_DIR / "series_codes_used.csv", index=False)
    annual = _load("A", codes)
    quarterly = _load("Q", codes)
    annual = _add_derived(annual, ["year", "date"])
    quarterly = _add_derived(quarterly, ["year", "quarter", "date"])
    cols_a = ["year", "date", "type", "measure", "series_code", "value"]
    cols_q = ["year", "quarter", "date", "type", "measure", "series_code", "value"]
    annual = (
        annual[cols_a].sort_values(["measure", "type", "year"]).reset_index(drop=True)
    )
    quarterly = (
        quarterly[cols_q]
        .sort_values(["measure", "type", "year", "quarter"])
        .reset_index(drop=True)
    )
    if save:
        annual.to_csv(PROCESSED / f"{NS}_annual.csv", index=False)
        quarterly.to_csv(PROCESSED / f"{NS}_quarterly.csv", index=False)
        meta = {
            "source": BASE_URL,
            "files": ["SeriesRegister.txt", "NipaDataA.txt", "NipaDataQ.txt"],
            "retrieved_utc": {
                n: retrieved_utc(n)
                for n in ("SeriesRegister.txt", "NipaDataA.txt", "NipaDataQ.txt")
            },
        }
        (PROCESSED / f"{NS}_meta.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
    return (annual, quarterly)


def wide(df: pd.DataFrame, measure: str, index: str = "year") -> pd.DataFrame:
    """Convenience: one measure as a wide table (rows=time, cols=type)."""
    return df[df["measure"] == measure].pivot_table(
        index=index, columns="type", values="value"
    )


def summary_numbers(annual: pd.DataFrame, quarterly: pd.DataFrame) -> dict[str, str]:
    """Return summary values from the processed data."""
    sh = wide(annual, "share_of_software_nominal_pct")
    nom = wide(annual, "nominal_musd")
    qi = wide(annual, "quantity_index")
    last = int(sh.index.max())
    first = int(sh.dropna().index.min())
    n = {}
    n["BeaFirstYear"] = str(first)
    n["BeaLastYear"] = str(last)
    for typ, nm in (
        ("prepackaged", "Prepackaged"),
        ("custom", "Custom"),
        ("own_account", "OwnAccount"),
    ):
        n[f"BeaShare{nm}Last"] = f"{sh.loc[last, typ]:.1f}"
        n[f"BeaShare{nm}TwentyFifteen"] = f"{sh.loc[2015, typ]:.1f}"
        n[f"BeaShare{nm}TwentyTwentyTwo"] = f"{sh.loc[2022, typ]:.1f}"
        n[f"BeaShare{nm}First"] = f"{sh.loc[first, typ]:.1f}"
        n[f"BeaShare{nm}TwoThousand"] = f"{sh.loc[2000, typ]:.1f}"
        n[f"BeaNominal{nm}LastBn"] = f"{nom.loc[last, typ] / 1000:,.0f}"
        n[f"BeaRealGrowth{nm}SinceTwentyTwoPct"] = (
            f"{(qi.loc[last, typ] / qi.loc[2022, typ] - 1) * 100:.1f}"
        )
        cagr = ((qi.loc[2022, typ] / qi.loc[2015, typ]) ** (1 / 7) - 1) * 100
        n[f"BeaRealCagr{nm}FifteenTwentyTwoPct"] = f"{cagr:.1f}"
        cagr2 = (
            (qi.loc[last, typ] / qi.loc[2022, typ]) ** (1 / (last - 2022)) - 1
        ) * 100
        n[f"BeaRealCagr{nm}SinceTwentyTwoPct"] = f"{cagr2:.1f}"
    n["BeaNominalSoftwareLastBn"] = f"{nom.loc[last, 'software_total'] / 1000:,.0f}"
    gdp = wide(annual, "software_share_of_gdp_pct")
    n["BeaSoftwareShareGdpLast"] = f"{gdp.loc[last, 'software_total']:.2f}"
    n["BeaSoftwareShareGdpTwentyFifteen"] = f"{gdp.loc[2015, 'software_total']:.2f}"
    q = quarterly[quarterly["type"] == "software_total"]
    qn = q[q["measure"] == "nominal_musd"].sort_values(["year", "quarter"])
    lq = qn.iloc[-1]
    n["BeaLastQuarter"] = f"{int(lq['year'])}Q{int(lq['quarter'])}"
    n["BeaNominalSoftwareLastQuarterBn"] = f"{lq['value'] / 1000:,.0f}"
    qq = q[q["measure"] == "quantity_index"].set_index(["year", "quarter"])["value"]
    yoy = (qq.iloc[-1] / qq.loc[int(lq["year"]) - 1, int(lq["quarter"])] - 1) * 100
    n["BeaRealSoftwareYoyLastQuarterPct"] = f"{yoy:.1f}"
    return n


if __name__ == "__main__":
    a, q = build()
    print(a.tail(), q.tail(), sep="\n")
    print(summary_numbers(a, q))
