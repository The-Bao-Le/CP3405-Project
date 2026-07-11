from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "data" / "verified_snapshot.json"
OUTPUT_DIR = BASE / "outputs"


def load_snapshot() -> dict[str, Any]:
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    fed = data["fedwatch"]
    total = (
        fed["ease_probability_pct"]
        + fed["no_change_probability_pct"]
        + fed["hike_probability_pct"]
    )
    if abs(total - 100.0) > 0.01:
        errors.append(f"FedWatch probabilities sum to {total}, not 100.")

    treasury_rows = data["treasury"]["rows"]
    dates = [row["date"] for row in treasury_rows]
    if dates != sorted(dates):
        errors.append("Treasury rows are not sorted by date.")

    if not treasury_rows or treasury_rows[-1]["date"] != "2026-07-10":
        errors.append("Expected the verified latest Treasury row to be 2026-07-10.")

    finviz = data["finviz"]["one_week_performance_pct"]
    required_assets = ["S&P 500", "Nasdaq 100", "VIX", "Crude Oil WTI", "Crude Oil Brent"]
    for asset in required_assets:
        if asset not in finviz:
            errors.append(f"Missing Finviz asset: {asset}")

    return errors


def bps(new: float, old: float) -> int:
    return round((new - old) * 100)


def analyse(data: dict[str, Any]) -> dict[str, Any]:
    fed = data["fedwatch"]
    treasury_rows = data["treasury"]["rows"]
    start = treasury_rows[0]
    latest = treasury_rows[-1]
    perf = data["finviz"]["one_week_performance_pct"]

    hold_change_pp = round(
        fed["no_change_probability_pct"]
        - fed["one_week_ago"]["no_change_probability_pct"],
        1,
    )
    hike_change_pp = round(
        fed["hike_probability_pct"]
        - fed["one_week_ago"]["hike_probability_pct"],
        1,
    )

    changes = {
        "2y_bps": bps(latest["2y"], start["2y"]),
        "10y_bps": bps(latest["10y"], start["10y"]),
        "30y_bps": bps(latest["30y"], start["30y"]),
        "10s2s_start_bps": bps(start["10y"], start["2y"]),
        "10s2s_latest_bps": bps(latest["10y"], latest["2y"]),
    }
    changes["10s2s_change_bps"] = (
        changes["10s2s_latest_bps"] - changes["10s2s_start_bps"]
    )

    bullish_score = 0
    bearish_score = 0
    reasons_bullish: list[str] = []
    reasons_bearish: list[str] = []

    if perf["S&P 500"] > 0 and perf["Nasdaq 100"] > 0:
        bullish_score += 2
        reasons_bullish.append("S&P 500 and Nasdaq 100 rose over the week.")
    if perf["VIX"] < 0:
        bullish_score += 1
        reasons_bullish.append("VIX fell, indicating lower market fear.")
    if fed["no_change_probability_pct"] > fed["hike_probability_pct"]:
        bullish_score += 1
        reasons_bullish.append("A rate hold remains the most likely Fed outcome.")

    if fed["hike_probability_pct"] >= 30:
        bearish_score += 2
        reasons_bearish.append("The probability of a hike is material at 34.2%.")
    if changes["10y_bps"] > 0:
        bearish_score += 1
        reasons_bearish.append("The 10-year Treasury yield rose during the period.")
    if perf["Crude Oil WTI"] > 0 and perf["Crude Oil Brent"] > 0:
        bearish_score += 1
        reasons_bearish.append("Oil prices rose, adding inflation pressure.")

    if bullish_score >= bearish_score + 2:
        bias = "Moderately Bullish"
    elif bearish_score >= bullish_score + 2:
        bias = "Moderately Bearish"
    else:
        bias = "Neutral to Moderately Bullish"

    return {
        "fedwatch": {
            "hold_probability_pct": fed["no_change_probability_pct"],
            "hike_probability_pct": fed["hike_probability_pct"],
            "ease_probability_pct": fed["ease_probability_pct"],
            "hold_change_vs_one_week_pp": hold_change_pp,
            "hike_change_vs_one_week_pp": hike_change_pp,
            "interpretation": (
                "Hold is still the base case, but pricing became more hawkish "
                "because the hike probability increased by 16.0 percentage points."
            ),
        },
        "treasury": {
            "latest_date": latest["date"],
            "latest_2y": latest["2y"],
            "latest_10y": latest["10y"],
            "latest_30y": latest["30y"],
            **changes,
        },
        "risk_assets": {
            "sp500_pct": perf["S&P 500"],
            "nasdaq100_pct": perf["Nasdaq 100"],
            "vix_pct": perf["VIX"],
            "wti_pct": perf["Crude Oil WTI"],
            "brent_pct": perf["Crude Oil Brent"],
            "usd_proxy_pct": perf["USD"],
        },
        "key_catalyst": {
            "event": "FOMC Minutes",
            "classification": "Binary Risk",
            "confidence": "High",
            "reason": (
                "The minutes can confirm or challenge the hawkish repricing visible "
                "in FedWatch probabilities and Treasury yields."
            ),
        },
        "macro_bias": bias,
        "confidence": "Medium",
        "bullish_factors": reasons_bullish,
        "bearish_factors": reasons_bearish,
        "sector_outlook": {
            "XLK Technology": "Neutral to Bullish",
            "XLF Financials": "Neutral to Bullish",
            "XLE Energy": "Bullish",
            "XLU Utilities": "Neutral to Bearish",
            "XLB Materials": "Neutral to Bullish",
        },
        "data_limitations": [
            "A DXY value is not visible in the supplied evidence, so it is not reported.",
            "AP News and Earnings Whispers are not used in this verified snapshot.",
            "The report distinguishes facts, market expectations and agent opinion.",
        ],
    }


def write_csv_files(data: dict[str, Any], analysis: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    with (OUTPUT_DIR / "treasury_yields.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=["date", "2y", "10y", "30y"])
        writer.writeheader()
        writer.writerows(data["treasury"]["rows"])

    with (OUTPUT_DIR / "economic_calendar.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        fields = ["date", "time", "event", "period", "actual", "previous", "consensus", "forecast"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data["economic_calendar"]["events"])

    with (OUTPUT_DIR / "finviz_performance.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=["asset", "one_week_return_pct"])
        writer.writeheader()
        for asset, value in sorted(
            data["finviz"]["one_week_performance_pct"].items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            writer.writerow({"asset": asset, "one_week_return_pct": value})

    with (OUTPUT_DIR / "fedwatch.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["outcome", "probability_pct", "one_week_ago_pct", "one_month_ago_pct"],
        )
        writer.writeheader()
        fed = data["fedwatch"]
        writer.writerows([
            {
                "outcome": "Ease",
                "probability_pct": fed["ease_probability_pct"],
                "one_week_ago_pct": fed["one_week_ago"]["ease_probability_pct"],
                "one_month_ago_pct": fed["one_month_ago"]["ease_probability_pct"],
            },
            {
                "outcome": "No Change",
                "probability_pct": fed["no_change_probability_pct"],
                "one_week_ago_pct": fed["one_week_ago"]["no_change_probability_pct"],
                "one_month_ago_pct": fed["one_month_ago"]["no_change_probability_pct"],
            },
            {
                "outcome": "Hike",
                "probability_pct": fed["hike_probability_pct"],
                "one_week_ago_pct": fed["one_week_ago"]["hike_probability_pct"],
                "one_month_ago_pct": fed["one_month_ago"]["hike_probability_pct"],
            },
        ])

    with (OUTPUT_DIR / "macro_summary.json").open("w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)


def write_report(data: dict[str, Any], analysis: dict[str, Any]) -> None:
    fed = analysis["fedwatch"]
    tr = analysis["treasury"]
    risk = analysis["risk_assets"]
    catalyst = analysis["key_catalyst"]

    lines = [
        "# R4 Macro Agent Report",
        "",
        "## Confirmed Facts",
        "",
        f"- The current Fed target range is **{data['fedwatch']['current_target_bps']} bps**.",
        f"- The verified Treasury close on **{tr['latest_date']}** was "
        f"2Y **{tr['latest_2y']:.2f}%**, 10Y **{tr['latest_10y']:.2f}%**, "
        f"and 30Y **{tr['latest_30y']:.2f}%**.",
        f"- From the first to the latest Treasury row, the 2Y changed "
        f"**{tr['2y_bps']:+d} bps**, the 10Y **{tr['10y_bps']:+d} bps**, "
        f"and the 30Y **{tr['30y_bps']:+d} bps**.",
        f"- Finviz one-week performance: S&P 500 **{risk['sp500_pct']:+.2f}%**, "
        f"Nasdaq 100 **{risk['nasdaq100_pct']:+.2f}%**, "
        f"VIX **{risk['vix_pct']:+.2f}%**, WTI **{risk['wti_pct']:+.2f}%**, "
        f"and Brent **{risk['brent_pct']:+.2f}%**.",
        "- ISM Services PMI was 54.0, Initial Jobless Claims were 215K, "
        "and Existing Home Sales were 4.09M in the supplied calendar evidence.",
        "",
        "## Market Expectations",
        "",
        f"- FedWatch: **{fed['hold_probability_pct']:.1f}% hold**, "
        f"**{fed['hike_probability_pct']:.1f}% hike**, "
        f"and **{fed['ease_probability_pct']:.1f}% ease**.",
        f"- The hike probability increased by **{fed['hike_change_vs_one_week_pp']:+.1f} percentage points** "
        "compared with one week earlier.",
        f"- Interpretation: {fed['interpretation']}",
        "",
        "## Key Market-Moving Event",
        "",
        f"- Event: **{catalyst['event']}**",
        f"- Classification: **{catalyst['classification']}**",
        f"- Confidence: **{catalyst['confidence']}**",
        f"- Reason: {catalyst['reason']}",
        "",
        "## Agent Opinion",
        "",
        f"- Macro bias: **{analysis['macro_bias']}**",
        f"- Confidence: **{analysis['confidence']}**",
        "",
        "### Bullish Factors",
        "",
    ]
    lines.extend(f"- {x}" for x in analysis["bullish_factors"])
    lines += ["", "### Bearish Factors", ""]
    lines.extend(f"- {x}" for x in analysis["bearish_factors"])
    lines += ["", "## Sector Outlook", "", "| Sector | Outlook |", "|---|---|"]
    lines.extend(f"| {k} | {v} |" for k, v in analysis["sector_outlook"].items())
    lines += [
        "",
        "## Final R4 Macro Thesis",
        "",
        "Risk appetite remains positive because major U.S. equity indices rose and the VIX fell. "
        "However, FedWatch pricing became more hawkish, Treasury yields increased, and oil prices rose. "
        "The most defensible conclusion is a **neutral-to-moderately-bullish but selective outlook**, "
        "with meaningful rate and inflation risk.",
        "",
        "## Data Integrity and Limitations",
        "",
    ]
    lines.extend(f"- {x}" for x in analysis["data_limitations"])
    lines += [
        "",
        "## Evidence Files",
        "",
        "- `evidence/01_cme_fedwatch.png`",
        "- `evidence/02_trading_economics_calendar.png`",
        "- `evidence/03_finviz_week_performance.png`",
        "- `evidence/04_us_treasury_yields.png`",
        "",
    ]
    (OUTPUT_DIR / "macro_agent_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def write_manifest() -> None:
    files = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and ".git" not in p.parts and p.name != "source_manifest.json"
    )
    manifest = []
    for p in files:
        manifest.append({
            "file": str(p.relative_to(BASE)).replace("\\", "/"),
            "sha256": __import__("hashlib").sha256(p.read_bytes()).hexdigest(),
            "size_bytes": p.stat().st_size,
        })
    (OUTPUT_DIR / "source_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def main() -> int:
    data = load_snapshot()
    errors = validate(data)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    analysis = analyse(data)
    write_csv_files(data, analysis)
    write_report(data, analysis)
    write_manifest()
    print("R4 Macro Agent outputs generated successfully.")
    print(f"Macro bias: {analysis['macro_bias']} ({analysis['confidence']} confidence)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
