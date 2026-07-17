# Calibration Log — W28

## Role R10 — QA and Learning Log Lead

## Purpose

This file records how well the team’s market prediction matched the actual weekly market result. The calibration is generated automatically from the prediction file and the actuals file.

---

## Scoring Rules

The same scoring method from W22 is reused for consistency.

| Confidence Level | Prediction Result | Score |
|---|---|---:|
| High | Correct | +3 |
| Medium | Correct | +2 |
| Low / Uncertain | Correct | +1 |
| High | Wrong | -2 |
| Medium | Wrong | 0 |
| Low / Uncertain | Wrong | +1 |

---

## W28 Team Prediction vs Actual Result

| Target | Team Prediction | Predicted Direction | Predicted Range | Confidence | Actual Result | Actual Direction | Hit / Miss | Range Check | Score |
|---|---|---|---:|---|---:|---|---|---|---:|

---

## Calibration Summary

**Direction Result:** 0 HIT, 0 MISS
**Hit Rate:** N/A
**Working Calibration Score:** +0
**Structured Result File:** `calibration_result_W28.json`

---

## Automation Warnings

Missing predictions: SPX, NDX, IWM
Missing actuals: XLK, XLC, XLY, XLP, XLE, XLF, XLV, XLI, XLB, XLRE, XLU

---

## QA Comment

This calibration measures directional accuracy with confidence weighting. The range check is reported separately and does not change the official W22-style score.

Generated automatically at: 2026-07-14 11:28:55
