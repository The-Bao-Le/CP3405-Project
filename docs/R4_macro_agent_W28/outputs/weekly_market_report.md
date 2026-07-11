# Automated Market Intelligence Report

Generated: 2026-07-11 08:23 UTC

## U.S. Treasury Interest Rates

Status: **OUTPUT INCLUDED**

The project contains structured Treasury rate data and an automated official-feed collector.

## AP News

Status: **OUTPUT INCLUDED**

Selected current AP market and geopolitical headlines are exported in `ap.csv` and `ap.json`.

## Trading Economics Calendar

Status: **API CREDENTIAL REQUIRED**

The official API collector is included. Add the API key in `.env` and run `python main.py`.

## CME FedWatch

Status: **OFFICIAL API CREDENTIAL REQUIRED**

The official FedWatch collector is included. Add the subscription endpoint and key in `.env`.

## Finviz Futures Performance

Status: **AUTOMATED COLLECTOR INCLUDED**

Run `python main.py` to refresh the current futures-performance output.

## Earnings Whispers

Status: **AUTOMATED BROWSER COLLECTOR INCLUDED**

Install Playwright Chromium and run `python main.py` to refresh the earnings output.

## Automation Result

The workflow:
1. Collects six required sources.
2. Processes each source independently.
3. Exports CSV and JSON files.
4. Creates one combined Markdown report.
5. Records failures and cached results instead of hiding them.
