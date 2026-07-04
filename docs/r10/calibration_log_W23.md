# Calibration Log — W23

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

## W23 Team Prediction vs Actual Result

| Target | Team Prediction | Predicted Direction | Predicted Range | Confidence | Actual Result | Actual Direction | Hit / Miss | Range Check | Score |
|---|---|---|---:|---|---:|---|---|---|---:|
| SPX | Down | down | -0.8% to -0.2% | Medium | -1.40% | down | HIT | Outside range | +2 |
| NDX | Down | down | -1.2% to -0.3% | Medium | -1.19% | down | HIT | Inside range | +2 |
| IWM | Down | down | -1.5% to -0.5% | Medium | +1.33% | up | MISS | Outside range | +0 |
| XLK Technology | Neutral-Bullish | up | N/A | Medium | -2.17% | down | MISS | N/A | +0 |
| XLC Communication Services | Neutral | neutral | N/A | Medium | -1.01% | down | MISS | N/A | +0 |
| XLY Consumer Discretionary | Neutral-Bearish | down | N/A | Medium | -0.68% | down | HIT | N/A | +2 |
| XLP Consumer Staples | Neutral-Bullish | up | N/A | Medium | +3.91% | up | HIT | N/A | +2 |
| XLE Energy | Neutral | neutral | N/A | Medium | -1.91% | down | MISS | N/A | +0 |
| XLF Financials | Bearish | down | N/A | Medium | +1.83% | up | MISS | N/A | +0 |
| XLV Health Care | Neutral | neutral | N/A | Medium | +0.28% | up | MISS | N/A | +0 |
| XLI Industrials | Neutral-Bearish | down | N/A | Medium | +0.32% | up | MISS | N/A | +0 |
| XLB Materials | Bearish | down | N/A | Medium | +1.50% | up | MISS | N/A | +0 |
| XLRE Real Estate | Bearish | down | N/A | Medium | +2.32% | up | MISS | N/A | +0 |
| XLU Utilities | Bullish | up | N/A | Medium | +1.11% | up | HIT | N/A | +2 |

---

## Calibration Summary

**Direction Result:** 5 HIT, 9 MISS
**Hit Rate:** 5 / 14 = 35.7%
**Working Calibration Score:** +10
**Structured Result File:** `calibration_result_W23.json`

---

## QA Comment

This calibration measures directional accuracy with confidence weighting. The range check is reported separately and does not change the official W22-style score.

Generated automatically at: 2026-07-04 08:13:48
