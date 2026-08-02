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


def column_name(code):
    return INDICATORS[code][0]


def label(code):
    return INDICATORS[code][1]


def unit(code):
    return INDICATORS[code][2]
