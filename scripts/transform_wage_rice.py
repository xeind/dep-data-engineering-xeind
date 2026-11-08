"""
Build the "kilos of rice one day's minimum wage buys" series, NCR, 1990-2025.

Reads  : data/raw/psa_rice_prices.json  (PSA API snapshot)
         data/raw/ncr_wage_orders.csv   (NWPC wage orders, hand-transcribed)
Writes : data/processed/wage_rice.csv   (one row per year)

Run: python scripts/transform_wage_rice.py   (after scripts/ingest_wage_rice.py)
"""

import json
import sys
from pathlib import Path

import pandas as pd

from ingest_wage_rice import RICE_FILE, WAGE_ORDERS_FILE

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
CSV_FILE = PROCESSED_DIR / "wage_rice.csv"

START_YEAR = 1990
END_YEAR = 2025

# Rice price series per year. The old series runs to 2020 and the 2018-based
# series starts in 2018, and the two disagree in the overlap. Each year takes
# exactly one series: old up to 2017, 2018-based from 2018. The 2018-based
# series is the one PSA still maintains, and it has all 12 months in
# 2018-2020 where the old series misses October 2020.
OLD_SERIES = "PSA-RP-0042M4ARP01"
NEW_SERIES = "PSA-2018NEW-0042M4ARN01"
SPLICE_YEAR = 2018

# PXWeb marks a missing cell with dots or a dash.
MISSING_MARKERS = {"..", ".", "-", ""}


def load_rice_table(table):
    """Long frame: year, period label, price. Codes decoded via stored metadata."""
    variables = {v["code"]: v for v in table["metadata"]["variables"]}
    years = dict(zip(variables["Year"]["values"], variables["Year"]["valueTexts"]))
    periods = dict(zip(variables["Period"]["values"], variables["Period"]["valueTexts"]))

    columns = [column["code"] for column in table["response"]["columns"]]
    year_at, period_at = columns.index("Year"), columns.index("Period")

    rows = []
    for cell in table["response"]["data"]:
        raw = cell["values"][0].strip()
        rows.append({
            "year": int(years[cell["key"][year_at]]),
            "period": periods[cell["key"][period_at]],
            "price": None if raw in MISSING_MARKERS else float(raw),
        })
    return pd.DataFrame(rows).astype({"price": "float64"})


def annual_rice_prices(table):
    """PSA's published annual average, plus how many months PSA reported.

    The annual figure is PSA's own, never recomputed from the months: PSA's
    annual does not always equal the mean of the monthly cells it shows.
    """
    frame = load_rice_table(table)
    annual = frame[frame["period"] == "Annual"].set_index("year")["price"]
    monthly = frame[frame["period"] != "Annual"]
    months = monthly.groupby("year")["price"].count()
    return pd.DataFrame({"price": annual, "months_reported": months})


def spliced_rice_prices(snapshot):
    old = annual_rice_prices(snapshot["tables"][OLD_SERIES])
    new = annual_rice_prices(snapshot["tables"][NEW_SERIES])

    overlap = old["price"].dropna().index.intersection(new.index)
    print("Rice series overlap (PHP/kg, NCR RMR annual):")
    for year in overlap:
        print(f"  {year}  old {old.loc[year, 'price']:6.2f}  2018-based {new.loc[year, 'price']:6.2f}")

    old = old[old.index < SPLICE_YEAR].assign(series=OLD_SERIES)
    new = new[new.index >= SPLICE_YEAR].assign(series=NEW_SERIES)
    return pd.concat([old, new])


def daily_wage_by_year(orders):
    """Day-weighted annual average of the NCR top-of-range total wage.

    Each day carries the rate of the latest order whose effective date is on
    or before it, so a mid-year order counts only for the days it was in
    force. TOTAL includes the COLA paid on top of the basic wage.
    """
    rates = orders.set_index("effective_date")["total_wage_high"]
    days = pd.date_range(rates.index.min(), f"{END_YEAR}-12-31", freq="D")
    daily = rates.reindex(days).ffill()
    return daily.groupby(daily.index.year).mean()


def transform():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for path in (RICE_FILE, WAGE_ORDERS_FILE):
        if not path.exists():
            raise SystemExit(f"{path} not found. Run scripts/ingest_wage_rice.py first.")

    snapshot = json.loads(RICE_FILE.read_text(encoding="utf-8"))
    orders = pd.read_csv(WAGE_ORDERS_FILE, parse_dates=["effective_date"])

    rice = spliced_rice_prices(snapshot)
    wage = daily_wage_by_year(orders)

    years = range(START_YEAR, END_YEAR + 1)
    frame = pd.DataFrame(index=pd.Index(years, name="year"))
    frame["ncr_min_wage_daily"] = wage.reindex(years).round(2)
    frame["rice_regular_milled_ncr"] = rice["price"].reindex(years)
    # Computed from the rounded columns, so the ratio recomputes exactly
    # from what the CSV shows.
    frame["rice_kg_per_day_wage"] = (
        frame["ncr_min_wage_daily"] / frame["rice_regular_milled_ncr"]
    ).round(4)
    frame["rice_price_series"] = rice["series"].reindex(years)
    frame["rice_months_reported"] = rice["months_reported"].reindex(years).astype("Int64")

    frame.to_csv(CSV_FILE)

    print(f"\n{len(frame)} years x {len(frame.columns)} columns")
    print(f"  {CSV_FILE}")
    print(f"  rice series: {OLD_SERIES} {START_YEAR}-{SPLICE_YEAR - 1}, "
          f"{NEW_SERIES} {SPLICE_YEAR}-{END_YEAR}")
    kg = frame["rice_kg_per_day_wage"]
    print(f"  kg per day: {START_YEAR} {kg.loc[START_YEAR]:.2f}, {END_YEAR} {kg.loc[END_YEAR]:.2f}, "
          f"min {kg.min():.2f} ({kg.idxmin()}), max {kg.max():.2f} ({kg.idxmax()})")
    return 0


if __name__ == "__main__":
    sys.exit(transform())
