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

## Likely Data Source

I will explore the **World Bank API** (https://api.worldbank.org/v2/country/PH) - free, no key, confirmed working. Provides GDP, life expectancy, inflation, population, unemployment, school enrollment, inequality (Gini), remittances, health spending, and household consumption. Earliest data from 1960.

Some questions (land affordability, food prices by commodity, rent-to-income ratio) may need fallback sources. PSA has this data but their site is blocked. Still investigating alternatives.

## Possible Final Dashboard

The dashboard should let someone explore their own question. One 65-year timeline as the base. GDP is the default line. Toggle on life expectancy. Toggle on inflation. Presidential eras appear as background bands. Event markers for recessions and crises. Era toggles: click "Internet Era" and the pre-1994 section grays out. Click "OFW Boom" and watch remittance lines against GDP. Pick any year - see what life was like. Pick two presidencies - see which had better numbers.

The point: not a dashboard with 30 charts. One timeline with smart layers that let people ask their own questions.
