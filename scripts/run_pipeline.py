"""
Run every pipeline step in order, from raw pull to validated output.

Three pipelines, each ingest -> transform -> validate:
  main       World Bank, Philippines  -> data/processed/indicators.csv/json
             then scripts/query.py    -> output/query-results.md
  peers      World Bank, 5 countries  -> data/processed/peers.csv
  wage-rice  PSA rice prices + NWPC   -> data/processed/wage_rice.csv

Then one export step copies the validated output into dashboard/src/data/:
  dashboard  export_dashboard_data.py -> the JSON the dashboard bundles

The main pipeline runs first: validate_peers.py reads indicators.csv. The
export runs last, so the dashboard only gets data that passed validation; it
skips itself when dashboard/src does not exist. The run stops at the first
step that exits non-zero.

Run: python scripts/run_pipeline.py              (full run, needs network)
     python scripts/run_pipeline.py --offline    (skip ingest, rebuild from data/raw/)
     python scripts/run_pipeline.py --notebooks  (also execute the notebooks in place)
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
NOTEBOOKS_DIR = ROOT / "notebooks"

# pipeline name -> scripts in run order. Ingest steps are the only ones that
# touch the network, so --offline drops exactly those.
PIPELINES = {
    "main": ["ingest.py", "transform.py", "validate.py", "query.py"],
    "peers": ["ingest_peers.py", "transform_peers.py", "validate_peers.py"],
    "wage-rice": ["ingest_wage_rice.py", "transform_wage_rice.py", "validate_wage_rice.py"],
    "dashboard": ["export_dashboard_data.py"],
}

# The notebooks read data/processed/ and write output/figures/.
NOTEBOOKS = ["insights.ipynb", "segmentation.ipynb", "kpis.ipynb"]


def is_ingest(script):
    return script.startswith("ingest")


def run_step(label, command, cwd):
    print(f"\n=== {label}", flush=True)
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        print(f"\nFAILED: {label} exited {result.returncode}. Later steps did not run.")
    return result.returncode


def run_pipeline(offline, notebooks):
    steps = []
    for pipeline, scripts in PIPELINES.items():
        for script in scripts:
            if offline and is_ingest(script):
                continue
            steps.append((f"{pipeline}: {script}", [sys.executable, script], SCRIPTS_DIR))

    if notebooks:
        for notebook in NOTEBOOKS:
            command = [
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "notebook", "--execute", "--inplace", notebook,
            ]
            steps.append((f"notebook: {notebook}", command, NOTEBOOKS_DIR))

    for label, command, cwd in steps:
        code = run_step(label, command, cwd)
        if code != 0:
            return code

    print(f"\nAll {len(steps)} steps passed.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Run the full data pipeline in order.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="skip the ingest steps and rebuild from the committed snapshots in data/raw/",
    )
    parser.add_argument(
        "--notebooks",
        action="store_true",
        help="after the data steps, execute the notebooks in place with nbconvert",
    )
    args = parser.parse_args()
    return run_pipeline(args.offline, args.notebooks)


if __name__ == "__main__":
    sys.exit(main())
