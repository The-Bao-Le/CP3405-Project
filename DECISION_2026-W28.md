# Sprint 6 Automation Decision

## Decision Summary

For Sprint 6 (W28), our team decided to extend the existing market-data automation into a fully connected, end-to-end weekly forecasting pipeline.

The goal is not to create a completely autonomous trading system. Instead, the team will automate the repeatable stages of the weekly prediction workflow while keeping the final judgement, Human Score, and release approval under human control.

The W28 pipeline will collect current market data, generate structured outputs from the Almanac, Macro, Technical, and Data agents, call at least two large language models through APIs, produce a structured W28 prediction file, validate missing or invalid data, update calibration evidence, and confirm completion through GitHub Actions and the correct `vW28` release tag.

## What We Chose to Automate

We chose to automate the complete evidence-to-prediction workflow for the weekly market forecast.

The pipeline will cover the following market indexes and sector proxies:

| Market Area | Proxy Ticker | Purpose |
|---|---|---|
| S&P 500 / SPX | ^GSPC | Broad US large-cap market proxy |
| Nasdaq 100 / NDX | ^NDX | Growth and technology-heavy market proxy |
| Russell 2000 / IWM | IWM | Small-cap market proxy |
| Information Technology | XLK | Technology sector proxy |
| Communication Services | XLC | Communication Services sector proxy |
| Consumer Discretionary | XLY | Consumer Discretionary sector proxy |
| Financials | XLF | Financial sector proxy |
| Health Care | XLV | Health Care sector proxy |
| Consumer Staples | XLP | Consumer Staples sector proxy |
| Energy | XLE | Energy sector proxy |
| Utilities | XLU | Utilities sector proxy |
| Industrials | XLI | Industrials sector proxy |
| Materials | XLB | Materials sector proxy |
| Real Estate | XLRE | Real Estate sector proxy |

The automated workflow will:

- Fetch the latest available market data.
- Generate structured Almanac, Macro, Technical, and Data outputs.
- Call at least two LLMs through APIs using consistent prompts.
- Save the model responses for comparison and audit.
- Generate the W28 prediction record.
- Detect missing, stale, or invalid market data.
- Update the calibration evidence.
- Run through GitHub Actions.
- Create the correct `vW28` release tag.

## Why We Chose This Scope

The team has already automated individual parts of the process in earlier sprints. For W28, the most valuable next step is to connect those parts into one repeatable workflow.

This scope was selected because it improves the reliability, consistency, and auditability of the weekly forecasting process. It also reduces repeated manual data collection and makes it easier for different roles to work from the same evidence base.

A fully autonomous prediction system would still be inappropriate because the final call depends on conflicting evidence, judgement, and accountability. For example, the W28 evidence contains disagreement between seasonal signals and current market momentum, especially in Energy and small-cap equities.

Therefore, the automation should support human judgement rather than replace it.

## Level Justification

This increment moves the team beyond isolated automation and toward an integrated Level 3 workflow.

It satisfies the current automation requirements because:

- It uses working Python-based data collection and processing.
- It retrieves live market information from external sources.
- It creates structured and reusable output files.
- It supports all required indexes and all 11 S&P 500 sectors.
- It calls at least two LLMs through APIs.
- It includes validation for missing or invalid data.
- It can run manually and through GitHub Actions.
- It produces evidence that can be inspected and calibrated.
- It supports release tagging and weekly audit.

It moves toward a more mature system because:

- Multiple agent outputs are connected in one pipeline.
- LLM responses are generated with consistent inputs.
- Prediction evidence can be compared across agents and models.
- Calibration becomes part of the repeated workflow.
- The same process can be reused in future weeks with less manual work.

However, the team is not claiming that the system can independently make a trustworthy market prediction. The Product Owner, Human Score Analyst, and team must still review the evidence and lock the final forecast.

## Definition of Done

Sprint 6 is complete when:

- Actual market data covers SPX, NDX, IWM, and all 11 S&P 500 sectors.
- Almanac, Macro, Technical, and Data agents produce structured outputs.
- At least two LLMs are called successfully through APIs.
- Raw LLM responses are saved for comparison.
- The W28 prediction file is generated.
- Missing, stale, or invalid data is detected and handled.
- Calibration evidence is updated.
- GitHub Actions completes successfully.
- All required files are committed to the repository.
- The correct `vW28` release tag is created and accessible.
- R1 reviews the evidence and approves the final locked prediction.

## Role Usage

The automated outputs support all team roles:

| Role | How the Output Helps |
|---|---|
| R1 Product Owner | Confirms the Sprint Goal and Definition of Done, reviews the evidence, and approves the final prediction narrative |
| R2 Scrum Master | Tracks blockers, deadlines, participation, and end-to-end process flow |
| R3 Almanac Agent | Provides seasonal patterns, historical baselines, and calendar-based signals |
| R4 Macro Agent | Provides Fed, yield, inflation, growth, oil, and sector-rotation evidence |
| R5 Technical Agent | Provides trend, EMA, support, resistance, and confidence signals for SPX, NDX, and IWM |
| R6 Data / Actuals Agent | Produces the market snapshot and records actual outcomes |
| R7 Human Score Analyst | Reviews all evidence, applies the Human Score, and confirms or overrides the AI consensus |
| R8 LLM Operator | Calls multiple LLMs, saves raw responses, and compares agreement, disagreement, and credibility |
| R9 GitHub Lead | Integrates files, verifies the workflow, maintains repository structure, and creates the release tag |
| R10 Calibration Lead | Evaluates prediction accuracy, tracks systematic bias, and updates calibration evidence |

## Evidence Considered for W28

The current W28 evidence indicates:

- SPX and NDX showed continued large-cap strength.
- IWM underperformed, showing weaker small-cap participation.
- Technology and Communication Services remained constructive.
- Energy showed strong recent momentum because of higher oil prices.
- Materials, Industrials, and Health Care were relatively weak.
- Treasury yields remained an important risk for growth and rate-sensitive assets.
- Seasonal evidence and current market momentum did not fully agree, especially for Energy and IWM.

These disagreements confirm that the final prediction should remain a human-reviewed team decision.

## Risks and Limitations

This automation has several limitations:

- Market data providers may update after the official close.
- Weekends, holidays, and early-close sessions may affect the latest available date.
- API calls may fail, time out, or return inconsistent outputs.
- LLMs may interpret the same evidence differently.
- Structured outputs do not guarantee accurate forecasts.
- Technical, macro, seasonal, and current-market signals may conflict.
- Calibration rules may not perform equally well in every market regime.
- GitHub Actions success proves workflow execution, not prediction correctness.

These limitations are acceptable because the purpose of Sprint 6 is to create a reliable and auditable forecasting workflow, not an autonomous trading model.

## Final Decision

The team will proceed with a fully connected W28 forecasting pipeline that automates data collection, agent output generation, multi-LLM API calls, prediction-file creation, data validation, calibration updates, GitHub Actions execution, and release tagging.

The final market call will remain under human control. R7 will provide the Human Score, and R1 will review the complete evidence set, confirm the Definition of Done, and approve the final locked prediction.

This decision keeps the system technically ambitious but still realistic. It improves the team’s workflow from separate automation components toward a repeatable, inspectable, and human-governed forecasting process.
