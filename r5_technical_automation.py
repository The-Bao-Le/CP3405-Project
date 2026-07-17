from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import argparse
import json
import time

import pandas as pd
import yfinance as yf
import mplfinance as mpf


NUMBER_OF_CHART_DAYS = 15
HISTORY_DAYS = 365
DOWNLOAD_RETRIES = 3

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


def normalize_week(week_value):
    """
    Normalize 29, '29', 'w29', or 'W29' to 'W29'.
    """
    raw = str(week_value).strip().upper()

    if raw.startswith("W"):
        raw = raw[1:]

    try:
        week_number = int(raw)
    except ValueError as exc:
        raise ValueError(
            f"Invalid market week: {week_value}. Use a value such as W29."
        ) from exc

    if not 1 <= week_number <= 53:
        raise ValueError("Market week must be between W01 and W53.")

    return f"W{week_number:02d}"


def calculate_trading_window(market_week, market_year):
    """
    Calculate a historical data window ending on the Friday of the requested
    ISO market week.

    yfinance treats the end date as exclusive, so Saturday is supplied as
    the end date in order to include Friday.
    """
    market_week = normalize_week(market_week)
    week_number = int(market_week[1:])

    monday = datetime.fromisocalendar(market_year, week_number, 1)
    friday = monday + timedelta(days=4)

    # Prevent requesting dates in the future during a midweek/manual run.
    effective_last_date = min(friday.date(), datetime.now().date())

    start_date = (
        datetime.combine(effective_last_date, datetime.min.time())
        - timedelta(days=HISTORY_DAYS)
    ).date()

    end_date_exclusive = effective_last_date + timedelta(days=1)

    print(f"Market week: {market_year}-{market_week}")
    print(f"Data window: {start_date} to {effective_last_date}")

    return (
        start_date.isoformat(),
        end_date_exclusive.isoformat(),
        effective_last_date.isoformat(),
    )


def flatten_yfinance_columns(dataframe):
    """
    Flatten MultiIndex columns sometimes returned by yfinance.
    """
    dataframe = dataframe.copy()

    if isinstance(dataframe.columns, pd.MultiIndex):
        dataframe.columns = dataframe.columns.get_level_values(0)

    dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()].copy()
    return dataframe


def validate_market_data(dataframe, symbol):
    """
    Validate downloaded OHLCV data.
    """
    if dataframe.empty:
        raise ValueError(f"No market data returned for {symbol}.")

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

    if dataframe.empty:
        raise ValueError(
            f"{symbol} contains no valid OHLC rows after cleaning."
        )

    dataframe.index = pd.to_datetime(dataframe.index)

    if getattr(dataframe.index, "tz", None) is not None:
        dataframe.index = dataframe.index.tz_localize(None)

    return dataframe


def download_market_data(
    symbol,
    start_date,
    end_date,
    retries=DOWNLOAD_RETRIES,
):
    """
    Download market data with retries and a fallback method.
    """
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            dataframe = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False,
            )
            return validate_market_data(dataframe, symbol)

        except Exception as exc:
            last_error = exc
            print(
                f"WARNING: yf.download failed for {symbol}, "
                f"attempt {attempt}/{retries}: {exc}"
            )

        try:
            dataframe = yf.Ticker(symbol).history(
                start=start_date,
                end=end_date,
                interval="1d",
                auto_adjust=False,
                actions=False,
            )
            return validate_market_data(dataframe, symbol)

        except Exception as exc:
            last_error = exc
            print(
                f"WARNING: Ticker.history failed for {symbol}, "
                f"attempt {attempt}/{retries}: {exc}"
            )

        if attempt < retries:
            time.sleep(attempt * 2)

    raise RuntimeError(
        f"Unable to download valid data for {symbol}. "
        f"Last error: {last_error}"
    )


def calculate_ema(dataframe, column, period):
    """
    Calculate an exponential moving average.
    """
    dataframe = dataframe.copy()
    dataframe[f"EMA_{period}"] = (
        dataframe[column]
        .astype(float)
        .ewm(span=period, adjust=False)
        .mean()
    )
    return dataframe


def calculate_support_resistance(
    dataframe,
    lookback=60,
    pivot_window=3,
):
    """
    Calculate support and resistance from recent pivot lows and highs.

    Support is the nearest valid pivot low below the current close.
    Resistance is the nearest valid pivot high above the current close.

    The program does not create artificial levels using plus or minus 5%.
    """
    recent = dataframe.tail(lookback).copy()

    if len(recent) < (pivot_window * 2 + 1):
        return None, None

    current_close = float(recent["Close"].iloc[-1])

    pivot_lows = []
    pivot_highs = []

    for index in range(
        pivot_window,
        len(recent) - pivot_window,
    ):
        high_window = recent["High"].iloc[
            index - pivot_window:index + pivot_window + 1
        ]
        low_window = recent["Low"].iloc[
            index - pivot_window:index + pivot_window + 1
        ]

        current_high = float(recent["High"].iloc[index])
        current_low = float(recent["Low"].iloc[index])

        if current_high == float(high_window.max()):
            pivot_highs.append(current_high)

        if current_low == float(low_window.min()):
            pivot_lows.append(current_low)

    valid_supports = [
        level for level in pivot_lows
        if level < current_close
    ]
    valid_resistances = [
        level for level in pivot_highs
        if level > current_close
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

    return (
        round(support, 4) if support is not None else None,
        round(resistance, 4) if resistance is not None else None,
    )


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


def create_chart(
    dataframe,
    label,
    asset_name,
    market_week,
    output_directory,
):
    """
    Generate a candlestick chart with EMA 8 and EMA 21.
    """
    chart_directory = output_directory / "charts" / market_week
    chart_directory.mkdir(parents=True, exist_ok=True)

    chart_dataframe = dataframe.tail(NUMBER_OF_CHART_DAYS).copy()
    chart_path = chart_directory / f"chart_{label}_{market_week}.png"

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
            "fname": str(chart_path),
            "dpi": 120,
            "pad_inches": 0.5,
        },
    )

    print(f"Generated chart: {chart_path}")
    return chart_path


def analyze_asset(
    label,
    asset_config,
    start_date,
    end_date,
    market_week,
    output_directory,
):
    """
    Download, analyze, and chart one asset.
    """
    symbol = asset_config["symbol"]
    asset_name = asset_config["name"]

    print(f"Processing {label}: {asset_name} ({symbol})")

    dataframe = download_market_data(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )

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
        dataframe=dataframe,
        label=label,
        asset_name=asset_name,
        market_week=market_week,
        output_directory=output_directory,
    )

    relative_chart_path = chart_path.relative_to(output_directory)

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
        "chart_file": relative_chart_path.as_posix(),
        "data_rows": int(len(dataframe)),
    }


def validate_snapshot(snapshot):
    """
    Stop the script before writing an empty JSON file.
    """
    metrics = snapshot.get("metrics", {})

    if not metrics:
        raise RuntimeError(
            "Snapshot validation failed: metrics is empty. "
            "No JSON file will be written."
        )

    if "SPX" not in metrics:
        raise RuntimeError(
            "Snapshot validation failed: SPX benchmark is missing."
        )

    if len(metrics) < 3:
        raise RuntimeError(
            f"Snapshot validation failed: only {len(metrics)} assets "
            "were successfully processed."
        )


def get_metric(metrics, label, field):
    """
    Safely extract one value from the metrics dictionary.
    """
    return metrics.get(label, {}).get(field, "N/A")


def format_level(value, missing_text):
    """
    Format support and resistance values.
    """
    if value in (None, "N/A"):
        return missing_text

    if isinstance(value, (int, float)):
        return f"{value:.2f}"

    return str(value)


def generate_spx_summary(metrics, market_week):
    """
    Generate the executive SPX summary.
    """
    return (
        f"For {market_week}, the R5 Technical Agent shows a "
        f"**{get_metric(metrics, 'SPX', 'bias')}** technical bias "
        f"for the S&P 500. SPX closed at "
        f"**{get_metric(metrics, 'SPX', 'close_price')}**, compared "
        f"with its 8-day EMA at "
        f"**{get_metric(metrics, 'SPX', 'ema_8')}** and its 21-day "
        f"EMA at **{get_metric(metrics, 'SPX', 'ema_21')}**. "
        f"The current trend is classified as "
        f"**{get_metric(metrics, 'SPX', 'trend')}**. Key support is "
        f"**{format_level(get_metric(metrics, 'SPX', 'support'), 'not identified')}**, "
        f"while resistance is "
        f"**{format_level(get_metric(metrics, 'SPX', 'resistance'), 'not identified')}**. "
        f"Signal confidence is "
        f"**{get_metric(metrics, 'SPX', 'confidence')}**."
    )


def generate_summary_table(metrics):
    """
    Generate a cross-asset Markdown table.
    """
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


def generate_asset_section(metrics, label):
    """
    Generate one full asset section in Markdown.
    """
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
* **Support:** {format_level(get_metric(metrics, label, 'support'), 'No clear support')}
* **Resistance:** {format_level(get_metric(metrics, label, 'resistance'), 'No clear nearby resistance')}
"""


def generate_report(snapshot, output_path):
    """
    Generate a complete Markdown technical report.
    """
    metrics = snapshot["metrics"]
    meta = snapshot["meta"]
    market_week = meta["market_week"]

    report_sections = [
        f"# R5 Technical Agent Report: {market_week}",
        "## Run Information",
        (
            f"* **Market year:** {meta['market_year']}\n"
            f"* **Generation time:** {meta['generation_time']}\n"
            f"* **Data window:** {meta['data_window_start']} to "
            f"{meta['data_window_end']}\n"
            f"* **Successful assets:** "
            f"{meta['successful_asset_count']}\n"
            f"* **Failed assets:** {meta['failed_asset_count']}"
        ),
        "## Executive Market Verdict",
        generate_spx_summary(metrics, market_week),
        "## Cross-Asset Technical Matrix",
        generate_summary_table(metrics),
    ]

    for label in ASSETS:
        if label in metrics:
            report_sections.append(
                generate_asset_section(metrics, label)
            )

    if snapshot.get("errors"):
        error_lines = [
            f"* **{label}:** {message}"
            for label, message in snapshot["errors"].items()
        ]

        report_sections.extend(
            [
                "## Download or Processing Warnings",
                "\n".join(error_lines),
            ]
        )

    report_sections.extend(
        [
            "## Methodology Note",
            (
                "Trend and bias are derived from the latest close, EMA 8, "
                "and EMA 21. Support and resistance are derived from recent "
                "pivot lows and highs. The program does not fabricate "
                "percentage-based support or resistance levels."
            ),
        ]
    )

    output_path.write_text(
        "\n\n".join(report_sections),
        encoding="utf-8",
    )

    print(f"Generated Markdown report: {output_path}")


def run_pipeline(
    market_week,
    market_year,
    output_directory,
):
    """
    Run the complete 14-asset analysis pipeline.
    """
    market_week = normalize_week(market_week)
    output_directory.mkdir(parents=True, exist_ok=True)

    start_date, end_date, effective_last_date = calculate_trading_window(
        market_week=market_week,
        market_year=market_year,
    )

    snapshot = {
        "meta": {
            "agent": "R5 Technical Agent",
            "market_week": market_week,
            "market_year": market_year,
            "generation_time": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "data_source": "Yahoo Finance via yfinance",
            "data_window_start": start_date,
            "data_window_end": effective_last_date,
            "requested_asset_count": len(ASSETS),
            "successful_asset_count": 0,
            "failed_asset_count": 0,
        },
        "metrics": {},
        "errors": {},
    }

    for label, asset_config in ASSETS.items():
        try:
            result = analyze_asset(
                label=label,
                asset_config=asset_config,
                start_date=start_date,
                end_date=end_date,
                market_week=market_week,
                output_directory=output_directory,
            )

            snapshot["metrics"][label] = result
            print(f"SUCCESS: {label}")

        except Exception as exc:
            snapshot["errors"][label] = str(exc)
            print(f"ERROR: {label}: {exc}")

    snapshot["meta"]["successful_asset_count"] = len(
        snapshot["metrics"]
    )
    snapshot["meta"]["failed_asset_count"] = len(
        snapshot["errors"]
    )

    # Critical: fail before writing an empty output file.
    validate_snapshot(snapshot)

    # Unified file names expected by the GitHub workflow.
    json_path = output_directory / (
        f"technical_agent_{market_week}.json"
    )
    markdown_path = output_directory / (
        f"technical_agent_{market_week}.md"
    )

    json_path.write_text(
        json.dumps(
            snapshot,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    generate_report(snapshot, markdown_path)

    print("=" * 72)
    print(f"Generated JSON: {json_path}")
    print(f"Generated Markdown: {markdown_path}")
    print(
        f"Successful assets: "
        f"{len(snapshot['metrics'])}/{len(ASSETS)}"
    )
    print("=" * 72)

    return json_path, markdown_path


def parse_arguments():
    """
    Parse command-line arguments.
    """
    current_iso = datetime.now().isocalendar()

    parser = argparse.ArgumentParser(
        description="R5 Technical Analysis Automation Engine"
    )

    parser.add_argument(
        "--market-week",
        required=True,
        help="Target ISO market week, for example W29.",
    )

    parser.add_argument(
        "--year",
        type=int,
        default=current_iso.year,
        help="ISO market year. Defaults to the current ISO year.",
    )

    parser.add_argument(
        "--output-dir",
        default=".",
        help=(
            "Directory for JSON, Markdown, and charts. "
            "Defaults to the repository root."
        ),
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print(
        f"--- R5 TECHNICAL ENGINE RUNNING FOR "
        f"{args.year}-{normalize_week(args.market_week)} ---"
    )

    run_pipeline(
        market_week=args.market_week,
        market_year=args.year,
        output_directory=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()
