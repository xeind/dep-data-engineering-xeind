-- Business question
-- Did remittances rise because life improved, or because families needed
-- someone abroad to survive?
--
-- If remittances climb while domestic growth stalls, money sent home is
-- filling a gap rather than marking success. Household consumption as a
-- share of GDP shows how much of the economy is families spending to get by.

SELECT
    (((year / 10) * 10) || 's')              AS decade,  -- parens: || binds tighter than * in SQLite
    COUNT(remittances)                       AS years_observed,
    ROUND(AVG(remittances), 2)               AS avg_remittances_pct_gdp,
    ROUND(AVG(gdp_growth_pct), 2)            AS avg_gdp_growth_pct,
    ROUND(AVG(unemployment), 2)              AS avg_unemployment_pct,
    ROUND(AVG(household_consumption), 1)     AS avg_household_consumption_pct_gdp
FROM indicators
WHERE remittances IS NOT NULL
GROUP BY year / 10
ORDER BY year / 10;
