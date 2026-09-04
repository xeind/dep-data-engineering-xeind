-- Business question
-- Did each decade's economic growth come with real gains in how long
-- Filipinos live, and at what cost in prices?
--
-- This is the project question in its shortest form. GDP per capita is the
-- anchor line; life expectancy is the cheapest honest test of whether
-- ordinary life kept pace with it.
--
-- Life years gained is measured from the first to the last observed value
-- inside each decade, not MAX minus MIN, so the 2021 COVID fall stays
-- visible instead of being flattened away.

WITH decade_years AS (
    SELECT
        (year / 10) * 10 AS decade_start,
        year,
        gdp_per_capita_const,
        gdp_growth_pct,
        life_expectancy,
        inflation
    FROM indicators
),
life_bounds AS (
    SELECT
        decade_start,
        MIN(CASE WHEN life_expectancy IS NOT NULL THEN year END) AS first_year,
        MAX(CASE WHEN life_expectancy IS NOT NULL THEN year END) AS last_year
    FROM decade_years
    GROUP BY decade_start
)
SELECT
    b.decade_start || 's'                            AS decade,
    ROUND(AVG(d.gdp_per_capita_const), 0)            AS avg_gdp_per_capita_usd2015,
    ROUND(AVG(d.gdp_growth_pct), 2)                  AS avg_annual_growth_pct,
    ROUND(AVG(d.inflation), 1)                       AS avg_inflation_pct,
    ROUND(
        (SELECT life_expectancy FROM indicators WHERE year = b.last_year)
      - (SELECT life_expectancy FROM indicators WHERE year = b.first_year)
    , 1)                                             AS life_years_gained
FROM decade_years d
JOIN life_bounds b ON b.decade_start = d.decade_start
GROUP BY b.decade_start
ORDER BY b.decade_start;
