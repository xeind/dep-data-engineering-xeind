"""
Pull peer-country indicator data from the World Bank API.

Milestone 5 (segmentation). The Philippine series alone cannot say whether
life got better compared to anyone else, so this pulls the same core
indicators for four Southeast Asian neighbours that started in a similar
place in 1960. Writes one raw JSON snapshot to data/raw/ with the request
URLs and pull timestamp, in the same shape as ingest.py.

Run: python scripts/ingest_peers.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from indicators import END_YEAR, INDICATORS, START_YEAR
from ingest import PER_PAGE, extract_rows, fetch_json

RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "world_bank_peers.json"

# code -> country name as the World Bank publishes it
PEER_COUNTRIES = {
    "PH": "Philippines",
    "TH": "Thailand",
    "VN": "Viet Nam",
    "ID": "Indonesia",
    "MY": "Malaysia",
}

# The subset of the registry that carries the comparison: income, survival,
# inequality, and the remittance dependence that sets the Philippines apart.
# Column names, labels, and units come from indicators.py.
PEER_INDICATORS = [
    "NY.GDP.PCAP.KD",
    "SP.DYN.LE00.IN",
    "SP.DYN.IMRT.IN",
    "SI.POV.GINI",
    "BX.TRF.PWKR.DT.GD.ZS",
]

DATE_RANGE = f"{START_YEAR}:{END_YEAR}"

# The API accepts several countries in one request, separated by semicolons.
BASE_URL = f"https://api.worldbank.org/v2/country/{';'.join(PEER_COUNTRIES)}/indicator"


def build_url(indicator_code, page=1):
    query = urlencode({
        "format": "json",
        "date": DATE_RANGE,
        "per_page": PER_PAGE,
        "page": page,
    })
    return f"{BASE_URL}/{indicator_code}?{query}"


def fetch_indicator(code):
    """Fetch every page for one indicator. Returns (metadata, rows, urls)."""
    urls = []
    page = 1
    all_rows = []
    metadata = {}

    while True:
        url = build_url(code, page)
        urls.append(url)
        metadata, rows = extract_rows(fetch_json(url))
        all_rows.extend(rows)
        total_pages = int(metadata.get("pages", 1) or 1)
        if page >= total_pages:
            break
        page += 1

    return metadata, all_rows, urls


def coverage_by_country(rows):
    """Observed count and span per country, so gaps show up at pull time."""
    coverage = {}
    for country in PEER_COUNTRIES:
        years = sorted(
            int(row["date"]) for row in rows
            if row["country"]["id"] == country and row.get("value") is not None
        )
        coverage[country] = {
            "observed_count": len(years),
            "first_year": years[0] if years else None,
            "last_year": years[-1] if years else None,
        }
    return coverage


def ingest_peers():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    snapshot = {
        "source": "World Bank API",
        "countries": list(PEER_COUNTRIES),
        "date_range": DATE_RANGE,
        "pulled_at_utc": datetime.now(timezone.utc).isoformat(),
        "indicators": {},
    }

    failures = []

    for code in PEER_INDICATORS:
        column, name, unit = INDICATORS[code]
        print(f"{code} ({column})")
        try:
            metadata, rows, urls = fetch_indicator(code)
        except (RuntimeError, ValueError) as error:
            print(f"  FAILED: {error}")
            failures.append(code)
            continue

        observed = [row for row in rows if row.get("value") is not None]
        coverage = coverage_by_country(rows)
        snapshot["indicators"][code] = {
            "column": column,
            "name": name,
            "unit": unit,
            "urls": urls,
            "row_count": len(rows),
            "observed_count": len(observed),
            "coverage": coverage,
            "source_last_updated": metadata.get("lastupdated"),
            "rows": rows,
        }
        for country, entry in coverage.items():
            span = f"{entry['first_year']}-{entry['last_year']}" if entry["observed_count"] else "no data"
            print(f"  {country}  {entry['observed_count']:2d} observed, {span}")

    OUTPUT_FILE.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nWrote {len(snapshot['indicators'])}/{len(PEER_INDICATORS)} indicators to {OUTPUT_FILE}")

    if failures:
        print(f"Failed indicators: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(ingest_peers())
