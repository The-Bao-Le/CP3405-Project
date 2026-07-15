from datetime import datetime, timedelta
import argparse
import json
import pandas as pd
import yfinance as yf
import mplfinance as mpf

NUMBER_OF_CHART_DAYS = 15  # Number of trading days to include on the generated charts

def calculate_ema(dataframe, column, period):
    """
    Function to calculate Exponential Moving Averages
    """
    dataframe[f"EMA_{period}"] = dataframe[column].ewm(span=period, adjust=False).mean()
    return dataframe

def calculate_support_resistance(dataframe, lookback=60, pivot_window=3):
    """
    Calculate simple support and resistance levels using recent pivot highs/lows.
    """
    recent = dataframe.tail(lookback).copy()

    if len(recent) < (pivot_window * 2 + 1):
        return None, None

    current_close = float(recent["Close"].iloc[-1])

    pivot_lows = []
    pivot_highs = []

    for i in range(pivot_window, len(recent) - pivot_window):
        high_window = recent["High"].iloc[i - pivot_window:i + pivot_window + 1]
        low_window = recent["Low"].iloc[i - pivot_window:i + pivot_window + 1]

        current_high = recent["High"].iloc[i]
        current_low = recent["Low"].iloc[i]

        if current_high == high_window.max():
            pivot_highs.append(float(current_high))

        if current_low == low_window.min():
            pivot_lows.append(float(current_low))

    support_level = None
    if pivot_lows:
        below_close = [x for x in pivot_lows if x < current_close]
        if below_close:
            support_level = max(below_close)
        else:
            support_level = min(pivot_lows)

    resistance_level = None
    if pivot_highs:
        above_close = [x for x in pivot_highs if x > current_close]
        if above_close:
            resistance_level = min(above_close)
        else:
            resistance_level = max(pivot_highs)

    return support_level, resistance_level

def get_metric(metrics_dict, label, field):
    """
    Safely extract fields from metrics nested dictionary
    """
    return metrics_dict.get(label, {}).get(field, "N/A")

def format_support(value):
    return f"{value:.2f}" if isinstance(value, (int, float)) else str(value)

def format_resistance(value):
    return f"{value:.2f}" if isinstance(value, (int, float)) else str(value)

def generate_sector_section(metrics, label, sector_name):
    """
    Helper function to generate Markdown string for a single asset sector.
    """
    spx_close = get_metric(metrics, "SPX", "close_price")
    spx_ema_8 = get_metric(metrics, "SPX", "ema_8")
    
    close = get_metric(metrics, label, "close_price")
    ema_8 = get_metric(metrics, label, "ema_8")
    ema_21 = get_metric(metrics, label, "ema_21")
    trend = get_metric(metrics, label, "trend")
    sup = get_metric(metrics, label, "support")
    res = get_metric(metrics, label, "resistance")

    return f"### {sector_name} ({label})\n* **Close:** {close}\n* **8-Day EMA:** {ema_8}\n* **21-Day EMA:** {ema_21}\n* **Trend:** {trend}\n* **Support:** {format_support(sup)}\n* **Resistance:** {format_resistance(res)}\n\n"

def generate_spx_summary(metrics, market_week_str):
    """
    Generates summary narrative using benchmark SPX technical metrics
    """
    spx_bias = get_metric(metrics, "SPX", "bias")
    spx_close = get_metric(metrics, "SPX", "close_price")
    spx_trend = get_metric(metrics, "SPX", "trend")
    spx_ema_8 = get_metric(metrics, "SPX", "ema_8")
    spx_ema_21 = get_metric(metrics, "SPX", "ema_21")
    spx_support = get_metric(metrics, "SPX", "support")
    spx_resistance = get_metric(metrics, "SPX", "resistance")

    return (
        f"For {market_week_str}, the R5 Technical Agent shows a **{spx_bias}** technical bias "
        f"for the S&P 500. SPX closed at **{spx_close}**, compared with its 8-day EMA at "
        f"**{spx_ema_8}** and 21-day EMA at **{spx_ema_21}**. The current trend is classified as "
        f"**{spx_trend}**. Key support is around **{format_support(spx_support)}**, while resistance is "
        f"**{format_resistance(spx_resistance)}**. The S&P 500 remains the main benchmark for the team prediction."
    )

def generate_report_from_snapshot(snapshot_path_input, market_week_str):
    """
    Generates markdown documentation report dynamically rendering all assets processed.
    """
    output_file = f"technical_agent-{market_week_str}.md"

    with open(snapshot_path_input, "r", encoding="utf-8") as file:
        snapshot = json.load(file)

    metrics = snapshot["metrics"]
    meta = snapshot["meta"]

    report_sections = [f"# R5 Technical Agent Report: {meta['market_week']}\n"]
    
    # Unified summary overview block at the top
    report_sections.append("## Executive Market Verdict")
    report_sections.append(generate_spx_summary(metrics, meta['market_week']))
    report_sections.append("\n---\n")

    for label in metrics.keys():
        section = f"""## {label} ({get_metric(metrics, label, 'ticker')})
**Current Trend:** {get_metric(metrics, label, 'trend')}
* **Close Price:** {get_metric(metrics, label, 'close_price')}
* **8-Day EMA:** {get_metric(metrics, label, 'ema_8')}
* **21-Day EMA:** {get_metric(metrics, label, 'ema_21')}"""
        report_sections.append(section)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n\n".join(report_sections))
    print(f"Successfully generated full technical markdown matrix: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="R5 Technical Analysis Automation Engine")
    parser.add_argument("--market-week", required=True, help="Target run week identifier (e.g. W29)")
    args = parser.parse_args()

    market_week = args.market_week
    print(f"--- R5 TECHNICAL ENGINE RUNNING FOR WEEK: {market_week} ---")

    # Complete 14 asset registries (11 Sector ETFs + 3 Benchmark Indices)
    target_tickers = [
        "SPX", "NDX", "IWM", 
        "XLK", "XLU", "XLF", "XLE", "XLB", "XLY", "XLP", "XLV", "XLI", "XLC", "XLRE"
    ]

    tickers = {
        "SPX": "^SPX",
        "NDX": "^NDX",
        "IWM": "IWM",
        "XLK": "XLK",
        "XLU": "XLU",
        "XLF": "XLF",
        "XLE": "XLE",
        "XLB": "XLB",
        "XLY": "XLY",
        "XLP": "XLP",
        "XLV": "XLV",
        "XLI": "XLI",
        "XLC": "XLC",
        "XLRE": "XLRE"
    }

    snapshot = {
        "meta": {
            "agent": "R5 Technical Agent",
            "market_week": market_week,
            "execution_time": datetime.now().isoformat()
        },
        "metrics": {}
    }

    for label in target_tickers:
        symbol = tickers[label]
        print(f"Processing historical matrix assets for: {label} ({symbol})")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120)
        
        df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
        
        if df.empty:
            print(f"Warning: No data for {label}")
            continue

        # 🛠️ CRITICAL FIX: Flatten yfinance MultiIndex columns to fit original script logic perfectly
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = calculate_ema(df, "Close", 8)
        df = calculate_ema(df, "Close", 21)
        sup, res = calculate_support_resistance(df)

        latest_close = float(df["Close"].iloc[-1])
        ema_8_val = float(df[f"EMA_8"].iloc[-1])
        ema_21_val = float(df[f"EMA_21"].iloc[-1])

        trend_status = "Bullish Phase" if latest_close > ema_8_val else "Bearish Phase"
        bias_status = "Long Strategy" if ema_8_val > ema_21_val else "Short Strategy"

        snapshot["metrics"][label] = {
            "ticker": symbol,
            "close_price": round(latest_close, 2),
            "ema_8": round(ema_8_val, 2),
            "ema_21": round(ema_21_val, 2),
            "support": round(sup, 2) if sup else latest_close * 0.95,
            "resistance": round(res, 2) if res else latest_close * 1.05,
            "trend": trend_status,
            "bias": bias_status
        }

    snapshot_file = f"technical_snapshot-{market_week}.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=4)
    print(f"Successfully secured technical snapshot data: {snapshot_file}")

    generate_report_from_snapshot(snapshot_file, market_week)

if __name__ == "__main__":
    main()
