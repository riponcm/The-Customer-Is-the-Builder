"""Public freelance marketplace operating metrics and monthly share prices."""

from __future__ import annotations
import pandas as pd
from src.fetch import get
from src.paths import PROCESSED

RETRIEVED = "2026-10-13"
PRICE_END = pd.Timestamp("2026-09-30")
START = pd.Timestamp("2021-01-01")
SOURCES = {
    "UPWK": "https://investors.upwork.com/news-releases/news-release-details/upwork-reports-second-quarter-2026-financial-results",
    "FVRR": "https://investors.fiverr.com/news-releases/news-release-details/fiverr-announces-second-quarter-2026-results",
}
OPERATING = [
    ("UPWK", "gross_services_volume", 1002650, 966439),
    ("UPWK", "revenue", 194939, 191660),
    ("UPWK", "active_clients", 796, 763),
    ("UPWK", "adjusted_ebitda", 57061, 64053),
    ("FVRR", "marketplace_revenue", 74689, 63141),
    ("FVRR", "annual_active_buyers", 3425, 2676),
    ("FVRR", "annual_spend_per_buyer", 318, 368),
    ("FVRR", "services_revenue", 33959, 34642),
]


def collect_prices() -> pd.DataFrame:
    rows = []
    for ticker in ("UPWK", "FVRR", "SPY"):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        body = get(
            url,
            {
                "period1": int(START.tz_localize("UTC").timestamp()),
                "period2": int(
                    (PRICE_END + pd.Timedelta(days=1)).tz_localize("UTC").timestamp()
                ),
                "interval": "1mo",
                "events": "history",
            },
            namespace="freelance_platforms",
            headers={"User-Agent": "Mozilla/5.0 (academic research)"},
        )
        result = body["chart"]["result"][0]
        quote = result["indicators"]["quote"][0]
        adjusted = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
        values = adjusted if adjusted else quote["close"]
        for ts, close in zip(result["timestamp"], values):
            if close is None:
                continue
            month = (
                pd.Timestamp(ts, unit="s", tz="UTC")
                .tz_localize(None)
                .to_period("M")
                .to_timestamp()
            )
            if month <= PRICE_END:
                rows.append(
                    {"month": month, "ticker": ticker, "adjusted_close_usd": close}
                )
    prices = pd.DataFrame(rows).sort_values(["ticker", "month"])
    assert set(prices.ticker) == {"UPWK", "FVRR", "SPY"}
    assert all(prices.groupby("ticker").month.max() == pd.Timestamp("2026-09-01"))
    assert not prices.duplicated(["ticker", "month"]).any()
    return prices


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    operating = pd.DataFrame(
        OPERATING, columns=["ticker", "metric", "q2_2025", "q2_2026"]
    )
    operating["yoy_pct"] = 100 * (operating.q2_2026 / operating.q2_2025 - 1)
    operating["source_url"] = operating.ticker.map(SOURCES)
    operating["retrieved_utc"] = RETRIEVED
    prices = collect_prices()
    operating.to_csv(PROCESSED / "freelance_platforms_operating.csv", index=False)
    prices.to_csv(PROCESSED / "freelance_platforms_prices.csv", index=False)
    return (operating, prices)


if __name__ == "__main__":
    operating, prices = build()
