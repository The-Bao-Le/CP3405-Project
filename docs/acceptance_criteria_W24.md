# Acceptance Criteria - Sprint 4 / W24

## Software Increment Acceptance Criteria

- [ ] A Python script exists at `scripts`.
- [ ] The script uses yfinance to fetch Yahoo Finance data.
- [ ] The script fetches data for SPY, QQQ, IWM, XLK, XLE, and XLF.
- [ ] The script generates appropriate `csv` and `json` files.
- [ ] The GitHub Actions workflow can run manually and is scheduled for Friday after US market close.
- [ ] `README.md` explains what the script does and how to run it.
- [ ] The team can explain how the script works during the demo.

## Weekly Archive Acceptance Criteria

* [ ] The automation archives each weekly market result under `data/archive/YYYY-WXX/`.
* [ ] The latest files remain easy to access in `data/latest/`.
* [ ] Previous weekly outputs are preserved instead of overwritten.
* [ ] The archive can be used later for calibration, delta reports, and prediction review.

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
