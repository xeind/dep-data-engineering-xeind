# Data Sources

## Primary: World Bank API

**Base URL:** `https://api.worldbank.org/v2/country/PH/indicator/{CODE}?format=json&per_page=100`

**Why this is the primary source:** The project asks a long-run national question: did life in the Philippines materially improve between 1960 and 2025? The World Bank API is the best fit because it gives one stable source for multi-decade annual indicators across the same country.

**Format:** JSON API

**Coverage:** Philippines, annual data, 1960-2025, with some indicators starting later or ending in 2024

**Access:** Public, no API key required

**Rate limits:** None documented for open data endpoints

### Selected indicators

| # | Code | Column | Indicator | Coverage | Why it matters |
|---|---|---|---|---|---|
| 1 | `NY.GDP.PCAP.CD` | `gdp_per_capita_current` | GDP per capita, current US$ | 1960-2025 | Headline economic growth |
| 2 | `NY.GDP.PCAP.KD` | `gdp_per_capita_const` | GDP per capita, constant 2015 US$ | 1960-2025 | Real growth over time |
| 3 | `NY.GNP.PCAP.KD` | `gni_per_capita_const` | GNI per capita, constant 2015 US$ | 1960-2025 | Income earned by residents, including primary income from abroad |
| 4 | `SP.DYN.LE00.IN` | `life_expectancy` | Life expectancy at birth | 1960-2024 | Health and survival |
| 5 | `FP.CPI.TOTL.ZG` | `inflation` | Inflation, consumer prices | 1960-2025 | Cost pressure |
| 6 | `SP.POP.TOTL` | `population` | Population, total | 1960-2025 | National context |
| 7 | `SL.UEM.TOTL.ZS` | `unemployment` | Unemployment, total | 1991-2025 | Labor market signal |
| 8 | `SE.PRM.ENRR` | `school_enrollment` | School enrollment, primary | 1971-2024 | Education access |
| 9 | `SI.POV.GINI` | `gini` | Gini index | 1985-2023 (14 points) | Inequality |
| 10 | `BX.TRF.PWKR.DT.GD.ZS` | `remittances` | Personal remittances, received (% of GDP) | 1977-2025 | OFW dependency and support |
| 11 | `SH.XPD.CHEX.GD.ZS` | `health_expenditure` | Current health expenditure (% of GDP) | 2000-2023 | Health system investment |
| 12 | `NE.CON.PRVT.ZS` | `household_consumption` | Household final consumption expenditure (% of GDP) | 1981-2025 | Household spending share |
| 13 | `SP.DYN.IMRT.IN` | `infant_mortality` | Mortality rate, infant (per 1,000 live births) | 1960-2024 | Child survival |
| 14 | `SP.DYN.TFRT.IN` | `fertility_rate` | Fertility rate, total (births per woman) | 1960-2024 | Family size |
| 15 | `EG.ELC.ACCS.ZS` | `electricity_access` | Access to electricity (% of population) | 1993-2024 | Basic household services |
| 16 | `SI.POV.NAHC` | `poverty_national` | Poverty headcount ratio at national poverty lines (% of population) | 2015-2023 (4 points) | Poverty by the national line |

Coverage is the first and last observed year in the committed snapshot,
`data/raw/world_bank_ph_indicators.json`. `scripts/indicators.py` holds this
list in code; [SCHEMA.md](./SCHEMA.md) gives observed counts.

### Why it fits the project

- It supports the core question with long-run national indicators.
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
| PSA OpenStat | Returned 403 in the Week 2 checks | Now used for rice prices. The 403 was a response to Python's default user agent; see below |
| BSP | Some pages return 404 or auth walls | Useful later, but not the simplest Week 2 source |
| data.gov.ph | Returns HTML instead of usable API data in current checks | Not needed because World Bank already covers the core indicators |
| EconDB | Authentication required | Added friction without clear Week 2 benefit |

---

## Peer countries: World Bank API

**URL:** `https://api.worldbank.org/v2/country/PH;TH;VN;ID;MY/indicator/{CODE}?format=json&date=1960:2025`

**Script:** `scripts/ingest_peers.py` -> `data/raw/world_bank_peers.json`

The same API as the primary source, one request per indicator for five
countries at once. It pulls five indicators already in the main list:
`NY.GDP.PCAP.KD`, `SP.DYN.LE00.IN`, `SP.DYN.IMRT.IN`, `SI.POV.GINI`, and
`BX.TRF.PWKR.DT.GD.ZS`, for the Philippines, Thailand, Vietnam, Indonesia,
and Malaysia, 1960-2025.

**Why:** the Philippine series alone cannot say whether life improved more
or less than it could have. Neighbours that started in a similar place in
1960 give that comparison. Choice of countries and every gap:
[PEERS.md](./PEERS.md).

---

## Rice prices: PSA OpenSTAT PXWeb API

**Base URL:** `https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB`

**Script:** `scripts/ingest_wage_rice.py` -> `data/raw/psa_rice_prices.json`

| Table | Path | Item | NCR code | Years used |
|---|---|---|---|---|
| `0042M4ARP01` Cereals: Retail Prices (Old Series) | `2M/RP/0042M4ARP01.px` | Regular Milled Rice (RMR) | `13` | 1990-2017 |
| `0042M4ARN01` Cereals: Retail Prices, 2018-based | `2M/2018NEW/0042M4ARN01.px` | RICE, REGULAR-MILLED, 1 KG | `130000000` | 2018-2025 |

**Format:** JSON. A metadata GET, then one POST query per table for NCR,
regular-milled rice, every year, every month, and PSA's annual average.

**Access:** Public, no API key. The server answers 403 to Python's default
`Python-urllib` user agent, so requests send a named project user agent.

**Known limitations:** NCR only. Machine-readable prices start in 1990. The
two tables disagree where they overlap (2018-2020), so each year takes
exactly one; see [WAGE-RICE.md](./WAGE-RICE.md).

---

## Minimum wage: NWPC wage-order summary (PDF)

**URL:** https://nwpc.dole.gov.ph/wp-content/uploads/2026/09/Summary-of-DMWR-per-Wage-Order-by-Region_Non-Agriculture-1989-to-Sep_2_2026-1.pdf

**Committed as:** `data/raw/nwpc_daily_minimum_wage_non_agriculture_2026-09-02.pdf`

**Transcribed to:** `data/raw/ncr_wage_orders.csv`

The National Wages and Productivity Commission publishes every regional wage
order since 1989 as one PDF table. There is no API and no CSV. The 36 NCR
rows on page 1 were typed into `ncr_wage_orders.csv` by hand, one row per
wage order or tranche, with the source URL, page, and the PDF's SHA-256 on
every row.

`ingest_wage_rice.py` downloads the PDF on every run, compares its hash with
the CSV, and, when Ghostscript (`gs`) is installed, compares each NCR row's
effective year and top-of-range total with the PDF text. Without `gs` the
row check prints `SKIPPED`.

**Known limitations:** NWPC replaces the PDF, under a new filename, with
every update, so the URL above will go stale. The re-transcription steps are
in [WAGE-RICE.md](./WAGE-RICE.md).

---

## Week 2 decision

- **Primary source:** World Bank API
- **Fallback source:** PSA Family Income and Expenditure Survey
