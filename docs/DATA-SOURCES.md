# Data Sources

## Primary: World Bank API

**Base URL:** `https://api.worldbank.org/v2/country/PH/indicator/{CODE}?format=json&per_page=100`

**Why this is the primary source:** The project asks a long-run national question: did life in the Philippines materially improve between 1960 and 2025? The World Bank API is the best fit because it gives one stable source for multi-decade annual indicators across the same country.

**Format:** JSON API

**Coverage:** Philippines, annual data, mostly 1960-2024 depending on indicator

**Access:** Public, no API key required

**Rate limits:** None documented for open data endpoints

### Selected indicators

Defined once in `scripts/indicators.py`, which is the single source of
truth. `ingest.py`, `transform.py`, and this table all read from it, so the
count cannot drift again.

| # | Code | Indicator | Typical coverage | Why it matters |
|---|---|---|---|---|
| 1 | `NY.GDP.PCAP.CD` | GDP per capita, current US$ | 1960-2024 | Headline economic growth |
| 2 | `NY.GDP.PCAP.KD` | GDP per capita, constant 2015 US$ | 1960-2024 | Real growth over time |
| 3 | `NY.GNP.PCAP.KD` | GNI per capita, constant 2015 US$ | 1960-2025 | Income kept by residents, not just output |
| 4 | `SP.DYN.LE00.IN` | Life expectancy at birth | 1960-2024 | Health and survival |
| 5 | `FP.CPI.TOTL.ZG` | Inflation, consumer prices | 1960-2024 | Cost pressure |
| 6 | `SP.POP.TOTL` | Population, total | 1960-2024 | National context |
| 7 | `SL.UEM.TOTL.ZS` | Unemployment, total | 1991-2024 | Labor market signal |
| 8 | `SE.PRM.ENRR` | School enrollment, primary | 1971-2023 | Education access |
| 9 | `SI.POV.GINI` | Gini index | 1985-2023 | Inequality |
| 10 | `BX.TRF.PWKR.DT.GD.ZS` | Personal remittances, received (% of GDP) | 1977-2024 | OFW dependency and support |
| 11 | `SH.XPD.CHEX.GD.ZS` | Current health expenditure (% of GDP) | 2000-2023 | Health system investment |
| 12 | `NE.CON.PRVT.ZS` | Household final consumption expenditure (% of GDP) | 1960-2024 | Household spending share |

### Why it fits the project

- It directly supports the core question with long-run national indicators.
- It is machine-readable and easy to ingest into a reproducible pipeline.
- It already covers GDP, life expectancy, inflation, inequality, remittances, and household consumption in one source.

### Known limitations

- It is strong for macro trends but weak for lived affordability details like rent, rice prices, fares, tuition, and land costs.
- Some indicators start later than 1960.
- National averages can hide regional and class differences.

---

## Fallback: PSA Family Income and Expenditure Survey (FIES)

**URL:** https://psa.gov.ph/statistics/income-expenditure/fies

**Format:** Official PSA statistical release pages with downloadable household survey tables/files

**Coverage:** Philippines household income and expenditure survey data, nationwide, reported by survey round instead of a full annual API series

**Why this is the fallback:** If the World Bank API is too macro-level for the affordability side of the question, FIES can still support a narrower version of the project focused on household income, spending, and purchasing-power trends.

### Why it could still work

- It is closer to household lived experience than macro-only indicators.
- It can support income, spending, and affordability analysis even if the final project scope narrows.
- It is an official Philippines government statistical source.

### Known limitations

- The PSA site is currently blocked by a Cloudflare challenge from this environment.
- The survey is less frequent than the World Bank annual series.
- Files may require manual download and cleaning.

---

## Other Blocked / Not Used Sources

| Source | Issue | Why not primary |
|---|---|---|
| PSA OpenStat | Cloudflare 403 blocks API from this environment | Too fragile for the main ingestion path right now |
| BSP | Some pages return 404 or auth walls | Useful later, but not the simplest Week 2 source |
| data.gov.ph | Returns HTML instead of usable API data in current checks | Not needed because World Bank already covers the core indicators |
| EconDB | Authentication required | Added friction without clear Week 2 benefit |

---

## Week 2 decision

- **Primary source:** World Bank API
- **Fallback source:** PSA Family Income and Expenditure Survey
