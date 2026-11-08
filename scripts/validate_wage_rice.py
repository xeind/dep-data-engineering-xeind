"""
Data quality checks on the wage-rice table and the wage orders behind it.

Run: python scripts/validate_wage_rice.py   (after scripts/transform_wage_rice.py)
Exits non-zero if any check fails, so it can gate the pipeline.
"""

import sys

import pandas as pd

from ingest_wage_rice import WAGE_ORDERS_FILE
from transform_wage_rice import (
    CSV_FILE,
    END_YEAR,
    NEW_SERIES,
    OLD_SERIES,
    SPLICE_YEAR,
    START_YEAR,
)
from validate import check

VALUE_COLUMNS = [
    "ncr_min_wage_daily",
    "rice_regular_milled_ncr",
    "rice_kg_per_day_wage",
]

# Plausible ranges. A value outside these means a source changed shape or a
# transcription slipped a digit.
BOUNDS = {
    "ncr_min_wage_daily": (80, 1_000),
    "rice_regular_milled_ncr": (5, 100),
    "rice_kg_per_day_wage": (5, 30),
}

# PSA reported 10 of 12 months in 2015 and 2016. Fewer than that and the
# published annual average rests on too little to trust.
MIN_MONTHS_REPORTED = 10


def check_wage_orders(results):
    orders = pd.read_csv(WAGE_ORDERS_FILE, parse_dates=["effective_date"])

    check(
        results,
        "wage orders: effective dates strictly increase",
        orders["effective_date"].is_monotonic_increasing
        and not orders["effective_date"].duplicated().any(),
    )

    # The top of the range is what the series uses. The bottom of WO NCR-12 is
    # misprinted in the source and is not checked.
    summed = (orders["basic_wage_high"] + orders["allowance"]).round(2)
    wrong = orders.loc[summed != orders["total_wage_high"], "order_id"].tolist()
    check(
        results,
        "wage orders: total top equals basic top plus allowance",
        not wrong,
        f"mismatched: {wrong}" if wrong else "",
    )

    falls = orders.loc[orders["total_wage_high"].diff() < 0, "order_id"].tolist()
    check(
        results,
        "wage orders: total top never falls from one order to the next",
        not falls,
        f"falls at: {falls}" if falls else "",
    )

    check(
        results,
        "wage orders: every row cites a source URL, page and hash",
        bool(orders[["source_url", "source_page", "source_sha256"]].notna().all().all()),
    )

    return orders.set_index("effective_date")["total_wage_high"]


def validate():
    if not CSV_FILE.exists():
        raise SystemExit(f"{CSV_FILE} not found. Run scripts/transform_wage_rice.py first.")

    frame = pd.read_csv(CSV_FILE, index_col="year")
    results = []

    rates = check_wage_orders(results)

    expected_years = list(range(START_YEAR, END_YEAR + 1))
    check(
        results,
        "year index is complete and gap-free",
        list(frame.index) == expected_years,
        f"{len(frame)} rows, expected {len(expected_years)}",
    )
    check(results, "no duplicate years", not frame.index.duplicated().any())
    check(
        results,
        "year index is an integer type",
        pd.api.types.is_integer_dtype(frame.index),
        f"got {frame.index.dtype}",
    )

    wrong_type = [
        column for column in VALUE_COLUMNS
        if not pd.api.types.is_float_dtype(frame[column])
    ]
    check(
        results,
        "every value column is a float type",
        not wrong_type,
        f"not float: {wrong_type}" if wrong_type else "",
    )

    # Nothing is imputed, and the series needs every year to answer the
    # question, so a gap here is a failure rather than a documented absence.
    empty = {
        column: [int(year) for year in frame.index[frame[column].isna()]]
        for column in frame.columns
        if frame[column].isna().any()
    }
    check(results, "no missing values", not empty, f"missing: {empty}" if empty else "")

    not_positive = [column for column in VALUE_COLUMNS if not (frame[column] > 0).all()]
    check(
        results,
        "every value is positive",
        not not_positive,
        f"not positive: {not_positive}" if not_positive else "",
    )

    for column, (low, high) in BOUNDS.items():
        series = frame[column].dropna()
        outside = series[(series < low) | (series > high)]
        check(
            results,
            f"{column} within [{low:g}, {high:g}]",
            outside.empty,
            f"outliers: {outside.to_dict()}" if not outside.empty else "",
        )

    recomputed = (frame["ncr_min_wage_daily"] / frame["rice_regular_milled_ncr"]).round(4)
    off = frame.index[(recomputed - frame["rice_kg_per_day_wage"]).abs() > 1e-9].tolist()
    check(
        results,
        "kg per day recomputes exactly from wage / price",
        not off,
        f"years off: {off}" if off else "",
    )

    wage = frame["ncr_min_wage_daily"]
    decreases = wage.index[wage.diff() < 0].tolist()
    check(
        results,
        "annual wage never decreases year to year",
        not decreases,
        f"decreases in: {decreases}" if decreases else "",
    )

    # An annual average must sit between the rate in force on 1 January and
    # the rate in force on 31 December, since rates only ever step up.
    outside_year = []
    for year, value in wage.items():
        first = rates.asof(pd.Timestamp(f"{year}-01-01"))
        last = rates.asof(pd.Timestamp(f"{year}-12-31"))
        if not first - 0.005 <= value <= last + 0.005:
            outside_year.append(year)
    check(
        results,
        "annual wage lies between the 1 Jan and 31 Dec rates in force",
        not outside_year,
        f"outside in: {outside_year}" if outside_year else "",
    )

    expected_series = pd.Series(
        [OLD_SERIES if year < SPLICE_YEAR else NEW_SERIES for year in frame.index],
        index=frame.index,
    )
    wrong_series = frame.index[frame["rice_price_series"] != expected_series].tolist()
    check(
        results,
        f"rice series is {OLD_SERIES} before {SPLICE_YEAR}, {NEW_SERIES} from {SPLICE_YEAR}",
        not wrong_series,
        f"wrong series in: {wrong_series}" if wrong_series else "",
    )

    thin = frame.index[frame["rice_months_reported"] < MIN_MONTHS_REPORTED].tolist()
    check(
        results,
        f"every annual rice price rests on at least {MIN_MONTHS_REPORTED} monthly reports",
        not thin,
        f"thin years: {thin}" if thin else "",
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
