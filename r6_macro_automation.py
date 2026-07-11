from __future__ import annotations

import argparse
import json
import math
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yfinance as yf


TICKERS: dict[str, str] = {
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

REQUIRED_LABELS: set[str] = {
    "SPX",
    "NDX",
    "IWM",
    "XLK",
    "XLC",
    "XLY",
    "XLF",
    "XLV",
    "XLP",
    "XLE",
    "XLU",
    "XLI",
    "XLB",
    "XLRE",
}

SECTOR_ROWS: tuple[tuple[str, str], ...] = (
    ("XLK", "Technology"),
    ("XLC", "Communication Services"),
    ("XLY", "Consumer Discretionary"),
    ("XLF", "Financials"),
    ("XLV", "Health Care"),
    ("XLP", "Consumer Staples"),
    ("XLE", "Energy"),
    ("XLU", "Utilities"),
    ("XLI", "Industrials"),
    ("XLB", "Materials"),
    ("XLRE", "Real Estate"),
)

CORE_ROWS: tuple[tuple[str, str], ...] = (
    ("SPX", "S&P 500"),
    ("NDX", "Nasdaq 100"),
    ("IWM", "Russell 2000"),
    ("GOLD", "Gold"),
    ("OIL", "Crude Oil"),
    ("US10Y", "10Y Treasury Yield"),
    ("TLT", "TLT"),
    ("BTC", "Bitcoin"),
)


class PipelineError(RuntimeError):
    """Raised when the pipeline cannot produce a complete required dataset."""


def normalize_week(week_str: str) -> str:
    """Return an ISO week in W01-W53 format."""
    cleaned = week_str.upper().strip()
    if cleaned.startswith("W"):
        cleaned = cleaned[1:]

    if not cleaned.isdigit():
        raise ValueError(f"Invalid week value: {week_str!r}. Use a value such as W28.")

    week_num = int(cleaned)
    if not 1 <= week_num <= 53:
        raise ValueError(f"ISO week must be between W01 and W53, received W{week_num}.")

    return f"W{week_num:02d}"


def week_number(week_str: str) -> int:
    """Extract the integer ISO week number."""
    return int(normalize_week(week_str)[1:])


def calculate_trading_window(
    market_year: int,
    market_week_str: str,
) -> tuple[date, date, date, date, date]:
    """Calculate the target week and a holiday-safe download window.

    Returns:
        market_monday: Monday of the requested ISO week.
        market_friday: Friday of the requested ISO week.
        baseline_target: Previous Friday; the code falls back to the nearest
            earlier available session when that Friday is a market holiday.
        fetch_start: Earlier date used to ensure fallback data is available.
        fetch_end: Exclusive yfinance end date (Saturday after market Friday),
            which includes Friday but excludes Saturday BTC data.
    """
    normalized_week = normalize_week(market_week_str)
    week_num = week_number(normalized_week)

    try:
        market_monday = datetime.fromisocalendar(market_year, week_num, 1).date()
    except ValueError as exc:
        raise ValueError(
            f"{market_year}-{normalized_week} is not a valid ISO week."
        ) from exc

    market_friday = market_monday + timedelta(days=4)
    baseline_target = market_monday - timedelta(days=3)

    # The extra lookback handles holidays and temporary missing sessions.
    fetch_start = baseline_target - timedelta(days=14)

    # yfinance's end date is exclusive. Saturday therefore includes Friday
    # market data while preventing BTC from extending into Saturday.
    fetch_end = market_monday + timedelta(days=5)

    print(f"Market period: {market_year}-{normalized_week}")
    print(f"Target week: {market_monday} to {market_friday}")
    print(f"Baseline target: {baseline_target}")
    print(f"Download window: {fetch_start} to {fetch_end} (end exclusive)")

    return (
        market_monday,
        market_friday,
        baseline_target,
        fetch_start,
        fetch_end,
    )


def fetch_history_with_retry(
    symbol: str,
    start_date: date,
    end_date: date,
    attempts: int = 3,
    retry_delay_seconds: int = 3,
):
    """Fetch daily raw price history with basic transient-error retries."""
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            df = yf.Ticker(symbol).history(
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                interval="1d",
                auto_adjust=False,
                actions=False,
            )
            if not df.empty:
                return df

            print(
                f"WARNING: Empty response for {symbol} "
                f"(attempt {attempt}/{attempts})."
            )
        except Exception as exc:  # yfinance may raise several network errors
            last_error = exc
            print(
                f"WARNING: Fetch failed for {symbol} "
                f"(attempt {attempt}/{attempts}): {exc}"
            )

        if attempt < attempts:
            time.sleep(retry_delay_seconds)

    if last_error is not None:
        print(f"ERROR: Final fetch error for {symbol}: {last_error}")

    return None


def extract_week_metric(
    df,
    baseline_target: date,
    market_monday: date,
    market_friday: date,
) -> dict[str, Any] | None:
    """Return close-to-close weekly data using holiday-safe session selection."""
    if df is None or df.empty or "Close" not in df.columns:
        return None

    clean_df = df.dropna(subset=["Close"]).copy()
    if clean_df.empty:
        return None

    clean_df["_session_date"] = [timestamp.date() for timestamp in clean_df.index]

    baseline_df = clean_df[clean_df["_session_date"] <= baseline_target]
    current_week_df = clean_df[
        (clean_df["_session_date"] >= market_monday)
        & (clean_df["_session_date"] <= market_friday)
    ]

    if baseline_df.empty or current_week_df.empty:
        return None

    baseline_row = baseline_df.iloc[-1]
    final_row = current_week_df.iloc[-1]

    baseline_close = float(baseline_row["Close"])
    final_close = float(final_row["Close"])

    if (
        not math.isfinite(baseline_close)
        or not math.isfinite(final_close)
        or baseline_close == 0
    ):
        return None

    weekly_delta_pct = ((final_close - baseline_close) / baseline_close) * 100

    return {
        "baseline_date": baseline_row["_session_date"].isoformat(),
        "baseline_close": round(baseline_close, 4),
        "final_date": final_row["_session_date"].isoformat(),
        "close_price": round(final_close, 4),
        "weekly_delta_pct": round(weekly_delta_pct, 2),
    }


def run_market_capture_pipeline(
    market_year: int,
    market_week_str: str,
    market_monday: date,
    market_friday: date,
    baseline_target: date,
    fetch_start: date,
    fetch_end: date,
) -> Path:
    """Fetch all instruments, validate required coverage, and write JSON."""
    normalized_week = normalize_week(market_week_str)
    snapshot_path = Path(f"market_snapshot_{normalized_week}.json")

    snapshot_data: dict[str, Any] = {
        "meta": {
            "market_year": market_year,
            "market_week": normalized_week,
            "generation_time_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "target_week": f"{market_monday} to {market_friday}",
            "baseline_target": baseline_target.isoformat(),
            "download_window": (
                f"{fetch_start.isoformat()} to {fetch_end.isoformat()} "
                "(end exclusive)"
            ),
            "return_method": (
                "Previous Friday close (or nearest earlier trading-day close) "
                "to final available close in the target ISO week"
            ),
            "price_adjustment": "Raw Close (auto_adjust=False)",
        },
        "metrics": {},
    }

    failed_labels: list[str] = []

    for label, symbol in TICKERS.items():
        print(f"\nFetching {label} ({symbol})...")
        df = fetch_history_with_retry(symbol, fetch_start, fetch_end)
        metric = extract_week_metric(
            df,
            baseline_target=baseline_target,
            market_monday=market_monday,
            market_friday=market_friday,
        )

        if metric is None:
            print(f"WARNING: Complete weekly metric unavailable for {label} ({symbol}).")
            failed_labels.append(label)
            continue

        snapshot_data["metrics"][label] = {
            "ticker": symbol,
            **metric,
        }

        print(
            f"Captured {label}: {metric['baseline_date']} close "
            f"{metric['baseline_close']} -> {metric['final_date']} close "
            f"{metric['close_price']} ({metric['weekly_delta_pct']:+.2f}%)"
        )

    missing_required = sorted(
        REQUIRED_LABELS - set(snapshot_data["metrics"].keys())
    )
    optional_missing = sorted(set(failed_labels) - REQUIRED_LABELS)

    snapshot_data["meta"]["required_instruments_complete"] = not missing_required
    snapshot_data["meta"]["missing_required"] = missing_required
    snapshot_data["meta"]["missing_optional"] = optional_missing

    if missing_required:
        raise PipelineError(
            "Required market data is incomplete. Missing: "
            + ", ".join(missing_required)
        )

    with snapshot_path.open("w", encoding="utf-8") as file:
        json.dump(snapshot_data, file, indent=4, ensure_ascii=False)

    print(f"\nGenerated: {snapshot_path}")
    if optional_missing:
        print(
            "WARNING: Optional instruments missing: "
            + ", ".join(optional_missing)
        )

    return snapshot_path


def get_metric(metrics: dict[str, Any], key: str, field: str) -> Any:
    """Read a metric field safely."""
    return metrics.get(key, {}).get(field)


def format_number(value: Any, decimals: int = 4) -> str:
    """Format a numeric table value without producing N/A%."""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return f"{float(value):.{decimals}f}"
    return str(value)


def format_pct(value: Any) -> str:
    """Format a percentage with a sign."""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return f"{float(value):+.2f}%"
    return str(value)


def build_core_rows(metrics: dict[str, Any]) -> str:
    """Build Markdown rows for core instruments."""
    rows: list[str] = []
    for key, display_name in CORE_ROWS:
        rows.append(
            "| "
            f"{display_name} | "
            f"{get_metric(metrics, key, 'ticker') or 'N/A'} | "
            f"{format_number(get_metric(metrics, key, 'close_price'))} | "
            f"{format_pct(get_metric(metrics, key, 'weekly_delta_pct'))} | "
            f"{get_metric(metrics, key, 'baseline_date') or 'N/A'} | "
            f"{get_metric(metrics, key, 'final_date') or 'N/A'} |"
        )
    return "\n".join(rows)


def build_sector_rows(metrics: dict[str, Any]) -> str:
    """Build Markdown rows for all 11 required sector ETFs."""
    rows: list[str] = []
    for key, sector_name in SECTOR_ROWS:
        rows.append(
            "| "
            f"{key} {sector_name} | "
            f"{format_number(get_metric(metrics, key, 'close_price'))} | "
            f"{format_pct(get_metric(metrics, key, 'weekly_delta_pct'))} | "
            f"{get_metric(metrics, key, 'baseline_date') or 'N/A'} | "
            f"{get_metric(metrics, key, 'final_date') or 'N/A'} |"
        )
    return "\n".join(rows)


def infer_actual_year(
    market_year: int,
    market_week_str: str,
    actual_week_str: str,
) -> int:
    """Handle W01 evaluating the previous year's W52/W53 correctly."""
    market_week_num = week_number(market_week_str)
    actual_week_num = week_number(actual_week_str)
    return market_year - 1 if actual_week_num > market_week_num else market_year


def generate_report_from_snapshot(
    snapshot_path: Path,
    actual_week_str: str,
) -> Path:
    """Generate the R6 Markdown actuals report from the JSON snapshot."""
    normalized_actual_week = normalize_week(actual_week_str)

    with snapshot_path.open("r", encoding="utf-8") as file:
        snapshot = json.load(file)

    metrics = snapshot["metrics"]
    meta = snapshot["meta"]
    market_year = int(meta["market_year"])
    market_week = str(meta["market_week"])
    actual_year = infer_actual_year(
        market_year,
        market_week,
        normalized_actual_week,
    )

    output_path = Path(f"actual_{actual_year}-{normalized_actual_week}.md")

    spx_change = format_pct(get_metric(metrics, "SPX", "weekly_delta_pct"))
    spx_baseline_date = get_metric(metrics, "SPX", "baseline_date") or "N/A"
    spx_final_date = get_metric(metrics, "SPX", "final_date") or "N/A"

    report = f"""# R6 Data / Actuals Agent Report: {actual_year}-{normalized_actual_week}

## 1. Evaluation Summary

**Prediction Week Evaluated:** {actual_year}-{normalized_actual_week}  
**Market Data Week Used:** {market_year}-{market_week}  
**Generated At (UTC):** {meta["generation_time_utc"]}  
**Target Week:** {meta["target_week"]}  
**Return Method:** {meta["return_method"]}  
**Price Basis:** {meta["price_adjustment"]}  
**Required Instruments Complete:** Yes  

---

## 2. Core Market Actuals

| Market | Ticker | Final Close | Weekly Change | Baseline Date | Final Date |
|---|---:|---:|---:|---:|---:|
{build_core_rows(metrics)}

---

## 3. Sector Actuals

| Sector ETF | Final Close | Weekly Change | Baseline Date | Final Date |
|---|---:|---:|---:|---:|
{build_sector_rows(metrics)}

---

## 4. R6 Monday Speaking Point

For {actual_year}-{normalized_actual_week}, the R6 Data / Actuals Agent automatically captured the completed market outcome for {market_year}-{market_week}. All three core benchmarks and all 11 S&P 500 sector ETFs were successfully recorded. Using a close-to-close comparison from {spx_baseline_date} to {spx_final_date}, the S&P 500 changed by **{spx_change}**. R10 can compare this result with the team prediction and update the cumulative calibration record.
"""

    output_path.write_text(report, encoding="utf-8")
    print(f"Generated: {output_path}")
    return output_path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="R6 Data Agent Automation Pipeline"
    )
    parser.add_argument(
        "--market-week",
        required=True,
        help="ISO market week, for example W28",
    )
    parser.add_argument(
        "--actual-week",
        required=True,
        help="Prediction week being evaluated, for example W27",
    )
    parser.add_argument(
        "--market-year",
        type=int,
        default=None,
        help=(
            "ISO market year. Defaults to the current ISO year, so the existing "
            "GitHub Actions command does not need to change."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Run the complete R6 pipeline."""
    args = parse_args()

    try:
        market_week = normalize_week(args.market_week)
        actual_week = normalize_week(args.actual_week)
        market_year = args.market_year or datetime.now().isocalendar().year

        (
            market_monday,
            market_friday,
            baseline_target,
            fetch_start,
            fetch_end,
        ) = calculate_trading_window(market_year, market_week)

        snapshot_path = run_market_capture_pipeline(
            market_year=market_year,
            market_week_str=market_week,
            market_monday=market_monday,
            market_friday=market_friday,
            baseline_target=baseline_target,
            fetch_start=fetch_start,
            fetch_end=fetch_end,
        )

        generate_report_from_snapshot(snapshot_path, actual_week)
        print("\nR6 pipeline completed successfully.")

    except (ValueError, PipelineError) as exc:
        raise SystemExit(f"R6 pipeline failed: {exc}") from exc


if __name__ == "__main__":
    main()
