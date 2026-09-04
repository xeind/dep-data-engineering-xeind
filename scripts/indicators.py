"""
Single source of truth for the World Bank indicators this project uses.

Both ingest.py and transform.py import from here so the raw pull, the
processed columns, and the docs can never drift apart.
"""

COUNTRY_CODE = "PH"
START_YEAR = 1960
END_YEAR = 2025

# code -> (column name, human label, unit)
INDICATORS = {
    "NY.GDP.PCAP.KD": ("gdp_per_capita_const", "GDP per capita, constant 2015 US$", "US$ (2015)"),
    "NY.GDP.PCAP.CD": ("gdp_per_capita_current", "GDP per capita, current US$", "US$"),
    "NY.GNP.PCAP.KD": ("gni_per_capita_const", "GNI per capita, constant 2015 US$", "US$ (2015)"),
    "SP.DYN.LE00.IN": ("life_expectancy", "Life expectancy at birth, total", "years"),
    "FP.CPI.TOTL.ZG": ("inflation", "Inflation, consumer prices", "% annual"),
    "SP.POP.TOTL": ("population", "Population, total", "people"),
    "SL.UEM.TOTL.ZS": ("unemployment", "Unemployment, total", "% of labor force"),
    "SE.PRM.ENRR": ("school_enrollment", "School enrollment, primary, gross", "% gross"),
    "SI.POV.GINI": ("gini", "Gini index", "index 0-100"),
    "BX.TRF.PWKR.DT.GD.ZS": ("remittances", "Personal remittances, received", "% of GDP"),
    "SH.XPD.CHEX.GD.ZS": ("health_expenditure", "Current health expenditure", "% of GDP"),
    "NE.CON.PRVT.ZS": ("household_consumption", "Household final consumption expenditure", "% of GDP"),
}

# The anchor line for the whole project. GDP says the country got richer —
# every other column exists to test whether ordinary life kept pace.
ANCHOR = "gdp_per_capita_const"

# Why each sparse column is sparse. Every gap in the processed table is a year
# the source never measured, so each one needs a stated reason rather than an
# imputed value. validate.py fails if a column has gaps and no entry here,
# which stops an undocumented gap reaching analysis.
GAP_REASONS = {
    "life_expectancy": "Published on a longer lag than the economic series; no 2025 value yet.",
    "unemployment": "ILO-modelled estimate; the World Bank does not publish it before 1991.",
    "school_enrollment": "Reported irregularly by the education ministry, with gaps within the span.",
    "gini": "Household surveys run roughly every 3 years; no Philippine figure exists before 1985.",
    "remittances": "Balance-of-payments reporting of worker remittances begins in 1977.",
    "health_expenditure": "The World Bank health accounts series does not extend before 2000.",
    "household_consumption": "National accounts detail is unavailable before 1981.",
    # Derived columns lose their first year by construction, not by missing data.
    "gdp_growth_pct": "Year-over-year change, so 1960 has no prior year to compare against.",
    "life_expectancy_gain": "Derived from life_expectancy and inherits its missing 2025 value.",
}


def column_name(code):
    return INDICATORS[code][0]


def label(code):
    return INDICATORS[code][1]


def unit(code):
    return INDICATORS[code][2]
