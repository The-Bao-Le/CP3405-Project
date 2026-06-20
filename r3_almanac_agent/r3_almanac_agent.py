#!/usr/bin/env python3
"""
R3 Almanac Agent Automation - upgraded version

What it does:
1. Finds the Stock Trader's Almanac 2026 PDF in the same folder as this script.
2. Reads the PDF with pypdf.
3. Automatically extracts:
   - June Vital Statistics
   - W25 week-specific pattern
   - Sector seasonality rows from the Sector Index Seasonality Table
4. Writes structured outputs:
   - outputs/almanac_agent_W25.json
   - outputs/almanac_agent_W25.csv
   - outputs/almanac_agent_W25.md

Folder name does not matter.
Just put this script and the PDF in the same folder.

Run:
    pip install -r requirements.txt
    python r3_almanac_agent.py
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


WEEK = "W25"
DATE_RANGE = "2026-06-22 to 2026-06-26"
AGENT = "R3 Almanac Agent"

# ETF proxy mapping used by our team presentation.
# The PDF table uses index tickers such as S5INFT, UTY, BKX, XOI, S5MATR.
# We map them to common ETF tickers for the project output.
SECTOR_REQUESTS = {
    "XLK": {
        "pdf_ticker": "S5INFT",
        "pdf_sector": "InfoTech",
        "project_sector": "Technology",
        "desired_type": "Long",
    },
    "XLU": {
        "pdf_ticker": "UTY",
        "pdf_sector": "Utilities",
        "project_sector": "Utilities",
        "desired_type": "Long",
    },
    "XLF": {
        "pdf_ticker": "BKX",
        "pdf_sector": "Banking",
        "project_sector": "Financials",
        "desired_type": "Short",
    },
    "XLE": {
        "pdf_ticker": "XOI",
        "pdf_sector": "Oil",
        "project_sector": "Energy",
        "desired_type": "Short",
    },
    "XLB": {
        "pdf_ticker": "S5MATR",
        "pdf_sector": "Materials",
        "project_sector": "Materials",
        "desired_type": "Short",
    },
}


def script_folder() -> Path:
    return Path(__file__).resolve().parent


def find_pdf(folder: Path) -> Path:
    pdfs = list(folder.glob("*.pdf"))

    if not pdfs:
        raise FileNotFoundError(
            "No PDF found. Put Stock Trader's Almanac 2026 PDF in the same folder as this script."
        )

    exact_names = [
        "Stock Trader's Almanac 2026_L.pdf",
        "Stock Trader's Almanac 2026_L(2).pdf",
    ]

    for name in exact_names:
        for pdf in pdfs:
            if pdf.name == name:
                return pdf

    for pdf in pdfs:
        if "almanac" in pdf.name.lower():
            return pdf

    return pdfs[0]


def read_pdf_pages(pdf_path: Path) -> list[dict[str, Any]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("Missing dependency. Run: pip install -r requirements.txt") from exc

    reader = PdfReader(str(pdf_path))
    pages: list[dict[str, Any]] = []

    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        pages.append({
            "page_number": i,
            "text": text,
        })

    return pages


def normalize_minus(value: str) -> str:
    return value.replace("–", "-").replace("−", "-")


def format_percent(value: str) -> str:
    value = normalize_minus(value.strip())
    if value.startswith("-"):
        return f"{value}%"
    return f"+{value}%"


def find_page(pages: list[dict[str, Any]], include: list[str], exclude: list[str] | None = None) -> dict[str, Any]:
    exclude = exclude or []

    for page in pages:
        text = page["text"]
        if all(term in text for term in include) and not any(term in text for term in exclude):
            return page

    raise ValueError(f"Could not find page with terms: {include}")


def extract_june_vital_statistics(pages: list[dict[str, Any]]) -> dict[str, Any]:
    page = find_page(
        pages,
        include=["JUNE ALMANAC", "June Vital Statistics", "Average % Change", "Midterm Yr Avg"],
        exclude=["TABLE OF CONTENTS"],
    )

    text = re.sub(r"\s+", " ", page["text"])

    rank_match = re.search(r"Rank\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text)
    avg_match = re.search(
        r"Average % Change\s+([–−-]?\d+\.\d+)\s+([–−-]?\d+\.\d+)\s+([–−-]?\d+\.\d+)\s+([–−-]?\d+\.\d+)\s+([–−-]?\d+\.\d+)",
        text,
    )
    midterm_match = re.search(
        r"Midterm Yr Avg % Chg\s+([–−-]?\d+\.\d+)\s+([–−-]?\d+\.\d+)\s+([–−-]?\d+\.\d+)\s+([–−-]?\d+\.\d+)\s+([–−-]?\d+\.\d+)",
        text,
    )

    if not rank_match or not avg_match or not midterm_match:
        raise ValueError("Could not parse June Vital Statistics from the PDF.")

    # PDF column order: DJIA, S&P 500, NASDAQ, Russell 1K, Russell 2K
    columns = ["DJIA", "SPX", "NDX", "RUSSELL_1000", "IWM"]
    names = {
        "DJIA": "Dow Jones Industrial Average",
        "SPX": "S&P 500",
        "NDX": "NASDAQ",
        "RUSSELL_1000": "Russell 1000",
        "IWM": "Russell 2000",
    }

    ranks = rank_match.groups()
    avgs = avg_match.groups()
    midterms = midterm_match.groups()

    result: dict[str, Any] = {}
    for idx, col in enumerate(columns):
        result[col] = {
            "index": names[col],
            "june_rank": int(ranks[idx]),
            "normal_june_average_return": format_percent(avgs[idx]),
            "midterm_june_average_return": format_percent(midterms[idx]),
            "source_page": page["page_number"],
            "extraction_method": "parsed_from_june_vital_statistics_table",
        }

    # The project prediction needs SPX, NDX, IWM.
    return {
        "SPX": result["SPX"],
        "NDX": result["NDX"],
        "IWM": result["IWM"],
    }


def extract_week_specific_pattern(pages: list[dict[str, Any]]) -> dict[str, Any]:
    page = find_page(
        pages,
        include=["JUNE 2026", "Week After June Triple-Witching"],
    )

    text = re.sub(r"\s+", " ", page["text"])
    match = re.search(
        r"Week After June Triple-Witching,\s*Dow Down\s*\d+\s*of Last\s*\d+\s*Average Loss Since\s*\d{4},\s*[–−-]?\d+\.\d+%?",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError("Could not parse W25 Week After June Triple-Witching pattern.")

    evidence = match.group(0).strip()

    return {
        "name": "Week After June Triple-Witching",
        "evidence": evidence,
        "source_page": page["page_number"],
        "extraction_method": "parsed_from_weekly_planner_page",
        "interpretation": "Bearish seasonal signal for W25.",
    }


def compact_window(start_month: str, start_part: str, finish_month: str, finish_part: str) -> str:
    part_map = {
        "B": "Early",
        "M": "Mid",
        "E": "Late",
    }
    return f"{part_map.get(start_part, start_part)} {start_month} to {part_map.get(finish_part, finish_part)} {finish_month}"


def extract_sector_table_rows(pages: list[dict[str, Any]]) -> dict[str, Any]:
    table_page = find_page(
        pages,
        include=["SECTOR INDEX SEASONALITY TABLE", "Average % Return"],
    )

    # Some rows continue to the next page, so join the table page and the next page.
    page_number = table_page["page_number"]
    combined_text = table_page["text"]

    for page in pages:
        if page["page_number"] == page_number + 1:
            combined_text += "\n" + page["text"]
            break

    lines = [line.strip() for line in combined_text.splitlines() if line.strip()]

    extracted: dict[str, Any] = {}

    for project_ticker, request in SECTOR_REQUESTS.items():
        pdf_ticker = request["pdf_ticker"]
        desired_type = request["desired_type"]

        found = False

        for i, line in enumerate(lines):
            if line != pdf_ticker:
                continue

            # Expected pattern after ticker:
            # ticker, sector, type, start_month, start_part, finish_month, finish_part, 25-year, 10-year, 5-year
            chunk = lines[i:i + 10]

            if len(chunk) < 10:
                continue

            _, pdf_sector, trade_type, start_month, start_part, finish_month, finish_part, avg_25, avg_10, avg_5 = chunk

            if trade_type.lower() != desired_type.lower():
                continue

            extracted[project_ticker] = {
                "project_ticker": project_ticker,
                "project_sector": request["project_sector"],
                "pdf_ticker": pdf_ticker,
                "pdf_sector": pdf_sector,
                "signal": trade_type.upper(),
                "seasonal_window": compact_window(start_month, start_part, finish_month, finish_part),
                "average_return_25_year": format_percent(avg_25),
                "average_return_10_year": format_percent(avg_10),
                "average_return_5_year": format_percent(avg_5),
                "source_page": page_number,
                "extraction_method": "parsed_from_sector_index_seasonality_table",
            }
            found = True
            break

        if not found:
            raise ValueError(f"Could not parse sector row for {project_ticker} / {pdf_ticker}.")

    return extracted


def build_report(pdf_path: Path, pages: list[dict[str, Any]]) -> dict[str, Any]:
    monthly_stats = extract_june_vital_statistics(pages)
    week_pattern = extract_week_specific_pattern(pages)
    sector_signals = extract_sector_table_rows(pages)

    return {
        "agent": AGENT,
        "week": WEEK,
        "date_range": DATE_RANGE,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_file": pdf_path.name,
        "automation_level": "PDF parsed automatically using pypdf; outputs generated as JSON, CSV, and Markdown.",
        "cycle_context": {
            "year": "2026",
            "cycle": "U.S. midterm election year",
            "summary": "Q2-Q3 is historically the weak spot of the 4-Year Presidential Cycle.",
            "source_note": "2026 Outlook and Introduction pages mention the midterm-year weak spot.",
        },
        "monthly_vital_statistics": monthly_stats,
        "week_specific_pattern": week_pattern,
        "sector_signals": sector_signals,
        "almanac_bias": "Bearish",
        "confidence": "Medium",
        "thesis": (
            "W25 is the week after June Triple-Witching. The Almanac weekly planner shows a weak historical pattern "
            "for this week. June vital statistics are also weak in midterm years. Sector seasonality favors Technology "
            "and Utilities, while Financials, Energy, and Materials remain seasonally weak."
        ),
    }


def write_json(report: dict[str, Any], output_dir: Path) -> Path:
    path = output_dir / "almanac_agent_W25.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_csv(report: dict[str, Any], output_dir: Path) -> Path:
    path = output_dir / "almanac_agent_W25.csv"

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "category",
            "ticker",
            "name",
            "signal",
            "window_or_rank",
            "return_or_evidence",
            "source_page",
            "extraction_method",
        ])

        for ticker, item in report["monthly_vital_statistics"].items():
            writer.writerow([
                "index_stat",
                ticker,
                item["index"],
                "",
                f"June rank {item['june_rank']}",
                f"Normal June {item['normal_june_average_return']}; Midterm June {item['midterm_june_average_return']}",
                item["source_page"],
                item["extraction_method"],
            ])

        for ticker, item in report["sector_signals"].items():
            writer.writerow([
                "sector_signal",
                ticker,
                item["project_sector"],
                item["signal"],
                item["seasonal_window"],
                item["average_return_25_year"],
                item["source_page"],
                item["extraction_method"],
            ])

        wp = report["week_specific_pattern"]
        writer.writerow([
            "week_pattern",
            WEEK,
            wp["name"],
            report["almanac_bias"],
            DATE_RANGE,
            wp["evidence"],
            wp["source_page"],
            wp["extraction_method"],
        ])

    return path


def write_markdown(report: dict[str, Any], output_dir: Path) -> Path:
    path = output_dir / "almanac_agent_W25.md"

    md = f"""# R3 Almanac Agent Report - {report['week']}

## Date Range

{report['date_range']}

## Source File

{report['source_file']}

## Automation Method

{report['automation_level']}

---

## Cycle Context

- 2026 is a U.S. midterm election year.
- Q2-Q3 is historically the weak spot of the 4-Year Presidential Cycle.

---

## June Vital Statistics

| Market | June Rank | Normal June Avg | Midterm June Avg | Source Page |
|---|---:|---:|---:|---:|
"""

    for ticker, item in report["monthly_vital_statistics"].items():
        md += (
            f"| {ticker} / {item['index']} | {item['june_rank']} | "
            f"{item['normal_june_average_return']} | {item['midterm_june_average_return']} | "
            f"{item['source_page']} |\n"
        )

    wp = report["week_specific_pattern"]
    md += f"""
---

## Week-Specific Pattern

**{wp['name']}**

Evidence extracted from PDF page {wp['source_page']}:

> {wp['evidence']}

Interpretation: **{wp['interpretation']}**

---

## Sector Seasonal Signals

| ETF Proxy | Project Sector | PDF Ticker | PDF Sector | Signal | Seasonal Window | 25-Year Avg Return | Source Page |
|---|---|---|---|---|---|---:|---:|
"""

    for ticker, item in report["sector_signals"].items():
        md += (
            f"| {ticker} | {item['project_sector']} | {item['pdf_ticker']} | {item['pdf_sector']} | "
            f"{item['signal']} | {item['seasonal_window']} | {item['average_return_25_year']} | "
            f"{item['source_page']} |\n"
        )

    md += f"""
---

## Almanac Bias

**{report['almanac_bias']}**

## Confidence

**{report['confidence']}**

## Thesis

{report['thesis']}
"""

    path.write_text(md, encoding="utf-8")
    return path


def main() -> None:
    folder = script_folder()
    output_dir = folder / "outputs"
    output_dir.mkdir(exist_ok=True)

    pdf_path = find_pdf(folder)
    print(f"Using PDF: {pdf_path.name}")

    pages = read_pdf_pages(pdf_path)
    report = build_report(pdf_path, pages)

    json_path = write_json(report, output_dir)
    csv_path = write_csv(report, output_dir)
    md_path = write_markdown(report, output_dir)

    print("Generated outputs:")
    print(f"- {json_path}")
    print(f"- {csv_path}")
    print(f"- {md_path}")


if __name__ == "__main__":
    main()
