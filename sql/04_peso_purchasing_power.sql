-- Business question
-- What is 100 pesos from any given year actually worth in 2024 money?
--
-- This is the tito-at-the-reunion claim, checked. "Dati, ang ₱100 kaya
-- bumili ng isang linggong ulam." The CPI chain in transform.py converts
-- every year onto one price base so the comparison is fair.
--
-- Landmark years only, to keep the answer readable. Nominal GDP per capita
-- sits beside it as a reminder that incomes rose too: the honest question
-- is not whether prices went up, but whether pay outran them.

SELECT
    year,
    ROUND(cpi_index_2024, 2)             AS cpi_index_2024_base,
    ROUND(peso100_in_2024_pesos, 0)      AS peso100_worth_in_2024_pesos,
    ROUND(inflation, 1)                  AS inflation_pct_that_year,
    ROUND(gdp_per_capita_const, 0)       AS real_gdp_per_capita_usd2015
FROM indicators
WHERE year IN (1960, 1970, 1980, 1984, 1986, 1990, 2000, 2010, 2020, 2024, 2025)
ORDER BY year;
