# Calibration Log — W23

## Role
R10 — QA and Learning Log Lead

## Purpose
This file records how well the team’s W23 market prediction matched the actual weekly market result.

The goal is not only to check whether the prediction direction was correct, but also whether the team’s confidence level was reasonable and whether the forecast range captured the actual move.

---

## Current Status
Completed for W23.

The actual W23 market results are now available and have been compared against the team’s W23 prediction for SPX, NDX, and IWM.

---

## Scoring Rules

The same scoring method from W22 is used for this calibration.

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

| Index | Team Prediction | Predicted Range | Confidence | Actual Result | Hit / Miss | Score | Comment |
|---|---|---:|---|---:|---|---:|---|
| SPX | Down / Neutral-Bearish | -0.8% to -0.2% | Medium | -1.40% | HIT | +2 | Direction was correct, but the actual downside was larger than the predicted range. |
| NDX | Down / Neutral-Bearish | -1.2% to -0.3% | Medium | -1.19% | HIT | +2 | Direction was correct and the actual result was inside the predicted range. |
| IWM | Down / Neutral-Bearish | -1.5% to -0.5% | Medium | +1.33% | MISS | 0 | Prediction missed because IWM moved up instead of down. |

---

## Calibration Summary

**Direction Result:** 2 HIT, 1 MISS  
**Hit Rate:** 2 / 3 = 66.7%  
**Working Calibration Score:** +4  
**Largest Miss:** IWM, because the team predicted a decline but IWM finished up +1.33%.

The team’s broad bearish view worked for SPX and NDX, but it did not work for IWM. The final score is +4 because SPX and NDX were both medium-confidence correct calls worth +2 each, while IWM was a medium-confidence wrong call worth 0.

---

## What Worked

SPX and NDX were successful direction calls. Both finished negative, matching the team’s W23 bearish direction.

NDX was the strongest calibration result because the actual move was -1.19%, which landed inside the predicted range of -1.2% to -0.3%.

The team correctly identified broad weakness in large-cap indices. The bearish technical evidence and macro risk view were useful for SPX and NDX.

---

## What Did Not Work

IWM was the main miss. The team expected small caps to fall, but IWM finished positive at +1.33%.

SPX was directionally correct, but the predicted range underestimated the downside. The team expected -0.8% to -0.2%, but the actual result was -1.40%.

The sector view was mixed. XLK was selected as the top sector but finished down, while XLF was selected as a weak/bearish sector but finished positive. This shows that sector rotation did not fully match the team’s forecast.

---

## Learning for Next Sprint

Separate direction accuracy from range accuracy. The W23 score is good directionally, but SPX shows that a correct direction can still miss the magnitude.

Treat IWM separately from SPX and NDX. Small caps did not follow the same bearish pattern as the large-cap indices, so future forecasts should include a stronger check on small-cap-specific drivers.

Add a clearer breadth or rotation check before making sector calls. The team should verify whether money is moving into defensive, growth, or cyclical sectors before naming top and bottom sectors.

Keep using the same scoring rules so calibration remains comparable across weeks.

---

## R10 Note

W23 calibration is now complete using the same scoring method as W22.

The final W23 working calibration score is **+4**, based on **2 hits and 1 miss**.

This score measures directional accuracy with confidence weighting. It does not apply an additional penalty for missing the exact percentage range.
