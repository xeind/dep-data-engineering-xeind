"""
Pull the two raw inputs for the wage-rice series: PSA rice prices and the
NWPC wage-order table.

Rice: queries the PSA OpenSTAT PXWeb API for the NCR retail price of
regular-milled rice, every month and the annual average, from both the old
series (1990-2020) and the 2018-based series (2018 onward). Writes one raw
JSON snapshot holding each response exactly as the API returned it, plus the
table metadata, queries, URLs and pull timestamp needed to reproduce it.

Wage: data/raw/ncr_wage_orders.csv is transcribed by hand from the NWPC PDF
(one row per wage order or tranche). This script downloads that PDF, checks
its SHA-256 against the hash recorded in the CSV, and, when Ghostscript is
installed, checks the CSV's effective year and top-of-range total against
the PDF text, row by row. A mismatch means the transcription is stale.

Run: python scripts/ingest_wage_rice.py
"""

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

from ingest import BACKOFF_SECONDS, MAX_RETRIES, TIMEOUT_SECONDS, fetch_json

RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RICE_FILE = RAW_DATA_DIR / "psa_rice_prices.json"
WAGE_ORDERS_FILE = RAW_DATA_DIR / "ncr_wage_orders.csv"
WAGE_PDF_FILE = RAW_DATA_DIR / "nwpc_daily_minimum_wage_non_agriculture_2026-09-02.pdf"

PXWEB_BASE = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB"

# PSA answers 403 to the default "Python-urllib" user agent and 200 to a
# named one. This header identifies the project; it does not imitate a browser.
USER_AGENT = "dep-data-engineering-xeind/1.0 (wage-rice ingest)"

# series id -> table path, NCR geolocation code, RMR commodity code, and the
# labels those codes must carry. The labels are checked against the live
# metadata so a silent recode on PSA's side fails here instead of pulling the
# wrong region or grade.
RICE_TABLES = {
    "PSA-RP-0042M4ARP01": {
        "name": "Cereals: Retail Prices (Old Series)",
        "path": "2M/RP/0042M4ARP01.px",
        "geolocation": ("13", "..NATIONAL CAPITAL REGION (NCR)"),
        "commodity": ("3", "Regular Milled Rice (RMR)"),
    },
    "PSA-2018NEW-0042M4ARN01": {
        "name": "Cereals: Retail Prices, 2018-based (New Geographic Code)",
        "path": "2M/2018NEW/0042M4ARN01.px",
        "geolocation": ("130000000", "..NCR - National Capital Region"),
        "commodity": ("1", "RICE, REGULAR-MILLED, 1 KG"),
    },
}

# The NWPC filename changes with every update. Re-check the index page and
# re-transcribe the CSV when it does:
# https://nwpc.dole.gov.ph/summary-of-daily-minimum-wage-rates-per-wage-order-by-region-non-agriculture-1989-present/
WAGE_PDF_URL = (
    "https://nwpc.dole.gov.ph/wp-content/uploads/2026/09/"
    "Summary-of-DMWR-per-Wage-Order-by-Region_Non-Agriculture-1989-to-Sep_2_2026-1.pdf"
)


def fetch_bytes(request):
    """GET or POST with retries and exponential backoff. Rejects short reads.

    The NWPC server has cut a PDF download short with HTTP 200, so the body
    length is checked against Content-Length rather than trusted.
    """
    url = request.full_url
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                body = response.read()
                expected = response.headers.get("Content-Length")
                if expected is not None and len(body) != int(expected):
                    raise IncompleteRead(body, int(expected) - len(body))
                return body
        except (HTTPError, URLError, TimeoutError, IncompleteRead) as error:
            last_error = error
            if attempt == MAX_RETRIES:
                break
            delay = BACKOFF_SECONDS ** attempt
            print(f"  attempt {attempt}/{MAX_RETRIES} failed ({error!r}); retrying in {delay}s")
            time.sleep(delay)
    raise RuntimeError(f"giving up on {url}: {last_error!r}")


def check_code(variables, code, value, label):
    variable = next(v for v in variables if v["code"] == code)
    actual = dict(zip(variable["values"], variable["valueTexts"])).get(value)
    if actual != label:
        raise ValueError(f"{code} {value!r} is {actual!r}, expected {label!r}")


def fetch_rice_table(table):
    """Metadata GET, then one POST for NCR x RMR x every year x every period."""
    url = f"{PXWEB_BASE}/{table['path']}"
    metadata = fetch_json(Request(url, headers={"User-Agent": USER_AGENT}))
    variables = metadata["variables"]

    geo_code, geo_label = table["geolocation"]
    commodity_code, commodity_label = table["commodity"]
    check_code(variables, "Geolocation", geo_code, geo_label)
    check_code(variables, "Commodity", commodity_code, commodity_label)

    # Year and Period are left out of the query, so PXWeb returns all of them.
    query = {
        "query": [
            {"code": "Geolocation", "selection": {"filter": "item", "values": [geo_code]}},
            {"code": "Commodity", "selection": {"filter": "item", "values": [commodity_code]}},
        ],
        "response": {"format": "json"},
    }
    request = Request(
        url,
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    # PXWeb prefixes the JSON body with a UTF-8 byte order mark.
    response = json.loads(fetch_bytes(request).decode("utf-8-sig"))
    return url, metadata, query, response


def ingest_rice():
    snapshot = {
        "source": "PSA OpenSTAT PXWeb API",
        "pulled_at_utc": datetime.now(timezone.utc).isoformat(),
        "tables": {},
    }
    for series_id, table in RICE_TABLES.items():
        print(f"{series_id} ({table['name']})")
        url, metadata, query, response = fetch_rice_table(table)
        snapshot["tables"][series_id] = {
            "name": table["name"],
            "url": url,
            "query": query,
            "metadata": metadata,
            "response": response,
        }
        print(f"  {len(response['data'])} cells")

    RICE_FILE.write_text(json.dumps(snapshot, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {RICE_FILE}")


def pdf_ncr_rows(pdf_path):
    """(effective year, top-of-range total) for each NCR line on PDF page 1.

    The NCR block runs from the line that starts with "NCR" to the line that
    starts with "CAR". The issued date uses a two-digit year, so the only
    four-digit year on a line is the effective date. The last amount on a
    line is the top of the TOTAL range.
    """
    text = subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=txtwrite",
         "-dFirstPage=1", "-dLastPage=1", "-sOutputFile=-", str(pdf_path)],
        capture_output=True, text=True, check=True,
    ).stdout

    rows = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("NCR"):
            in_block = True
        elif stripped.startswith("CAR"):
            break
        if not in_block or not stripped:
            continue
        years = [token for token in stripped.replace(",", " ").replace("/", " ").split()
                 if token.isdigit() and len(token) == 4]
        total = stripped.replace("-", " ").split()[-1]
        rows.append((int(years[-1]), float(total)))
    return rows


def ingest_wage():
    print("NWPC wage-order PDF")
    body = fetch_bytes(Request(WAGE_PDF_URL, headers={"User-Agent": USER_AGENT}))
    WAGE_PDF_FILE.write_bytes(body)
    digest = hashlib.sha256(body).hexdigest()
    print(f"  {len(body)} bytes, sha256 {digest}")
    print(f"Wrote {WAGE_PDF_FILE}")

    orders = pd.read_csv(WAGE_ORDERS_FILE)
    failures = []

    recorded = set(orders["source_sha256"])
    if recorded != {digest}:
        failures.append(f"PDF hash {digest} does not match the CSV's {sorted(recorded)}")

    if shutil.which("gs") is None:
        print("  SKIPPED row check: Ghostscript (gs) not installed")
    else:
        from_pdf = pdf_ncr_rows(WAGE_PDF_FILE)
        from_csv = list(zip(
            pd.to_datetime(orders["effective_date"]).dt.year,
            orders["total_wage_high"].astype(float),
        ))
        if from_pdf != from_csv:
            mismatched = [
                (index, pdf_row, csv_row)
                for index, (pdf_row, csv_row) in enumerate(zip(from_pdf, from_csv))
                if pdf_row != csv_row
            ]
            failures.append(
                f"CSV rows differ from PDF text: {len(from_pdf)} PDF rows, "
                f"{len(from_csv)} CSV rows, first differences {mismatched[:3]}"
            )
        else:
            print(f"  {len(from_csv)} CSV rows match the PDF text (effective year, total top)")

    for failure in failures:
        print(f"  FAILED: {failure}")
    return failures


def ingest():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    failures = []
    try:
        ingest_rice()
    except (RuntimeError, ValueError, KeyError) as error:
        print(f"  FAILED: {error}")
        failures.append("rice")

    print()
    try:
        if ingest_wage():
            failures.append("wage")
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"  FAILED: {error}")
        failures.append("wage")

    if failures:
        print(f"\nFailed: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(ingest())
