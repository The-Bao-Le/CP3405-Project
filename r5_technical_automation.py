from datetime import datetime, timedelta
from pathlib import Path
import argparse
import json

import pandas as pd
import yfinance as yf
import mplfinance as mpf


NUMBER_OF_CHART_DAYS = 15
HISTORY_DAYS = 365

ASSETS = {
    "SPX": {"symbol": "^GSPC", "name": "S&P 500"},
    "NDX": {"symbol": "^NDX", "name": "NASDAQ 100"},
    "IWM": {"symbol": "IWM", "name": "Russell 2000 ETF"},
    "XLK": {"symbol": "XLK", "name": "Technology"},
    "XLU": {"symbol": "XLU", "name": "Utilities"},
    "XLF": {"symbol": "XLF", "name": "Financials"},
    "XLE": {"symbol": "XLE", "name": "Energy"},
    "XLB": {"symbol": "XLB", "name": "Materials"},
    "XLY": {"symbol": "XLY", "name": "Consumer Discretionary"},
    "XLP": {"symbol": "XLP", "name": "Consumer Staples"},
    "XLV": {"symbol": "XLV", "name": "Health Care"},
    "XLI": {"symbol": "XLI", "name": "Industrials"},
    "XLC": {"symbol": "XLC", "name": "Communication Services"},
    "XLRE": {"symbol": "XLRE", "name": "Real Estate"},
}


def normalize_week(week_str):
    """Normalize values such as '29' or 'w29' to 'W29'."""
    week_str = week_str.upper().strip()
    if not week_str.startswith("W"):
        week_str = f"W{week_str}"

    week_num = int(week_str[1:])
    if not 1 <= week_num <= 53:
        raise ValueError("Market week must be between W1 and W53.")

    return f"W{week_num:02d}"


def calculate_trading_window(market_week_str, year=None):
    """
    Build the data window for the requested ISO market week.

    yfinance's end date is exclusive, so Saturday is used to ensure that
    Friday's session is included.
    """
    market_week_str = normalize_week(market_week_str)
    year = year or datetime.now().year
    week_num = int(market_week_str[1:])

    monday = datetime.fromisocalendar(year, week_num, 1)
    friday = monday + timedelta(days=4)

    start_date = (monday - timedelta(days=HISTORY_DAYS)).strftime("%Y-%m-%d")
    end_date_exclusive = (friday + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"Market week: {year}-{market_week_str}")
    print(f"Data window: {start_date} to {friday.strftime('%Y-%m-%d')}")

    return start_date, end_date_exclusive, friday.strftime("%Y-%m-%d")


def flatten_yfinance_columns(dataframe):
    """Flatten yfinance MultiIndex columns produced by yf.download()."""
    dataframe = dataframe.copy()

    if isinstance(dataframe.columns, pd.MultiIndex):
        dataframe.columns = dataframe.columns.get_level_values(0)

    dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()].copy()
    return dataframe


def calculate_ema(dataframe, column, period):
    """Calculate an exponential moving average."""
    dataframe = dataframe.copy()
    dataframe[f"EMA_{period}"] = (
        dataframe[column]
        .ewm(span=period, adjust=False)
        .mean()
    )
    return dataframe


def calculate_support_resistance(dataframe, lookback=60, pivot_window=3):
    """
    Find the nearest valid pivot support below the current close and the
    nearest valid pivot resistance above the current close.

    No artificial resistance is created when price is above all recent
    pivot highs.
    """
    recent = dataframe.tail(lookback).copy()

    if len(recent) < (pivot_window * 2 + 1):
        return None, None

    current_close = float(recent["Close"].iloc[-1])
    pivot_lows = []
    pivot_highs = []

    for i in range(pivot_window, len(recent) - pivot_window):
        high_window = recent["High"].iloc[
            i - pivot_window:i + pivot_window + 1
        ]
        low_window = recent["Low"].iloc[
            i - pivot_window:i + pivot_window + 1
        ]

        current_high = float(recent["High"].iloc[i])
        current_low = float(recent["Low"].iloc[i])

        if current_high == float(high_window.max()):
            pivot_highs.append(current_high)

        if current_low == float(low_window.min()):
            pivot_lows.append(current_low)

    valid_supports = [level for level in pivot_lows if level < current_close]
    valid_resistances = [
        level for level in pivot_highs if level > current_close
    ]

    support = (
        max(valid_supports)
        if valid_supports
        else float(recent["Low"].min())
    )
    resistance = (
        min(valid_resistances)
        if valid_resistances
        else None
    )

    return round(support, 4), (
        round(resistance, 4) if resistance is not None else None
    )


def classify_technical_signal(close_price, ema_8, ema_21):
    """Classify trend, directional bias, and confidence."""
    if close_price > ema_8 > ema_21:
        return "Bullish / Recovery", "Bullish", "Medium"

    if close_price < ema_8 < ema_21:
        return "Bearish", "Bearish", "Medium"

    if close_price > ema_8 and ema_8 < ema_21:
        return "Mixed / Early Recovery", "Slightly Bullish", "Low"

    if close_price < ema_8 and ema_8 > ema_21:
        return "Pullback / Weakening", "Slightly Bearish", "Low"

    return "Neutral / Mixed", "Neutral", "Low"


def download_market_data(symbol, start_date, end_date):
    """Download and validate one asset's daily OHLCV data."""
    dataframe = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if dataframe.empty:
        return dataframe

    dataframe = flatten_yfinance_columns(dataframe)

    required_columns = {"Open", "High", "Low", "Close", "Volume"}
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        raise ValueError(
            f"{symbol} is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    dataframe = dataframe.dropna(
        subset=["Open", "High", "Low", "Close"]
    ).copy()

    return dataframe


def create_chart(dataframe, label, asset_name, market_week, output_dir):
    """Create a candlestick chart with EMA 8 and EMA 21."""
    chart_dataframe = dataframe.tail(NUMBER_OF_CHART_DAYS).copy()
    chart_filename = output_dir / f"chart_{label}_{market_week}.png"

    chart_style = mpf.make_mpf_style(
        base_mpf_style="yahoo",
        rc={"axes.edgecolor": "black"},
    )

    additional_plots = [
        mpf.make_addplot(
            chart_dataframe["EMA_8"],
            type="line",
            color="#ec915c",
            width=2,
            label="EMA 8",
        ),
        mpf.make_addplot(
            chart_dataframe["EMA_21"],
            type="line",
            color="#4687d3",
            width=2,
            label="EMA 21",
        ),
    ]

    mpf.plot(
        chart_dataframe,
        type="candle",
        style=chart_style,
        volume=True,
        addplot=additional_plots,
        title=f"{asset_name} ({label}) - {market_week}",
        tight_layout=True,
        savefig={
            "fname": str(chart_filename),
            "dpi": 120,
            "pad_inches": 0.5,
        },
    )

    print(f"Generated chart: {chart_filename}")
    return chart_filename


def analyze_asset(
    label,
    asset_config,
    start_date,
    end_date,
    market_week,
    output_dir,
):
    """Download, calculate indicators, classify, and chart one asset."""
    symbol = asset_config["symbol"]
    asset_name = asset_config["name"]

    print(f"Processing {label} ({symbol})...")
    dataframe = download_market_data(symbol, start_date, end_date)

    if dataframe.empty:
        print(f"WARNING: No data for {label} ({symbol}). Skipped.")
        return None

    dataframe = calculate_ema(dataframe, "Close", 8)
    dataframe = calculate_ema(dataframe, "Close", 21)

    latest_close = float(dataframe["Close"].iloc[-1])
    ema_8 = float(dataframe["EMA_8"].iloc[-1])
    ema_21 = float(dataframe["EMA_21"].iloc[-1])

    support, resistance = calculate_support_resistance(dataframe)
    trend, bias, confidence = classify_technical_signal(
        latest_close,
        ema_8,
        ema_21,
    )

    chart_path = create_chart(
        dataframe,
        label,
        asset_name,
        market_week,
        output_dir,
    )

    return {
        "ticker": symbol,
        "asset_name": asset_name,
        "last_trading_date": dataframe.index[-1].strftime("%Y-%m-%d"),
        "close_price": round(latest_close, 4),
        "ema_8": round(ema_8, 4),
        "ema_21": round(ema_21, 4),
        "support": support,
        "resistance": resistance,
        "trend": trend,
        "bias": bias,
        "confidence": confidence,
        "chart_file": chart_path.name,
    }


def get_metric(metrics, label, field):
    """Safely retrieve one field from the nested metrics dictionary."""
    return metrics.get(label, {}).get(field, "N/A")


def format_level(value, missing_text):
    """Format technical levels without fabricating a value."""
    if value in (None, "N/A"):
        return missing_text

    if isinstance(value, (int, float)):
        return f"{value:.2f}"

    return str(value)


def format_support(value):
    return format_level(value, "No clear support level found")


def format_resistance(value):
    return format_level(value, "No clear nearby resistance")


def generate_spx_summary(metrics, market_week_str):
    """Build the executive narrative from the SPX benchmark."""
    if "SPX" not in metrics:
        return (
            f"For {market_week_str}, SPX data was unavailable, so the "
            "benchmark-level verdict could not be generated."
        )

    return (
        f"For {market_week_str}, the R5 Technical Agent shows a "
        f"**{get_metric(metrics, 'SPX', 'bias')}** technical bias for "
        f"the S&P 500. SPX closed at "
        f"**{get_metric(metrics, 'SPX', 'close_price')}**, compared with "
        f"its 8-day EMA at **{get_metric(metrics, 'SPX', 'ema_8')}** and "
        f"21-day EMA at **{get_metric(metrics, 'SPX', 'ema_21')}**. "
        f"The current trend is classified as "
        f"**{get_metric(metrics, 'SPX', 'trend')}**. Key support is "
        f"around **{format_support(get_metric(metrics, 'SPX', 'support'))}**, "
        f"while resistance is "
        f"**{format_resistance(get_metric(metrics, 'SPX', 'resistance'))}**. "
        f"Signal confidence is "
        f"**{get_metric(metrics, 'SPX', 'confidence')}**."
    )


def generate_asset_section(metrics, label):
    """Build a complete Markdown section for one processed asset."""
    return f"""## {get_metric(metrics, label, 'asset_name')} ({label})

![{label} chart]({get_metric(metrics, label, 'chart_file')})

* **Yahoo ticker:** {get_metric(metrics, label, 'ticker')}
* **Last trading date:** {get_metric(metrics, label, 'last_trading_date')}
* **Current trend:** {get_metric(metrics, label, 'trend')}
* **Technical bias:** {get_metric(metrics, label, 'bias')}
* **Confidence:** {get_metric(metrics, label, 'confidence')}
* **Close price:** {get_metric(metrics, label, 'close_price')}
* **8-day EMA:** {get_metric(metrics, label, 'ema_8')}
* **21-day EMA:** {get_metric(metrics, label, 'ema_21')}
* **Support:** {format_support(get_metric(metrics, label, 'support'))}
* **Resistance:** {format_resistance(get_metric(metrics, label, 'resistance'))}
"""


def generate_summary_table(metrics):
    """Build a compact cross-asset Markdown matrix."""
    rows = [
        "| Asset | Close | EMA 8 | EMA 21 | Trend | Bias | Confidence |",
        "|---|---:|---:|---:|---|---|---|",
    ]

    for label in ASSETS:
        if label not in metrics:
            continue

        rows.append(
            f"| {label} | "
            f"{get_metric(metrics, label, 'close_price')} | "
            f"{get_metric(metrics, label, 'ema_8')} | "
            f"{get_metric(metrics, label, 'ema_21')} | "
            f"{get_metric(metrics, label, 'trend')} | "
            f"{get_metric(metrics, label, 'bias')} | "
            f"{get_metric(metrics, label, 'confidence')} |"
        )

    return "\n".join(rows)


def generate_report_from_snapshot(snapshot_path, output_dir):
    """Generate a complete dynamic Markdown report."""
    with snapshot_path.open("r", encoding="utf-8") as file:
        snapshot = json.load(file)

    metrics = snapshot["metrics"]
    meta = snapshot["meta"]
    market_week = meta["market_week"]

    report_sections = [
        f"# R5 Technical Agent Report: {market_week}",
        "## Executive Market Verdict",
        generate_spx_summary(metrics, market_week),
        "## Cross-Asset Technical Matrix",
        generate_summary_table(metrics),
    ]

    for label in ASSETS:
        if label in metrics:
            report_sections.append(generate_asset_section(metrics, label))

    report_sections.append(
        "## Methodology Note\n\n"
        "Trend and bias are derived from the relationship among the latest "
        "close, EMA 8, and EMA 21. Support and resistance use recent pivot "
        "lows and highs. A missing resistance means no valid nearby pivot "
        "high was found above the latest close; no artificial level is added."
    )

    output_file = output_dir / f"technical_agent-{market_week}.md"
    output_file.write_text(
        "\n\n".join(report_sections),
        encoding="utf-8",
    )

    print(f"Generated report: {output_file}")
    return output_file


def run_pipeline(market_week, year, output_dir):
    """Run the full 14-asset technical analysis pipeline."""
    market_week = normalize_week(market_week)
    start_date, end_date, final_market_date = calculate_trading_window(
        market_week,
        year,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    generation_time = datetime.now().isoformat(timespec="seconds")

    snapshot = {
        "meta": {
            "agent": "R5 Technical Agent",
            "market_week": market_week,
            "market_year": year,
            "generation_time": generation_time,
            "data_window_start": start_date,
            "data_window_end": final_market_date,
        },
        "metrics": {},
    }

    for label, asset_config in ASSETS.items():
        try:
            result = analyze_asset(
                label=label,
                asset_config=asset_config,
                start_date=start_date,
                end_date=end_date,
                market_week=market_week,
                output_dir=output_dir,
            )
            if result is not None:
                snapshot["metrics"][label] = result
        except Exception as exc:
            print(f"ERROR: Failed to process {label}: {exc}")

    snapshot_file = output_dir / f"technical_snapshot-{market_week}.json"
    snapshot_file.write_text(
        json.dumps(snapshot, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Generated snapshot: {snapshot_file}")

    report_file = generate_report_from_snapshot(
        snapshot_file,
        output_dir,
    )

    return snapshot_file, report_file


def main():
    parser = argparse.ArgumentParser(
        description="R5 Technical Analysis Automation Engine"
    )
    parser.add_argument(
        "--market-week",
        required=True,
        help="Target ISO market week, for example W29 or 29.",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.now().year,
        help="ISO market year. Defaults to the current year.",
    )
    parser.add_argument(
        "--output-dir",
        default="technical_output",
        help="Directory for JSON, Markdown, and chart files.",
    )
    args = parser.parse_args()

    print(
        f"--- R5 TECHNICAL ENGINE: "
        f"{args.year}-{normalize_week(args.market_week)} ---"
    )

    run_pipeline(
        market_week=args.market_week,
        year=args.year,
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()
