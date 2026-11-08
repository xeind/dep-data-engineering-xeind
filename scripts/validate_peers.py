"""
Data quality checks on the peer-country table.

Run: python scripts/validate_peers.py   (after scripts/transform_peers.py)
Exits non-zero if any check fails, so it can gate the pipeline.
"""

import sys
from pathlib import Path

import pandas as pd

from indicators import COUNTRY_CODE, END_YEAR, START_YEAR, column_name
from ingest_peers import PEER_COUNTRIES, PEER_INDICATORS
from transform_peers import KEY_COLUMNS

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
PEERS_FILE = PROCESSED_DIR / "peers.csv"
INDICATORS_FILE = PROCESSED_DIR / "indicators.csv"


def check(results, name, passed, detail=""):
    results.append((name, passed, detail))


def validate_peers():
    for path, script in [(PEERS_FILE, "transform_peers.py"), (INDICATORS_FILE, "transform.py")]:
        if not path.exists():
            raise SystemExit(f"{path} not found. Run scripts/{script} first.")

    frame = pd.read_csv(PEERS_FILE)
    results = []

    countries = set(frame["country_code"])
    expected_countries = set(PEER_COUNTRIES)
    check(
        results,
        "country set is exact",
        countries == expected_countries,
        f"extra: {sorted(countries - expected_countries)}, "
        f"missing: {sorted(expected_countries - countries)}"
        if countries != expected_countries else "",
    )

    check(
        results,
        "no duplicate years within a country",
        not frame.duplicated(["country_code", "year"]).any(),
    )

    expected_years = list(range(START_YEAR, END_YEAR + 1))
    incomplete = [
        country for country, group in frame.groupby("country_code")
        if sorted(group["year"]) != expected_years
    ]
    check(
        results,
        "every country covers every year",
        not incomplete,
        f"incomplete: {incomplete}" if incomplete else "",
    )

    value_columns = [c for c in frame.columns if c not in KEY_COLUMNS]
    expected_columns = [column_name(code) for code in PEER_INDICATORS] + ["gdp_index_1960"]
    check(
        results,
        "value columns match the peer registry",
        value_columns == expected_columns,
        f"got {value_columns}" if value_columns != expected_columns else "",
    )

    wrong_type = [
        column for column in value_columns
        if not pd.api.types.is_float_dtype(frame[column])
    ]
    check(
        results,
        "every value column is a float type",
        not wrong_type,
        f"not float: {wrong_type}" if wrong_type else "",
    )

    negative = {
        column: int((frame[column] < 0).sum())
        for column in value_columns
        if (frame[column] < 0).any()
    }
    check(
        results,
        "no negative values",
        not negative,
        f"negative counts: {negative}" if negative else "",
    )

    # The Philippine rows here and the main table come from separate pulls.
    # If the World Bank revised a series between them, the comparison charts
    # would disagree with the single-country charts. This catches that.
    reference = pd.read_csv(INDICATORS_FILE, index_col="year")
    home = frame[frame["country_code"] == COUNTRY_CODE].set_index("year")
    shared = [column for column in value_columns if column in reference.columns]
    mismatched = {}
    for column in shared:
        left = home[column].reindex(reference.index)
        right = reference[column]
        same = ((left - right).abs() < 1e-9) | (left.isna() & right.isna())
        if not same.all():
            mismatched[column] = [int(year) for year in reference.index[~same]]
    check(
        results,
        f"{COUNTRY_CODE} rows match indicators.csv on {len(shared)} shared columns",
        bool(shared) and not mismatched,
        f"mismatched years: {mismatched}" if mismatched else "",
    )

    failed = 0
    for name, passed, detail in results:
        mark = "PASS" if passed else "FAIL"
        suffix = f"  ({detail})" if detail else ""
        print(f"[{mark}] {name}{suffix}")
        if not passed:
            failed += 1

    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(validate_peers())
