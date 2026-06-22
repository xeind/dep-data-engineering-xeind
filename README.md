# 1960 vs 2025: Who Had It Better?

## Thought Process

I'm still figuring out what exactly I want to build. But here's where my head is at.

Johnny Harris did this thing - [1955 vs 2025: Who had it better in the US?](https://www.youtube.com/watch?v=J4qqIJ312zI). He stacked decades of data on GDP, wages, housing, inflation, and asked: did life actually improve? Simple format. No 30-dropdown dashboards. Just a question and the numbers.

Every older Filipino I know says the same thing: *"Dati, mas madali ang buhay."* My grandparents. The tindera sa kanto. Every tito at the family reunion talking about how his first salary bought a full week of groceries and may sukli pa. *"Kami noon, nakabili na ng bahay at lupa sa first job pa lang."* *"Kayo kasi, ang lapit lang naka-Grab pa."* Before, life was easier. Pero totoo ba? Or is that just nostalgia with a side of *"kayo kasi, puro kayo Grab at Shopee"*?

So I started pulling data. World Bank API goes back to 1960 for the Philippines. GDP, life expectancy, inflation, inequality, remittances, internet access. And now I'm wondering: **could you actually build one timeline that lets you see Filipino quality of life unfold across 65 years?**

What I'm imagining: zoom into any year - 1980, 1997, 2010 - and see what life looked like. GDP was X. Life expectancy was Y. A jeepney ride cost Z. OFW remittances were surging (or not yet). The internet was still a decade away. Martial Law just ended (or was still happening). Toggle between presidencies. Compare Marcos Sr.'s GDP numbers against Cory's. Turn on Internet Era and watch what changed after 1994. Turn on OFW Boom and see remittances track against GDP.

The graph would be one 65-year timeline with layers you can toggle: GDP as the default line, then overlay life expectancy, inflation, inequality. Color-coded presidency bands in the background. Event markers for Martial Law, EDSA, Asian Financial Crisis, COVID. Era toggles that gray out sections of the timeline so you can see "before internet" vs "after internet" side by side.

I don't know if I can get all the data I want. Land prices from 1970? Probably not. What a jeepney ride cost in 1985? Unlikely. But maybe I can paint enough of the picture with what World Bank gives me: 11 indicators, 65 years, free. And if the gaps are honest and transparent, that's still a story worth telling.

The question I keep coming back to: **did the average Filipino's life actually get better?** Not just GDP. The whole picture. Health. Education. Opportunity. For whom?

I'm not sure yet. That's what the project is supposed to figure out.

---

## Problem Statement

I want to answer: "**Did the average Filipino's life actually get better between 1960 and 2025?**"

Not just "did GDP go up" (it did - pero *sino ang yumaman?*). Did the things that matter - health, education, purchasing power, the ability to actually afford rent and still have savings - improve at the same pace? Or did the line go up for the top 1% and stay flat for everyone else?

## Audience

This project is for **Filipinos wondering if progress is real**. Anyone asking whether their parents had it easier, whether it's still worth having kids *in this economy*, or whether *"mahirap na talaga ngayon"* is a feeling or a fact. Your tito at the family reunion who won't stop talking about how ₱100 used to feed a whole barangay. The fresh grad deciding between staying in PH or taking that JO abroad. The OFW parent asking if the sacrifice was worth it. Basically: anyone who has ever looked at a payslip and thought *"saan napupunta yung tax ko?"*

## KPI or Key Metric

The main metric I want to track is **Real GDP per capita over time**. But GDP alone is lazy. I want to also look at life expectancy, inflation, inequality (Gini), remittance dependency, school enrollment, and household spending. No single number tells the whole story. The dashboard should let people toggle between them.

## Comparison Approach

The thing I want to copy from the Johnny Harris format is not the exact US metrics. It's the logic:

> GDP says the country got richer. But did ordinary life actually get easier?

So GDP per capita becomes the anchor line, then I compare it against lived-reality indicators. For the Philippines, that means asking questions like:

- How many kilos of rice could one day of work buy?
- Did household consumption improve as GDP grew?
- Did inequality fall, or did growth mostly stay at the top?
- Did remittances rise because life improved, or because families needed someone abroad to survive?
- Did health and education outcomes improve enough to say life got better?

The comparison needs two layers:

1. **Official progress:** real GDP per capita over time.
2. **Lived progress:** what a Filipino worker or household could actually afford, access, or survive through in the same year.

If GDP rises but purchasing power, inequality, or remittance dependency gets worse, then the answer is not a clean "yes." It becomes: life improved in some ways, but not evenly and not for everyone.

## Fair Comparison Notes

I don't want to define "the average Filipino" carelessly because that can hide too much. A national average can blur class, region, household size, and whether a family has OFW income.

So the first fair version should compare three profiles:

1. **Minimum-wage worker** - useful for basic purchasing power: rice, transport, food, electricity, and other daily costs.
2. **Middle-income household** - useful for the Harris-style lifestyle comparison: rent, food, education, healthcare, savings, and stability.
3. **National average** - useful for macro indicators like GDP per capita, life expectancy, inflation, and household consumption.

For a "middle-class Filipino," I should not define it by vibes. The cleanest approach is to use income position:

- Prefer official household income data, like FIES income deciles or quintiles.
- If I need a class threshold, use a poverty-threshold-based definition from Philippine policy research and clearly state the multiplier.
- Keep household size explicit, probably a family of five when comparing against PSA-style poverty and income thresholds.

Money should be adjusted into **constant pesos** so years are comparable. For now, **2024 pesos** makes the most sense because many confirmed indicators currently run through 2024. If reliable full-year 2025 CPI, wage, and price data are available later, I can switch to 2025 pesos.

The basic conversion is:

> value in 2024 pesos = historical value x (CPI in 2024 / CPI in historical year)

For lifestyle comparisons, ratios may be more honest than raw pesos:

- House price divided by annual household income
- Monthly rent divided by monthly household income
- Daily wage divided by price of 1 kg of rice
- Food basket cost divided by monthly income
- Health or out-of-pocket cost divided by income

The question is not just "were prices lower before?" Of course they were. The better question is: **after adjusting for inflation and income, what could a Filipino household actually afford?**

## Likely Data Source

I will explore the **World Bank API** (https://api.worldbank.org/v2/country/PH) - free, no key, confirmed working. Provides GDP, life expectancy, inflation, population, unemployment, school enrollment, inequality (Gini), remittances, health spending, and household consumption. Earliest data from 1960.

Some questions (land affordability, food prices by commodity, rent-to-income ratio) may need fallback sources. PSA has this data but their site is blocked. Still investigating alternatives.

## Data Source Notes

### Primary Source

- **Name:** World Bank API - Philippines country indicators
- **URL:** https://api.worldbank.org/v2/country/PH/indicator/{CODE}?format=json
- **Format:** JSON API
- **Coverage:** Philippines, annual data, mostly 1960-2024 depending on indicator
- **Why it fits:** This can answer the long-term national question: did GDP, health, education, inequality, remittances, and household consumption improve over time?
- **Known limitations:** World Bank can show the big-picture trend, but it does not fully answer lived affordability questions like rent, land prices, jeepney fares, tuition, or exact food-basket purchasing power.

Useful starting indicators:

| Indicator | World Bank Code | Why it matters |
|---|---:|---|
| GDP per capita, current US$ | `NY.GDP.PCAP.CD` | Main economic progress line |
| GDP per capita, constant 2015 US$ | `NY.GDP.PCAP.KD` | Better for real growth over time |
| Life expectancy | `SP.DYN.LE00.IN` | Health / survival progress |
| Inflation | `FP.CPI.TOTL.ZG` | Price pressure |
| Population | `SP.POP.TOTL` | Scale / context |
| Unemployment | `SL.UEM.TOTL.ZS` | Job market signal |
| School enrollment | `SE.PRM.ENRR` | Education access |
| Gini index | `SI.POV.GINI` | Inequality |
| Remittances, % of GDP | `BX.TRF.PWKR.DT.GD.ZS` | OFW dependency / support |
| Health expenditure, % of GDP | `SH.XPD.CHEX.GD.ZS` | Health system investment |
| Household consumption, % of GDP | `NE.CON.PRVT.ZS` | How much of the economy is household spending |

### Fallback / Stretch Sources

- **PSA / FIES / OpenStat:** Best candidate for household income, poverty threshold, wages, CPI, and possibly food-price or expenditure data. Main risk: access can be blocked or messy, so this is not the M0 dependency.
- **BSP:** Possible source for remittances, exchange rates, inflation context, and housing price index. Main risk: some pages are difficult to access or routed through documents/SharePoint.
- **Manual historical references:** Possible for jeepney fares, rice prices, tuition, or rent examples, but these need careful citation and should be treated as illustrative unless the source is consistent.

For M0, World Bank is enough. For the full "who had it better?" version, the project should later add at least one affordability source so GDP can be compared against what Filipino households could actually buy.

## Possible Final Dashboard

The dashboard should let someone explore their own question. One 65-year timeline as the base. GDP is the default line. Toggle on life expectancy. Toggle on inflation. Presidential eras appear as background bands. Event markers for recessions and crises. Era toggles: click "Internet Era" and the pre-1994 section grays out. Click "OFW Boom" and watch remittance lines against GDP. Pick any year - see what life was like. Pick two presidencies - see which had better numbers.

The point: not a dashboard with 30 charts. One timeline with smart layers that let people ask their own questions.
