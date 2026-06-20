# R3 Almanac Agent Automation

## What this does

This is the upgraded R3 Almanac Agent automation.

It reads the **Stock Trader's Almanac 2026 PDF** from the same folder as the Python script and automatically extracts:

- June Vital Statistics
- W25 week-specific pattern
- Sector Index Seasonality rows

Then it generates:

```text
outputs/almanac_agent_W25.json
outputs/almanac_agent_W25.csv
outputs/almanac_agent_W25.md
```

## Folder rule

The folder name does not matter.

Just keep these files together:

```text
r3_almanac_agent.py
requirements.txt
Stock Trader's Almanac 2026_L.pdf
```

## How to run

```bash
pip install -r requirements.txt
python r3_almanac_agent.py
```

## Why this satisfies Sprint 5

Sprint 5 requires automated structured agent output.

This script parses the PDF and produces JSON / CSV / Markdown files automatically.
