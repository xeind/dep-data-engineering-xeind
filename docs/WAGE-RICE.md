# Wage-Rice Series

How many kilos of regular-milled rice one day of the Metro Manila minimum wage
buys, each year from 1990 to 2025. It tests the claim "dati, mas madali ang
buhay" in a unit anyone can picture.

Output: `data/processed/wage_rice.csv`, one row per year, 36 rows.

## How To Run

```bash
python scripts/ingest_wage_rice.py      # PSA API snapshot, NWPC PDF, transcription check
python scripts/transform_wage_rice.py   # build data/processed/wage_rice.csv
python scripts/validate_wage_rice.py    # 18 checks, non-zero exit on any failure
```

`ingest_wage_rice.py` needs network access. Its transcription check needs
Ghostscript (`gs`) on the PATH. Without `gs` it prints `SKIPPED` and checks
only the PDF hash.

## Columns

| Column | Type | Description |
|---|---|---|
| `year` | int | Primary key, 1990-2025, complete. |
| `ncr_min_wage_daily` | float | NCR daily minimum wage, non-agriculture, top of range, basic plus COLA, day-weighted annual average. PHP, 2 decimals. |
| `rice_regular_milled_ncr` | float | PSA annual average retail price of regular-milled rice in NCR. PHP per kg, as published. |
| `rice_kg_per_day_wage` | float | `ncr_min_wage_daily / rice_regular_milled_ncr`, 4 decimals. |
| `rice_price_series` | str | PSA table that supplied the rice price for that year. |
| `rice_months_reported` | int | Months with a PSA price that year, out of 12. |

## Sources

| Input | Source | Years used | How it arrives |
|---|---|---|---|
| Rice, old series | PSA OpenSTAT `2M/RP/0042M4ARP01`, "Regular Milled Rice (RMR)", NCR (`13`) | 1990-2017 | PXWeb API, scripted |
| Rice, 2018-based series | PSA OpenSTAT `2M/2018NEW/0042M4ARN01`, "RICE, REGULAR-MILLED, 1 KG", NCR (`130000000`) | 2018-2025 | PXWeb API, scripted |
| NCR wage orders | NWPC, *Daily Minimum Wage Rates per Wage Order by Region, Non-Agriculture, 1989 - September 2, 2026*, page 1 ([PDF](https://nwpc.dole.gov.ph/wp-content/uploads/2026/09/Summary-of-DMWR-per-Wage-Order-by-Region_Non-Agriculture-1989-to-Sep_2_2026-1.pdf)) | RA 6727 (1 Jul 1989) to WO NCR-26 (18 Jul 2025) | Hand-transcribed CSV, checked by script |

Raw files in `data/raw/`:

- `psa_rice_prices.json`: both PSA responses exactly as returned (NCR, RMR,
  every year, every month plus the annual figure), with the table metadata,
  POST queries, URLs and UTC pull time.
- `ncr_wage_orders.csv`: one row per wage order or tranche, with source URL,
  page and the PDF's SHA-256 on every row.
- `nwpc_daily_minimum_wage_non_agriculture_2026-09-02.pdf`: the PDF the CSV
  was transcribed from, downloaded on every ingest.

PSA's API was reachable, so the FAO GIEWS mirror (backup source R4 in the
research notes) is not used.

## Manual Steps

1. **Wage-order transcription.** The 36 NCR rows on page 1 of the NWPC PDF
   were typed into `ncr_wage_orders.csv`: order, tranche, issued date,
   effective date, basic low/high, allowance (COLA), total low/high. Values
   are as printed, dates converted to ISO. Tranches without their own
   order number in the PDF carry the order they belong to and a blank
   issued date, as printed.
2. **Re-transcription when NWPC updates the PDF.** The filename changes with
   each update. Check the index page linked in `ingest_wage_rice.py`, update
   `WAGE_PDF_URL` and `WAGE_PDF_FILE`, add the new rows, and replace
   `source_sha256`. Ingest fails until the hash and the rows match.

Ingest guards the transcription two ways. It compares the downloaded PDF's
SHA-256 with the hash in the CSV, and it extracts the PDF text with
Ghostscript and compares (effective year, top-of-range total) row by row
with the CSV. Both passed on 2026-10-05: 36 of 36 rows.

## Method

**Wage.** Each day of the year carries the top-of-range TOTAL of the latest
order in force on that day, effective date inclusive. The annual figure is
the mean over all days of the year, 365 or 366. Example, 2025: P645 for 198
days, then P695 from 18 July for 167 days, gives P667.88.

**Rice.** The annual figure is PSA's published annual average, not a mean
recomputed from the months. They differ in some years (1995: published
15.80, mean of the 12 monthly cells 15.68; 2015: published 36.69, mean of the
10 reported months 36.91). PSA's figure is the official one.

**Ratio.** Computed from the two rounded columns, so it recomputes exactly
from the CSV.

Nothing is imputed, smoothed or deflated. Kilos of rice is already a real
measure.

## Pitfalls Handled

| Pitfall | Handling |
|---|---|
| Wage orders take effect mid-year | Day-weighted annual average, as above. |
| NCR wage is a range from WO NCR-07 (Oct 1999) | Top of range: the non-agriculture rate. The bottom covers agriculture and small retail, service and manufacturing firms. |
| COLA paid on top of basic wage (Nov 2001 - Aug 2007, Jun - Aug 2008, May 2011 - Nov 2018) | TOTAL column, which includes the allowance. Validation checks top total = top basic + allowance on every row. |
| COLA folded into basic pay (Aug 2007, Aug 2008, Jan 2014, Nov 2018) | No special case. TOTAL stays continuous across integration. |
| Regular-milled vs well-milled | Regular-milled only. Commodity codes are checked against their labels on every pull, so a PSA recode fails ingest. |
| Item names differ between PSA tables | Mapped explicitly in `RICE_TABLES` in `ingest_wage_rice.py`. |
| PSA rejects the Python default user agent (HTTP 403) | Requests send a named project user agent. It identifies the project and does not imitate a browser. |
| PXWeb JSON starts with a UTF-8 byte order mark | Decoded as `utf-8-sig`. |
| NWPC server cut a PDF download short with HTTP 200 (130,854 of 210,813 bytes on 2026-10-05) | Body length checked against `Content-Length`. Short reads retry. |
| Flat NCR prices: 18.00 in 1998-2001, 30.00 in 2010-2012 | Kept as published. Monthly cells are flat too (every month 18.00 or 30.00), so the flat annual figure is what PSA recorded. This looks like administered or NFA-anchored pricing and is a limit, not a fix. |
| PSA missed months in 2015 (Nov, Dec) and 2016 (May, Jun) | Published annual kept. `rice_months_reported` shows 10. Validation fails any year under 10. |
| WO NCR-27 (Jul 2026) stalled by court order | In the CSV for completeness, outside the series. Series ends at 2025. |
| WO NCR-12 bottom of range misprinted (288.00 + 50.00 shown as 313.00) | Transcribed as printed, noted in the row. Only the top of range is used, and it adds up. |

## The 2018 Join

The old PSA series covers 1990-2020. The 2018-based series starts in 2018.
They disagree in the overlap:

| Year | Old series | 2018-based | Kg per day, old | Kg per day, 2018-based |
|---|---:|---:|---:|---:|
| 2018 | 40.01 | 39.01 | 12.87 | 13.20 |
| 2019 | 37.84 | 37.44 | 14.19 | 14.34 |
| 2020 | 36.83 | 37.22 | 14.58 | 14.43 |

Decision: old series for 1990-2017, 2018-based series from 2018. The join
sits at the first year of the new series, so each series covers one
unbroken block of years. The 2018-based series is the one PSA maintains,
and it has all 12 months in 2018-2020. The old series is missing October
2020 and has only one month of 2021. The `rice_price_series` column shows
which table each year uses. Validation fails if any year breaks the rule.

Effect: within 0.33 kg per day in any overlap year. The research spot check
for 2020 (14.6) used the old series, so this table shows 14.43.

## Limits

- **NCR only.** Wages and rice prices in other regions differ. The NCR wage
  is the highest in the country.
- **Minimum-wage earners, not the average Filipino.** The legal minimum is a
  floor that many workers earn more than, and that some, mostly informal,
  workers do not get at all. Compliance has never been complete.
- **Regular-milled rice only.** Not well-milled, not special, not NFA rice.
  Well-milled runs about P4-8 per kg higher.
- **One commodity.** Rice is the staple, but a household buys more than rice.
  This series does not stand in for the cost of living.
- **Starts in 1990.** PSA's machine-readable rice prices start in 1990.
  Earlier years need scanned yearbooks (see the research notes) and are not
  in this table.
- **A day's wage, not a month's.** Days worked per month and days paid are
  out of scope.

## Spot Checks

Research values from `research/wage-rice-sources.md` against this table:

| Year | Wage | Rice | Kg per day | Research |
|---|---:|---:|---:|---:|
| 1990 | 91.84 | 8.86 | 10.37 | 10.4 |
| 2000 | 227.92 | 18.00 | 12.66 | 12.7 |
| 2010 | 393.09 | 30.00 | 13.10 | 13.1 |
| 2020 | 537.00 | 37.22 | 14.43 | 14.6 (old series) |
| 2025 | 667.88 | 41.17 | 16.22 | 16.2 |
