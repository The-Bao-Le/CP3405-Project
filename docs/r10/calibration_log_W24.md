# Calibration Log — W24

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

## W24 Team Prediction vs Actual Result

| Target | Team Prediction | Predicted Direction | Predicted Range | Confidence | Actual Result | Actual Direction | Hit / Miss | Range Check | Score |
|---|---|---|---:|---|---:|---|---|---|---:|
| SPX | Neutral → Cautiously Up | up | -0.2% to +0.8% | Medium | +1.21% | up | HIT | Outside range | +2 |
| NDX | Up | up | +0.4% to +1.4% | Medium | +3.49% | up | HIT | Outside range | +2 |
| IWM | Flat → Up | up | -0.3% to +0.9% | Medium | +1.60% | up | HIT | Outside range | +2 |
| XLK Technology | Up | up | +0.8% to +2.0% | High | +4.48% | up | HIT | Outside range | +3 |
| XLE Energy | Down | down | -1.5% to -0.3% | Medium | -5.32% | down | HIT | Outside range | +2 |
| XLF Financials | Neutral → Up | up | 0.0% to +1.0% | Medium | +1.15% | up | HIT | Outside range | +2 |

---

## Calibration Summary

**Direction Result:** 6 HIT, 0 MISS
**Hit Rate:** 6 / 6 = 100.0%
**Working Calibration Score:** +13
**Structured Result File:** `calibration_result_W24.json`

---

## QA Comment

This calibration measures directional accuracy with confidence weighting. The range check is reported separately and does not change the official W22-style score.

Generated automatically at: 2026-06-21 12:30:48
