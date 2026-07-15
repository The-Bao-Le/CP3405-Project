# R4 Macro Agent Report — 2026-W29

**As of (SGT):** 2026-07-15  
**Target period:** 2026-07-13 to 2026-07-18  
**Automated schedule:** Saturday  
**Method:** Free/public data + headline collection + transparent rules; no LLM API.

## Executive Screen

- Rule-based macro bias: **Moderately Bearish**
- Confidence: **Medium**
- Numeric score: **-3**
- Limitation: This is deterministic screening, not semantic news analysis. R4 must read the linked articles and write the final weekly interpretation.

## Key Macro Events — This Week and Next Week

Times are converted to Singapore time. Official U.S. calendars are preferred; public-calendar and recurring-schedule fallbacks are clearly labelled. Release schedules can change, so R4 should recheck high-impact items before the final write-up.

### This week

| Date/time (SGT) | Impact | Category | Event | Source / basis |
|---|---|---|---|---|
| 2026-07-14 00:30 | Medium | Fed communication | Speech - Governor Christopher J. Waller — Economic Outlook | [Federal Reserve calendar](https://www.federalreserve.gov/newsevents/2026-july.htm) |
| 2026-07-14 20:30 | High | Inflation | Consumer Price Index | [BLS release calendar](https://www.bls.gov/schedule/news_release/bls.ics) |
| 2026-07-14 22:00 | Medium | Fed communication | Testimony - Chairman Kevin Warsh — Semiannual Monetary Policy Report to Congress | [Federal Reserve calendar](https://www.federalreserve.gov/newsevents/2026-july.htm) |
| 2026-07-15 20:30 | High | Inflation | Producer Price Index | [BLS release calendar](https://www.bls.gov/schedule/news_release/bls.ics) |
| 2026-07-15 22:00 | Medium | Fed communication | Testimony - Chairman Kevin Warsh — Semiannual Monetary Policy Report to Congress | [Federal Reserve calendar](https://www.federalreserve.gov/newsevents/2026-july.htm) |
| 2026-07-16 01:00 | Medium | Fed communication | Speech - Governor Lisa D. Cook — The Economic Outlook | [Federal Reserve calendar](https://www.federalreserve.gov/newsevents/2026-july.htm) |
| 2026-07-16 02:00 | Medium | Monetary policy | Beige Book | [Federal Reserve calendar](https://www.federalreserve.gov/newsevents/2026-july.htm) |
| 2026-07-16 20:30 | Medium | Labour | Initial Jobless Claims (expected recurring release) | [U.S. Department of Labor release cadence](https://www.dol.gov/newsroom/releases/opa/opa20200701) |
| 2026-07-16 20:30 | Medium | Consumption | Retail Sales | [Public economic calendar fallback](https://www.forexfactory.com/calendar) |
| 2026-07-17 07:00 | Medium | Fed communication | Speech - Vice Chair Philip N. Jefferson — Navigating Economic Shocks | [Federal Reserve calendar](https://www.federalreserve.gov/newsevents/2026-july.htm) |
| 2026-07-17 20:30 | Medium | Inflation / trade | U.S. Import and Export Price Indexes | [BLS release calendar](https://www.bls.gov/schedule/news_release/bls.ics) |
| 2026-07-17 21:15 | Medium | Growth | G.17 - Industrial Production and Capacity Utilization | [Federal Reserve calendar](https://www.federalreserve.gov/newsevents/2026-july.htm) |
| 2026-07-17 22:00 | Medium | Consumption | Consumer Sentiment | [Public economic calendar fallback](https://www.forexfactory.com/calendar) |

### Next week

| Date/time (SGT) | Impact | Category | Event | Source / basis |
|---|---|---|---|---|
| 2026-07-22 22:00 | Medium | Labour | State Job Openings and Labor Turnover | [BLS release calendar](https://www.bls.gov/schedule/news_release/bls.ics) |
| 2026-07-23 20:30 | Medium | Labour | Initial Jobless Claims (expected recurring release) | [U.S. Department of Labor release cadence](https://www.dol.gov/newsroom/releases/opa/opa20200701) |

## Confirmed Structured Data

### Inflation and Labour

| Metric | Period | Latest | Previous comparison |
|---|---:|---:|---:|
| CPI-U YoY | 2026-06 | 3.53% | 4.25% |
| Unemployment rate | 2026-06 | 4.20% | N/A |
| Initial jobless claims (SA) | 2026-07-04 | 215000 | N/A |

### U.S. Treasury Yields

| Date | 2Y | 10Y | 30Y |
|---|---:|---:|---:|
| 2026-07-10 | 4.21% | 4.56% | 5.06% |
| 2026-07-13 | 4.26% | 4.62% | 5.10% |
| 2026-07-14 | 4.18% | 4.58% | 5.08% |

Week-to-date change: 2Y **-3.00 bps**, 10Y **+2.00 bps**, 30Y **+2.00 bps**.

### Cross-Asset Performance

| Asset | Ticker | Latest date | Latest close | Weekly return |
|---|---:|---:|---:|---:|
| SPX | ^GSPC | 2026-07-14 | 7543.5898 | -0.42% |
| NDX | ^NDX | 2026-07-14 | 29586.2871 | -0.80% |
| IWM | IWM | 2026-07-14 | 294.5100 | -0.50% |
| VIX | ^VIX | 2026-07-14 | 16.5000 | +9.78% |
| WTI | CL=F | 2026-07-14 | 80.1700 | +12.27% |
| BRENT | BZ=F | 2026-07-14 | 85.7500 | +12.81% |
| DXY | DX-Y.NYB | 2026-07-14 | 100.7860 | -0.18% |

## All 11 S&P Sector ETFs

| ETF | Sector | Weekly return | Rule-only label |
|---|---|---:|---|
| XLK | Technology | -1.16% | Bearish momentum |
| XLV | Health Care | -1.59% | Bearish momentum |
| XLF | Financials | +0.84% | Neutral momentum |
| XLY | Consumer Discretionary | -1.14% | Bearish momentum |
| XLC | Communication Services | -0.17% | Neutral momentum |
| XLI | Industrials | -0.81% | Neutral momentum |
| XLP | Consumer Staples | -0.83% | Neutral momentum |
| XLE | Energy | +3.40% | Bullish momentum |
| XLB | Materials | -0.49% | Neutral momentum |
| XLRE | Real Estate | +0.07% | Neutral momentum |
| XLU | Utilities | +0.62% | Neutral momentum |

## Rule-Based Factors

### Bullish
- Latest CPI year-over-year inflation is below its prior reading.

### Bearish
- SPX and NDX are both negative for the measured week.
- VIX rose by at least 2%, a risk-aversion signal.
- WTI rose by at least 2%, increasing near-term inflation risk.

### Neutral / Mixed
- None triggered.

## Weekly Macro Headlines — Human Review Required

These are headline-level leads only. A headline is not evidence of the article's full meaning.

- Geopolitical: 13 headline(s) require human review.
- Inflation: 13 headline(s) require human review.
- Labor: 1 headline(s) require human review.
- Monetary Policy: 16 headline(s) require human review.
- Oil Energy: 8 headline(s) require human review.

| Published SGT | Categories | Publisher | Headline |
|---|---|---|---|
| 2026-07-15T05:13+08:00 | inflation, oil_energy, geopolitical | Reuters | [Stocks gain on softer inflation, bank results while oil rises on US-Iran hostilities - Reuters](https://news.google.com/rss/articles/CBMigwFBVV95cUxPdWRaMVFPRFNSMDhQQ1dQT09aWlhsdzdhVGVFcGUzblZreE9kSms3eXc3ZjRlbVhvdUtFRW5IQ3ZSSE42bnhoTGxIaVlwbVVQR0tLUE0yY1N3NTJ2Qko2S01pNHREcW5CbmpweXpORmVRRzdCR0RDcTRjeG9oS2tqR2hIWQ?oc=5) |
| 2026-07-15T02:55+08:00 | monetary_policy | Federal Reserve speeches | [Bowman, Responsible Innovation and Financial Inclusion](https://www.federalreserve.gov/newsevents/speech/bowman20260714a.htm) |
| 2026-07-15T02:00+08:00 | monetary_policy | Federal Reserve press releases | [Minutes of the Board's discount rate meetings on June 8 and June 17, 2026](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260714a.htm) |
| 2026-07-15T00:40+08:00 | monetary_policy | Federal Reserve speeches | [Barr, Will Artificial Intelligence Broadly Raise Living Standards or Drive Income and Wealth Inequality?](https://www.federalreserve.gov/newsevents/speech/barr20260714a.htm) |
| 2026-07-14T21:58+08:00 | monetary_policy, inflation, geopolitical | AP News | [Warsh says Fed has ‘no tolerance’ for high inflation but provides no hints on next move - AP News](https://news.google.com/rss/articles/CBMilgFBVV95cUxOcE5VWkJ4VDlOdXE4OFNrTmFhdHdNMFFWMm1BTW45MXpvRGtoYlh3MlZoOHJFeFpCRnV0dGlrZ3BlRTdCc3dIb0xvVUtVN3hrWFc4cWdDY2puWGpHbDg4VFB2dmFYcWx3Qnc0ZEZrZFZKN3NwdUFQYXVaa09GUURwVEVhSFp4UFVhNDlQNGpXQnNiUm8wVEE?oc=5) |
| 2026-07-14T00:30+08:00 | monetary_policy | Federal Reserve speeches | [Waller, Monetary Policy at a Crossroads](https://www.federalreserve.gov/newsevents/speech/waller20260713a.htm) |
| 2026-07-13T17:25+08:00 | monetary_policy | Federal Reserve speeches | [Bowman, Modernizing Financial Regulation](https://www.federalreserve.gov/newsevents/speech/bowman20260713a.htm) |
| 2026-07-10T03:00+08:00 | monetary_policy | Federal Reserve press releases | [Federal Reserve announces the leadership and objectives of its task forces to advance the conduct of monetary policy](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260709a.htm) |
| 2026-07-09T23:00+08:00 | monetary_policy | Federal Reserve press releases | [Federal Reserve Board issues enforcement action with TS Banking Group, Inc. and TS Contrarian Bancshares, Inc.](https://www.federalreserve.gov/newsevents/pressreleases/enforcement20260709a.htm) |
| 2026-07-09T02:00+08:00 | monetary_policy | Federal Reserve press releases | [Minutes of the Federal Open Market Committee, June 16-17, 2026](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260708a.htm) |
| 2026-07-08T03:00+08:00 | monetary_policy | Federal Reserve press releases | [Federal Reserve Board requests comment on a proposal to amend its requirements for banks to maintain anti-money laundering programs](https://www.federalreserve.gov/newsevents/pressreleases/bcreg20260707a.htm) |
| 2026-07-14T10:30+08:00 | oil_energy, geopolitical | MarketWatch | [The U.S. is maxing out its strategic oil reserves as Trump vows to control the Strait of Hormuz - MarketWatch](https://news.google.com/rss/articles/CBMi0wFBVV95cUxOdGpWRTFwU3FaVElwNTNnS0FwVF9mWGYyQTR0eFBDNi0xN0ZKbjBjS1RSSjB0cmxlU0pBVHcwcFdHdnVKWHhpbDdmcWRzVU1ZN0tjUXV4OXpFcFNZMEhrWm5fSnNxMERTb1lzQm9nN3FmTUdHWHRxeXJLRkVhMjRvSW8wd0Q1OGVjNTJ2dEkxdTdkX0lOYW55X1g4MzZOVlllN2VXNUxvbEprQkZTclFHRUNRNWJnTDh2X3Q0d19wOGV3OGs1cDljS1lNOGV3OF9YdDdR?oc=5) |
| 2026-07-14T06:26+08:00 | monetary_policy, geopolitical | PBS | [WATCH LIVE: Fed chair Kevin Warsh testifies on monetary policy in House hearing - PBS](https://news.google.com/rss/articles/CBMivAFBVV95cUxOYlotT0JwOFhmNUVucnU4STkwV01PM002U1ByNlM2cGd2a1UxQVpoZWFhVlpHTkwydUp6Sno2aUt1dlFtTDJQR2YtRm9PeHVuRWxURmhHSTcwU3ZBcjFOZjltS091VUE4ODAwcGJIOWpuX3pVT3FIemkwZjhDUzVVNVFVeXdWV1VDV0xMejE2d1VwN3lURTJJZmFKZTVFa2xJWm9QVVZaQjlPcF93LUVYc3ZnLUZPRHhSeGY3U9IBvAFBVV95cUxOYlotT0JwOFhmNUVucnU4STkwV01PM002U1ByNlM2cGd2a1UxQVpoZWFhVlpHTkwydUp6Sno2aUt1dlFtTDJQR2YtRm9PeHVuRWxURmhHSTcwU3ZBcjFOZjltS091VUE4ODAwcGJIOWpuX3pVT3FIemkwZjhDUzVVNVFVeXdWV1VDV0xMejE2d1VwN3lURTJJZmFKZTVFa2xJWm9QVVZaQjlPcF93LUVYc3ZnLUZPRHhSeGY3Uw?oc=5) |
| 2026-07-14T04:19+08:00 | oil_energy, geopolitical | AP News | [Oil prices jump following the latest fighting in the Middle East, while AI stocks sink - AP News](https://news.google.com/rss/articles/CBMikgFBVV95cUxPcHZ0YWpGZjBZakNRRmRveklzX1hRUklIWUc2MzVoWE51Z1Bjc0JFU05vd2tGVWhaSVVVSmFvbHU3QWJZcEs0R2dkRjFxcG9WaGMtWFo2SmhqTTVjSDNFVFk5Zl8xcmdiaTFHUmM5cWU0RzNDeDU2TGM4RWJJMjg3Y2lYeEJBWkdqeXFWUjg0eWpNZw?oc=5) |
| 2026-07-11T23:32+08:00 | monetary_policy, inflation | AP News | [America In Focus: Fed officials divided on US inflation views; US home prices hit all-time high - AP News](https://news.google.com/rss/articles/CBMiowFBVV95cUxNYmRkSnA4a1VCa3Fpb1FiQ1ZseFd0dW5VdVMwajdWLV91MUdtb3YydktCMEdwRk5jeGo0SnhkWlgtT281NjdibVhjUko5alZ6YmZrRVIyVjBSeTYyclRYNkFKVDY1ekNqTlZlQ0tweWYxeHdfa0c3WHoxNFM5b3FEM1UzR1RNWVdsU0p2NWwyZDRDaDZiRHJpVlZVekpjVGViQXc0?oc=5) |
| 2026-07-10T13:39+08:00 | inflation, oil_energy | Reuters | [Investors get inflation 'wake-up call' as Trump fires up oil prices - Reuters](https://news.google.com/rss/articles/CBMijAFBVV95cUxNOUlsWGRCWlNlNDNKOWRucV85aUlzWVRwaUpkanJjbGltWURSSWlFbWUwaFpwX0JjbXRfa2Z0cHk4WXJ2QlJiSDNOeG9PcXphYUNnRDZTQmdkTks4MDVqV3lRODZrVE1oSU02c0h5RkItN1FtMG45cDVwQUoyYko0elhIaGoyY3Y1RFhERA?oc=5) |
| 2026-07-10T06:47+08:00 | labor, geopolitical | Reuters | [Dollar slips as labor market remains stable, US-Iran tensions flare - Reuters](https://news.google.com/rss/articles/CBMivwFBVV95cUxPcEtZMUh4bWpMRVNDRm42NVlyN2dsWExFZGsyNnlFa3FRelRxT1RlcVJGRkRYODBsa3JfbkxoTWhoUHVpWWxHUWx4dW1ERDlwMlc1b0pzSE9rS3J4OU9yeUx1cHNIUm9kcW9xNjhFTl9oaXdJSFVqWHpWVkpOM3VHTnphOHo1WXBmNXFodHZ5TVVhXzE4ZFFsN2JKQmNGbE93ejhjY2VRM0JwNkNaOE1oUkdtYXZZYUZ4M3JUMFpRdw?oc=5) |
| 2026-07-09T04:47+08:00 | oil_energy, geopolitical | AP News | [Oil prices rise, and stocks drop worldwide after Trump says ceasefire with Iran is ‘over’ - AP News](https://news.google.com/rss/articles/CBMijAFBVV95cUxQM255ZEIteU82bFZRNFpWYW9fTTlFaXdIajdXbjBYNmEzQTZBNUdXYjNjTGxTRm02S0NUQTBDa2lmYndWOV9sN3JqVFFvemRIaXhXTXFEdlFiVDB3cnc2b09hVF9Pd0dBVWhLMWpsV0UzV0NGQ194SFNVRjZBdGJRbExDN3dyVWROTFJscg?oc=5) |
| 2026-07-09T03:08+08:00 | monetary_policy, inflation | AP News | [Fed minutes: Officials deeply divided over future path of US inflation - AP News](https://news.google.com/rss/articles/CBMilgFBVV95cUxQMHk1X2dxdlJMSVBaYnZuTnJBSGFfYjktN2ZSa2N3VkZVUDd6dU9LZl9QOU9BMko5MDltYkh6ZDhKMlJpZGt0R0k5SXN0Rjd4WUhTZFdqaUk0UG0tVFZBLW1xZjMzTkhEOFZxVEk0RVFpajhjMTloWVZZeXhsYVdRM2pRV2Q4b1JNTTdGUXNZRnFZTGhJdVE?oc=5) |
| 2026-07-15T04:52+08:00 | inflation | AP News | [US stocks rise after data shows slowing inflation, even as IBM plunges - AP News](https://news.google.com/rss/articles/CBMilwFBVV95cUxNOEF6RnpLaF9jU0tsSVNGdDZ4SW41OGZhMlplaTl3cExkUUJlS1g5Y2JveDRTbWFwa2RRWXlEdDgwTE9HNzc2aXVrdEltZ1JVcHhCdW5kd2JxOTF5MTNTb1l6ZDZIXzUxVnZaWVRjbTMtWTlRZjRCV2xORzcxYi1wNzRPdDN4cnlicno2aUhZdS1mN2R3X0F3?oc=5) |
| 2026-07-15T04:51+08:00 | geopolitical | AP News | [Mahmoud Khalil files suit alleging a ‘public-private’ conspiracy to target Israel’s critics - AP News](https://news.google.com/rss/articles/CBMirAFBVV95cUxOLXM0djZrOEdJMndKeVpQV1F5SlJFaFZmTXVRTnFmNDJ5VmRZOHNBNXlZemMyTTJUTFFubkRXdzJPS1dnTG1fUmtVRUFRTmNWTUp1bXJ6U2hBbVJ3bDd4bjlWbW9sS0dldnpqYlBoS1h3RzRFX3dlOHNjb3hvZW93UE1ZRWlIMmNjbnZnanQtc3huTDJ0dmV5Vmp0QlI2OVNhbzBud2NXcjNabzNy?oc=5) |
| 2026-07-15T04:32+08:00 | inflation | Yahoo Finance | [Nasdaq rebounds as cooling US inflation weighs on dollar - Yahoo Finance](https://news.google.com/rss/articles/CBMijAFBVV95cUxOX3dfVTR3ZktxVkhLeUxaX293S0Fwc3Z2bExHaHNHcFdRbG1fY1RCSzdwakFnNHRPdDBxRzFyNkcxQlh5Rld3eTBrSzh2TnRRTFNQa0x2NUJ6S1hmVFhoR0tiOVNpc05ERGlzcTE1Rks0OFIzc0Q3YXZEQUlpT2xYd0JRdmxYSUc0U0RMWA?oc=5) |
| 2026-07-15T03:13+08:00 | inflation | AP News | [Inflation cools more than expected in June as gas costs fall, underlying prices ease - AP News](https://news.google.com/rss/articles/CBMilgFBVV95cUxOZ0ZNbFlHYm1IRUhtaVZuak9fcUVtc0UySC1qWnN6Snk2Rzl1NEFQWU9DblNXVGNVak8wNDNCVEwzRFUtc0xVM0xWWUFEMGFWSzlzcDdJYVQ5U0FxMHkxVDZ6YnpJNmNvdWhJRFlsMWpXYUoyRVd3SVVQS0xuNEdiMWdERkh3VDhHMXNjNDV4c0xURVBfOHc?oc=5) |
| 2026-07-15T02:42+08:00 | monetary_policy, inflation, oil_energy, geopolitical | Baltimore Sun | [Cooling inflation eases pressure on Fed as oil prices jump when US, Iran trade strikes - Baltimore Sun](https://news.google.com/rss/articles/CBMixAFBVV95cUxOSEJ5bFN4R19jWXZOb0xzUWF3aEdTZmVWcmNibDk5Ql9KTUQtN2pNQzZ6VHlJRzc2Q2dCRVM1dTFfM3lINWpDeHlNOWhqeVlkRWhING9UWWhrWDB4blBlUlRIOTJTQU1RQnBmeE1KWGRYUU1wNWhsVXZud1l1VkFJdzNQczFkUV9nUU9YeFF2NFdoTkF5UWVsM2dOMjFPbnN2Z1F0bEdWSEFyRDNlWEZzRENFd2dPaGJqcC0xOUpGNUxVNHB1?oc=5) |
| 2026-07-15T02:27+08:00 | geopolitical | AP News | [Federal judge awards $314 million to 3 Americans held and allegedly tortured in Venezuela - AP News](https://news.google.com/rss/articles/CBMioAFBVV95cUxNaTNWbXdzSU9VTGFMRzRqNkpWZFRwY2lSNS05UHJOdG94N2lJbFlIYWtycjZpZ2VHRW9CcFVHYkZKTF81QUZJeW5VTkJDWVhtVTlrQjVleVVvaXZvZDRJS0VpQkNKdW80MlNSWWJpVmFBNUxhci0yQnBuZXhnekRjMzN0eXZMRE9CZmFJY3pQSU4xOUZqTWxKZm9HT0F0SGR3?oc=5) |
| 2026-07-15T01:19+08:00 | monetary_policy, inflation, oil_energy, geopolitical | WBFF | [Cooling inflation eases pressure on Fed as oil prices jump as US and Iran trade strikes - WBFF](https://news.google.com/rss/articles/CBMi4gJBVV95cUxNd2pDUHBUVFJXMzhyOE9VMFVaRnVac1FDT1hIRHh5WXlUOHBmTk90Q3NtYXVQMkFUN3RrU25XT0hOMmF3QVdsU3I2OVFmTkdveWlQTjFBRXZMQjZ5Qi1oTmJjc1dGTzVxWDhQbWgtTWxKVlZWcTNjeTVhS0NCSjNQUUVwdDF3MU5hakFfSjhHNXJvVHZuakptTm8wc0pHNXBsbzZJcnZGUUdIXzdCRmhNQUtrVklpcmhzTGZKMTVqVkkwcGUwd0pzdTBIYzlmMnpMRXgwZWxvRzUzSUk2ZS12WlhlUGFUNV9hZkJUM3RnLVVKRm84aGpDdUZzMUJrWHN5MElPNm9RNU1vN2poaUd6c2xUMXlZNFpkOHp5bGlMWGxJZmxUWHNlUFI0dlpyRFlkeklvOUQzUEZnc2s3YzBvanJFdERPYlJucEpPUTVGVXM4NFgzQUF5Q01CcXBlWUVVcEE?oc=5) |
| 2026-07-15T00:27+08:00 | monetary_policy, inflation, oil_energy, geopolitical | Hindustan Times | [Why cooling US inflation eases pressure on the Fed despite oil prices jumping after Iran strikes \| Hindustan Times - Hindustan Times](https://news.google.com/rss/articles/CBMi-wFBVV95cUxNak0zZXhqOW5zNXZEVnZ2d0o1djdGc1I5SjM0cWdrOHJFck9IWm5zejQzd1RLaWw3X0ZqRXd3VHA4Z2RPbm9aTGhxbmxPZjRIM0M3Ylo0YlJTSVNjNVNjNDIzRGtvLUtUSTR2TDZuWW5WMUFXVDE4MHBZNThjUElXb1lIbDRURi1oY3hnQmdGeUdCeC03NDItazIxWG53R1FRbTZqNk51MG5nSnhjSVlwbkRrOHQ5TDlZRmxDRWlrMV9qb01kd3dtNWt0LVNBeTdxV21RZjYzMzJrQlFiTU1TZVI1bTlrRG9IelJxNk43bk5yZU9IZUgwQWxFNNIBgAJBVV95cUxQdEhURmFRZUMyaGpIaHNfbXNjVFRkV0ZSU0xoZ002SS16dFJobVRYTl9SUUJyTHE0bHk4Z21YcmxWTmdES0JrNUZnanBHUEZQR0RuQ3k0YUgwTVhmOG96ejhwQzljSXVtYVozYmhGeWR4UDF1VWtXMkZxMWdjZmFjY2lHVW85Y0dsR3BzRlA3aVFOQUlOaXlqWmNwbld1QzFoLWRudWpGNzRldFdyWElaR1VoYTZ0bkV5dHFYT1NSUEVVTTZuNUd4VzhzcUp0bTVnY1g1OHlmV1J4RXlTTFdCQ1N1djJWQkQ3Q0pUTWlfRVBFYlN3RDBaLU1wYnNqTVpU?oc=5) |
| 2026-07-14T20:31+08:00 | inflation | Financial Times | [US inflation fell more than expected to 3.5% in June as petrol prices tumbled - Financial Times](https://news.google.com/rss/articles/CBMihAFBVV95cUxQMmFLWHRoUE9ORGZ2eHNRSWlWSU5fejViWlBjT1NWcndmX2ZRUXQxd1lQNWU5WGlLbjI5WmpYVnJUQk1icWJUdXV1NEUtck15cDgtWk5sZDVic01NRzRNbWpzbDBxWndhRDlENnphU3ZuOXlWUWgydEc1WVlzLVlVR1BEMVA?oc=5) |
| 2026-07-14T12:10+08:00 | geopolitical | AP News | [US attacks Iran and Tehran retaliates across the Middle East as both vie for control of strait - AP News](https://news.google.com/rss/articles/CBMinwFBVV95cUxNQXlDMHpMczFma2paOVJQMzZuZzVNVFZLeS04V0VXUk1zUFBSTGRaelYzaU1fQlg0azEwQ1dQQ2lfV2VmOFBMZ0ZGa0tjSWJGUWVFdDhhUTdCbmpKMy1QRHVOdE5YRnliNmJfVkRKU09zdVhYSm1hQW94MDlUbEp1OXB0ZjIzZlFtYUdZZHBQb2pHT1V5bjZtbVE0QVN3cTg?oc=5) |
| 2026-07-14T11:27+08:00 | inflation | CNBC | [Gold recovers from two-week low ahead of US inflation figures - CNBC](https://news.google.com/rss/articles/CBMipAFBVV95cUxQMm5wQjk2LXVYREZ5OWl3S3hTZnRDRWNtc1ZOenctMFpIcHY2X2l1ak5jbW91Z1RMUGhEa0czakVobFNfV3lMXzltQm1aWU5pUXVwZUUzeV9SdUJubHRLWUtQX2RXaFRIVzk4eUlxS2tFR3c1LVRoWlFoRlctT3F0NEEzTHRfUk1vU2ROVU9ZVTkybFRRaWd3Q2VYSS1vUDJyck83StIBpAFBVV95cUxQMm5wQjk2LXVYREZ5OWl3S3hTZnRDRWNtc1ZOenctMFpIcHY2X2l1ak5jbW91Z1RMUGhEa0czakVobFNfV3lMXzltQm1aWU5pUXVwZUUzeV9SdUJubHRLWUtQX2RXaFRIVzk4eUlxS2tFR3c1LVRoWlFoRlctT3F0NEEzTHRfUk1vU2ROVU9ZVTkybFRRaWd3Q2VYSS1vUDJyck83Sg?oc=5) |

## R4 Manual Interpretation Checklist

- Read the highest-impact linked stories and verify them against the full article.
- Check CME FedWatch manually and record the next-meeting probabilities.
- Recheck high-impact items in the automated BLS/BEA/Fed event table for schedule changes.
- Use Trading Economics or another public calendar manually only as a cross-check.
- Check AP or another reputable wire for geopolitical developments not captured by the feeds.
- Check Earnings Whispers only if individual earnings are material to the team forecast.

## Source Status and Automation Scope

| Source | Status | Detail |
|---|---|---|
| U.S. Treasury daily par yields | ok | collection and parsing succeeded |
| BLS public timeseries API | ok | collection and parsing succeeded |
| U.S. Department of Labor weekly claims | ok | collection and parsing succeeded |
| Yahoo Finance via yfinance | ok | collection and parsing succeeded |
| BLS official release calendar | ok | 160 key events parsed before date filtering |
| BEA official release schedule | ok | 17 key events parsed before date filtering |
| Federal Reserve official calendar | ok | 8 key events parsed from 1 month page(s) |
| DOL weekly claims release cadence | derived | 2 expected Thursday release(s); holiday changes require verification |
| Free public weekly economic-calendar fallback | ok | 11 key U.S. events parsed; used only to fill official-calendar gaps |
| Federal Reserve press releases | ok | 5 relevant dated headlines |
| Federal Reserve speeches | ok | 4 relevant dated headlines |
| Google News AP-only search | ok | 22 relevant dated headlines |
| Google News macro search | ok | 91 relevant dated headlines |
| CME FedWatch | skipped | No stable free public FedWatch API; dynamic dashboard remains a manual R4 check. |
| Trading Economics calendar API | skipped | Reliable API access requires credentials; guest endpoint returns HTTP 410. |
| Finviz futures performance | replaced | Direct scraping is fragile; market moves use yfinance or the same-week R6 snapshot. |
| AP News full-article analysis | skipped | No paid/licensed AP API is configured; headline links may appear via news RSS only. |
| Earnings Whispers calendar | skipped | No stable free public API; earnings calendar remains a manual check. |
| LLM news interpretation | skipped | No LLM key is required or used; final narrative is intentionally human-reviewed. |

### Implemented

- Official Treasury yields, BLS CPI/unemployment, DOL claims where available.
- Cross-asset returns and 11-sector ETF collection through yfinance, with same-week R6 fallback.
- Federal Reserve RSS and macro/geopolitical headline-only RSS collection.
- This-week/next-week key event table from official BLS, BEA and Federal Reserve calendars.
- CSV/JSON/Markdown outputs, explicit source health, and rule-based screening.
