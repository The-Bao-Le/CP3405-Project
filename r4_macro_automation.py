from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from collectors import ap_news, cme_fedwatch, earnings_whispers, finviz, trading_economics, treasury

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

COLLECTORS = {
    "treasury": treasury.collect,
    "calendar": trading_economics.collect,
    "ap": ap_news.collect,
    "finviz": finviz.collect,
    "earnings": earnings_whispers.collect,
    "fedwatch": cme_fedwatch.collect,
}


def export_csv(name: str, data: list[dict]) -> None:
    pd.DataFrame(data).to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")


def markdown_report(results: dict) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# Automated Market Intelligence Report", "", f"Generated: {stamp}", ""]
    for name, result in results.items():
        status = "OK" if result.ok else ("STALE CACHE" if result.stale_cache else "FAILED")
        lines += [f"## {result.source}", "", f"Status: **{status}**  ", f"Method: {result.method}  ", f"Fetched at: {result.fetched_at}  "]
        if result.error:
            lines += [f"Note: {result.error}  "]
        lines.append("")
        if result.data:
            df = pd.DataFrame(result.data[:15]).fillna("")
            lines += [df.to_markdown(index=False), ""]
        else:
            lines += ["No data available.", ""]
    return "\n".join(lines)


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="CP3405 R4 reusable market-data automation")
    parser.add_argument("--sources", nargs="*", choices=COLLECTORS, default=list(COLLECTORS), help="Collectors to run")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if any live collector fails")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    results = {}
    for name in args.sources:
        logging.info("Collecting %s", name)
        result = COLLECTORS[name]()
        results[name] = result
        export_csv(name, result.data)
        (OUT / f"{name}.json").write_text(json.dumps(result.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        logging.info("%s: ok=%s rows=%d cache=%s", name, result.ok, len(result.data), result.stale_cache)

    (OUT / "weekly_market_report.md").write_text(markdown_report(results), encoding="utf-8")
    manifest = {name: r.as_dict() | {"data": f"{len(r.data)} rows"} for name, r in results.items()}
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [r for r in results.values() if not r.ok and not r.stale_cache]
    return 2 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
