from datetime import datetime, timedelta
import yfinance as yf
import argparse
import json

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

    start_date = (base_date - timedelta(days=365)).strftime("%Y-%m-%d")  # Need lots of data for accurate EMA calculation
    end_date = (base_date + timedelta(days=6)).strftime("%Y-%m-%d")

    print(f"Market week: {market_week_str}")
    print(f"Data window: {start_date} to {end_date}")

    return start_date, end_date

def run_technical_agent_pipeline(market_week_str, start_date, end_date):
    market_week_str = normalize_week(market_week_str)
    snapshot_filename = f"technical_agent_{market_week_str}.json"

    tickers = {
        "SPX": "^GSPC",
        "NDX": "^NDX",
        "IWM": "IWM"
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

        df = calculate_ema(df, "Close", 8)
        df = calculate_ema(df, "Close", 21)
        final_close = df["Close"].iloc[-1]
        ema_8 = df["EMA_8"].iloc[-1]
        ema_21 = df["EMA_21"].iloc[-1]

        snapshot_data["metrics"][label] = {
            "ticker": symbol,
            "close_price": round(float(final_close), 4),
            "ema_8": round(float(ema_8), 4),
            "ema_21": round(float(ema_21), 4)
        }

    with open(snapshot_filename, "w", encoding="utf-8") as file:
        json.dump(snapshot_data, file, indent=4, ensure_ascii=False)

    print(f"Generated: {snapshot_filename}")
    return snapshot_filename

def get_metric(metrics, key, field):
    if key not in metrics:
        return "N/A"
    return metrics[key].get(field, "N/A")

def generate_report_from_snapshot(snapshot_path, market_week_str):
    output_file = f"technical_agent-{market_week_str}.md"

    with open(snapshot_path, "r", encoding="utf-8") as file:
        snapshot = json.load(file)

    metrics = snapshot["metrics"]
    meta = snapshot["meta"]

    report = f"""# R5 Technical Agent Report: {meta["market_week"]}

## S&P 500 (SPX)
**Current Trend:** (TODO)
* **Close Price:** {get_metric(metrics, "SPX", "close_price")}
* **8-Day EMA:** {get_metric(metrics, "SPX", "ema_8")}
* **21-Day EMA:** {get_metric(metrics, "SPX", "ema_21")}
* **Support Level:** (TODO)
* **Resistance Level:** (TODO)
* **Technical Bias:** (TODO)
* **Confidence:** (TODO)

## NASDAQ 100 (NDX)
**Current Trend:** (TODO)
* **Close Price:** {get_metric(metrics, "NDX", "close_price")}
* **8-Day EMA:** {get_metric(metrics, "NDX", "ema_8")}
* **21-Day EMA:** {get_metric(metrics, "NDX", "ema_21")}
* **Support Level:** (TODO)
* **Resistance Level:** (TODO)
* **Technical Bias:** (TODO)
* **Confidence:** (TODO)

## Russell 2000 (IWM)
**Current Trend:** (TODO)
* **Close Price:** {get_metric(metrics, "IWM", "close_price")}
* **8-Day EMA:** {get_metric(metrics, "IWM", "ema_8")}
* **21-Day EMA:** {get_metric(metrics, "IWM", "ema_21")}
* **Support Level:** (TODO)
* **Resistance Level:** (TODO)
* **Technical Bias:** (TODO)
* **Confidence:** (TODO)

## Overall Technical Verdict

For {market_week_str}, the R5 Technical Agent (TODO)). The key benchmark for the team prediction is the S&P 500 result. The SPX 8-day EMA was **{get_metric(metrics, "SPX", "ema_8")}%**. TODO.
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