# Acceptance Criteria — W28

## Prediction coverage

The W28 prediction file includes forecasts for:

- SPX
- NDX
- IWM
- Technology
- Communication Services
- Consumer Discretionary
- Financials
- Health Care
- Consumer Staples
- Energy
- Utilities
- Industrials
- Materials
- Real Estate

Each market target includes:

- A clear directional prediction, such as up, down, or neutral
- A forecast range
- A confidence level
- Short supporting reasoning based on agent or LLM evidence

## Market data automation

The market data workflow runs automatically through GitHub Actions.

The generated market snapshot covers SPX, NDX, IWM, and all 11 S&P 500 sector proxies.

The output includes:

- Latest available close price
- Weekly percentage change
- Clear ticker identification
- Generation time
- Data window

The output is saved in a structured format such as JSON or CSV using a clear W28 filename.

Example:

- `market_snapshot_W28.json`

## Almanac agent automation

The Almanac agent produces structured W28 output.

The output includes relevant seasonal and calendar-based evidence such as:

- Historical July patterns
- Midterm Election Year patterns
- Sector seasonal windows
- Important market-calendar risks

The output is saved in the repository using a clear W28 filename.

## Macro agent automation

The Macro agent produces structured W28 output.

The output includes relevant macroeconomic evidence such as:

- Federal Reserve expectations
- Treasury yields
- Inflation and employment indicators
- Oil-price movements
- Risk sentiment
- Sector rotation

The output identifies the overall macro bias and confidence level.

## Technical agent automation

The Technical agent produces structured output for:

- SPX
- NDX
- IWM

The output includes relevant technical indicators such as:

- Close price
- 8-day EMA
- 21-day EMA
- Support
- Resistance
- Trend
- Technical bias
- Confidence

The output is saved using a clear W28 filename.

## LLM API automation

At least two LLMs are called successfully through APIs using consistent prompts.

The raw responses are saved in the repository.

The LLM comparison identifies:

- Areas of agreement
- Areas of disagreement
- Model credibility
- Overall consensus
- Prediction uncertainty

The outputs can be used by R7 and R1 when reviewing the final prediction.

## Data validation

The workflow checks for:

- Missing data
- Invalid values
- Stale market dates
- Missing tickers
- Failed API responses
- Incomplete agent outputs

The workflow reports or handles validation failures clearly.

## GitHub Actions workflow

The automation workflow:

- Can run without manual data collection
- Installs required dependencies
- Runs the required scripts and agents
- Calls at least two LLM APIs
- Generates and saves the required output files
- Can be triggered manually using `workflow_dispatch`
- Includes evidence of a successful run
- Is configured to support future scheduled execution

## W28 prediction file

The workflow or team generates:

- `prediction_2026-W28_team2.md`

The prediction file includes:

- Primary predictions
- Sector calls
- Top sector
- Bottom sector
- Key evidence
- Key contradiction
- Invalidation conditions
- Human Score
- LLM consensus
- Final team view

## Calibration evidence

The calibration process compares the previous team prediction against actual market outcomes.

The calibration evidence includes:

- Prediction direction
- Actual result
- Hit or miss status
- Range accuracy where applicable
- Score contribution
- Accuracy summary
- Identified systematic bias

The calibration method remains consistent with the existing team scoring rule.

## Decision and sprint documentation

The repository includes:

- `docs/sprint_goal_W28.md`
- `docs/acceptance_criteria_W28.md`
- `DECISION_2026-W28.md`

The documentation explains:

- What was automated
- Why the team selected this scope
- What files are generated
- How the workflow runs
- What limitations remain
- How the final prediction is reviewed and approved

## Release readiness

All required evidence files are committed to the repository.

The latest GitHub Actions workflow completes successfully.

The final W28 prediction is reviewed and approved by R1.

The correct `vW28` release tag is created and accessible.

## Presentation readiness

The team can demonstrate:

- Structured outputs from the required agents
- At least two saved LLM API responses
- A successful GitHub Actions run
- Data-validation evidence
- Updated calibration evidence
- The final W28 prediction
- The correct `vW28` release tag

The team can explain how the automated evidence supported the final prediction and where human judgement was still required.
