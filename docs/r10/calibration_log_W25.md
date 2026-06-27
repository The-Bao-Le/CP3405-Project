# Calibration Log — W25

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

## W25 Team Prediction vs Actual Result

| Target | Team Prediction | Predicted Direction | Predicted Range | Confidence | Actual Result | Actual Direction | Hit / Miss | Range Check | Score |
|---|---|---|---:|---|---:|---|---|---|---:|
| SPX | Up | up | +0.2% to +1.2% | Medium | -1.95% | down | MISS | Outside range | +0 |
| NDX | Up | up | +0.8% to +2.0% | Medium | -4.62% | down | MISS | Outside range | +0 |
| XLK Technology | Up | up | +1.0% to +2.5% | High | -6.14% | down | MISS | Outside range | -2 |
| XLE Energy | Down | down | -1.8% to -0.5% | Medium | +0.58% | up | MISS | Outside range | +0 |
| XLU Utilities | Neutral | neutral | -0.3% to +0.8% | Medium | +3.87% | up | MISS | Outside range | +0 |

---

## Calibration Summary

**Direction Result:** 0 HIT, 5 MISS
**Hit Rate:** 0 / 5 = 0.0%
**Working Calibration Score:** -2
**Structured Result File:** `calibration_result_W25.json`

---

## Automation Warnings

Missing actuals: IWM, XLF, XLB

---

## QA Comment

This calibration measures directional accuracy with confidence weighting. The range check is reported separately and does not change the official W22-style score.

Generated automatically at: 2026-06-27 08:13:49
