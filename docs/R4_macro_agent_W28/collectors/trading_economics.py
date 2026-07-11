from __future__ import annotations

import os
from datetime import date, timedelta

from .common import CollectorResult, fail_with_cache, finish, get

SOURCE = "Trading Economics Calendar"
BASE = "https://api.tradingeconomics.com/calendar/country"


def collect() -> CollectorResult:
    key = os.getenv("TRADING_ECONOMICS_API_KEY", "").strip()
    if not key:
        return fail_with_cache(SOURCE, "official REST API", RuntimeError("TRADING_ECONOMICS_API_KEY is not configured"))
    try:
        countries = [x.strip() for x in os.getenv("COUNTRIES", "united states").split(",") if x.strip()]
        days = int(os.getenv("DAYS_AHEAD", "7"))
        start, end = date.today(), date.today() + timedelta(days=days)
        items = []
        for country in countries:
            url = f"{BASE}/{country}/{start.isoformat()}/{end.isoformat()}"
            payload = get(url, params={"c": key}).json()
            if isinstance(payload, dict) and payload.get("message"):
                raise RuntimeError(payload["message"])
            for e in payload:
                items.append({
                    "date": e.get("Date"),
                    "country": e.get("Country"),
                    "event": e.get("Event"),
                    "category": e.get("Category"),
                    "importance": e.get("Importance"),
                    "actual": e.get("Actual"),
                    "forecast": e.get("Forecast"),
                    "previous": e.get("Previous"),
                    "source": e.get("Source"),
                    "source_url": e.get("SourceURL"),
                    "url": e.get("URL"),
                })
        allowed = {int(x) for x in os.getenv("IMPORTANCE", "2,3").split(",") if x.strip().isdigit()}
        if allowed:
            items = [e for e in items if e.get("importance") in allowed]
        items.sort(key=lambda e: e.get("date") or "")
        return finish(SOURCE, items, "official REST API")
    except Exception as exc:
        return fail_with_cache(SOURCE, "official REST API", exc)
