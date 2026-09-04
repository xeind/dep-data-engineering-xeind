# Project Architecture

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────┐
│                   DATA LAYER                             │
│                                                          │
│  World Bank API  ──────►  data/raw/                      │
│  (11 indicators)          (JSON responses cached)        │
│                                                          │
│  data/raw/  ───────────►  scripts/transform.py           │
│                            │                             │
│                            ▼                             │
│                     data/processed/                       │
│                     (unified time-series CSV)            │
└────────────────────────────┬────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                     ▼
  notebooks/          output/figures/         dashboard/
  (analysis jupyter)  (Plotly PNG/SVG)       (React SPA)
        │                                        │
        └────────────────┬───────────────────────┘
                         ▼
                   LaTeX → PDF
                   ("65 Years of Filipino Progress")
```

## Directory Structure

```
dep-data-engineering-xeind/
├── data/
│   ├── raw/              # Raw JSON responses from World Bank API
│   └── processed/        # Cleaned, merged CSV files
├── scripts/
│   ├── ingest.py         # Fetches 11 indicators from World Bank API
│   └── transform.py      # Merges, cleans, normalizes into unified CSV
├── notebooks/            # Jupyter notebooks for analysis (Phase 4-5)
├── output/figures/       # Exported charts for LaTeX report
├── dashboard/
│   └── index.html        # React + Liveline + Plotly dashboard
├── docs/
│   ├── DATA-SOURCES.md   # Confirmed data sources + indicators
│   └── ARCHITECTURE.md   # This file
├── requirements.txt      # Python dependencies
└── README.md             # Project overview
```

## Data Flow

### Phase 1: Ingest (`scripts/ingest.py`)
1. Loop through 11 World Bank indicator codes
2. Call API for each: `https://api.worldbank.org/v2/country/PH/indicator/{CODE}?format=json`
3. Save raw JSON to `data/raw/{indicator}.json`

### Phase 2: Transform (`scripts/transform.py`)
1. Load all raw JSON files
2. Extract `{date, value}` pairs per indicator
3. Merge into single DataFrame: `year | indicator | value`
4. Pivot to wide format: `year | gdp | life_exp | inflation | ...`
5. Add derived columns: `gdp_growth`, `real_wage_proxy`, etc.
6. Save to `data/processed/indicators.csv`

### Phase 3: Analyze (`notebooks/`)
1. Load unified CSV
2. Generate Plotly charts
3. Export figures to `output/figures/`
4. Write insights to notebook markdown cells

### Phase 4: Dashboard (`dashboard/index.html`)
1. React app loads from static HTML
2. Fetches `data/processed/indicators.csv` (or embedded JSON)
3. Renders Plotly main timeline + Liveline KPI cards
4. Filter bar triggers summary card overlay

### Phase 5: Report (LaTeX)
1. Uses exported figures from `output/figures/`
2. Compiles to PDF: "65 Years of Filipino Progress"

## Tech Stack

| Layer | Technology | License | Purpose |
|-------|-----------|---------|---------|
| Data ingestion | Python 3.10+ | - | Fetch WB API, parse JSON |
| Data transform | Python (pandas) | BSD | Merge, clean, normalize |
| Analysis | Jupyter + Plotly | BSD + MIT | Exploration, chart generation |
| Dashboard UI | React 18 | MIT | Component framework |
| Live charts | Liveline v0.0.7 | MIT | 60fps animated KPI cards |
| Analytical chart | Plotly.js | MIT | 65-year timeline with annotations |
| Styling | CSS custom properties | - | Dark theme, responsive |
| Deployment | GitHub Pages | - | Static hosting |
| CI/CD | GitHub Actions | - | Auto-deploy on push |
| Report | LaTeX | - | Professional whitepaper |

## GitHub Actions

### pages.yml (manual trigger only until Phase 6)
- Builds and deploys `dashboard/` to GitHub Pages
- Currently set to `workflow_dispatch`
- Will be enabled with proper cron + deploy in Phase 6

### Future: data-refresh.yml (Phase 3+)
- Weekly cron: runs `ingest.py` + `transform.py`
- Commits updated data files
- Triggers dashboard rebuild

## Design Decisions

### Why World Bank API only?
PSA, BSP, and data.gov.ph are all blocked or broken. World Bank API is the only reliable source - and it's more than enough. 11 indicators across 65 years from one clean JSON endpoint.

### Why Liveline + Plotly instead of just one?
Liveline excels at "live feel" - mini KPI charts that animate smoothly. Plotly excels at complex annotated time-series. They complement each other. React ties them together with zero build step via CDN imports.

### Why static HTML dashboard (no build step)?
GitHub Pages hosts static files. A build step (Vite/Webpack) adds complexity without benefit. React 18 + Liveline + Plotly all load from CDN via esm.sh. The dashboard is a single HTML file - portable, fast, zero-config.

### Why dark theme?
Our World in Data uses light theme, but dark works better for data-dense dashboards (less eye strain, higher contrast for colored lines). Liveline's default is dark. Consistent.
