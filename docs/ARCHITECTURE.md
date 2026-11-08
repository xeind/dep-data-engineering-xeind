# Project Architecture

## Pipeline Overview

Three pipelines, each ingest -> transform -> validate.
`scripts/run_pipeline.py` runs them in this order and stops at the first
failure. `--offline` skips the three ingest steps; `--notebooks` executes
the notebooks after the data steps.

```
MAIN
World Bank API, PH, 16 indicators
  -> scripts/ingest.py           -> data/raw/world_bank_ph_indicators.json
  -> scripts/transform.py        -> data/processed/indicators.csv     66 years x 21 columns
                                    data/processed/indicators.json    same table, dashboard shape
                                    data/processed/cleaning-report.json
  -> scripts/validate.py         25 checks
  -> scripts/query.py            -> output/query-results.md           5 SQL questions

PEERS                                        (validate_peers.py reads indicators.csv)
World Bank API, PH TH VN ID MY, 5 indicators
  -> scripts/ingest_peers.py     -> data/raw/world_bank_peers.json
  -> scripts/transform_peers.py  -> data/processed/peers.csv          330 country-years
  -> scripts/validate_peers.py   7 checks

WAGE-RICE
PSA OpenSTAT API (rice)  +  NWPC PDF -> data/raw/ncr_wage_orders.csv (hand-transcribed)
  -> scripts/ingest_wage_rice.py     -> data/raw/psa_rice_prices.json
                                        data/raw/nwpc_daily_minimum_wage_non_agriculture_2026-09-02.pdf
  -> scripts/transform_wage_rice.py  -> data/processed/wage_rice.csv  36 years
  -> scripts/validate_wage_rice.py   18 checks

ANALYSIS                                    reads data/processed/
  notebooks/insights.ipynb       indicators.csv                -> output/figures/01-*.png ... 05-*.png
  notebooks/segmentation.ipynb   indicators.csv, peers.csv     -> output/figures/seg-*.png
  notebooks/kpis.ipynb           indicators.csv, wage_rice.csv -> output/figures/kpi-*.png

DASHBOARD
  dashboard/  React app, bundles indicators.json at build time -> GitHub Pages
```

## Directory Structure

```
dep-data-engineering-xeind/
├── data/
│   ├── raw/                        # source snapshots, committed
│   │   ├── world_bank_ph_indicators.json
│   │   ├── world_bank_peers.json
│   │   ├── psa_rice_prices.json
│   │   ├── ncr_wage_orders.csv     # hand-transcribed from the NWPC PDF
│   │   └── nwpc_daily_minimum_wage_non_agriculture_2026-09-02.pdf
│   ├── reference/
│   │   └── presidencies.csv        # lookup for query.py
│   └── processed/
│       ├── indicators.csv
│       ├── indicators.json
│       ├── cleaning-report.json
│       ├── peers.csv
│       └── wage_rice.csv
├── scripts/
│   ├── run_pipeline.py             # one entry point, runs everything below in order
│   ├── indicators.py               # the 16 indicator codes — single source of truth
│   ├── ingest.py                   # main: fetch
│   ├── transform.py                # main: reshape + derive
│   ├── validate.py                 # main: data quality gate
│   ├── query.py                    # main: run sql/ against indicators.csv
│   ├── ingest_peers.py             # peers: fetch
│   ├── transform_peers.py          # peers: reshape
│   ├── validate_peers.py           # peers: data quality gate
│   ├── ingest_wage_rice.py         # wage-rice: fetch rice, check transcription
│   ├── transform_wage_rice.py      # wage-rice: annualise + ratio
│   └── validate_wage_rice.py       # wage-rice: data quality gate
├── sql/                            # 5 business questions, one file each
├── notebooks/
│   ├── insights.ipynb
│   ├── segmentation.ipynb
│   └── kpis.ipynb
├── output/
│   ├── figures/                    # exported charts
│   └── query-results.md
├── dashboard/                      # Vite + React app
│   ├── src/
│   │   ├── data/                   # dataset.ts + bundled indicators.json
│   │   ├── components/ui/          # shadcn-style primitives
│   │   └── components/charts/      # ProgressGapChart, SeriesChart
│   └── dist/                       # build output, not committed
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CLEANING-NOTES.md
│   ├── DATA-SOURCES.md
│   ├── LIMITATIONS.md
│   ├── PEERS.md
│   ├── SCHEMA.md
│   ├── STAKEHOLDER-BRIEF.md
│   └── WAGE-RICE.md
├── requirements.txt
└── README.md
```

## Data Flow

### Run everything (`scripts/run_pipeline.py`)

Runs each script below as a subprocess, in order, with the same Python
interpreter. It stops at the first non-zero exit and names the step. The
main pipeline goes first because `validate_peers.py` compares the Philippine
peer rows against `indicators.csv`.

### Ingest (`scripts/ingest.py`)

Loops the 16 codes in `scripts/indicators.py`, requests each with retries and
exponential backoff, follows pagination, and writes one JSON snapshot holding
every response plus the request URLs and a UTC pull timestamp. A failed
indicator is reported and the process exits non-zero rather than writing a
silently incomplete file.

### Transform (`scripts/transform.py`)

Pivots to one row per year over a fixed 1960–2025 index, casts to float, and
adds five derived columns — growth rate, index-to-1960, life-expectancy gain,
a chained CPI index rebased to 2024, and the peso conversion. Nothing is
imputed or smoothed. See [CLEANING-NOTES.md](./CLEANING-NOTES.md).

### Validate (`scripts/validate.py`)

25 checks covering index completeness, column coverage, plausible ranges,
monotonic population, and the CPI base year. This is the gate between the
pipeline and anything that consumes its output.

### Query (`scripts/query.py`)

Loads `indicators.csv` and `data/reference/presidencies.csv` into an
in-memory SQLite database, runs every file in `sql/`, and writes the results
to `output/query-results.md`. No database file is kept.

### Peers (`scripts/*_peers.py`)

Reuses the main ingest's fetch and retry code, with one paginated request
per indicator covering all five countries. The transform writes a long table,
one row per country-year, and indexes each country's GDP to its own 1960
value. Seven checks gate it. See [PEERS.md](./PEERS.md).

### Wage-rice (`scripts/*_wage_rice.py`)

Ingest pulls NCR rice prices from two PSA OpenSTAT tables and downloads the
NWPC wage-order PDF. It checks the PDF hash against the hand-transcribed
`ncr_wage_orders.csv`, and with Ghostscript installed, checks the rows too.
The transform joins the two rice tables at 2018, turns wage orders into a
day-weighted annual wage, and divides. Eighteen checks gate it. See
[WAGE-RICE.md](./WAGE-RICE.md).

### Notebooks (`notebooks/`)

Read only from `data/processed/` and write only to `output/figures/`. They
are committed with outputs embedded, so GitHub renders every chart.

### Dashboard (`dashboard/`)

A Vite + React app. `indicators.json` is imported at build time rather than
fetched, so there is no runtime data request and no base-path problem on
Pages. Deployed by `.github/workflows/pages.yml` on any push to `main` that
touches `dashboard/` or `data/processed/`.

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Orchestration | Python stdlib (`subprocess`, `argparse`) | `run_pipeline.py` |
| Ingestion | Python 3.11+ stdlib; pandas for the wage-order check | Fetch and snapshot the APIs and the PDF |
| PDF text | Ghostscript (`gs`), optional | Check the wage-order transcription |
| Query | SQLite (stdlib `sqlite3`) | Business questions in SQL |
| Transform | pandas | Reshape, derive, write |
| Validation | pandas | Data quality gate |
| Analysis | Jupyter + Plotly | Exploration, figure export |
| App | React + TypeScript + Vite | Dashboard |
| Styling | Tailwind CSS v4 | Design tokens, layout |
| Components | shadcn-style primitives | Card, Button |
| Charts | Recharts | Line, area, reference bands and markers |
| Motion | motion | Entrance and state transitions |
| Deployment | GitHub Pages via Actions | Static hosting |

## Design Decisions

### Why one indicator registry?

`docs/DATA-SOURCES.md`, `dep-cohort1.md`, and `ingest.py` had each drifted to
a different indicator list — 11, a different 11, and 10. `scripts/indicators.py`
now defines the codes, column names, and units once, and both `ingest.py` and
`transform.py` import it.

### Why index everything to 1960 = 100?

The original plan was one timeline with GDP, life expectancy, and inflation
overlaid. Those have different units, which means two y-scales, and the
alignment between two y-scales is arbitrary — it invents a correlation the
data does not contain. Indexing every series to a shared 1960 base puts them
on one honest axis, and the gap between the GDP line and the life-expectancy
line becomes the answer to the project question rather than an artifact of
scale choice.

Only series with a real 1960 observation appear on that chart. Indexing the
Gini series, which starts in 1985, to a 1960 base it never had would be
fabrication. Those series get their own charts in native units.

### Why a build step, when the earlier plan said none?

The earlier decision was a single static `index.html` pulling React and
Plotly from a CDN, chosen because Pages hosts static files. shadcn/ui cannot
work that way — it is component source copied into the project, and it needs
Tailwind compiled. Since the stack now includes it, the app is built by Vite
and Actions uploads `dist/` as the Pages artifact. Pages still only ever
serves static files; the build just happens in CI instead of not at all.

### Why Recharts instead of Plotly?

Recharts composes with the React component tree and the Tailwind token layer,
so the charts inherit the same colour and type scale as the rest of the UI.
Plotly brings its own rendering and theming model, which would mean
maintaining two design systems. Plotly stays in the notebooks, where static
figure export is what matters.

### When charts animate, and when they do not

Recharts draws lines progressively on mount. Firing that on page load meant
five charts animating at once, most of them off-screen where nobody saw
them, and any interruption left a truncated line that looked like a bug.

The single-series charts now mount when they scroll into view instead, so
the line draws itself as the reader arrives at it. A two-second fallback
renders them regardless, so a chart never sits blank when it is printed,
opened on a very tall viewport, or jumped to directly.

The main chart does not draw on mount. It is the first thing on the page and
carries the argument, so its data appears immediately. Its motion is in the
brush: jumping to an administration glides the window over 500ms rather than
snapping, which keeps the reader oriented in the 66-year range.

All of it is disabled under `prefers-reduced-motion`, which renders every
chart immediately and turns the brush jump into an instant move.

### Colour

Palette, contrast, and colourblind separation follow a validated categorical
scale, checked with a script rather than by eye, in both light and dark. Hues
are assigned per series identity and never by rank, so toggling a series off
never repaints the others. Three light-mode hues fall below 3:1 against the
surface, so the main chart carries direct endpoint labels and a table view —
identity is never colour alone.
