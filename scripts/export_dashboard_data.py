"""
Copy the processed datasets the dashboard bundles into dashboard/src/data/.

The dashboard imports these JSON files at build time, so they must be
refreshed after every pipeline run. The Pages workflow runs this script
before `npm run build`.
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
REFERENCE = ROOT / "data" / "reference"
TARGET = ROOT / "dashboard" / "src" / "data"


def records(csv_path):
    # NaN becomes null so a missing measurement stays visibly missing.
    frame = pd.read_csv(csv_path)
    return json.loads(frame.to_json(orient="records"))


def write(name, payload):
    path = TARGET / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {path.relative_to(ROOT)}")


def main():
    # The React app lands in the repo after the data pipeline does. Until
    # dashboard/src exists there is nothing to export into, which is not a
    # pipeline failure.
    if not TARGET.parent.is_dir():
        print("SKIPPED: dashboard/src does not exist yet")
        return

    TARGET.mkdir(parents=True, exist_ok=True)

    indicators = json.loads((PROCESSED / "indicators.json").read_text())
    write("indicators.json", indicators)

    write("peers.json", {
        "source": "World Bank API, see docs/PEERS.md",
        "rows": records(PROCESSED / "peers.csv"),
    })

    write("wage_rice.json", {
        "source": "NWPC wage orders and PSA OpenSTAT, see docs/WAGE-RICE.md",
        "rows": records(PROCESSED / "wage_rice.csv"),
    })

    sources = json.loads((REFERENCE / "primary_sources.json").read_text())
    write("primary_sources.json", sources)


if __name__ == "__main__":
    main()
