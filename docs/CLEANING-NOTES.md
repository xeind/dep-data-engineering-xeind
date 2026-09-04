# Cleaning Notes

What `scripts/transform.py` does to the raw data, what it deliberately does
not do, and which limitations any reader of the charts needs to know about.

## What the transform does

1. **Reads one raw snapshot.** `ingest.py` writes every indicator into a
   single timestamped JSON file with the request URLs attached, so any
   figure in this project can be traced back to a specific API call.
2. **Reshapes long to wide.** The API returns one record per year per
   indicator. The transform pivots this into one row per year and one
   column per indicator, over a fixed 1960–2025 index.
3. **Forces a complete year index.** Years with no observation still get a
   row, holding empty cells. This keeps gaps visible instead of letting a
   series silently skip years.
4. **Casts values to float.** The API returns numbers already; the cast
   guards against a string sneaking in and breaking arithmetic downstream.
5. **Adds derived columns.** Growth rate, index-to-1960, life-expectancy
   gain, and the CPI-based peso conversion. See [SCHEMA.md](./SCHEMA.md).
6. **Rounds to 4 decimals on write.** Enough precision for every chart here,
   and it keeps the CSV diff-friendly in git.

## What the transform deliberately does not do

- **No imputation.** Missing years stay missing. Filling the 1960–1984 Gini
  gap by interpolation would invent 25 years of inequality data that nobody
  measured. Charts show gaps as gaps.
- **No smoothing.** The 2021 life-expectancy crash and the 1984 inflation
  spike are real events, not noise to be averaged away.
- **No outlier removal.** The validator flags implausible values so a source
  change gets caught, but nothing is dropped automatically.
- **No currency conversion of the GDP series.** Those columns stay in the
  constant US dollars the World Bank publishes. The peso columns are a
  separate, clearly-labelled derivation from the CPI series.

## Known gaps and why they exist

| Column | Gap | Why |
|---|---|---|
| `gini` | Only 14 points, 1985–2023 | Comes from household surveys run every ~3 years, not annually. There is no Philippine Gini before 1985 in this source. |
| `health_expenditure` | Starts 2000 | The World Bank's health accounts series does not extend earlier. |
| `unemployment` | Starts 1991 | Modelled ILO estimate; earlier years are not published. |
| `household_consumption` | Starts 1981 | National accounts detail is unavailable before then. |
| `school_enrollment` | Starts 1971, gaps within | Reported irregularly by the education ministry. |
| `life_expectancy` | No 2025 value | Published on a longer lag than the economic series. |

## Limitations that affect the conclusions

These belong in any honest reading of the charts.

- **National averages hide distribution.** GDP per capita is total output
  divided by people. It says nothing about who received it. This is exactly
  why the Gini column is in the dataset, and why the analysis does not treat
  GDP growth alone as proof that life improved.
- **Reported unemployment is implausibly low.** The series sits at 2.2% for
  2023–2025. That is the ILO-modelled rate; it does not capture
  underemployment or the large informal sector, both of which matter far
  more for Filipino lived experience. Do not read low unemployment as a
  healthy job market.
- **Gross enrollment can exceed 100%.** It counts all enrolled pupils
  against the official-age population, so repeaters and over-age pupils push
  it above 100. It measures access, not completion or quality.
- **The CPI chain is only as good as its weakest year.** `cpi_index_2024` is
  a cumulative product across 66 annual inflation figures. Any revision to
  an early year shifts every later value. It is right for showing orders of
  magnitude, not for precise peso claims.
- **Constant 2015 US dollars are not pesos.** The GDP columns are already
  inflation-adjusted, but in dollars, so they also carry exchange-rate
  effects. The peso columns exist to answer affordability questions; the
  dollar columns answer growth questions. They should not be mixed.
- **2025 is partial for some indicators.** Life expectancy has no 2025
  value, and other 2025 figures may be revised.

## Reproducing

```
python scripts/ingest.py      # pull raw JSON from the World Bank API
python scripts/transform.py   # build indicators.csv + indicators.json
python scripts/validate.py    # 21 data quality checks, non-zero exit on failure
python scripts/query.py       # run sql/ against the processed table
```

`validate.py` is the gate: it checks the year index is complete, every
registered indicator has a column, the four core series each cover at least
60 years, every value sits inside a plausible range, population only
increases, and the CPI index rises monotonically and equals 100 in 2024.

`query.py` loads the processed CSV and the presidency lookup into an
in-memory SQLite database, runs every file in `sql/`, and writes
`output/query-results.md`. Nothing is stored as a `.db` file, so there is no
second copy of the data that can drift out of step with the CSV.

`transform.py` and `query.py` both produce byte-identical output on repeated
runs. The only thing that changes between runs is the raw snapshot, and only
when `ingest.py` is run again.
