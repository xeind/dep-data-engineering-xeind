-- Business question
-- Whose years were actually better to live through? Compare real growth,
-- inflation, and remittance dependency across every administration from
-- 1960 to 2025.
--
-- Total real change is measured against the year BEFORE the term starts,
-- so a president is not credited with the level they inherited. Garcia is
-- null for that column because 1959 is outside the dataset. That gap is
-- left visible rather than filled.
--
-- A year is credited to whoever held office for most of it. Ties, where a
-- handover fell on June 30, go to the outgoing president, since that year's
-- budget was set under them. See docs/SCHEMA.md.

WITH term_stats AS (
    SELECT
        p.president,
        p.start_year,
        p.end_year,
        COUNT(i.year)           AS years_in_data,
        AVG(i.gdp_growth_pct)   AS avg_growth,
        AVG(i.inflation)        AS avg_inflation,
        AVG(i.remittances)      AS avg_remittances
    FROM presidencies p
    JOIN indicators i ON i.year BETWEEN p.start_year AND p.end_year
    GROUP BY p.president, p.start_year, p.end_year
)
SELECT
    t.president,
    t.start_year || '-' || t.end_year      AS term,
    t.years_in_data,
    ROUND(t.avg_growth, 2)                 AS avg_annual_gdp_growth_pct,
    ROUND(
        (SELECT gdp_per_capita_const FROM indicators WHERE year = t.end_year) * 100.0
      / (SELECT gdp_per_capita_const FROM indicators WHERE year = t.start_year - 1)
      - 100
    , 1)                                   AS total_real_gdp_per_capita_change_pct,
    ROUND(t.avg_inflation, 1)              AS avg_inflation_pct,
    ROUND(t.avg_remittances, 2)            AS avg_remittances_pct_gdp
FROM term_stats t
ORDER BY t.start_year;
