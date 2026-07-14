from datetime import datetime, timedelta
import argparse
import json
import pandas as pd
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

    valid_supports = [level for level in pivot_lows if level < current_close]
    valid_resistances = [level for level in pivot_highs if level > current_close]

    support = max(valid_supports) if valid_supports else float(recent["Low"].min())
    resistance = min(valid_resistances) if valid_resistances else None

    return round(support, 4), round(resistance, 4) if resistance is not None else None

def classify_technical_signal(close_price, ema_8, ema_21):
    """
    Classify trend, bias, and confidence using close price and EMA alignment.
    """
    if close_price > ema_8 > ema_21:
        return "Bullish / Recovery", "Bullish", "Medium"

    if close_price < ema_8 < ema_21:
        return "Bearish", "Bearish", "Medium"

    if close_price > ema_8 and ema_8 < ema_21:
        return "Mixed / Early Recovery", "Slightly Bullish", "Low"

    if close_price < ema_8 and ema_8 > ema_21:
        return "Pullback / Weakening", "Slightly Bearish", "Low"

    return "Neutral / Mixed", "Neutral", "Low"

def normalize_week(week_str):
    week_str = week_str.upper().strip()
    if not week_str.startswith("W"):
        week_str = "W" + week_str
    return week_str

def load_r6_market_data(file_path="r6_market_data.json"):
    """
    Loads historical market data provided by R6 pipeline output.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"ERROR: Failed to load R6 data from {file_path}. Details: {e}")
        return {}

def run_technical_agent_pipeline(market_week_str):
    """
    Runs the agent pipeline parsing data from R6 local repository input.
    """
    market_week_str = normalize_week(market_week_str)
    snapshot_filename = f"technical_agent_{market_week_str}.json"
    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Complete list of required market indices and sector ETFs specified for Sprint 7
    tickers = {
        "SPX": "SPX",
        "NDX": "NDX",
        "IWM": "IWM",
        "XLK": "XLK",
        "XLF": "XLF",
        "XLV": "XLV",
        "XLY": "XLY",
        "XLE": "XLE",
        "XLC": "XLC"
    }

    r6_data = load_r6_market_data("r6_market_data.json")

    snapshot_data = {
        "meta": {
            "market_week": market_week_str,
            "generation_time": generation_time,
            "data_source": "R6 Output Pipeline",
        },
        "metrics": {},
    }

    for label, symbol in tickers.items():
        print(f"Processing {label} from R6 data...")

        if label not in r6_data or not r6_data[label]:
            print(f"WARNING: No R6 data found for {label}. Skipped.")
            continue

        df = pd.DataFrame(r6_data[label])
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        df = df.sort_index()

        if df.empty:
            print(f"WARNING: DataFrame empty for {label}. Skipped.")
            continue

        df = calculate_ema(df, "Close", 8)
        df = calculate_ema(df, "Close", 21)
        final_close = df["Close"].iloc[-1]
        ema_8 = df["EMA_8"].iloc[-1]
        ema_21 = df["EMA_21"].iloc[-1]

        support, resistance = calculate_support_resistance(df)
        trend, bias, confidence = classify_technical_signal(final_close, ema_8, ema_21)

        snapshot_data["metrics"][label] = {
            "ticker": symbol,
            "close_price": round(float(final_close), 4),
            "ema_8": round(float(ema_8), 4),
            "ema_21": round(float(ema_21), 4),
            "support": support,
            "resistance": resistance,
            "trend": trend,
            "bias": bias,
            "confidence": confidence
        }

        # Chart configuration setup
        chart_dataframe = df.tail(NUMBER_OF_CHART_DAYS)
        chart_filename = f"chart_{label}_{market_week_str}.png"
        chart_style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.edgecolor" : "black"})
        chart_title = f"{label} - {market_week_str}\nGenerated via R6 Data on {generation_time}"
        additional_plots = [
            mpf.make_addplot(chart_dataframe["EMA_8"], type="line", color="#ec915c", width=2, label="EMA 8"),
            mpf.make_addplot(chart_dataframe["EMA_21"], type="line", color="#4687d3", width=2, label="EMA 21")
        ]

        mpf.plot(chart_dataframe,
                 type="candle",
                 style=chart_style,
                 volume=True,
                 addplot=additional_plots,
                 title={"title": chart_title, "y": 1, "x": 0.58},
                 tight_layout=True,
                 savefig=dict(fname=chart_filename, dpi=100, pad_inches=0.5))
        print(f"Generated: {chart_filename}")

    with open(snapshot_filename, "w", encoding="utf-8") as file:
        json.dump(snapshot_data, file, indent=4, ensure_ascii=False)

    print(f"Generated: {snapshot_filename}")
    return snapshot_filename

def get_metric(metrics, key, field):
    if key not in metrics:
        return "N/A"
    return metrics[key].get(field, "N/A")

def format_support(value):
    if value in ["N/A", None]:
        return "No clear support level found"
    return value

def format_resistance(value):
    if value in ["N/A", None]:
        return "No clear nearby resistance"
    return value

def build_overall_verdict(metrics, market_week_str):
    spx_trend = get_metric(metrics, "SPX", "trend")
    spx_bias = get_metric(metrics, "SPX", "bias")
    spx_close = get_metric(metrics, "SPX", "close_price")
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
    
    for label in metrics.keys():
        section = f"""## {label} ({get_metric(metrics, label, 'ticker')})
**Current Trend:** {get_metric(metrics, label, 'trend')}
* **Close Price:** {get_metric(metrics, label, 'close_price')}
* **8-Day EMA:** {get_metric(metrics, label, 'ema_8')}
* **21-Day EMA:** {get_metric(metrics, label, 'ema_21')}
* **Support Level:** {format_support(get_metric(metrics, label, 'support'))}
* **Resistance Level:** {format_resistance(get_metric(metrics, label, 'resistance'))}
* **Technical Bias:** {get_metric(metrics, label, 'bias')}
* **Confidence:** {get_metric(metrics, label, 'confidence')}
"""
        report_sections.append(section)
        
    verdict_section = f"\n## Overall Technical Verdict\n\n{build_overall_verdict(metrics, market_week_str)}\n"
    report_sections.append(verdict_section)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(report_sections))

    print(f"Generated: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="R5 Technical Agent Automation Pipeline (R6 Data Source)")
    parser.add_argument("--market-week", required=True, help="Market week, e.g. W24")
    args = parser.parse_args()

    snapshot_path = run_technical_agent_pipeline(args.market_week)
    generate_report_from_snapshot(snapshot_path, args.market_week)
