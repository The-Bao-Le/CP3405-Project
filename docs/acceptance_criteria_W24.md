# Acceptance Criteria - Sprint 4 / W24

## Software Increment Acceptance Criteria

- [ ] A Python script exists at `scripts`.
- [ ] The script uses yfinance to fetch Yahoo Finance data.
- [ ] The script fetches data for SPY, QQQ, IWM, XLK, XLE, and XLF.
- [ ] The script generates `data/friday_close_market_snapshot.csv`.
- [ ] The script generates `data/friday_close_market_snapshot.json`.
- [ ] The script generates `data/friday_close_5d_prices.csv`.
- [ ] The script generates `data/friday_close_5d_prices.json`.
- [ ] The output includes latest close, 5-day return, 20-day return, 20-day SMA, above/below 20-day average, and signal.
- [ ] The GitHub Actions workflow can run manually and is scheduled for Friday after US market close.
- [ ] `README.md` explains what the script does and how to run it.
- [ ] The team can explain how the script works during the demo.

## Prediction Acceptance Criteria

- [ ] The W4 prediction file includes SPX / S&P 500.
- [ ] The W4 prediction file includes NDX / Nasdaq 100.
- [ ] The W4 prediction file includes IWM / Russell 2000.
- [ ] The W4 prediction file includes Information Technology / XLK.
- [ ] The W4 prediction file includes Energy / XLE.
- [ ] The W4 prediction file includes Financials / XLF.
- [ ] The prediction includes direction, confidence, supporting evidence, and invalidation condition.
- [ ] The prediction uses the automated CSV/JSON output as evidence.
- [ ] The W3 delta report is included or linked.
- [ ] The repo is tagged `vW24` before the deadline.
