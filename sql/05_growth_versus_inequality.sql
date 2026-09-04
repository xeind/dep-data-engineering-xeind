-- Business question
-- The economy grew. For whom?
--
-- Gini only exists for 14 survey years between 1985 and 2023, so this pairs
-- each survey year with the real GDP per capita of that same year and the
-- change since the previous survey. Missing years are not interpolated;
-- there is simply no Philippine Gini before 1985 in this source.
--
-- If GDP per capita climbs while Gini refuses to fall, growth stayed at the
-- top and "life got better" is not a clean yes.

WITH surveys AS (
    SELECT
        year,
        gini,
        gdp_per_capita_const,
        LAG(year)                 OVER (ORDER BY year) AS prev_year,
        LAG(gini)                 OVER (ORDER BY year) AS prev_gini,
        LAG(gdp_per_capita_const) OVER (ORDER BY year) AS prev_gdp
    FROM indicators
    WHERE gini IS NOT NULL
)
SELECT
    year                                              AS survey_year,
    prev_year                                         AS previous_survey,
    ROUND(gini, 1)                                    AS gini,
    ROUND(gini - prev_gini, 1)                        AS gini_change,
    ROUND(gdp_per_capita_const, 0)                    AS real_gdp_per_capita_usd2015,
    ROUND((gdp_per_capita_const / prev_gdp - 1) * 100, 1) AS real_gdp_change_pct
FROM surveys
ORDER BY year;
