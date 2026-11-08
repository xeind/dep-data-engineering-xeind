# Stakeholder Brief

**Did the average Filipino's life actually get better between 1960 and 2025?**

For Filipinos wondering if progress is real: the tito who says *dati, mas
madali ang buhay*, the fresh grad weighing a job abroad, the OFW parent asking
if the sacrifice paid.

## Short answer

Mostly yes, and slower than next door. Income per person is 3.6 times its
1960 level, though the 1982 peak was not beaten until 2004. A day's minimum
wage buys more rice than in 1990, and infant deaths fell by two-thirds. Every
neighbour we compared did better: in 1960 the Philippines was second-richest
of the four with data (Vietnam's starts in 1984), and by 2025 it was the
poorest of all five.

## Five KPIs

| KPI | Baseline → latest | Verdict |
|---|---|---|
| Real GDP per capita | $1,124 (1960) → $4,066 (2025) | Improved |
| Infant deaths per 1,000 births | 62.3 (1960) → 21.7 (2024) | Mixed: fell 65%, flat since 2014 |
| Inequality (Gini, income) | 47.7 (2000) → 39.3 (2023) | Improved |
| Remittances, % of GDP | 1.5% (1977) → 8.5% (2025) | Mixed: peaked at 12.8% in 2005, falling since 2015 |
| Rice per day's NCR minimum wage | 10.4 kg (1990) → 16.2 kg (2025) | Improved, but no year from 2008 to 2024 matched 2002-2007 (15.1-15.8 kg); 2025 is one year of cheaper rice |

"Improved" means better over the whole series and over the last ten years.
A move under 5% counts as flat.

On inequality: the Gini fell from 47.7 in 2000 to 39.3 in 2023 on the income
basis. Before 2000 the World Bank measured how evenly households spend, not
how evenly they earn, so the 1985 reading of 41.0 does not compare with 2023.

## What segmentation shows

- **Eras.** Income grew fastest in 2010-2019, 4.66% a year. Health improved
  fastest in 1986-1997, when lifespan rose 3.74 years per decade while income
  grew 1.36% a year.
- **Birth cohorts.** For a Filipino born in 1975, income per person was only
  6.7% higher at age 20 than at birth, after six shrinking years. For one born
  in 2005 it was 99.5% higher, even with the 2020 crash.
- **Peers.** In 1960 the Philippines had the longest life expectancy of five
  neighbours, and its $1,124 per person sat close to Malaysia's $1,266. By
  2025 it was last on income, at $4,066 behind Vietnam's $4,308. By 2024 it
  was also last on life expectancy (69.9 years) and infant mortality (21.7).

## What this cannot say

- Every number except the rice ratio is a national average. None says how a
  given household, region or income group fared.
- Nothing here shows cause. The eras name who governed, and the data shows
  what changed during those years. It does not show who or what changed it.
  The gap with the neighbours is the same.
- The rice ratio covers NCR minimum-wage earners and regular-milled rice only.
  It leaves out workers paid below the minimum, other regions, and the rest
  of the grocery bill.

The full list of assumptions and gaps is in [LIMITATIONS.md](./LIMITATIONS.md).

## Where to look

- `notebooks/kpis.ipynb`: KPI definitions, calculations, trend charts,
  scorecard.
- `notebooks/segmentation.ipynb`: eras, birth cohorts, peer countries.
- `output/figures/`: every chart as a PNG (`kpi-*`, `seg-*`).
