from datetime import datetime, timedelta
import yfinance as yf
import argparse
import json
import mplfinance as mpf

NUMBER_OF_CHART_DAYS = 15  # Number of trading days to include on the generated charts

def calculate_ema(dataframe, column, period):
    """
    Function to calculate Exponential Moving Averages
    :param dataframe: input dataframe
    :param column: column to calculate EMA for
    :param period: period to calculate EMA for
    :return: modified dataframe
    """
    dataframe[f"EMA_{period}"] = dataframe[column].ewm(span=period, adjust=False).mean()
    return dataframe

def calculate_support_resistance(dataframe, lookback=60, pivot_window=3):
    """
    Calculate simple support and resistance levels using recent pivot highs/lows.

    Support = nearest recent pivot low below the current close.
    Resistance = nearest recent pivot high above the current close.

    If no valid resistance exists above the current close, resistance is returned as None.
    This avoids the mistake of showing a resistance level below the current price.
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

def calculate_trading_window(market_week_str):
    market_week_str = normalize_week(market_week_str)
    current_year = datetime.now().year
    week_num = int(market_week_str.replace("W", ""))

    base_date = datetime.fromisocalendar(current_year, week_num, 1)

    start_date_output = (base_date - timedelta(days=365)).strftime("%Y-%m-%d")  # Need lots of data for accurate EMA calculation
    # Use Friday as the final trading day of the market week.
    # The workflow runs on Sunday after markets have closed.
    end_date_output = (base_date + timedelta(days=4)).strftime("%Y-%m-%d")

    print(f"Market week: {market_week_str}")
    print(f"Data window: {start_date_output} to {end_date_output}")

    return start_date_output, end_date_output

def run_technical_agent_pipeline(market_week_str, start_date_input, end_date_input):
    market_week_str = normalize_week(market_week_str)
    snapshot_filename = f"technical_agent_{market_week_str}.json"
    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tickers = {
        "SPX": "^GSPC",
        "NDX": "^NDX",
        "IWM": "IWM"
    }

    snapshot_data = {
        "meta": {
            "market_week": market_week_str,
            "generation_time": generation_time,
            "data_window": f"{start_date_input} to {end_date_input}",
        },
        "metrics": {},
    }

    for label, symbol in tickers.items():
        print(f"Fetching {label} ({symbol})...")

        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date_input, end=end_date_input)

        if df.empty:
            print(f"WARNING: No data for {label} ({symbol}). Skipped.")
            continue

        # Add required values to snapshot
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

        # Create chart
        chart_dataframe = df.tail(NUMBER_OF_CHART_DAYS)
        chart_filename = f"chart_{label}_{market_week_str}.png"
        chart_style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.edgecolor" : "black"})
        chart_title = f"{label} - {market_week_str}\nGenerated on {generation_time}"
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
    output_file = f"technical_agent-{market_week_str}.md"

    with open(snapshot_path_input, "r", encoding="utf-8") as file:
        snapshot = json.load(file)

    metrics = snapshot["metrics"]
    meta = snapshot["meta"]

    report = f"""# R5 Technical Agent Report: {meta["market_week"]}

## S&P 500 (SPX)
**Current Trend:** {get_metric(metrics, "SPX", "trend")}
* **Close Price:** {get_metric(metrics, "SPX", "close_price")}
* **8-Day EMA:** {get_metric(metrics, "SPX", "ema_8")}
* **21-Day EMA:** {get_metric(metrics, "SPX", "ema_21")}
* **Support Level:** {format_support(get_metric(metrics, "SPX", "support"))}
* **Resistance Level:** {format_resistance(get_metric(metrics, "SPX", "resistance"))}
* **Technical Bias:** {get_metric(metrics, "SPX", "bias")}
* **Confidence:** {get_metric(metrics, "SPX", "confidence")}

## NASDAQ 100 (NDX)
**Current Trend:** {get_metric(metrics, "NDX", "trend")}
* **Close Price:** {get_metric(metrics, "NDX", "close_price")}
* **8-Day EMA:** {get_metric(metrics, "NDX", "ema_8")}
* **21-Day EMA:** {get_metric(metrics, "NDX", "ema_21")}
* **Support Level:** {format_support(get_metric(metrics, "NDX", "support"))}
* **Resistance Level:** {format_resistance(get_metric(metrics, "NDX", "resistance"))}
* **Technical Bias:** {get_metric(metrics, "NDX", "bias")}
* **Confidence:** {get_metric(metrics, "NDX", "confidence")}

## Russell 2000 ETF (IWM)
**Current Trend:** {get_metric(metrics, "IWM", "trend")}
* **Close Price:** {get_metric(metrics, "IWM", "close_price")}
* **8-Day EMA:** {get_metric(metrics, "IWM", "ema_8")}
* **21-Day EMA:** {get_metric(metrics, "IWM", "ema_21")}
* **Support Level:** {format_support(get_metric(metrics, "IWM", "support"))}
* **Resistance Level:** {format_resistance(get_metric(metrics, "IWM", "resistance"))}
* **Technical Bias:** {get_metric(metrics, "IWM", "bias")}
* **Confidence:** {get_metric(metrics, "IWM", "confidence")}

## Overall Technical Verdict

{build_overall_verdict(metrics, market_week_str)}
"""

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"Generated: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="R5 Technical Agent Automation Pipeline")
    parser.add_argument("--market-week", required=True, help="Market week, e.g. W24")
    args = parser.parse_args()

    start_date, end_date = calculate_trading_window(args.market_week)
    snapshot_path = run_technical_agent_pipeline(args.market_week, start_date, end_date)
    generate_report_from_snapshot(snapshot_path, args.market_week)
