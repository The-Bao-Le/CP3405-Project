from __future__ import annotations

from datetime import datetime
import xml.etree.ElementTree as ET

from .common import CollectorResult, fail_with_cache, finish, get

SOURCE = "U.S. Treasury Daily Par Yield Curve"
BASE = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"


def collect() -> CollectorResult:
    try:
        year = datetime.utcnow().year
        params = {
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value": str(year),
        }
        text = get(BASE, params=params).text
        root = ET.fromstring(text)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
            "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
        }
        rows = []
        for entry in root.findall("atom:entry", ns):
            props = entry.find("atom:content/m:properties", ns)
            if props is None:
                continue
            raw = {child.tag.split("}")[-1]: child.text for child in props}
            date = raw.get("NEW_DATE") or raw.get("Date")
            if not date:
                continue
            row = {"date": date[:10]}
            for k, v in raw.items():
                if k.startswith("BC_") and v not in (None, ""):
                    row[k.removeprefix("BC_").replace("MONTH", "M").replace("YEAR", "Y")] = float(v)
            rows.append(row)
        rows.sort(key=lambda x: x["date"], reverse=True)
        if not rows:
            raise ValueError("Treasury XML feed returned no yield rows")
        return finish(SOURCE, rows[:10], "official XML feed")
    except Exception as exc:
        return fail_with_cache(SOURCE, "official XML feed", exc)
