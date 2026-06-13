import json
import argparse
from datetime import datetime, timedelta

import yfinance as yf


def normalize_week(week_str):
    week_str = week_str.upper().strip()
    if not week_str.startswith("W"):
        week_str = "W" + week_str
    return week_str


def calculate_trading_window(market_week_str):
    market_week_str = normalize_week(market_week_str)
    current_year = datetime.now().year
    week_num = int(market_week_str.replace("W", ""))

    base_date = datetime.fromisocalendar(current_year, week_num, 1)

    start_date = (base_date - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = (base_date + timedelta(days=6)).strftime("%Y-%m-%d")

    print(f"Market week: {market_week_str}")
    print(f"Data window: {start_date} to {end_date}")

    return start_date, end_date


def run_market_capture_pipeline(market_week_str, start_date, end_date):
    market_week_str = normalize_week(market_week_str)
    snapshot_filename = f"market_snapshot_{market_week_str}.json"

    tickers = {
        "SPX": "^GSPC",
        "NDX": "^NDX",
        "IWM": "IWM",
        "GOLD": "GC=F",
        "OIL": "CL=F",
        "US10Y": "^TNX",
        "TLT": "TLT",
        "BTC": "BTC-USD",
        "XLK": "XLK",
        "XLC": "XLC",
        "XLY": "XLY",
        "XLF": "XLF",
        "XLV": "XLV",
        "XLP": "XLP",
        "XLE": "XLE",
        "XLU": "XLU",
        "XLI": "XLI",
        "XLB": "XLB",
        "XLRE": "XLRE",
    }

    snapshot_data = {
        "meta": {
            "market_week": market_week_str,
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_window": f"{start_date} to {end_date}",
        },
        "metrics": {},
    }

    for label, symbol in tickers.items():
        print(f"Fetching {label} ({symbol})...")

        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            print(f"WARNING: No data for {label} ({symbol}). Skipped.")
            continue

        initial_open = df["Open"].iloc[0]
        final_close = df["Close"].iloc[-1]
        weekly_delta_pct = ((final_close - initial_open) / initial_open) * 100

        snapshot_data["metrics"][label] = {
            "ticker": symbol,
            "close_price": round(float(final_close), 4),
            "weekly_delta_pct": round(float(weekly_delta_pct), 2),
        }

    with open(snapshot_filename, "w", encoding="utf-8") as file:
        json.dump(snapshot_data, file, indent=4, ensure_ascii=False)

    print(f"Generated: {snapshot_filename}")
    return snapshot_filename


def get_metric(metrics, key, field):
    if key not in metrics:
        return "N/A"
    return metrics[key].get(field, "N/A")


def generate_report_from_snapshot(snapshot_path, actual_week_str):
    actual_week_str = normalize_week(actual_week_str)
    output_file = f"actual_2026-{actual_week_str}.md"

    with open(snapshot_path, "r", encoding="utf-8") as file:
        snapshot = json.load(file)

    metrics = snapshot["metrics"]
    meta = snapshot["meta"]

    report = f"""# R6 Data / Actuals Agent Report: {actual_week_str}

## 1. Evaluation Summary

**Prediction Week Evaluated:** {actual_week_str}  
**Market Data Week Used:** {meta["market_week"]}  
**Generated At:** {meta["generation_time"]}  
**Data Window:** {meta["data_window"]}  

---

## 2. Core Market Actuals

| Market | Ticker | Close | Weekly Change |
|---|---:|---:|---:|
| S&P 500 | {get_metric(metrics, "SPX", "ticker")} | {get_metric(metrics, "SPX", "close_price")} | {get_metric(metrics, "SPX", "weekly_delta_pct")}% |
| Nasdaq 100 | {get_metric(metrics, "NDX", "ticker")} | {get_metric(metrics, "NDX", "close_price")} | {get_metric(metrics, "NDX", "weekly_delta_pct")}% |
| Russell 2000 | {get_metric(metrics, "IWM", "ticker")} | {get_metric(metrics, "IWM", "close_price")} | {get_metric(metrics, "IWM", "weekly_delta_pct")}% |
| Gold | {get_metric(metrics, "GOLD", "ticker")} | {get_metric(metrics, "GOLD", "close_price")} | {get_metric(metrics, "GOLD", "weekly_delta_pct")}% |
| Crude Oil | {get_metric(metrics, "OIL", "ticker")} | {get_metric(metrics, "OIL", "close_price")} | {get_metric(metrics, "OIL", "weekly_delta_pct")}% |
| 10Y Treasury Yield | {get_metric(metrics, "US10Y", "ticker")} | {get_metric(metrics, "US10Y", "close_price")} | {get_metric(metrics, "US10Y", "weekly_delta_pct")}% |
| TLT | {get_metric(metrics, "TLT", "ticker")} | {get_metric(metrics, "TLT", "close_price")} | {get_metric(metrics, "TLT", "weekly_delta_pct")}% |
| Bitcoin | {get_metric(metrics, "BTC", "ticker")} | {get_metric(metrics, "BTC", "close_price")} | {get_metric(metrics, "BTC", "weekly_delta_pct")}% |

---

## 3. Sector Actuals

| Sector ETF | Weekly Change |
|---|---:|
| XLK Technology | {get_metric(metrics, "XLK", "weekly_delta_pct")}% |
| XLC Communication Services | {get_metric(metrics, "XLC", "weekly_delta_pct")}% |
| XLY Consumer Discretionary | {get_metric(metrics, "XLY", "weekly_delta_pct")}% |
| XLF Financials | {get_metric(metrics, "XLF", "weekly_delta_pct")}% |
| XLV Healthcare | {get_metric(metrics, "XLV", "weekly_delta_pct")}% |
| XLP Consumer Staples | {get_metric(metrics, "XLP", "weekly_delta_pct")}% |
| XLE Energy | {get_metric(metrics, "XLE", "weekly_delta_pct")}% |
| XLU Utilities | {get_metric(metrics, "XLU", "weekly_delta_pct")}% |
| XLI Industrials | {get_metric(metrics, "XLI", "weekly_delta_pct")}% |
| XLB Materials | {get_metric(metrics, "XLB", "weekly_delta_pct")}% |
| XLRE Real Estate | {get_metric(metrics, "XLRE", "weekly_delta_pct")}% |

---

## 4. R6 Monday Speaking Point

For {actual_week_str}, the R6 Data / Actuals Agent recorded the actual market outcome using the generated market snapshot. The key benchmark for the team prediction is the S&P 500 result. The SPX weekly change was **{get_metric(metrics, "SPX", "weekly_delta_pct")}%**. This figure should be compared against the team’s previous prediction to update the calibration record.
"""

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"Generated: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="R6 Data Agent Automation Pipeline")
    parser.add_argument("--market-week", required=True, help="Market week, e.g. W24")
    parser.add_argument("--actual-week", required=True, help="Prediction week to evaluate, e.g. W23")
    args = parser.parse_args()

    start_date, end_date = calculate_trading_window(args.market_week)
    snapshot_path = run_market_capture_pipeline(args.market_week, start_date, end_date)
    generate_report_from_snapshot(snapshot_path, args.actual_week)
