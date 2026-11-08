# 1960 vs 2025: Who Had It Better?

## Thought Process

I'm still figuring out what exactly I want to build. But here's where my head is at.

Johnny Harris did this thing - [1955 vs 2025: Who had it better in the US?](https://www.youtube.com/watch?v=J4qqIJ312zI). He stacked decades of data on GDP, wages, housing, inflation, and asked: did life actually improve? The format is simple: one question and the numbers, no 30-dropdown dashboards.

Every older Filipino I know says the same thing: *"Dati, mas madali ang buhay."* My grandparents. The tindera sa kanto. Every tito at the family reunion talking about how his first salary bought a full week of groceries and may sukli pa. *"Kami noon, nakabili na ng bahay at lupa sa first job pa lang."* *"Kayo kasi, ang lapit lang naka-Grab pa."* Before, life was easier. Pero totoo ba? Or is that just nostalgia with a side of *"kayo kasi, puro kayo Grab at Shopee"*?

So I started pulling data. World Bank API goes back to 1960 for the Philippines. GDP, life expectancy, inflation, inequality, remittances, internet access. And now I'm wondering: **could you actually build one timeline that lets you see Filipino quality of life unfold across 65 years?**

What I'm imagining: zoom into any year - 1980, 1997, 2010 - and see what life looked like. GDP was X. Life expectancy was Y. A jeepney ride cost Z. OFW remittances were surging (or not yet). The internet was still a decade away. Martial Law just ended (or was still happening). Toggle between presidencies. Compare Marcos Sr.'s GDP numbers against Cory's. Turn on Internet Era and watch what changed after 1994. Turn on OFW Boom and see remittances track against GDP.

The graph would be one 65-year timeline with layers you can toggle: GDP as the default line, then overlay life expectancy, inflation, inequality. Color-coded presidency bands in the background. Event markers for Martial Law, EDSA, Asian Financial Crisis, COVID. Era toggles that gray out sections of the timeline so you can see "before internet" vs "after internet" side by side.

I don't know if I can get all the data I want. Land prices from 1970? Probably not. What a jeepney ride cost in 1985? Unlikely. But maybe what World Bank gives me is enough: 11 indicators, 65 years, free. And if I'm upfront about the gaps, the project still works.

The question I keep coming back to: **did the average Filipino's life actually get better?** I mean more than GDP: health, education, opportunity, and who got them.

I'm not sure yet. That's what the project is supposed to figure out.

---

## Problem Statement

I want to answer: "**Did the average Filipino's life actually get better between 1960 and 2025?**"

GDP went up, pero *sino ang yumaman?* Did health, education, purchasing power, and the ability to actually afford rent and still have savings improve at the same pace? Or did the line go up for the top 1% and stay flat for everyone else?

## Audience

This project is for **Filipinos wondering if progress is real**. Anyone asking whether their parents had it easier, whether it's still worth having kids *in this economy*, or whether *"mahirap na talaga ngayon"* is a feeling or a fact. Your tito at the family reunion who won't stop talking about how ₱100 used to feed a whole barangay. The fresh grad deciding between staying in PH or taking that JO abroad. The OFW parent asking if the sacrifice was worth it. Anyone who has ever looked at a payslip and thought *"saan napupunta yung tax ko?"*

## KPI or Key Metric

The main metric I want to track is **Real GDP per capita over time**. But GDP alone is lazy, so four more KPIs sit beside it. Each one tests GDP from a different side: survival, distribution, dependence on work abroad, and what a day's pay buys.

| KPI | Column | Unit | Better is | First value | Latest value |
|---|---|---|---|---|---|
| Real GDP per capita | `gdp_per_capita_const` | constant 2015 US$ | up | 1,124 (1960) | 4,066 (2025) |
| Infant mortality | `infant_mortality` | deaths per 1,000 live births | down | 62.3 (1960) | 21.7 (2024) |
| Inequality (Gini) | `gini` | index 0–100 | down | 41.0 (1985) | 39.3 (2023) |
| Remittances | `remittances` | % of GDP | read with care | 1.5 (1977) | 8.5 (2025) |
| Kilos of rice per day's NCR minimum wage | `rice_kg_per_day_wage` | kg | up | 10.37 (1990) | 16.22 (2025) |

The Gini series changes basis in 2000, from consumption to income, so 1985 and 2023 are not directly comparable; within the income basis it fell from 47.7 (2000) to 39.3 (2023). Remittances have no clean "better" direction. A high share can mean families are doing well abroad, or that home cannot employ them. The first four come from `data/processed/indicators.csv`; the rice KPI comes from `data/processed/wage_rice.csv`. [`notebooks/kpis.ipynb`](notebooks/kpis.ipynb) builds the KPI charts.

## Comparison Approach

I want to copy the logic of the Johnny Harris format, not the exact US metrics:

> GDP says the country got richer. But did ordinary life actually get easier?

So GDP per capita becomes the anchor line, then I compare it against lived-reality indicators. For the Philippines, that means asking questions like:

- How many kilos of rice could one day of work buy?
- Did household consumption improve as GDP grew?
- Did inequality fall, or did growth mostly stay at the top?
- Did remittances rise because life improved, or because families needed someone abroad to survive?
- Did health and education outcomes improve enough to say life got better?

The comparison needs two layers:

1. **Official progress:** real GDP per capita over time.
2. **Lived progress:** what a Filipino worker or household could actually afford, access, or survive through in the same year.

If GDP rises but purchasing power, inequality, or remittance dependency gets worse, the answer is a qualified yes: life improved in some ways, but not evenly and not for everyone.

## Fair Comparison Notes

I don't want to define "the average Filipino" carelessly because that can hide too much. A national average can blur class, region, household size, and whether a family has OFW income.

So the first fair version should compare three profiles:

1. **Minimum-wage worker** - useful for basic purchasing power: rice, transport, food, electricity, and other daily costs.
2. **Middle-income household** - useful for the Harris-style lifestyle comparison: rent, food, education, healthcare, savings, and stability.
3. **National average** - useful for macro indicators like GDP per capita, life expectancy, inflation, and household consumption.

For a "middle-class Filipino," I should not define it by vibes. The cleanest approach is to use income position:

- Prefer official household income data, like FIES income deciles or quintiles.
- If I need a class threshold, use a poverty-threshold-based definition from Philippine policy research and clearly state the multiplier.
- Keep household size explicit, probably a family of five when comparing against PSA-style poverty and income thresholds.

Money should be adjusted into **constant pesos** so years are comparable. For now, **2024 pesos** makes the most sense because many confirmed indicators currently run through 2024. If reliable full-year 2025 CPI, wage, and price data are available later, I can switch to 2025 pesos.

The basic conversion is:

> value in 2024 pesos = historical value x (CPI in 2024 / CPI in historical year)

For lifestyle comparisons, ratios may be more honest than raw pesos:

- House price divided by annual household income
- Monthly rent divided by monthly household income
- Daily wage divided by price of 1 kg of rice
- Food basket cost divided by monthly income
- Health or out-of-pocket cost divided by income

Prices were lower before, of course. The better question is: **after adjusting for inflation and income, what could a Filipino household actually afford?**

## Likely Data Source

My primary source is the **World Bank API** (https://api.worldbank.org/v2/country/PH), which is free, requires no API key, and provides Philippines indicators such as GDP per capita, life expectancy, inflation, population, unemployment, inequality, remittances, health spending, and household consumption from 1960 onward.

My fallback source is the **Philippine Statistics Authority Family Income and Expenditure Survey (FIES)** (https://psa.gov.ph/statistics/income-expenditure/fies), which can support a narrower household affordability version of the project if the World Bank data is too broad for lived-cost analysis.

Two more sources now feed the pipeline:

- **World Bank API, peer countries.** The same core indicators for Thailand, Vietnam, Indonesia, and Malaysia, so the Philippine trend has something to compare against. See [`docs/PEERS.md`](docs/PEERS.md).
- **PSA OpenSTAT and NWPC.** NCR retail rice prices from the PSA OpenSTAT API (tables `0042M4ARP01` and `0042M4ARN01`), and NCR minimum wage orders hand-transcribed from the NWPC wage-order PDF. Together they give the kilos-of-rice KPI. See [`docs/WAGE-RICE.md`](docs/WAGE-RICE.md).

## Data Source Notes

### Primary Source

- **Name:** World Bank API - Philippines country indicators
- **URL:** https://api.worldbank.org/v2/country/PH/indicator/NY.GDP.PCAP.KD?format=json&per_page=100
- **Format:** JSON API
- **Coverage:** Philippines, annual data, 1960-2024 for the main time-series, with some indicators starting later
- **Why it fits:** This can answer the long-term national question: did GDP, health, education, inequality, remittances, and household consumption improve over time?
- **Known limitations:** World Bank can show the big-picture trend, but it does not fully answer lived affordability questions like rent, land prices, jeepney fares, tuition, or exact food-basket purchasing power.

Useful starting indicators:

| Indicator | World Bank Code | Why it matters |
|---|---:|---|
| GDP per capita, current US$ | `NY.GDP.PCAP.CD` | Main economic progress line |
| GDP per capita, constant 2015 US$ | `NY.GDP.PCAP.KD` | Better for real growth over time |
| Life expectancy | `SP.DYN.LE00.IN` | Health / survival progress |
| Inflation | `FP.CPI.TOTL.ZG` | Price pressure |
| Population | `SP.POP.TOTL` | Scale / context |
| Unemployment | `SL.UEM.TOTL.ZS` | Job market signal |
| School enrollment | `SE.PRM.ENRR` | Education access |
| Gini index | `SI.POV.GINI` | Inequality |
| Remittances, % of GDP | `BX.TRF.PWKR.DT.GD.ZS` | OFW dependency / support |
| Health expenditure, % of GDP | `SH.XPD.CHEX.GD.ZS` | Health system investment |
| Household consumption, % of GDP | `NE.CON.PRVT.ZS` | How much of the economy is household spending |
| Infant mortality, per 1,000 live births | `SP.DYN.IMRT.IN` | Child survival |
| Fertility rate, births per woman | `SP.DYN.TFRT.IN` | Family size |
| Access to electricity, % of population | `EG.ELC.ACCS.ZS` | Basic household services |
| Poverty headcount, national poverty lines | `SI.POV.NAHC` | Poverty by the national line (2015-2023 only) |

### Fallback Source

- **Name:** Philippine Statistics Authority Family Income and Expenditure Survey (FIES)
- **URL:** https://psa.gov.ph/statistics/income-expenditure/fies
- **Format:** Official PSA statistical release pages with downloadable household survey tables/files
- **Coverage:** Philippines household income and expenditure survey data, nationwide, reported by survey round instead of a full annual API series
- **Why it could still work:** If the World Bank API is too macro-level for the affordability question, FIES can still support a narrower version of the project focused on household income, spending, and living-standard trends.
- **Known limitations:** The PSA site is currently blocked by a Cloudflare challenge from this environment, the survey is less frequent than the World Bank annual series, and the files may need manual download and cleaning.

For Week 2, my committed plan is: **primary source = World Bank API**, **fallback source = PSA FIES**.

## How To Run

Needs Python 3.11 or later (pandas 3.0 requires it).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/run_pipeline.py --offline
```

That one command rebuilds every processed file from the raw snapshots in
`data/raw/` and runs every validation. It stops at the first step that fails
and names it.

| Command | What it does | Network |
|---|---|---|
| `python scripts/run_pipeline.py` | Pulls fresh data from every source, then rebuilds and validates | yes |
| `python scripts/run_pipeline.py --offline` | Skips the three ingest steps and rebuilds from `data/raw/` | no |
| `python scripts/run_pipeline.py --offline --notebooks` | Also re-executes the three notebooks in place, which re-exports the figures | no |

The raw snapshots are committed, so `--offline` reproduces every number in
this repo. All transform steps write byte-identical output on repeated runs.

### Step by step

The same run, one script at a time. Order matters. Each step reads what the
step before it wrote, and `validate_peers.py` also reads `indicators.csv`, so
the main pipeline goes first.

```bash
# Main: Philippines, 16 World Bank indicators, 1960-2025
python scripts/ingest.py               # 1. pull raw JSON from the World Bank API
python scripts/transform.py            # 2. build the clean dataset
python scripts/validate.py             # 3. 25 data quality checks
python scripts/query.py                # 4. answer the business questions in SQL

# Peers: the Philippines and 4 neighbours, 5 indicators, 1960-2025
python scripts/ingest_peers.py         # 5. pull raw JSON for 5 countries
python scripts/transform_peers.py      # 6. build peers.csv
python scripts/validate_peers.py       # 7. 7 checks

# Wage-rice: NCR minimum wage against the NCR rice price, 1990-2025
python scripts/ingest_wage_rice.py     # 8. PSA rice prices, NWPC PDF, transcription check
python scripts/transform_wage_rice.py  # 9. build wage_rice.csv
python scripts/validate_wage_rice.py   # 10. 18 checks

# Analysis, after the data steps
jupyter nbconvert --to notebook --execute --inplace notebooks/insights.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/segmentation.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/kpis.ipynb
```

Only the three ingest steps need the network. Skip them to work offline.

| Step | Reads | Writes |
|---|---|---|
| `ingest.py` | World Bank API, 16 indicators | `data/raw/world_bank_ph_indicators.json` |
| `transform.py` | the raw snapshot | `data/processed/indicators.csv`, `indicators.json`, `cleaning-report.json` |
| `validate.py` | `indicators.csv` | nothing; exits non-zero if a check fails |
| `query.py` | `indicators.csv` + `data/reference/presidencies.csv` | `output/query-results.md` |
| `ingest_peers.py` | World Bank API, 5 countries × 5 indicators | `data/raw/world_bank_peers.json` |
| `transform_peers.py` | the peers snapshot | `data/processed/peers.csv` |
| `validate_peers.py` | `peers.csv` + `indicators.csv` | nothing; exits non-zero if a check fails |
| `ingest_wage_rice.py` | PSA OpenSTAT API, NWPC PDF, `data/raw/ncr_wage_orders.csv` | `data/raw/psa_rice_prices.json`, the NWPC PDF |
| `transform_wage_rice.py` | `psa_rice_prices.json` + `ncr_wage_orders.csv` | `data/processed/wage_rice.csv` |
| `validate_wage_rice.py` | `wage_rice.csv` + `ncr_wage_orders.csv` | nothing; exits non-zero if a check fails |

`scripts/indicators.py` is not a step. It holds the 16 indicator codes,
column names, units, and gap reasons, and every other script imports it.

**Optional system dependency: Ghostscript (`gs`).** `ingest_wage_rice.py`
uses it to check the hand-transcribed wage orders against the PDF text, row
by row. Without `gs` that check prints `SKIPPED` and the script still checks
the PDF's SHA-256. No other step needs it.

### The validation gates

`validate.py` checks the year index is complete and typed as an integer,
every value column is a float, every registered indicator has a column, the
four core series each cover at least 60 years, every value sits in a
plausible range, population only ever increases, and the CPI index rises
monotonically and equals 100 in its base year. Two more checks guard the
documentation itself. Any column with gaps must have a stated reason in
`scripts/indicators.py`, and a reason for a column that no longer has gaps
is reported as stale.

`validate_peers.py` checks the country set, one row per country-year, the
column set, types, and that the Philippine rows equal `indicators.csv` on
every shared column. `validate_wage_rice.py` checks the wage orders add up
and run in date order, the year index is complete, the kilos figure
recomputes exactly from wage and price, and every rice price rests on at
least 10 monthly reports.

All 50 checks currently pass: 25 + 7 + 18.

## Datasets

| File | One row per | Key | Coverage | Documented in |
|---|---|---|---|---|
| `data/processed/indicators.csv` | year | `year` | 1960–2025, 66 rows × 21 columns | [`SCHEMA.md`](docs/SCHEMA.md), [`CLEANING-NOTES.md`](docs/CLEANING-NOTES.md) |
| `data/processed/indicators.json` | same table, shaped for the dashboard | `years` array | 1960–2025 | [`SCHEMA.md`](docs/SCHEMA.md) |
| `data/processed/peers.csv` | country-year | `country_code` + `year` | 5 countries × 1960–2025, 330 rows | [`SCHEMA.md`](docs/SCHEMA.md), [`PEERS.md`](docs/PEERS.md) |
| `data/processed/wage_rice.csv` | year | `year` | 1990–2025, 36 rows | [`SCHEMA.md`](docs/SCHEMA.md), [`WAGE-RICE.md`](docs/WAGE-RICE.md) |
| `data/processed/cleaning-report.json` | column of `indicators.csv` | column name | coverage and gap reason per column | [`CLEANING-NOTES.md`](docs/CLEANING-NOTES.md) |

Empty cells are years the source did not measure. Nothing is imputed.

## Outputs

| Output | Built by | What it shows |
|---|---|---|
| [`notebooks/insights.ipynb`](notebooks/insights.ipynb) | Jupyter | Five charts, each with Observation, Implication, and Possible Action |
| [`notebooks/segmentation.ipynb`](notebooks/segmentation.ipynb) | Jupyter | When the gains landed and who got them: eras, birth cohorts, peer countries |
| [`notebooks/kpis.ipynb`](notebooks/kpis.ipynb) | Jupyter | The five headline KPIs and a scorecard |
| `output/figures/01-*.png` to `05-*.png` | `insights.ipynb` | Exported charts |
| `output/figures/seg-*.png` | `segmentation.ipynb` | Exported charts |
| `output/figures/kpi-*.png` | `kpis.ipynb` | Exported charts |
| [`output/query-results.md`](output/query-results.md) | `query.py` | The five SQL answers |

The notebooks are committed with their outputs, so GitHub shows every chart
without running anything.

## Documentation

| Document | What it covers |
|---|---|
| [`docs/STAKEHOLDER-BRIEF.md`](docs/STAKEHOLDER-BRIEF.md) | The answer, for the audience above |
| [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) | What the data cannot say |
| [`docs/DATA-SOURCES.md`](docs/DATA-SOURCES.md) | Every source, endpoint, and table |
| [`docs/SCHEMA.md`](docs/SCHEMA.md) | Every column in every processed file |
| [`docs/CLEANING-NOTES.md`](docs/CLEANING-NOTES.md) | What the transforms do, what they refuse to do, and known gaps |
| [`docs/PEERS.md`](docs/PEERS.md) | Why these four countries, and their gaps |
| [`docs/WAGE-RICE.md`](docs/WAGE-RICE.md) | The wage-rice method, the manual transcription, and the 2018 series join |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Pipeline diagram, directory tree, design decisions |

## Questions Answered In SQL

`query.py` loads the processed table and the presidency lookup into an
in-memory SQLite database and runs every file in `sql/`. Results are written
to [`output/query-results.md`](output/query-results.md).

| Query | Business question |
|---|---|
| [`01_progress_by_decade.sql`](sql/01_progress_by_decade.sql) | Did each decade's growth come with real gains in how long Filipinos live, and at what cost in prices? |
| [`02_who_had_it_better_by_presidency.sql`](sql/02_who_had_it_better_by_presidency.sql) | Whose years were actually better to live through? |
| [`03_remittance_dependency.sql`](sql/03_remittance_dependency.sql) | Did remittances rise because life improved, or because families needed someone abroad? |
| [`04_peso_purchasing_power.sql`](sql/04_peso_purchasing_power.sql) | What is ₱100 from any given year worth in 2024 money? |
| [`05_growth_versus_inequality.sql`](sql/05_growth_versus_inequality.sql) | The economy grew. For whom? |

Three findings that shape the rest of the project:

- **₱100 in 1960 is worth about ₱14,142 in 2024 pesos.** The tito is right
  that prices exploded. Whether pay kept up is the separate question, and
  real GDP per capita did roughly triple over the same stretch.
- **The 1980s lost ground.** Average real growth of −0.6% a year with 15.6%
  inflation. It is the only decade in the dataset where the anchor line fell.
- **Remittances went from 1.7% of GDP in the 1970s to 11.2% in the 2000s**
  while growth stayed weak through the 1990s. Sending someone abroad looks
  more like a response to weak growth at home than a sign of success.

Each query file opens with a comment block stating its business question and
the judgement calls inside it. Every number above is regenerated by
`python scripts/query.py`; none are typed in by hand.

## Key Findings

Five charts with a written reading under each are in
[`notebooks/insights.ipynb`](notebooks/insights.ipynb). Exported figures are in
[`output/figures/`](output/figures/).

- **Income per person is 3.6 times its 1960 level**, $1,124 to $4,066 in
  constant 2015 US dollars. It took until 2004 to beat the 1982 level of $1,898.
- **The worst crashes cut income per person by more than 9%.** The three
  worst years are 2020 (−10.55%), 1984 (−9.69%) and 1985 (−9.37%).
- **Filipinos live 10.8 years longer than in 1960**, 59.2 to 69.9 years. Almost
  all of that came before 2015, and 2024 still sits below the 2020 peak of 70.1.
- **Remittances rose from 1.5% of GDP in 1977 to 8.5% in 2025**, after peaking
  at 12.8% in 2005.
- **Inequality fell from 47.7 in 2000 to 39.3 in 2023** on the World Bank's
  income-based Gini. Readings before 2000 measure consumption and do not
  compare directly.

The short answer: a person born now is better off than one born in 1960 on
income and lifespan, the two measures that reach back that far. Most of the
gain came before 2015. The notebook's inference section states what the data
cannot show, including cause.

## Possible Final Dashboard

The dashboard should let someone explore their own question. One 65-year timeline as the base. GDP is the default line. Toggle on life expectancy or inflation. Presidential eras appear as background bands. Event markers for recessions and crises. Era toggles: click "Internet Era" and the pre-1994 section grays out. Click "OFW Boom" and watch remittance lines against GDP. Pick any year - see what life was like. Pick two presidencies - see which had better numbers.
