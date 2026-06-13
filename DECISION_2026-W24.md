# Sprint 4 Automation Decision

## Decision Summary

For Sprint 4, our team decided to build a focused Python-based market data collection automation rather than attempting a full AI prediction system. Based on the level definitions, our current approach is already close to Level 2, and our goal is to move toward Level 3 by automating one repeatable part of the weekly prediction workflow.

The automation will fetch market data from Yahoo Finance using Python, then export structured output that can support the weekly market analysis and prediction process.

## What We Chose to Automate

We chose to automate the data collection layer for the weekly market snapshot.

The script will fetch data for the required index and sector proxies:

| Market Area            | Proxy Ticker | Purpose                                 |
| ---------------------- | ------------ | --------------------------------------- |
| S&P 500 / SPX          | ^GSPC        | Broad US large-cap market proxy         |
| Nasdaq 100 / NDX       | ^NDX         | Growth and technology-heavy index proxy |
| Russell 2000 / IWM     | IWM          | Small-cap market proxy                  |
| Information Technology | XLK          | Selected S&P sector proxy               |
| Financials             | XLF          | Selected S&P sector proxy               |
| Energy                 | XLE          | Selected S&P sector proxy               |

The script will produce structured output files for weekly analysis, including the latest market snapshot and recent five-trading-day price data.

## Why We Chose This First

We chose market data collection as the first automation target because it is repetitive, evidence-based, and directly connected to the weekly prediction task. In previous weeks, the team relied heavily on manually collecting and interpreting market evidence. Automating this step gives the team a more repeatable and inspectable evidence base.

This approach is also realistic within the Sprint 4 time limit. A full AI prediction system would be too large and risky to complete properly in this sprint. Instead, this automation focuses on one working software increment that can be run, demonstrated, and explained clearly.

## Level Justification

This increment is intended to move the team from Level 2 toward Level 3.

It satisfies Level 2 because:

* It uses a working Python script.
* It fetches live market data from an external source.
* It produces structured output files.
* It can be run locally or through GitHub Actions.
* It supports the team’s weekly prediction process.

It moves toward Level 3 because:

* The data collection process becomes repeatable.
* The output can be reused by multiple team roles.
* The script can be scheduled to run after the Friday US market close.
* The generated output can support the following week’s prediction discussion.

However, we are not claiming this is a full AI prediction system. The final prediction still requires human interpretation, role-based analysis, and team validation.

## Role Usage

The output from the automation will support several roles:

| Role     | How the Output Helps                                                 |
| -------- | -------------------------------------------------------------------- |
| R1       | Validates that the sprint goal and Definition of Done are met        |
| R3       | Uses the market snapshot alongside almanac and seasonal evidence     |
| R4       | Compares macro context against the market and sector data            |
| R5       | Uses recent price movement and trend signals for technical analysis  |
| R6 / R10 | Supports comparison and calibration against previous predictions     |
| R8       | Provides structured input for LLM comparison                         |
| R9       | Owns repository integration, workflow execution, and release tagging |

For R4 specifically, the macro data needed for interpretation should be defined separately and used to validate the output after the Friday market close.

## Risks and Limitations

This automation has several limitations:

* Yahoo Finance data may update a few minutes after the market close.
* The selected ETFs are proxies, not the exact underlying indexes or sector indexes.
* The script does not automatically generate a final prediction.
* The signal logic is intentionally simple and should not be treated as a complete trading model.
* Market holidays or early-close days may affect the latest available data date.

These limitations are acceptable for Sprint 4 because the goal is to automate one evidence collection step, not to build a complete autonomous forecasting system.

## Final Decision

The team will proceed with a Python/yfinance market snapshot automation for Sprint 4. This is the most practical increment because it is achievable within the sprint, supports the required W4 prediction, produces inspectable CSV/JSON evidence, and creates a foundation for future automation.

This decision keeps the scope realistic while still improving the team’s workflow from manual evidence collection toward a repeatable, software-supported prediction process.
