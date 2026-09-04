"""
Data quality checks on the processed table.

Run: python scripts/validate.py   (after scripts/transform.py)
Exits non-zero if any check fails, so it can gate the pipeline.
"""

import sys
from pathlib import Path

import pandas as pd

from indicators import ANCHOR, END_YEAR, GAP_REASONS, INDICATORS, START_YEAR

CSV_FILE = Path(__file__).resolve().parents[1] / "data" / "processed" / "indicators.csv"

# Indicators the project treats as required. The rest are known to be sparse
# and are documented as such in docs/CLEANING-NOTES.md.
REQUIRED_COLUMNS = [
    "gdp_per_capita_const",
    "life_expectancy",
    "inflation",
    "population",
]

# Plausible ranges. A value outside these means the source changed shape.
BOUNDS = {
    "gdp_per_capita_const": (500, 20_000),
    "life_expectancy": (40, 90),
    "inflation": (-10, 100),
    "population": (20e6, 200e6),
    "unemployment": (0, 40),
    "school_enrollment": (50, 130),
    "gini": (25, 60),
    "remittances": (0, 30),
    "health_expenditure": (0, 20),
    "household_consumption": (30, 100),
}


def check(results, name, passed, detail=""):
    results.append((name, passed, detail))


def validate():
    if not CSV_FILE.exists():
        raise SystemExit(f"{CSV_FILE} not found. Run scripts/transform.py first.")

    frame = pd.read_csv(CSV_FILE, index_col="year")
    results = []

    expected_years = list(range(START_YEAR, END_YEAR + 1))
    check(
        results,
        "year index is complete and gap-free",
        list(frame.index) == expected_years,
        f"{len(frame)} rows, expected {len(expected_years)}",
    )

    check(results, "no duplicate years", not frame.index.duplicated().any())

    expected_columns = {column for column, _, _ in INDICATORS.values()}
    missing = expected_columns - set(frame.columns)
    check(
        results,
        "every registered indicator has a column",
        not missing,
        f"missing: {sorted(missing)}" if missing else "",
    )

    # Types. The checklist asks for numbers as numbers; a single stray string
    # in the source would turn a whole column to object dtype and break every
    # chart downstream in a way range checks would never catch.
    check(
        results,
        "year index is an integer type",
        pd.api.types.is_integer_dtype(frame.index),
        f"got {frame.index.dtype}",
    )

    wrong_type = [
        column for column in frame.columns
        if not pd.api.types.is_float_dtype(frame[column])
    ]
    check(
        results,
        "every value column is a float type",
        not wrong_type,
        f"not float: {wrong_type}" if wrong_type else "",
    )

    # Gaps are allowed, undocumented gaps are not. This is the checklist's
    # "flagged with a reason" turned into something that actually fails.
    undocumented = [
        column for column in frame.columns
        if frame[column].isna().any() and column not in GAP_REASONS
    ]
    check(
        results,
        "every column with gaps has a documented reason",
        not undocumented,
        f"undocumented: {undocumented}" if undocumented else "",
    )

    # And the reverse: a reason for a column that no longer has gaps is stale
    # documentation, which is how the indicator count drifted before.
    stale = [
        column for column in GAP_REASONS
        if column in frame.columns and not frame[column].isna().any()
    ]
    check(
        results,
        "no stale gap reasons",
        not stale,
        f"documented but complete: {stale}" if stale else "",
    )

    for column in REQUIRED_COLUMNS:
        series = frame[column].dropna()
        check(
            results,
            f"{column} covers at least 60 years",
            len(series) >= 60,
            f"{len(series)} observed",
        )

    for column, (low, high) in BOUNDS.items():
        if column not in frame.columns:
            continue
        series = frame[column].dropna()
        outside = series[(series < low) | (series > high)]
        check(
            results,
            f"{column} within [{low:g}, {high:g}]",
            outside.empty,
            f"outliers: {outside.round(2).to_dict()}" if not outside.empty else "",
        )

    population = frame["population"].dropna()
    check(
        results,
        "population only ever increases",
        bool((population.diff().dropna() > 0).all()),
    )

    anchor = frame[ANCHOR].dropna()
    check(results, f"{ANCHOR} is never negative", bool((anchor > 0).all()))

    cpi = frame["cpi_index_2024"].dropna()
    check(
        results,
        "cpi index rises monotonically",
        bool((cpi.diff().dropna() > 0).all()),
    )
    check(
        results,
        "cpi index is 100 in its base year",
        abs(cpi.loc[2024] - 100) < 1e-6,
        f"got {cpi.loc[2024]}",
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
    sys.exit(validate())
