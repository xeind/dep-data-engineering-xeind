"""
Pull raw Philippines indicator data from the World Bank API.

Path A (API ingestion). Writes one raw JSON snapshot to data/raw/ holding
every indicator response exactly as the API returned it, plus the URLs and
pull timestamp needed to reproduce it.

Run: python scripts/ingest.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from indicators import COUNTRY_CODE, END_YEAR, INDICATORS, START_YEAR

RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "world_bank_ph_indicators.json"

DATE_RANGE = f"{START_YEAR}:{END_YEAR}"
BASE_URL = f"https://api.worldbank.org/v2/country/{COUNTRY_CODE}/indicator"

PER_PAGE = 200
MAX_RETRIES = 4
BACKOFF_SECONDS = 2
TIMEOUT_SECONDS = 30


def build_url(indicator_code, page=1):
    query = urlencode({
        "format": "json",
        "date": DATE_RANGE,
        "per_page": PER_PAGE,
        "page": page,
    })
    return f"{BASE_URL}/{indicator_code}?{query}"


def fetch_json(url):
    """GET with retries and exponential backoff. Raises on final failure."""
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt == MAX_RETRIES:
                break
            delay = BACKOFF_SECONDS ** attempt
            print(f"  attempt {attempt}/{MAX_RETRIES} failed ({error}); retrying in {delay}s")
            time.sleep(delay)
    raise RuntimeError(f"giving up on {url}: {last_error}")


def extract_rows(payload):
    """World Bank returns [metadata, rows]. An error returns [{'message': ...}]."""
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError(f"unexpected API response shape: {payload}")
    metadata, rows = payload[0], payload[1]
    if rows is None:
        rows = []
    if not isinstance(rows, list):
        raise ValueError(f"expected a list of rows, got {type(rows).__name__}")
    return metadata, rows


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


def ingest():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    snapshot = {
        "source": "World Bank API",
        "country": COUNTRY_CODE,
        "date_range": DATE_RANGE,
        "pulled_at_utc": datetime.now(timezone.utc).isoformat(),
        "indicators": {},
    }

    failures = []

    for code, (column, name, unit) in INDICATORS.items():
        print(f"{code} ({column})")
        try:
            metadata, rows, urls = fetch_indicator(code)
        except (RuntimeError, ValueError) as error:
            print(f"  FAILED: {error}")
            failures.append(code)
            continue

        observed = [row for row in rows if row.get("value") is not None]
        years = sorted(int(row["date"]) for row in observed)
        snapshot["indicators"][code] = {
            "column": column,
            "name": name,
            "unit": unit,
            "urls": urls,
            "row_count": len(rows),
            "observed_count": len(observed),
            "first_year": years[0] if years else None,
            "last_year": years[-1] if years else None,
            "source_last_updated": metadata.get("lastupdated"),
            "rows": rows,
        }
        span = f"{years[0]}-{years[-1]}" if years else "no data"
        print(f"  {len(observed)}/{len(rows)} observed, {span}")

    OUTPUT_FILE.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nWrote {len(snapshot['indicators'])}/{len(INDICATORS)} indicators to {OUTPUT_FILE}")

    if failures:
        print(f"Failed indicators: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(ingest())
