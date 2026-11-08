"""
Turn the raw peer-country snapshot into one tidy comparison table.

Reads  : data/raw/world_bank_peers.json
Writes : data/processed/peers.csv   (long by country, one row per country-year)

Run: python scripts/transform_peers.py   (after scripts/ingest_peers.py)
"""

import json
import sys
from pathlib import Path

import pandas as pd

from indicators import ANCHOR, END_YEAR, START_YEAR, column_name
from ingest_peers import PEER_COUNTRIES, PEER_INDICATORS

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "world_bank_peers.json"
PROCESSED_DIR = ROOT / "data" / "processed"
CSV_FILE = PROCESSED_DIR / "peers.csv"

KEY_COLUMNS = ["country_code", "country", "year"]


def load_snapshot():
    if not RAW_FILE.exists():
        raise SystemExit(f"{RAW_FILE} not found. Run scripts/ingest_peers.py first.")
    return json.loads(RAW_FILE.read_text(encoding="utf-8"))


def to_long(snapshot):
    """One row per country per year, one column per indicator.

    Every country gets the full 1960-2025 index, so a year the source never
    measured is an empty cell rather than a missing row.
    """
    index = pd.MultiIndex.from_product(
        [list(PEER_COUNTRIES), range(START_YEAR, END_YEAR + 1)],
        names=["country_code", "year"],
    )
    frame = pd.DataFrame(index=index)

    for code, payload in snapshot["indicators"].items():
        series = {
            (row["country"]["id"], int(row["date"])): row["value"]
            for row in payload["rows"]
            if row.get("value") is not None
        }
        frame[payload["column"]] = pd.Series(series, dtype="float64")

    # Keep column order stable and matching the registry, not the JSON.
    return frame[[column_name(code) for code in PEER_INDICATORS]]


def add_derived(frame):
    """Anchor indexed to each country's own 1960 value.

    A country with no 1960 observation gets an empty index rather than one
    rebased to some later year, so every value in the column means the same
    thing.
    """
    anchor = frame[ANCHOR]
    base = anchor.xs(START_YEAR, level="year")
    frame["gdp_index_1960"] = anchor / base.reindex(anchor.index, level="country_code") * 100
    return frame


def transform_peers():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    frame = add_derived(to_long(load_snapshot()))

    frame = frame.reset_index()
    frame.insert(1, "country", frame["country_code"].map(PEER_COUNTRIES))
    frame = frame[KEY_COLUMNS + [c for c in frame.columns if c not in KEY_COLUMNS]]

    frame.round(4).to_csv(CSV_FILE, index=False)

    value_columns = [c for c in frame.columns if c not in KEY_COLUMNS]
    print(f"{len(frame)} rows ({len(PEER_COUNTRIES)} countries x "
          f"{END_YEAR - START_YEAR + 1} years) x {len(value_columns)} value columns")
    print(f"  {CSV_FILE}")
    print("\nCoverage:")
    for country, group in frame.groupby("country_code", sort=False):
        print(f"  {country}")
        for column in value_columns:
            observed = group[column].notna()
            years = group.loc[observed, "year"]
            span = f"{years.min()}-{years.max()}" if len(years) else "empty"
            print(f"    {column:24s} {observed.sum():3d}/{len(group)}  {span}")

    return 0


if __name__ == "__main__":
    sys.exit(transform_peers())
