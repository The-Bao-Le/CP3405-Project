# Sprint Goal — W28

Deliver a fully automated end-to-end W28 forecasting pipeline so the team can generate structured, repeatable, and auditable market evidence for the weekly prediction.

The pipeline will collect the latest available data for SPX, NDX, IWM, and all 11 S&P 500 sectors, generate structured outputs from the Almanac, Macro, Technical, and Data agents, call at least two LLMs through APIs, and produce the final W28 prediction file.

The sprint will also validate missing or invalid market data, update calibration evidence, run successfully through GitHub Actions, and create the correct vW28 release tag. The final prediction will remain under human review, with R7 applying the Human Score and R1 approving the locked team prediction.
