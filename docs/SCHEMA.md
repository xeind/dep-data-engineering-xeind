# Schema

`data/processed/indicators.csv` — one row per year, 1960–2025, 66 rows.
Produced by `scripts/transform.py` from `data/raw/world_bank_ph_indicators.json`.

## Key

| Column | Type | Description |
|---|---|---|
| `year` | int | Primary key. Complete and gap-free, 1960–2025. |

## Source columns

Pulled directly from the World Bank API, one column per indicator. Column
names, labels, and units are defined once in `scripts/indicators.py`.

| Column | World Bank code | Unit | Observed | Span |
|---|---|---|---:|---|
| `gdp_per_capita_const` | `NY.GDP.PCAP.KD` | US$ (2015) | 66 | 1960–2025 |
| `gdp_per_capita_current` | `NY.GDP.PCAP.CD` | US$ | 66 | 1960–2025 |
| `gni_per_capita_const` | `NY.GNP.PCAP.KD` | US$ (2015) | 66 | 1960–2025 |
| `life_expectancy` | `SP.DYN.LE00.IN` | years | 65 | 1960–2024 |
| `inflation` | `FP.CPI.TOTL.ZG` | % annual | 66 | 1960–2025 |
| `population` | `SP.POP.TOTL` | people | 66 | 1960–2025 |
| `unemployment` | `SL.UEM.TOTL.ZS` | % of labor force | 35 | 1991–2025 |
| `school_enrollment` | `SE.PRM.ENRR` | % gross | 50 | 1971–2024 |
| `gini` | `SI.POV.GINI` | index 0–100 | 14 | 1985–2023 |
| `remittances` | `BX.TRF.PWKR.DT.GD.ZS` | % of GDP | 49 | 1977–2025 |
| `health_expenditure` | `SH.XPD.CHEX.GD.ZS` | % of GDP | 24 | 2000–2023 |
| `household_consumption` | `NE.CON.PRVT.ZS` | % of GDP | 45 | 1981–2025 |

## Derived columns

Computed in `transform.py`. These do not exist in the source.

| Column | Unit | How it is computed |
|---|---|---|
| `gdp_growth_pct` | % | Year-over-year change in `gdp_per_capita_const`. |
| `gdp_index_1960` | index | `gdp_per_capita_const` / its 1960 value × 100. |
| `life_expectancy_gain` | years | `life_expectancy` minus its 1960 value. |
| `cpi_index_2024` | index | Cumulative product of `1 + inflation/100`, rebased so 2024 = 100. |
| `peso100_in_2024_pesos` | pesos | `100 × cpi_2024 / cpi_year`. What ₱100 of that year's money is worth in 2024 pesos. |

`cpi_index_2024` and `peso100_in_2024_pesos` are what make peso comparisons
across 65 years honest. Without them, every "things were cheaper before"
claim is unadjusted and meaningless.

## Missing values

Empty cells are genuinely absent from the source, never imputed. See
[CLEANING-NOTES.md](./CLEANING-NOTES.md) for why each gap exists and how
analysis should treat it.

## Reference table

`data/reference/presidencies.csv` — one row per administration, 10 rows
covering 1960–2025. Hand-maintained, not pulled from any API. It exists so
SQL can group 66 annual rows into the political eras people actually argue
about.

| Column | Type | Description |
|---|---|---|
| `president` | text | Full name. |
| `start_year` | int | First year credited to this administration. |
| `end_year` | int | Last year credited to this administration. |

Joined to `indicators` on `year BETWEEN start_year AND end_year`.

### How years are assigned

The dataset is annual; Philippine terms start on 30 June. A year is credited
to whoever held office for **most** of it. Where a handover fell on 30 June
and the split is even, the year goes to the **outgoing** president, because
that year's national budget was enacted under them.

This rule, not vibes, is why 1992 sits with Aquino rather than Ramos and 2016
with Aquino III rather than Duterte. Any comparison across administrations
depends on it, so it is stated here rather than buried in a query.

Two boundary years are worth naming: Marcos Sr. is credited 1966–1985 because
he was deposed in February 1986, and Garcia's row has no total-change figure
in query 02 because that calculation needs 1959, which predates the dataset.

## Companion file

`data/processed/cleaning-report.json` records, per column, the observed and
missing counts, the observed span, the dtype, the exact missing years, and the
documented reason for the gap. It is generated, never hand-edited.

`data/processed/indicators.json` holds the same table shaped for the
dashboard: a `meta` block (source, pull timestamp, price base year, column
labels and units), a `years` array, and one array per column with `null` for
missing values.
