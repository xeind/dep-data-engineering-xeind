# Limitations

Read these before quoting any number from the notebooks or the
[stakeholder brief](./STAKEHOLDER-BRIEF.md). Per-table detail is in
[CLEANING-NOTES.md](./CLEANING-NOTES.md), [PEERS.md](./PEERS.md) and
[WAGE-RICE.md](./WAGE-RICE.md).

## Assumptions and limits

- **National averages hide distribution.** GDP per capita is total output
  divided by people. It says nothing about who got it. That is why the Gini
  index is a KPI, and why no conclusion rests on GDP growth alone.
- **No causality.** Eras carry political names, and peer countries carry
  their own histories. The data shows what changed and when. It does not show
  that any government, policy or event made the change.
- **The Gini series changes measure in 2000.** `SI.POV.GINI` for the
  Philippines comes from the PSA Family Income and Expenditure Survey. The
  World Bank Poverty and Inequality Platform (PIP) lists the 1985-1997
  readings as consumption-based and the 2000-2023 readings as income-based.
  Source request:
  `https://api.worldbank.org/pip/v1/pip?country=PHL&year=all&fill_gaps=false&format=json`.
  Income is spread less evenly than consumption, so no reading before 2000
  compares with any reading from 2000 on. The KPI verdict uses 2000-2023 only:
  the Gini fell from 47.7 in 2000 to 39.3 in 2023 on the income basis.
  PIP also publishes consumption Ginis for 2000-2023. They are a cross-check
  here, not a replacement series: 42.8 in 2000 to 35.2 in 2023, the same
  direction. PIP also flags changes in survey method in 2003 and 2015, so even
  the income readings are not strictly comparable across those years.
- **Peer Ginis use different bases.** PIP lists Thailand, Vietnam and
  Indonesia as consumption-based and Malaysia as income-based. The notebooks
  make no cross-country Gini comparison.
- **Gini has 14 readings, 1985-2023.** Surveys run about every three years.
  There is no Philippine Gini before 1985 in this source.
- **Life expectancy and infant mortality are modelled estimates.** They move
  smoothly from year to year and are published on a lag. Neither has a 2025
  value, for the Philippines or any peer.
- **Constant 2015 US dollars are not pesos.** GDP per capita is
  inflation-adjusted, but in dollars, so it also carries exchange-rate
  movement. It answers growth questions, not affordability questions.
- **The chained CPI is right for orders of magnitude, not exact pesos.**
  `cpi_index_2024` multiplies 66 annual inflation figures together. A revision
  to any early year moves every later value. "₱100 of 1960 money is about
  ₱14,142 in 2024" means the peso lost roughly two orders of magnitude, not
  14,142 exactly.
- **The 2.2% unemployment rate (2025) is not a fact about the job market.** It
  is an ILO-modelled estimate that excludes underemployment and much of the
  informal sector. No KPI or conclusion uses it.
- **Gross enrollment can exceed 100%.** It counts all enrolled pupils against
  the official-age population, so repeaters and over-age pupils push it past
  100. It measures access, not completion or quality.
- **The rice ratio is narrow.** It covers NCR only, where the minimum wage is
  the highest in the country. The minimum wage is a legal floor; some
  workers, mostly informal, earn below it. It uses regular-milled rice only,
  one food item, from 1990 only. PSA's rice price series changes in 2018, and
  the two series differ by up to 0.33 kg per day in the overlap years.
- **Peer coverage is uneven.** Vietnam's GDP per capita starts in 1984, its
  infant mortality in 1964, and its remittances cover only 2000-2004.
  Malaysia's remittances miss 1980-1986.
- **Nothing is imputed, smoothed or dropped.** Missing years stay missing.
  The 2021 lifespan drop and the 1984 inflation spike are real readings, kept
  as published.
- **Era and cohort boundaries are a judgement call.** Eras follow political
  and crisis breaks, not anything in the data. Other cuts give other era
  rates. The annual series underneath do not change.

## What this cannot answer

The project holds national annual data, plus one NCR wage-and-rice series. It
says nothing about:

- **Rent, land and house prices.** No series at any level.
- **Jeepney, bus and tricycle fares.** None.
- **Tuition.** Enrollment rates only, no cost.
- **The cost of living.** Rice in NCR from 1990 is the only price. There is
  no food basket.
- **Wages beyond the NCR minimum.** No average wage, no wage by sector, no
  regional minimum.
- **Region, class or household type.** No split of any kind.

Affordability ratios like rent over income or house price over annual income
need household data. The source for that is the PSA Family Income and
Expenditure Survey (https://psa.gov.ph/statistics/income-expenditure/fies).
It holds household income, spending and deciles.

FIES is not in the pipeline. When this was first tried, psa.gov.ph returned a
Cloudflare challenge to the pipeline; PSA's OpenSTAT API, which supplies the
rice prices, was reachable. FIES also runs by survey round, not every year,
and its files need manual download and cleaning. Until it is in, read every
finding as a statement about the country, never about a household.
