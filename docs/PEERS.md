# Peer Countries

`data/processed/peers.csv` puts the Philippines beside four Southeast Asian
neighbours. The main table can show that Filipino life changed since 1960;
this table shows whether it changed more or less than it did next door.

## Why these four

Thailand, Vietnam, Indonesia, and Malaysia share the region, a colonial or
wartime past, and a mostly farm-based economy in 1960. All five were poor
by world standards that year. They then took different paths, which is what
makes the comparison useful.

They did not start level. GDP per capita in constant 2015 US$:

| Country | 1960 | 2025 | 2025 ÷ first year |
|---|---:|---:|---:|
| Philippines | 1,124 | 4,066 | 3.6× |
| Malaysia | 1,266 | 12,352 | 9.8× |
| Thailand | 592 | 6,783 | 11.4× |
| Indonesia | 598 | 4,555 | 7.6× |
| Vietnam | no value (1984: 595) | 4,308 | 7.2× from 1984 |

In 1960 the Philippines stood close to Malaysia and about twice as rich as
Thailand and Indonesia. By 2025 it had the lowest GDP per capita of the
five. Any chart built on this table should state the starting gap, or the
1960 head start disappears from view.

## Coverage

First year, last year, and observed count, over 1960–2025 (66 years).

| Column | Philippines | Thailand | Vietnam | Indonesia | Malaysia |
|---|---|---|---|---|---|
| `gdp_per_capita_const` | 1960–2025 (66) | 1960–2025 (66) | 1984–2025 (42) | 1960–2025 (66) | 1960–2025 (66) |
| `life_expectancy` | 1960–2024 (65) | 1960–2024 (65) | 1960–2024 (65) | 1960–2024 (65) | 1960–2024 (65) |
| `infant_mortality` | 1960–2024 (65) | 1960–2024 (65) | 1964–2024 (61) | 1960–2024 (65) | 1960–2024 (65) |
| `gini` | 1985–2023 (14) | 1981–2024 (30) | 1992–2022 (13) | 1984–2025 (33) | 1984–2021 (14) |
| `remittances` | 1977–2025 (49) | 1975–2025 (51) | 2000–2004 (5) | 1983–2025 (43) | 1975–2024 (43) |
| `gdp_index_1960` | 1960–2025 (66) | 1960–2025 (66) | empty | 1960–2025 (66) | 1960–2025 (66) |

Column names, labels, and units are the ones in `scripts/indicators.py`.
`gdp_index_1960` is each country's `gdp_per_capita_const` divided by its own
1960 value, × 100.

## Gaps and why they exist

Nothing is imputed. An empty cell is a year the source did not measure.

| Gap | Why |
|---|---|
| Vietnam `gdp_per_capita_const` before 1984 | The World Bank national accounts for Vietnam start in 1984. |
| Vietnam `gdp_index_1960`, all years | No 1960 GDP value to index against. The column stays empty rather than rebase to 1984, so every value in it means "1960 = 100". |
| Vietnam `infant_mortality` before 1964 | The UN inter-agency estimate for Vietnam starts in 1964. |
| Vietnam `remittances` outside 2000–2004 | The World Bank carries only these five years. The US$ series (`BX.TRF.PWKR.CD.DT`) has the same five, so the gap is in the source, not in the percent-of-GDP calculation. |
| Malaysia `remittances` 1980–1986 | Missing in the source inside an otherwise continuous series. |
| `gini`, every country | Household surveys every few years, not annual. Spans also differ by country, so compare survey years, not a continuous line. |
| `life_expectancy`, `infant_mortality` in 2025 | Published on a lag; no 2025 value yet for any country. |
| `remittances` before the mid-1970s or 1980s | Balance-of-payments reporting starts later than the national accounts. |

## How to run

```
python scripts/ingest_peers.py      # pull raw JSON for 5 countries x 5 indicators
python scripts/transform_peers.py   # build data/processed/peers.csv
python scripts/validate_peers.py    # 7 checks, non-zero exit on failure
```

`validate_peers.py` reads `data/processed/indicators.csv` too, so run the
main pipeline first. It checks that the country set is exact, each country
has every year once, the value columns match the registry, no value is
negative, and the Philippine rows equal the main table on every shared
column. If that last check fails, the World Bank revised a series between
the two pulls. Rerun both ingests.
