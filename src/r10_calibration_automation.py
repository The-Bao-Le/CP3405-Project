import argparse
import json
import re
from datetime import datetime
from pathlib import Path


TARGETS = {
    # Core indices
    "SPX": {
        "display": "SPX",
        "actual_aliases": ["S&P 500", "^GSPC", "SPX"],
    },
    "NDX": {
        "display": "NDX",
        "actual_aliases": ["Nasdaq 100", "^NDX", "NDX"],
    },
    "IWM": {
        "display": "IWM",
        "actual_aliases": ["Russell 2000", "IWM"],
    },

    # 11 S&P sectors
    "XLK": {
        "display": "XLK Technology",
        "actual_aliases": ["XLK Technology", "Technology", "XLK"],
    },
    "XLC": {
        "display": "XLC Communication Services",
        "actual_aliases": ["XLC Communication Services", "Communication Services", "XLC"],
    },
    "XLY": {
        "display": "XLY Consumer Discretionary",
        "actual_aliases": ["XLY Consumer Discretionary", "Consumer Discretionary", "XLY"],
    },
    "XLP": {
        "display": "XLP Consumer Staples",
        "actual_aliases": ["XLP Consumer Staples", "Consumer Staples", "XLP"],
    },
    "XLE": {
        "display": "XLE Energy",
        "actual_aliases": ["XLE Energy", "Energy", "XLE"],
    },
    "XLF": {
        "display": "XLF Financials",
        "actual_aliases": ["XLF Financials", "Financials", "XLF"],
    },
    "XLV": {
        "display": "XLV Health Care",
        "actual_aliases": ["XLV Health Care", "Health Care", "Healthcare", "XLV"],
    },
    "XLI": {
        "display": "XLI Industrials",
        "actual_aliases": ["XLI Industrials", "Industrials", "XLI"],
    },
    "XLB": {
        "display": "XLB Materials",
        "actual_aliases": ["XLB Materials", "Materials", "XLB"],
    },
    "XLRE": {
        "display": "XLRE Real Estate",
        "actual_aliases": ["XLRE Real Estate", "Real Estate", "XLRE"],
    },
    "XLU": {
        "display": "XLU Utilities",
        "actual_aliases": ["XLU Utilities", "Utilities", "XLU"],
    },
}

WEEKLY_REQUIRED_TARGETS = {
    "W24": ["SPX", "NDX", "IWM", "XLK", "XLE", "XLF"],
    "W25": ["SPX", "NDX", "IWM", "XLK", "XLE", "XLF", "XLU", "XLB"],
}

FULL_TARGETS = [
    "SPX", "NDX", "IWM",
    "XLK", "XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLRE", "XLU",
]


def get_week_number(week: str) -> int:
    match = re.search(r"W(\d+)", week.upper())
    if not match:
        return 0
    return int(match.group(1))


def get_required_targets_for_week(week: str, parsed_predictions: dict) -> list:
    """
    Decides which targets should be calibrated for the week.

    W24 = 3 indices + Tech, Energy, Financials
    W25 = W24 + Utilities + Materials
    W27 onward = 3 indices + all 11 sectors
    Other weeks = auto-detect from prediction file
    """
    week = week.upper()
    week_number = get_week_number(week)

    if week in WEEKLY_REQUIRED_TARGETS:
        return WEEKLY_REQUIRED_TARGETS[week]

    if week_number >= 27:
        return FULL_TARGETS

    # Fallback for W26 or special weeks:
    # only calibrate what the prediction file actually contains.
    return [target for target in FULL_TARGETS if target in parsed_predictions]

# W22 scoring rule reused for consistency.
# Source rule:
# High correct = +3
# Medium correct = +2
# Low / Uncertain correct = +1
# High wrong = -2
# Medium wrong = 0
# Low / Uncertain wrong = +1
SCORING_RULES = {
    ("High", True): 3,
    ("Medium", True): 2,
    ("Low / Uncertain", True): 1,
    ("High", False): -2,
    ("Medium", False): 0,
    ("Low / Uncertain", False): 1,
}


def normalize_week(week: str) -> str:
    week = week.upper().strip()
    if not week.startswith("W"):
        week = f"W{week}"
    return week


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return path.read_text(encoding="utf-8")


def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_confidence(confidence: str) -> str:
    text = confidence.lower().strip()

    if "high" in text:
        return "High"

    if "low" in text or "uncertain" in text:
        return "Low / Uncertain"

    return "Medium"


def normalize_prediction_direction(direction_text: str) -> str:
    text = direction_text.lower().strip()

    if "neutral-bearish" in text:
        return "down"

    if "neutral-bullish" in text:
        return "up"

    if "bearish" in text or "down" in text:
        return "down"

    if "bullish" in text or "up" in text or "cautiously up" in text:
        return "up"

    if "flat" in text or "sideways" in text or "neutral" in text:
        return "neutral"

    return "unknown"


def actual_direction_from_pct(pct: float, neutral_band: float = 0.05) -> str:
    if pct > neutral_band:
        return "up"
    if pct < -neutral_band:
        return "down"
    return "neutral"


def is_direction_hit(predicted_direction: str, actual_pct: float) -> bool:
    actual_direction = actual_direction_from_pct(actual_pct)

    if predicted_direction == "up":
        return actual_direction == "up"

    if predicted_direction == "down":
        return actual_direction == "down"

    if predicted_direction == "neutral":
        return actual_direction == "neutral"

    return False


def parse_range(range_text: str):
    if not range_text:
        return None

    matches = re.findall(r"[-+]?\d+(?:\.\d+)?", range_text)
    if len(matches) < 2:
        return None

    low = float(matches[0])
    high = float(matches[1])

    if low > high:
        low, high = high, low

    return low, high


def range_status(predicted_range, actual_pct: float) -> str:
    if predicted_range is None:
        return "N/A"

    low, high = predicted_range

    if low <= actual_pct <= high:
        return "Inside range"

    return "Outside range"


def parse_explicit_prediction_section(text: str, target: str):
    """
    Parses sections like:
    ### SPX
    Direction: Up
    % Range: +0.4% to +1.4%
    Confidence: Medium

    Also works when the markdown has been compressed onto one line.
    """
    target_pattern = re.escape(target)

    pattern = re.compile(
        rf"###\s*{target_pattern}(?:\s*\([^)]+\))?\s+"
        rf"(.*?)(?=\s+###\s+[A-Z]{{2,4}}\b|\s+---|\s+##\s+|$)",
        re.IGNORECASE | re.DOTALL,
    )

    match = pattern.search(text)
    if not match:
        return None

    section = match.group(1)

    direction_match = re.search(
        r"Direction:\s*(.*?)(?=\s*%?\s*Range:|\s*Confidence:|$)",
        section,
        re.IGNORECASE | re.DOTALL,
    )

    range_match = re.search(
        r"%?\s*Range:\s*(.*?)(?=\s*Confidence:|$)",
        section,
        re.IGNORECASE | re.DOTALL,
    )

    confidence_match = re.search(
        r"Confidence:\s*([A-Za-z /\-]+)",
        section,
        re.IGNORECASE,
    )

    if not direction_match:
        return None

    direction_text = clean_spaces(direction_match.group(1))
    range_text = clean_spaces(range_match.group(1)) if range_match else "N/A"
    confidence_text = clean_spaces(confidence_match.group(1)) if confidence_match else "Medium"

    return {
        "target": target,
        "prediction_text": direction_text,
        "predicted_direction": normalize_prediction_direction(direction_text),
        "predicted_range_text": range_text,
        "predicted_range": parse_range(range_text),
        "confidence_raw": confidence_text,
        "confidence": normalize_confidence(confidence_text),
        "source": "primary_prediction_section",
    }


def parse_sector_fallback(text: str, target: str):
    """
    Fallback parser for sector calls like:
    | XLK (Technology) | Bullish |
    or compressed text:
    XLK (Technology) Neutral-Bullish
    """
    sector_words = [
        "Neutral-Bullish",
        "Neutral-Bearish",
        "Bullish",
        "Bearish",
        "Neutral",
        "Up",
        "Down",
    ]

    sector_pattern = "|".join(sector_words)

    pattern = re.compile(
        rf"{target}\s*(?:\([^)]+\))?\s*\|?\s*({sector_pattern})",
        re.IGNORECASE,
    )

    match = pattern.search(text)
    if not match:
        return None

    direction_text = clean_spaces(match.group(1))

    return {
        "target": target,
        "prediction_text": direction_text,
        "predicted_direction": normalize_prediction_direction(direction_text),
        "predicted_range_text": "N/A",
        "predicted_range": None,
        "confidence_raw": "Medium",
        "confidence": "Medium",
        "source": "sector_call_fallback",
    }


def parse_predictions(prediction_text: str):
    prediction_text = clean_spaces(prediction_text)
    results = {}

    for target in TARGETS:
        parsed = parse_explicit_prediction_section(prediction_text, target)

        if parsed is None:
            parsed = parse_sector_fallback(prediction_text, target)

        if parsed is not None:
            results[target] = parsed

    return results


def parse_actuals(actual_text: str):
    actual_text = clean_spaces(actual_text)
    actuals = {}

    # Core market table parser.
    # Example:
    # | S&P 500 | ^GSPC | 7500.5801 | 1.21% |
    core_pattern = re.compile(
        r"\|\s*(S&P 500|Nasdaq 100|Russell 2000)\s*"
        r"\|\s*([^|]+)\s*"
        r"\|\s*([^|]+)\s*"
        r"\|\s*([-+]?\d+(?:\.\d+)?)%\s*\|",
        re.IGNORECASE,
    )

    for market_name, ticker, close_price, weekly_change in core_pattern.findall(actual_text):
        market_name_clean = clean_spaces(market_name)
        pct = float(weekly_change)

        if market_name_clean.lower() == "s&p 500":
            key = "SPX"
        elif market_name_clean.lower() == "nasdaq 100":
            key = "NDX"
        elif market_name_clean.lower() == "russell 2000":
            key = "IWM"
        else:
            continue

        actuals[key] = {
            "actual_label": market_name_clean,
            "ticker": clean_spaces(ticker),
            "close_price": clean_spaces(close_price),
            "actual_pct": pct,
            "actual_direction": actual_direction_from_pct(pct),
        }

    # Sector table parser.
    # Example:
    # | XLK Technology | 4.48% |
    sector_pattern = re.compile(
    r"\|\s*(XLK|XLC|XLY|XLP|XLE|XLF|XLV|XLI|XLB|XLRE|XLU)\s+[A-Za-z ]+\s*"
    r"\|\s*([-+]?\d+(?:\.\d+)?)%\s*\|",
    re.IGNORECASE,
    )

    for sector, weekly_change in sector_pattern.findall(actual_text):
        key = sector.upper()
        pct = float(weekly_change)

        actuals[key] = {
            "actual_label": TARGETS[key]["display"],
            "ticker": key,
            "close_price": "N/A",
            "actual_pct": pct,
            "actual_direction": actual_direction_from_pct(pct),
        }

    return actuals


def score_item(prediction, actual):
    hit = is_direction_hit(prediction["predicted_direction"], actual["actual_pct"])
    score = SCORING_RULES[(prediction["confidence"], hit)]
    range_result = range_status(prediction["predicted_range"], actual["actual_pct"])

    return {
        "target": prediction["target"],
        "display": TARGETS[prediction["target"]]["display"],
        "prediction": prediction["prediction_text"],
        "predicted_direction": prediction["predicted_direction"],
        "predicted_range": prediction["predicted_range_text"],
        "confidence_raw": prediction["confidence_raw"],
        "confidence_scoring_bucket": prediction["confidence"],
        "actual_pct": actual["actual_pct"],
        "actual_direction": actual["actual_direction"],
        "hit": hit,
        "range_result": range_result,
        "score": score,
        "prediction_source": prediction["source"],
    }


def generate_markdown(week, scored_items, missing_predictions, missing_actuals, output_json_name):
    hits = sum(1 for item in scored_items if item["hit"])
    misses = sum(1 for item in scored_items if not item["hit"])
    total_score = sum(item["score"] for item in scored_items)

    lines = [
        f"# Calibration Log — {week}",
        "",
        "## Role R10 — QA and Learning Log Lead",
        "",
        "## Purpose",
        "",
        "This file records how well the team’s market prediction matched the actual weekly market result. "
        "The calibration is generated automatically from the prediction file and the actuals file.",
        "",
        "---",
        "",
        "## Scoring Rules",
        "",
        "The same scoring method from W22 is reused for consistency.",
        "",
        "| Confidence Level | Prediction Result | Score |",
        "|---|---|---:|",
        "| High | Correct | +3 |",
        "| Medium | Correct | +2 |",
        "| Low / Uncertain | Correct | +1 |",
        "| High | Wrong | -2 |",
        "| Medium | Wrong | 0 |",
        "| Low / Uncertain | Wrong | +1 |",
        "",
        "---",
        "",
        f"## {week} Team Prediction vs Actual Result",
        "",
        "| Target | Team Prediction | Predicted Direction | Predicted Range | Confidence | Actual Result | Actual Direction | Hit / Miss | Range Check | Score |",
        "|---|---|---|---:|---|---:|---|---|---|---:|",
    ]

    for item in scored_items:
        hit_text = "HIT" if item["hit"] else "MISS"
        actual_pct = f"{item['actual_pct']:+.2f}%"

        lines.append(
            f"| {item['display']} | {item['prediction']} | {item['predicted_direction']} | "
            f"{item['predicted_range']} | {item['confidence_scoring_bucket']} | "
            f"{actual_pct} | {item['actual_direction']} | {hit_text} | "
            f"{item['range_result']} | {item['score']:+d} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## Calibration Summary",
            "",
            f"**Direction Result:** {hits} HIT, {misses} MISS",
            f"**Hit Rate:** {hits} / {len(scored_items)} = {(hits / len(scored_items) * 100):.1f}%" if scored_items else "**Hit Rate:** N/A",
            f"**Working Calibration Score:** {total_score:+d}",
            f"**Structured Result File:** `{output_json_name}`",
            "",
        ]
    )

    if missing_predictions or missing_actuals:
        lines.extend(
            [
                "---",
                "",
                "## Automation Warnings",
                "",
            ]
        )

        if missing_predictions:
            lines.append(f"Missing predictions: {', '.join(missing_predictions)}")

        if missing_actuals:
            lines.append(f"Missing actuals: {', '.join(missing_actuals)}")

        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## QA Comment",
            "",
            "This calibration measures directional accuracy with confidence weighting. "
            "The range check is reported separately and does not change the official W22-style score.",
            "",
            f"Generated automatically at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="R10 calibration automation using prediction and actual files.")
    parser.add_argument("--week", required=True, help="Prediction week to evaluate, e.g. W25")
    parser.add_argument("--prediction-file", required=False, help="Optional prediction file path")
    parser.add_argument("--actual-file", required=False, help="Optional actual file path")
    parser.add_argument("--output-dir", default="docs/r10", help="Output folder for calibration files")
    args = parser.parse_args()

    week = normalize_week(args.week)

    prediction_path = Path(args.prediction_file or f"prediction_2026-{week}_team2.md")
    actual_path = Path(args.actual_file or f"actual_2026-{week}.md")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    prediction_text = read_text(prediction_path)
    actual_text = read_text(actual_path)

    predictions = parse_predictions(prediction_text)
    actuals = parse_actuals(actual_text)

    scored_items = []
    missing_predictions = []
    missing_actuals = []

    targets_to_score = get_required_targets_for_week(week, predictions)

    for target in targets_to_score:
        if target not in predictions:
            missing_predictions.append(target)
            continue

        if target not in actuals:
            missing_actuals.append(target)
            continue

        scored_items.append(score_item(predictions[target], actuals[target]))

    result = {
        "week": week,
        "prediction_file": str(prediction_path),
        "actual_file": str(actual_path),
        "scoring_rule": "W22 confidence-weighted directional scoring",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "targets_requested": targets_to_score,
        "full_target_universe": FULL_TARGETS,
        "items_scored": scored_items,
        "missing_predictions": missing_predictions,
        "missing_actuals": missing_actuals,
        "summary": {
            "hits": sum(1 for item in scored_items if item["hit"]),
            "misses": sum(1 for item in scored_items if not item["hit"]),
            "total_items": len(scored_items),
            "working_calibration_score": sum(item["score"] for item in scored_items),
        },
    }

    json_name = f"calibration_result_{week}.json"
    md_name = f"calibration_log_{week}.md"

    json_path = output_dir / json_name
    md_path = output_dir / md_name

    json_path.write_text(json.dumps(result, indent=4), encoding="utf-8")
    md_path.write_text(
        generate_markdown(week, scored_items, missing_predictions, missing_actuals, json_name),
        encoding="utf-8",
    )

    print(f"Generated: {json_path}")
    print(f"Generated: {md_path}")
    print(f"Working calibration score: {result['summary']['working_calibration_score']:+d}")


if __name__ == "__main__":
    main()