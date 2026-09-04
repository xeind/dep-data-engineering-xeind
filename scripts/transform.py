"""
Turn the raw World Bank snapshot into one analysis-ready table.

Reads  : data/raw/world_bank_ph_indicators.json
Writes : data/processed/indicators.csv      (wide, one row per year)
         data/processed/indicators.json     (same data, shaped for the dashboard)
         data/processed/cleaning-report.json (per-column coverage and gap reasons)

Run: python scripts/transform.py   (after scripts/ingest.py)
"""

import json
import sys
from pathlib import Path

import pandas as pd

from indicators import ANCHOR, END_YEAR, GAP_REASONS, INDICATORS, START_YEAR

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "world_bank_ph_indicators.json"
PROCESSED_DIR = ROOT / "data" / "processed"
CSV_FILE = PROCESSED_DIR / "indicators.csv"
JSON_FILE = PROCESSED_DIR / "indicators.json"
REPORT_FILE = PROCESSED_DIR / "cleaning-report.json"

# Money is expressed in constant pesos of this year, per the project's
# fair-comparison rule. 2024 is the last year with a full inflation figure.
PRICE_BASE_YEAR = 2024


def load_snapshot():
    if not RAW_FILE.exists():
        raise SystemExit(f"{RAW_FILE} not found. Run scripts/ingest.py first.")
    return json.loads(RAW_FILE.read_text(encoding="utf-8"))


def to_wide(snapshot):
    """One row per year, one column per indicator."""
    frame = pd.DataFrame({"year": range(START_YEAR, END_YEAR + 1)}).set_index("year")

    for code, payload in snapshot["indicators"].items():
        column = payload["column"]
        series = {
            int(row["date"]): row["value"]
            for row in payload["rows"]
            if row.get("value") is not None
        }
        frame[column] = pd.Series(series, dtype="float64")

    # Keep column order stable and matching the registry, not the JSON.
    return frame[[column for column, _, _ in INDICATORS.values()]]


def add_derived(frame):
    """Columns the raw API does not give us but the project question needs."""
    anchor = frame[ANCHOR]

    # Real growth of the anchor line, year over year.
    frame["gdp_growth_pct"] = anchor.pct_change() * 100

    # Anchor indexed to the first year, so "how much richer since 1960" is
    # readable without doing arithmetic in your head.
    frame["gdp_index_1960"] = anchor / anchor.loc[START_YEAR] * 100

    # Years of life gained since 1960 — the clearest "life got better" column.
    life = frame["life_expectancy"]
    frame["life_expectancy_gain"] = life - life.loc[START_YEAR]

    # Cumulative price level built from annual inflation, rebased so that
    # PRICE_BASE_YEAR = 100. This is what makes peso comparisons honest.
    growth_factor = 1 + frame["inflation"] / 100
    cpi = growth_factor.cumprod()
    cpi = cpi / cpi.loc[PRICE_BASE_YEAR] * 100
    frame[f"cpi_index_{PRICE_BASE_YEAR}"] = cpi

    # What 100 pesos of that year's money is worth in PRICE_BASE_YEAR pesos.
    # The tito-at-the-reunion column: "dati, ang ₱100 kaya bumili ng..."
    frame[f"peso100_in_{PRICE_BASE_YEAR}_pesos"] = 100 * cpi.loc[PRICE_BASE_YEAR] / cpi

    return frame


def to_dashboard_json(frame, snapshot):
    """Nulls instead of NaN, and a meta block the dashboard can render."""
    payload = {
        "meta": {
            "title": "65 Years of Filipino Progress",
            "range": f"{START_YEAR}-{END_YEAR}",
            "source": snapshot["source"],
            "pulled_at_utc": snapshot["pulled_at_utc"],
            "price_base_year": PRICE_BASE_YEAR,
            "anchor": ANCHOR,
            "columns": {
                payload["column"]: {"label": payload["name"], "unit": payload["unit"]}
                for payload in snapshot["indicators"].values()
            },
        },
        "years": [int(year) for year in frame.index],
    }
    for column in frame.columns:
        payload[column] = [
            None if pd.isna(value) else round(float(value), 4)
            for value in frame[column]
        ]
    return payload


def to_cleaning_report(frame):
    """Per-column coverage, with a stated reason for every gap.

    Nothing is imputed, so a gap is a fact about the source, not a defect in
    the table. Writing the reasons out beside the counts means the claim
    "missing values are flagged with a reason" can be checked by a machine
    instead of taken on trust from prose.
    """
    columns = {}
    for column in frame.columns:
        observed = frame[column].notna()
        years = frame.index[observed]
        missing = frame.index[~observed]
        entry = {
            "observed": int(observed.sum()),
            "missing": int((~observed).sum()),
            "first_year": int(years.min()) if len(years) else None,
            "last_year": int(years.max()) if len(years) else None,
            "dtype": str(frame[column].dtype),
        }
        if len(missing):
            entry["missing_years"] = [int(year) for year in missing]
            entry["reason"] = GAP_REASONS.get(column, "UNDOCUMENTED")
        columns[column] = entry

    return {
        "policy": "No imputation, no smoothing, no outlier removal. "
                  "Every empty cell is a year the source did not measure.",
        "rows": int(len(frame)),
        "columns": len(frame.columns),
        "complete_columns": sum(1 for c in columns.values() if c["missing"] == 0),
        "per_column": columns,
    }


def transform():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    snapshot = load_snapshot()
    frame = add_derived(to_wide(snapshot))

    frame.round(4).to_csv(CSV_FILE)
    JSON_FILE.write_text(
        json.dumps(to_dashboard_json(frame, snapshot), indent=1),
        encoding="utf-8",
    )

    REPORT_FILE.write_text(
        json.dumps(to_cleaning_report(frame), indent=2),
        encoding="utf-8",
    )

    print(f"{len(frame)} years x {len(frame.columns)} columns")
    print(f"  {CSV_FILE}")
    print(f"  {JSON_FILE}")
    print(f"  {REPORT_FILE}")
    print("\nCoverage:")
    for column in frame.columns:
        observed = frame[column].notna()
        years = frame.index[observed]
        span = f"{years.min()}-{years.max()}" if len(years) else "empty"
        print(f"  {column:28s} {observed.sum():3d}/{len(frame)}  {span}")

    return 0


if __name__ == "__main__":
    sys.exit(transform())
