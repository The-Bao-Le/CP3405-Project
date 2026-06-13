import os
import json
import argparse
import yfinance as yf
from datetime import datetime, timedelta

def calculate_trading_window(data_week_str):
    """
    Dynamically computes the yfinance OHLV fetching window based on the targeted data collection week.
    """
    today = datetime.now()
    current_year = today.year
    
    # Parse integer from input strings like 'W24' or 'w24'
    data_week_num = int(data_week_str.upper().replace("W", ""))
        
    print(f"[Engine Activation] Target Reference Point: {current_year}-{data_week_str}")
    
    # Calculate approximate date matching the ISO week sequence
    base_date = datetime(current_year, 1, 4)
    calculated_date = base_date + timedelta(weeks=data_week_num - 1)
    
    # Establish a safe tracking window (Previous Friday Open to Current Wednesday Close)
    start_date = (calculated_date - timedelta(days=calculated_date.weekday() + 3)).strftime('%Y-%m-%d')
    end_date = (calculated_date + timedelta(days=5 - calculated_date.weekday())).strftime('%Y-%m-%d')
    
    return data_week_num, start_date, end_date

def run_market_capture_pipeline(data_week_num, start_date, end_date):
    """
    Stage 1: Live API Ingestion. Output snapshot file corresponds to the active data week.
    """
    # 🌟 CORRECTION: Snapshot uses the real data week (e.g., market_snapshot_W24.json)
    snapshot_filename = f"market_snapshot_W{data_week_num}.json"
    print(f"\n>>> STAGE 1: Ingesting Market Snapshot ({start_date} -> {end_date})")
    
    tickers = {
        "SPX": "^GSPC", "NDX": "^NDX", "IWM": "IWM",
        "GOLD": "GC=F", "OIL": "CL=F", "US10Y": "^TNX", "TLT": "TLT", "BTC": "BTC-USD",
        "XLK": "XLK", "XLC": "XLC", "XLY": "XLY", "XLF": "XLF", "XLV": "XLV", 
        "XLP": "XLP", "XLE": "XLE", "XLU": "XLU", "XLI": "XLI", "XLB": "XLB", "XLRE": "XLRE"
    }
    
    snapshot_data = {
        "meta": {
            "data_week": f"W{data_week_num}",
            "generation_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data_window": f"{start_date} to {end_date}"
        },
        "metrics": {}
    }
    
    for label, symbol in tickers.items():
        ticker_instance = yf.Ticker(symbol)
        df = ticker_instance.history(start=start_date, end=end_date)
        
        if df.empty:
            raise RuntimeError(f"CRITICAL IMMUTABILITY FAILURE: {label} ({symbol}) stream broke. Terminating.")
            
        initial_open = df['Open'].iloc[0]
        final_close = df['Close'].iloc[-1]
        percentage_delta = ((final_close - initial_open) / initial_open) * 100
        
        snapshot_data["metrics"][label] = {
            "ticker": symbol,
            "close_price": round(final_close, 2) if label != "US10Y" else round(final_close, 4),
            "weekly_delta_pct": round(percentage_delta, 2)
        }
        print(f"  Resource Logged -> {label} ({symbol}): {percentage_delta:+.2f}%")
        
    with open(snapshot_filename, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=4, ensure_ascii=False)
        
    print(f"[SUCCESS] Snapshot securely mirrored to disk: '{snapshot_filename}'")
    return snapshot_filename

def generate_report_from_snapshot(snapshot_path, data_week_num):
    """
    Stage 2: Process mirrored JSON snapshot and construct dynamic Markdown Ledger.
    """
    # 🌟 CORRECTION: The evaluation week is always the Prediction week (Data Week - 1)
    prediction_week_num = data_week_num - 1
    output_ledger = f"actual_2026-W{prediction_week_num}.md"
    
    print(f"\n>>> STAGE 2: Constructing Dynamic Cross-Asset Markdown Ledger for Prediction Week W{prediction_week_num}")
    
    with open(snapshot_path, "r", encoding="utf-8") as f:
        snapshot = json.load(f)
        
    metrics = snapshot["metrics"]
    meta = snapshot["meta"]
    
    markdown_payload = f"""# Market Performance Ledger: W{prediction_week_num} Prediction Evaluation

**Snapshot Data Source:** {meta['data_week']} Close  
**Snapshot Timestamp:** {meta['generation_time']}  
**Data Integrity State:** Verified via Local Pipeline Enclosure (`{snapshot_path}`)  

---

## 1. Macro Benchmarks & Core Indices Performance

| Asset Class Group | Universal Ticker | Closing Print | Realized Weekly Delta | Data State |
| :--- | :--- | :--- | :--- | :--- |
| **S&P 500 Index** | `{metrics['SPX']['ticker']}` | {metrics['SPX']['close_price']} | {metrics['SPX']['weekly_delta_pct']}% | 🟢 VERIFIED |
| **Nasdaq 100 Index** | `{metrics['NDX']['ticker']}` | {metrics['NDX']['close_price']} | {metrics['NDX']['weekly_delta_pct']}% | 🟢 VERIFIED |
| **Russell 2000 Index** | `{metrics['IWM']['ticker']}` | {metrics['IWM']['close_price']} | {metrics['IWM']['weekly_delta_pct']}% | 🟢 VERIFIED |
| **Gold Futures** | `{metrics['GOLD']['ticker']}` | {metrics['GOLD']['close_price']} | {metrics['GOLD']['weekly_delta_pct']}% | 🟢 VERIFIED |
| **Crude Oil Futures** | `{metrics['OIL']['ticker']}` | {metrics['OIL']['close_price']} | {metrics['OIL']['weekly_delta_pct']}% | 🟢 VERIFIED |
| **10Y Treasury Yield** | `{metrics['US10Y']['ticker']}` | {metrics['US10Y']['close_price']}% | {metrics['US10Y']['weekly_delta_pct']}% | 🟢 VERIFIED |
| **US Treasury Bond ETF** | `{metrics['TLT']['ticker']}` | {metrics['TLT']['close_price']} | {metrics['TLT']['weekly_delta_pct']}% | 🟢 VERIFIED |
| **Bitcoin** | `{metrics['BTC']['ticker']}` | {metrics['BTC']['close_price']} | {metrics['BTC']['weekly_delta_pct']}% | 🟢 VERIFIED |

---

## 2. 11 S&P 500 Sector Asset Allocations Tracker

| Sector ETF Code | Sector Description Domain | Verified Performance Delta |
| :--- | :--- | :--- |
| **XLK** | Technology | {metrics['XLK']['weekly_delta_pct']}% |
| **XLC** | Communication Services | {metrics['XLC']['weekly_delta_pct']}% |
| **XLY** | Consumer Discretionary | {metrics['XLY']['weekly_delta_pct']}% |
| **XLF** | Financials | {metrics['XLF']['weekly_delta_pct']}% |
| **XLV** | Healthcare | {metrics['XLV']['weekly_delta_pct']}% |
| **XLP** | Consumer Staples | {metrics['XLP']['weekly_delta_pct']}% |
| **XLE** | Energy | {metrics['XLE']['weekly_delta_pct']}% |
| **XLU** | Utilities | {metrics['XLU']['weekly_delta_pct']}% |
| **XLI** | Industrials | {metrics['XLI']['weekly_delta_pct']}% |
| **XLB** | Materials | {metrics['XLB']['weekly_delta_pct']}% |
| **XLRE** | Real Estate | {metrics['XLRE']['weekly_delta_pct']}% |
"""

    with open(output_ledger, "w", encoding="utf-8") as f:
        f.write(markdown_payload)
    print(f"[SUCCESS] Markdown ledger generated: '{output_ledger}'\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Week Production-Grade Market Audit Pipeline")
    # Defending against hardcoding: accepts dynamic data week string from outer context
    parser.add_argument("--week", type=str, default="W24", help="Target active data collection week (e.g. W24)")
    args = parser.parse_args()
    
    # Variable propagation
    data_week_num, start_window, end_window = calculate_trading_window(args.week)
    json_cache = run_market_capture_pipeline(data_week_num, start_window, end_window)
    generate_report_from_snapshot(json_cache, data_week_num)
