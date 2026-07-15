from __future__ import annotations

import argparse
import csv
import html
import io
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo


BASE = Path(__file__).resolve().parent
SGT = ZoneInfo("Asia/Singapore")
USER_AGENT = "CP3405-Team2-R4-Macro-Agent/2.0 (educational project)"

TREASURY_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&"
    "field_tdr_date_value={year}&page&_format=csv"
)
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
DOL_CLAIMS_URL = "https://oui.doleta.gov/unemploy/DataDashboard.asp"
FED_PRESS_RSS = "https://www.federalreserve.gov/feeds/press_all.xml"
FED_SPEECH_RSS = "https://www.federalreserve.gov/feeds/speeches.xml"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?{query}"
BLS_RELEASE_CALENDAR_URL = "https://www.bls.gov/schedule/news_release/bls.ics"
BEA_RELEASE_CALENDAR_URL = "https://www.bea.gov/news/schedule"
FED_CALENDAR_URL = "https://www.federalreserve.gov/newsevents/{year}-{month}.htm"
FOREX_FACTORY_CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
DOL_CLAIMS_CADENCE_URL = "https://www.dol.gov/newsroom/releases/opa/opa20200701"
US_EASTERN = ZoneInfo("America/New_York")

BLS_SERIES = {
    "cpi": "CUUR0000SA0",  # CPI-U, All items, U.S. city average, not seasonally adjusted
    "unemployment_rate": "LNS14000000",  # Civilian unemployment rate
}

MARKET_TICKERS = {
    "SPX": "^GSPC",
    "NDX": "^NDX",
    "IWM": "IWM",
    "VIX": "^VIX",
    "WTI": "CL=F",
    "BRENT": "BZ=F",
    "DXY": "DX-Y.NYB",
    "XLK": "XLK",
    "XLV": "XLV",
    "XLF": "XLF",
    "XLY": "XLY",
    "XLC": "XLC",
    "XLI": "XLI",
    "XLP": "XLP",
    "XLE": "XLE",
    "XLB": "XLB",
    "XLRE": "XLRE",
    "XLU": "XLU",
}

SECTOR_NAMES = {
    "XLK": "Technology",
    "XLV": "Health Care",
    "XLF": "Financials",
    "XLY": "Consumer Discretionary",
    "XLC": "Communication Services",
    "XLI": "Industrials",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
}

HEADLINE_KEYWORDS = {
    "monetary_policy": (
        "federal reserve",
        " fed ",
        "fomc",
        "powell",
        "interest rate",
        "rate cut",
        "rate hike",
        "central bank",
    ),
    "inflation": ("inflation", " cpi", " pce", "consumer price", "producer price"),
    "labor": (
        "jobs",
        "payroll",
        "unemployment",
        "jobless",
        "claims",
        "labor market",
    ),
    "oil_energy": ("oil", "crude", "opec", "gasoline", "energy price", "lng"),
    "geopolitical": (
        "geopolit",
        "iran",
        "israel",
        "ukraine",
        "russia",
        "china",
        "middle east",
        "war",
        "conflict",
        "sanction",
        "tariff",
        "hormuz",
    ),
}

KEY_MACRO_EVENT_RULES = (
    (("consumer price index", " cpi"), "Inflation", "High"),
    (("producer price index", " ppi"), "Inflation", "High"),
    (("personal income and outlays", " pce"), "Inflation / consumption", "High"),
    (("employment situation", "nonfarm payroll"), "Labour", "High"),
    (("employment cost index",), "Labour / inflation", "High"),
    (("job openings and labor turnover", " jolts"), "Labour", "Medium"),
    (("unemployment claims", "initial jobless claims"), "Labour", "Medium"),
    (("productivity and costs",), "Labour / growth", "Medium"),
    (("import and export price indexes",), "Inflation / trade", "Medium"),
    (("gross domestic product", "gdp ("), "Growth", "High"),
    (("international trade in goods and services",), "Trade", "Medium"),
    (("industrial production and capacity utilization",), "Growth", "Medium"),
    (("retail sales",), "Consumption", "Medium"),
    (("consumer sentiment", "consumer confidence"), "Consumption", "Medium"),
    (("ism manufacturing", "ism services", "pmi"), "Growth", "Medium"),
    (("durable goods orders",), "Growth", "Medium"),
    (("beige book",), "Monetary policy", "Medium"),
    (("fomc meeting",), "Monetary policy", "High"),
)

FED_SPEECH_KEYWORDS = (
    "economic outlook",
    "economic shocks",
    "economy",
    "inflation",
    "labor market",
    "monetary policy",
    "financial stability",
    "interest rate",
)


class CollectionError(RuntimeError):
    """Raised when a source response cannot be parsed into useful data."""


def fetch_text(
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: int = 100,
    attempts: int = 2,
) -> str:
    """Download UTF-8 text with a small retry policy."""
    data = None
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                charset = response.headers.get_content_charset() or "utf-8"
                return raw.decode(charset, errors="replace")
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(attempt * 2)

    raise CollectionError(f"request failed after {attempts} attempts: {last_error}")


def target_period(as_of: date) -> tuple[int, int, date, date]:
    """Return ISO year/week and Monday-Saturday boundaries for an SGT date."""
    iso = as_of.isocalendar()
    monday = as_of - timedelta(days=iso.weekday - 1)
    saturday = monday + timedelta(days=5)
    return iso.year, iso.week, monday, saturday


def macro_event_window(as_of: date) -> tuple[date, date, date]:
    """Return current Monday/Sunday and the following Sunday in Singapore."""
    current_monday = as_of - timedelta(days=as_of.isoweekday() - 1)
    current_sunday = current_monday + timedelta(days=6)
    next_sunday = current_sunday + timedelta(days=7)
    return current_monday, current_sunday, next_sunday


def _strip_html(text: str) -> str:
    clean = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", clean).strip()


def _parse_eastern_time(day: date, time_text: str) -> datetime | None:
    """Parse the ET convention used by BLS, BEA and Federal Reserve calendars."""
    normalized = re.sub(r"\s+", " ", _strip_html(time_text)).strip()
    normalized = re.sub(r"a\.m\.?", "AM", normalized, flags=re.I)
    normalized = re.sub(r"p\.m\.?", "PM", normalized, flags=re.I)
    if not normalized:
        return None
    for pattern in ("%I:%M %p", "%I %p"):
        try:
            local_time = datetime.strptime(normalized.upper(), pattern).time()
            return datetime.combine(day, local_time, tzinfo=US_EASTERN).astimezone(SGT)
        except ValueError:
            continue
    return None


def classify_macro_event(title: str) -> tuple[str, str] | None:
    """Classify only releases that are material to a weekly macro forecast."""
    normalized = f" {title.casefold()} "
    for keywords, category, impact in KEY_MACRO_EVENT_RULES:
        if any(keyword in normalized for keyword in keywords):
            return category, impact
    return None


def _make_macro_event(
    title: str,
    scheduled_sgt: datetime,
    source: str,
    source_url: str,
    *,
    category: str | None = None,
    impact: str | None = None,
) -> dict[str, Any] | None:
    classified = (category, impact) if category and impact else classify_macro_event(title)
    if classified is None:
        return None
    event_category, event_impact = classified
    return {
        "scheduled_sgt": scheduled_sgt.isoformat(timespec="minutes"),
        "date_sgt": scheduled_sgt.date().isoformat(),
        "time_sgt": scheduled_sgt.strftime("%H:%M"),
        "event": re.sub(r"\s+", " ", html.unescape(title)).strip(),
        "category": event_category,
        "impact": event_impact,
        "source": source,
        "source_url": source_url,
        "schedule_note": "Official calendar",
    }


def _unescape_ics(value: str) -> str:
    return (
        value.replace("\\n", " ")
        .replace("\\N", " ")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def parse_bls_calendar_ics(text: str, source_url: str = BLS_RELEASE_CALENDAR_URL) -> list[dict[str, Any]]:
    """Parse the official BLS iCalendar and retain high/medium-impact releases."""
    raw_lines = text.lstrip("\ufeff").splitlines()
    unfolded: list[str] = []
    for line in raw_lines:
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line.rstrip("\r"))

    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in unfolded:
        if line == "BEGIN:VEVENT":
            current = []
        elif line == "END:VEVENT" and current is not None:
            blocks.append(current)
            current = None
        elif current is not None:
            current.append(line)
    if not blocks:
        raise CollectionError("BLS calendar response contains no VEVENT records")

    events: list[dict[str, Any]] = []
    for block in blocks:
        properties: dict[str, tuple[str, str]] = {}
        for line in block:
            if ":" not in line:
                continue
            raw_name, value = line.split(":", 1)
            name = raw_name.split(";", 1)[0].upper()
            properties[name] = (raw_name, value)
        title = _unescape_ics(properties.get("SUMMARY", ("", ""))[1]).strip()
        raw_name, raw_value = properties.get("DTSTART", ("", ""))
        if not title or not raw_value:
            continue
        try:
            if raw_value.endswith("Z"):
                source_dt = datetime.strptime(raw_value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            elif "T" in raw_value:
                parsed = None
                for pattern in ("%Y%m%dT%H%M%S", "%Y%m%dT%H%M"):
                    try:
                        parsed = datetime.strptime(raw_value, pattern)
                        break
                    except ValueError:
                        continue
                if parsed is None:
                    continue
                tzid_match = re.search(r"TZID=([^;:]+)", raw_name, re.I)
                try:
                    source_zone = ZoneInfo(tzid_match.group(1)) if tzid_match else US_EASTERN
                except (KeyError, ValueError):
                    source_zone = US_EASTERN
                source_dt = parsed.replace(tzinfo=source_zone)
            else:
                source_day = datetime.strptime(raw_value, "%Y%m%d").date()
                source_dt = datetime.combine(source_day, datetime.min.time(), tzinfo=US_EASTERN)
        except ValueError:
            continue
        event = _make_macro_event(
            title,
            source_dt.astimezone(SGT),
            "BLS release calendar",
            source_url,
        )
        if event:
            events.append(event)
    return events


def parse_bea_calendar_html(text: str, source_url: str = BEA_RELEASE_CALENDAR_URL) -> list[dict[str, Any]]:
    """Parse key GDP, PCE and trade releases from the official BEA schedule."""
    events: list[dict[str, Any]] = []
    for table in re.findall(r"<table\b[^>]*>(.*?)</table>", text, flags=re.I | re.S):
        year_match = re.search(r"Year\s+(\d{4})", _strip_html(table), re.I)
        if not year_match:
            continue
        year = int(year_match.group(1))
        for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", table, flags=re.I | re.S):
            date_match = re.search(r'class="release-date"[^>]*>(.*?)</div>', row, re.I | re.S)
            time_match = re.search(r'<small\b[^>]*>(.*?)</small>', row, re.I | re.S)
            title_match = re.search(r'<td\b[^>]*class="[^"]*release-title[^"]*"[^>]*>(.*?)</td>', row, re.I | re.S)
            if not date_match or not time_match or not title_match:
                continue
            try:
                release_day = datetime.strptime(
                    f"{year} {_strip_html(date_match.group(1))}", "%Y %B %d"
                ).date()
            except ValueError:
                continue
            scheduled = _parse_eastern_time(release_day, time_match.group(1))
            if scheduled is None:
                continue
            event = _make_macro_event(
                _strip_html(title_match.group(1)),
                scheduled,
                "BEA release schedule",
                source_url,
            )
            if event:
                events.append(event)
    if not re.search(r"release-schedule-table", text, re.I):
        raise CollectionError("BEA release schedule table was not found")
    return events


def parse_fed_calendar_html(text: str, source_url: str) -> list[dict[str, Any]]:
    """Parse policy meetings, selected data releases and macro-focused Fed remarks."""
    month_match = re.search(
        r'<h4\b[^>]*class="[^"]*text-center[^"]*"[^>]*>\s*([A-Za-z]+)\s+(\d{4})\s*</h4>',
        text,
        re.I,
    )
    if not month_match:
        raise CollectionError("Federal Reserve calendar month heading was not found")
    month_number = datetime.strptime(month_match.group(1), "%B").month
    year = int(month_match.group(2))

    heading_pattern = re.compile(
        r'<div\b[^>]*class="[^"]*cal-nojs__rowTitle[^"]*"[^>]*>.*?'
        r'<h4\b[^>]*>(.*?)</h4>.*?</div>',
        re.I | re.S,
    )
    headings = list(heading_pattern.finditer(text))
    events: list[dict[str, Any]] = []
    for index, heading in enumerate(headings):
        section = _strip_html(heading.group(1))
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end():section_end]
        if section not in {"Speeches", "Testimony", "FOMC Meetings", "Beige Book", "Statistical Releases"}:
            continue
        entry_pattern = re.compile(
            r'<div class="col-xs-2">\s*<p>(.*?)</p>.*?'
            r'<div class="col-xs-7"[^>]*>(.*?)</div>\s*'
            r'<div class="col-xs-3">\s*<p>(.*?)</p>',
            re.I | re.S,
        )
        for time_html, title_html, days_html in entry_pattern.findall(body):
            first_paragraph = re.search(r"<p(?:\s+[^>]*)?>(.*?)</p>", title_html, re.I | re.S)
            if not first_paragraph:
                continue
            title = _strip_html(first_paragraph.group(1))
            topic_match = re.search(
                r"<p\b[^>]*class=['\"]calendar__title['\"][^>]*>(.*?)</p>",
                title_html,
                re.I | re.S,
            )
            topic = _strip_html(topic_match.group(1)) if topic_match else ""
            if topic and topic.casefold() not in title.casefold():
                title = f"{title} — {topic}"

            normalized_title = title.casefold()
            if section in {"Speeches", "Testimony"}:
                if not any(keyword in normalized_title for keyword in FED_SPEECH_KEYWORDS):
                    continue
                category, impact = "Fed communication", "Medium"
            else:
                classified = classify_macro_event(title)
                if classified is None:
                    continue
                category, impact = classified

            for day_number in (int(value) for value in re.findall(r"\d+", _strip_html(days_html))):
                try:
                    release_day = date(year, month_number, day_number)
                except ValueError:
                    continue
                scheduled = _parse_eastern_time(release_day, time_html)
                if scheduled is None:
                    continue
                event = _make_macro_event(
                    title,
                    scheduled,
                    "Federal Reserve calendar",
                    source_url,
                    category=category,
                    impact=impact,
                )
                if event:
                    events.append(event)
    return events


def parse_public_calendar_json(
    text: str,
    source_url: str = "https://www.forexfactory.com/calendar",
) -> list[dict[str, Any]]:
    """Parse the free weekly export used only to backstop blocked official calendars."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CollectionError(f"invalid public calendar JSON: {exc}") from exc
    if not isinstance(payload, list):
        raise CollectionError("public calendar response is not an event list")

    events: list[dict[str, Any]] = []
    canonical_titles = (
        (("core cpi", "cpi "), "Consumer Price Index (CPI)"),
        (("core ppi", "ppi "), "Producer Price Index (PPI)"),
        (("unemployment claims",), "Initial Jobless Claims"),
        (("retail sales",), "Retail Sales"),
        (("consumer sentiment",), "Consumer Sentiment"),
    )
    for item in payload:
        if not isinstance(item, dict) or item.get("country") != "USD":
            continue
        title = str(item.get("title", "")).strip()
        normalized = f" {title.casefold()} "
        for keywords, canonical in canonical_titles:
            if any(keyword in normalized for keyword in keywords):
                title = canonical
                break
        try:
            scheduled = datetime.fromisoformat(str(item.get("date", "")))
            if scheduled.tzinfo is None:
                scheduled = scheduled.replace(tzinfo=US_EASTERN)
        except ValueError:
            continue
        event = _make_macro_event(
            title,
            scheduled.astimezone(SGT),
            "Public economic calendar fallback",
            source_url,
        )
        if event:
            event["schedule_note"] = "Public-calendar fallback; verify against the named agency."
            events.append(event)
    return events


def recurring_dol_claims_events(window_start: date, window_end: date) -> list[dict[str, Any]]:
    """Add DOL's usual Thursday 08:30 ET claims release, clearly marked tentative."""
    events: list[dict[str, Any]] = []
    cursor = window_start
    while cursor <= window_end:
        if cursor.isoweekday() == 4:
            scheduled = _parse_eastern_time(cursor, "8:30 AM")
            if scheduled is not None:
                event = _make_macro_event(
                    "Initial Jobless Claims (expected recurring release)",
                    scheduled,
                    "U.S. Department of Labor release cadence",
                    DOL_CLAIMS_CADENCE_URL,
                    category="Labour",
                    impact="Medium",
                )
                if event:
                    event["schedule_note"] = "Usual Thursday cadence; verify holiday changes."
                    events.append(event)
        cursor += timedelta(days=1)
    return events


def collect_macro_events(as_of: date, status: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect and label key events for the current and following Singapore weeks."""
    window_start, current_sunday, window_end = macro_event_window(as_of)
    collected: list[dict[str, Any]] = []

    sources = (
        (
            "BLS official release calendar",
            BLS_RELEASE_CALENDAR_URL,
            lambda: parse_bls_calendar_ics(fetch_text(BLS_RELEASE_CALENDAR_URL, timeout=45)),
        ),
        (
            "BEA official release schedule",
            BEA_RELEASE_CALENDAR_URL,
            lambda: parse_bea_calendar_html(fetch_text(BEA_RELEASE_CALENDAR_URL, timeout=45)),
        ),
    )
    for name, url, collector in sources:
        started = datetime.now(timezone.utc)
        try:
            rows = collector()
            collected.extend(rows)
            add_status(status, name, url, "ok", f"{len(rows)} key events parsed before date filtering", started)
        except Exception as exc:
            add_status(status, name, url, "error", str(exc), started)

    month_cursor = date(window_start.year, window_start.month, 1)
    month_pages: list[tuple[str, str]] = []
    while month_cursor <= window_end:
        url = FED_CALENDAR_URL.format(
            year=month_cursor.year,
            month=month_cursor.strftime("%B").casefold(),
        )
        month_pages.append((month_cursor.strftime("%Y-%m"), url))
        month_cursor = (
            date(month_cursor.year + 1, 1, 1)
            if month_cursor.month == 12
            else date(month_cursor.year, month_cursor.month + 1, 1)
        )
    fed_started = datetime.now(timezone.utc)
    fed_rows: list[dict[str, Any]] = []
    fed_errors: list[str] = []
    for month_label, url in month_pages:
        try:
            fed_rows.extend(parse_fed_calendar_html(fetch_text(url, timeout=45), url))
        except Exception as exc:
            fed_errors.append(f"{month_label}: {exc}")
    collected.extend(fed_rows)
    fed_state = "ok" if not fed_errors else ("partial" if fed_rows else "error")
    fed_detail = f"{len(fed_rows)} key events parsed from {len(month_pages)} month page(s)"
    if fed_errors:
        fed_detail += "; " + "; ".join(fed_errors)
    add_status(
        status,
        "Federal Reserve official calendar",
        month_pages[0][1],
        fed_state,
        fed_detail,
        fed_started,
    )

    dol_rows = recurring_dol_claims_events(window_start, window_end)
    collected.extend(dol_rows)
    add_status(
        status,
        "DOL weekly claims release cadence",
        DOL_CLAIMS_CADENCE_URL,
        "derived",
        f"{len(dol_rows)} expected Thursday release(s); holiday changes require verification",
    )

    fallback_started = datetime.now(timezone.utc)
    try:
        fallback_rows = parse_public_calendar_json(
            fetch_text(FOREX_FACTORY_CALENDAR_URL, timeout=45, attempts=1)
        )
        collected.extend(fallback_rows)
        add_status(
            status,
            "Free public weekly economic-calendar fallback",
            FOREX_FACTORY_CALENDAR_URL,
            "ok",
            f"{len(fallback_rows)} key U.S. events parsed; used only to fill official-calendar gaps",
            fallback_started,
        )
    except Exception as exc:
        add_status(
            status,
            "Free public weekly economic-calendar fallback",
            FOREX_FACTORY_CALENDAR_URL,
            "error",
            str(exc),
            fallback_started,
        )

    deduplicated: dict[tuple[str, str], dict[str, Any]] = {}
    for row in collected:
        event_day = date.fromisoformat(row["date_sgt"])
        if not window_start <= event_day <= window_end:
            continue
        row["period"] = "This week" if event_day <= current_sunday else "Next week"
        row["timing"] = "Past" if event_day < as_of else ("Today" if event_day == as_of else "Upcoming")
        key = (row["scheduled_sgt"], row["category"])
        deduplicated.setdefault(key, row)
    return sorted(
        deduplicated.values(),
        key=lambda row: (row["scheduled_sgt"], 0 if row["impact"] == "High" else 1, row["event"]),
    )


def _float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def parse_treasury_csv(text: str, week_start: date, week_end: date) -> dict[str, Any]:
    """Parse the official Treasury CSV and compute week-to-date yield moves."""
    parsed: list[dict[str, Any]] = []
    for raw in csv.DictReader(io.StringIO(text.lstrip("\ufeff"))):
        try:
            row_date = datetime.strptime(raw["Date"], "%m/%d/%Y").date()
        except (KeyError, TypeError, ValueError):
            continue
        parsed.append(
            {
                "date": row_date.isoformat(),
                "2y": _float(raw.get("2 Yr")),
                "10y": _float(raw.get("10 Yr")),
                "30y": _float(raw.get("30 Yr")),
            }
        )

    parsed.sort(key=lambda row: row["date"])
    eligible = [row for row in parsed if date.fromisoformat(row["date"]) <= week_end]
    current = [
        row
        for row in eligible
        if week_start <= date.fromisoformat(row["date"]) <= week_end
    ]
    earlier = [row for row in eligible if date.fromisoformat(row["date"]) < week_start]
    if not current:
        raise CollectionError("Treasury CSV contains no observation for the target week")

    baseline = earlier[-1] if earlier else current[0]
    latest = current[-1]
    changes: dict[str, int | None] = {}
    for maturity in ("2y", "10y", "30y"):
        old = baseline[maturity]
        new = latest[maturity]
        changes[f"{maturity}_change_bps"] = (
            round((new - old) * 100) if old is not None and new is not None else None
        )

    rows = ([baseline] if baseline not in current else []) + current
    return {
        "baseline": baseline,
        "latest": latest,
        "changes_bps": changes,
        "rows": rows,
        "method": "Previous available close to latest target-week close",
    }


def parse_bls_response(text: str) -> dict[str, Any]:
    """Parse CPI and unemployment series returned by the public BLS API."""
    payload = json.loads(text)
    if payload.get("status") != "REQUEST_SUCCEEDED":
        raise CollectionError(f"BLS returned status {payload.get('status')!r}")

    series_by_id = {
        item.get("seriesID"): item.get("data", [])
        for item in payload.get("Results", {}).get("series", [])
    }

    def observations(series_id: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for item in series_by_id.get(series_id, []):
            period = str(item.get("period", ""))
            value = _float(item.get("value"))
            if not re.fullmatch(r"M\d{2}", period) or period == "M13" or value is None:
                continue
            result.append(
                {
                    "year": int(item["year"]),
                    "month": int(period[1:]),
                    "period": f"{item['year']}-{period[1:]}",
                    "value": value,
                }
            )
        return sorted(result, key=lambda row: (row["year"], row["month"]))

    cpi = observations(BLS_SERIES["cpi"])
    unemployment = observations(BLS_SERIES["unemployment_rate"])
    if not cpi or not unemployment:
        raise CollectionError("BLS response is missing CPI or unemployment observations")

    cpi_lookup = {(row["year"], row["month"]): row["value"] for row in cpi}
    yoy_rows: list[dict[str, Any]] = []
    for row in cpi:
        previous_year = cpi_lookup.get((row["year"] - 1, row["month"]))
        if previous_year:
            yoy_rows.append(
                {
                    "period": row["period"],
                    "index": row["value"],
                    "yoy_pct": round((row["value"] / previous_year - 1) * 100, 2),
                }
            )

    if not yoy_rows:
        raise CollectionError("BLS CPI response has no year-over-year comparison")

    return {
        "cpi_latest": yoy_rows[-1],
        "cpi_previous": yoy_rows[-2] if len(yoy_rows) > 1 else None,
        "unemployment_latest": unemployment[-1],
        "series_notes": {
            "cpi": "CPI-U All items, U.S. city average, not seasonally adjusted",
            "unemployment": "Civilian unemployment rate, seasonally adjusted",
        },
    }


def parse_dol_claims_page(text: str) -> dict[str, Any]:
    """Extract the current seasonally adjusted initial-claims card from DOL."""
    clean = html.unescape(re.sub(r"<[^>]+>", " ", text))
    clean = re.sub(r"\s+", " ", clean)
    patterns = (
        r"Seasonally Adjusted Initial Claims\s*\((\d{2}/\d{2}/\d{4})\)\s*([\d,]+)",
        r"Seasonally Adjusted Initial Claims.*?(\d{2}/\d{2}/\d{4}).*?([\d,]{4,})",
    )
    match = next((re.search(pattern, clean, re.I) for pattern in patterns if re.search(pattern, clean, re.I)), None)
    if not match:
        raise CollectionError("DOL page layout did not expose the initial-claims card")
    return {
        "week_ending": datetime.strptime(match.group(1), "%m/%d/%Y").date().isoformat(),
        "initial_claims_sa": int(match.group(2).replace(",", "")),
    }


def _extract_close_frame(frame: Any, symbol: str) -> Any:
    """Return a one-dimensional Close series across yfinance column layouts."""
    if getattr(frame, "empty", True):
        return None
    columns = frame.columns
    if getattr(columns, "nlevels", 1) == 1:
        return frame["Close"] if "Close" in columns else None
    if symbol in columns.get_level_values(0):
        block = frame[symbol]
        return block["Close"] if "Close" in block.columns else None
    if symbol in columns.get_level_values(1):
        block = frame.xs(symbol, axis=1, level=1)
        return block["Close"] if "Close" in block.columns else None
    return None


def collect_market_data(week_start: date, week_end: date) -> dict[str, Any]:
    """Fetch weekly cross-asset and all 11 sector ETF prices using yfinance."""
    try:
        import yfinance as yf
    except ImportError as exc:
        raise CollectionError("yfinance is not installed") from exc

    symbols = list(MARKET_TICKERS.values())
    fetch_start = week_start - timedelta(days=10)
    fetch_end = week_end + timedelta(days=2)  # yfinance end is exclusive
    frame = yf.download(
        symbols,
        start=fetch_start.isoformat(),
        end=fetch_end.isoformat(),
        interval="1d",
        auto_adjust=False,
        actions=False,
        group_by="ticker",
        # Parallel requests can trigger Yahoo throttling and yfinance cookie-DB locks.
        threads=False,
        progress=False,
    )

    metrics: dict[str, Any] = {}
    for label, symbol in MARKET_TICKERS.items():
        close = _extract_close_frame(frame, symbol)
        if close is None:
            continue
        points: list[tuple[date, float]] = []
        for timestamp, value in close.dropna().items():
            observed = timestamp.date() if hasattr(timestamp, "date") else date.fromisoformat(str(timestamp)[:10])
            number = _float(value)
            if number is not None and observed <= week_end:
                points.append((observed, number))
        baseline = [point for point in points if point[0] < week_start]
        current = [point for point in points if week_start <= point[0] <= week_end]
        if not baseline or not current or baseline[-1][1] == 0:
            continue
        old_date, old_value = baseline[-1]
        new_date, new_value = current[-1]
        metrics[label] = {
            "ticker": symbol,
            "baseline_date": old_date.isoformat(),
            "baseline_close": round(old_value, 4),
            "latest_date": new_date.isoformat(),
            "latest_close": round(new_value, 4),
            "weekly_return_pct": round((new_value / old_value - 1) * 100, 2),
        }

    missing_sectors = sorted(set(SECTOR_NAMES) - set(metrics))
    if not metrics:
        raise CollectionError("yfinance returned no usable weekly observations")
    return {
        "metrics": metrics,
        "missing_sectors": missing_sectors,
        "all_11_sectors_complete": not missing_sectors,
        "method": "Previous available close to latest target-week close; raw Close",
    }


def load_r6_market_fallback(iso_year: int, iso_week: int) -> dict[str, Any]:
    """Reuse the same-week R6 market snapshot if Yahoo blocks R4's direct call."""
    week_label = f"W{iso_week:02d}"
    path = BASE / f"market_snapshot_{week_label}.json"
    if not path.exists():
        raise CollectionError(f"same-week R6 snapshot not found: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    meta = payload.get("meta", {})
    if str(meta.get("market_week")) != week_label or int(meta.get("market_year", 0)) != iso_year:
        raise CollectionError("R6 snapshot week/year does not match the R4 target")

    metrics: dict[str, Any] = {}
    for label, row in payload.get("metrics", {}).items():
        r4_label = "WTI" if label == "OIL" else label
        metrics[r4_label] = {
            "ticker": row.get("ticker"),
            "baseline_date": row.get("baseline_date"),
            "baseline_close": row.get("baseline_close"),
            "latest_date": row.get("final_date"),
            "latest_close": row.get("close_price"),
            "weekly_return_pct": row.get("weekly_delta_pct"),
        }
    missing_sectors = sorted(set(SECTOR_NAMES) - set(metrics))
    if not metrics:
        raise CollectionError("same-week R6 snapshot has no metrics")
    return {
        "metrics": metrics,
        "missing_sectors": missing_sectors,
        "all_11_sectors_complete": not missing_sectors,
        "method": f"Same-week R6 snapshot fallback ({path.name}); {meta.get('return_method', '')}",
        "fallback_file": path.name,
    }


def classify_headline(title: str) -> list[str]:
    """Return transparent keyword categories for a headline."""
    normalized = f" {title.casefold()} "
    return [
        category
        for category, keywords in HEADLINE_KEYWORDS.items()
        if any(keyword in normalized for keyword in keywords)
    ]


def parse_rss(
    text: str,
    feed_name: str,
    window_start: date,
    window_end: date,
) -> list[dict[str, Any]]:
    """Parse RSS items, retaining only dated and macro-relevant headlines."""
    try:
        root = ET.fromstring(text.lstrip("\ufeff"))
    except ET.ParseError as exc:
        raise CollectionError(f"invalid RSS XML: {exc}") from exc

    items: list[dict[str, Any]] = []
    for node in root.findall(".//item"):
        title = html.unescape((node.findtext("title") or "").strip())
        link = (node.findtext("link") or "").strip()
        published_text = (node.findtext("pubDate") or "").strip()
        source_node = node.find("source")
        source = (
            (source_node.text or "").strip()
            if source_node is not None
            else feed_name
        )
        try:
            published = parsedate_to_datetime(published_text)
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            published_date = published.astimezone(SGT).date()
        except (TypeError, ValueError, OverflowError):
            continue
        categories = classify_headline(title)
        if not categories and feed_name.startswith("Federal Reserve"):
            categories = ["monetary_policy"]
        if not categories or not (window_start <= published_date <= window_end):
            continue
        items.append(
            {
                "published_sgt": published.astimezone(SGT).isoformat(timespec="minutes"),
                "title": title,
                "publisher": source,
                "feed": feed_name,
                "categories": categories,
                "link": link,
            }
        )
    return items


def collect_headlines(
    as_of: date,
    status: list[dict[str, Any]],
    limit: int = 30,
) -> list[dict[str, Any]]:
    """Collect official Fed items and free headline-only news search results."""
    query = urllib.parse.urlencode(
        {
            "q": (
                "(Federal Reserve OR inflation OR jobless claims OR oil OR geopolitical) "
                "when:7d"
            ),
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en",
        }
    )
    ap_query = urllib.parse.urlencode(
        {
            "q": (
                "site:apnews.com (Federal Reserve OR inflation OR oil OR economy OR geopolitical) "
                "when:7d"
            ),
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en",
        }
    )
    feeds = (
        ("Federal Reserve press releases", FED_PRESS_RSS),
        ("Federal Reserve speeches", FED_SPEECH_RSS),
        ("Google News AP-only search", GOOGLE_NEWS_RSS.format(query=ap_query)),
        ("Google News macro search", GOOGLE_NEWS_RSS.format(query=query)),
    )
    window_start = as_of - timedelta(days=7)
    collected: list[dict[str, Any]] = []
    for name, url in feeds:
        started = datetime.now(timezone.utc)
        try:
            text = fetch_text(url, timeout=45)
            rows = parse_rss(text, name, window_start, as_of)
            collected.extend(rows)
            add_status(status, name, url, "ok", f"{len(rows)} relevant dated headlines", started)
        except Exception as exc:  # an optional RSS feed must not break the report
            add_status(status, name, url, "error", str(exc), started)

    deduplicated: dict[str, dict[str, Any]] = {}
    for row in collected:
        key = re.sub(r"\W+", " ", row["title"].casefold()).strip()
        deduplicated.setdefault(key, row)
    trusted_publishers = {
        "Associated Press",
        "AP News",
        "Reuters",
        "Federal Reserve",
        "CNBC",
        "Bloomberg",
        "Financial Times",
        "The Wall Street Journal",
        "MarketWatch",
        "PBS",
        "Yahoo Finance",
    }

    def priority(row: dict[str, Any]) -> tuple[int, str]:
        score = len(row["categories"])
        if row["feed"].startswith("Federal Reserve"):
            score += 5
        if row["publisher"] in trusted_publishers or "AP-only" in row["feed"]:
            score += 3
        return score, row["published_sgt"]

    return sorted(deduplicated.values(), key=priority, reverse=True)[:limit]


def add_status(
    status: list[dict[str, Any]],
    name: str,
    url: str,
    state: str,
    detail: str,
    started: datetime | None = None,
) -> None:
    elapsed = None
    if started is not None:
        elapsed = round((datetime.now(timezone.utc) - started).total_seconds(), 2)
    status.append(
        {
            "source": name,
            "url": url,
            "status": state,
            "detail": detail[:500],
            "elapsed_seconds": elapsed,
        }
    )


def collect_source(
    status: list[dict[str, Any]],
    name: str,
    url: str,
    collector: Callable[[], Any],
) -> Any | None:
    started = datetime.now(timezone.utc)
    try:
        result = collector()
        add_status(status, name, url, "ok", "collection and parsing succeeded", started)
        return result
    except Exception as exc:
        add_status(status, name, url, "error", str(exc), started)
        return None


def analyse(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Create a deterministic signal summary without claiming LLM understanding."""
    score = 0
    bullish: list[str] = []
    bearish: list[str] = []
    neutral: list[str] = []

    market = (snapshot.get("market") or {}).get("metrics", {})

    def market_return(label: str) -> float | None:
        return _float(market.get(label, {}).get("weekly_return_pct"))

    spx = market_return("SPX")
    ndx = market_return("NDX")
    vix = market_return("VIX")
    oil = market_return("WTI")
    if spx is not None and ndx is not None:
        if spx > 0 and ndx > 0:
            score += 2
            bullish.append("SPX and NDX are both positive for the measured week.")
        elif spx < 0 and ndx < 0:
            score -= 2
            bearish.append("SPX and NDX are both negative for the measured week.")
        else:
            neutral.append("SPX and NDX direction is mixed.")
    if vix is not None:
        if vix <= -2:
            score += 1
            bullish.append("VIX fell by at least 2%, a risk-appetite signal.")
        elif vix >= 2:
            score -= 1
            bearish.append("VIX rose by at least 2%, a risk-aversion signal.")
    if oil is not None:
        if oil >= 2:
            score -= 1
            bearish.append("WTI rose by at least 2%, increasing near-term inflation risk.")
        elif oil <= -2:
            score += 1
            bullish.append("WTI fell by at least 2%, easing near-term inflation pressure.")

    treasury_change = _float(
        (snapshot.get("treasury") or {}).get("changes_bps", {}).get("10y_change_bps")
    )
    if treasury_change is not None:
        if treasury_change >= 5:
            score -= 1
            bearish.append("The 10-year Treasury yield rose by at least 5 bps.")
        elif treasury_change <= -5:
            score += 1
            bullish.append("The 10-year Treasury yield fell by at least 5 bps.")

    macro = snapshot.get("labor_inflation") or {}
    cpi_latest = _float((macro.get("cpi_latest") or {}).get("yoy_pct"))
    cpi_previous = _float((macro.get("cpi_previous") or {}).get("yoy_pct"))
    if cpi_latest is not None and cpi_previous is not None:
        if cpi_latest < cpi_previous:
            score += 1
            bullish.append("Latest CPI year-over-year inflation is below its prior reading.")
        elif cpi_latest > cpi_previous:
            score -= 1
            bearish.append("Latest CPI year-over-year inflation is above its prior reading.")

    if score >= 3:
        bias = "Moderately Bullish"
    elif score <= -3:
        bias = "Moderately Bearish"
    else:
        bias = "Neutral / Mixed"

    category_counts = Counter(
        category
        for item in snapshot.get("headlines", [])
        for category in item.get("categories", [])
    )
    headline_flags = [
        f"{category.replace('_', ' ').title()}: {count} headline(s) require human review."
        for category, count in sorted(category_counts.items())
    ]

    sectors = [
        {
            "ticker": ticker,
            "sector": SECTOR_NAMES[ticker],
            "weekly_return_pct": market_return(ticker),
            "momentum_label": (
                "Bullish momentum"
                if market_return(ticker) is not None and market_return(ticker) >= 1
                else "Bearish momentum"
                if market_return(ticker) is not None and market_return(ticker) <= -1
                else "Neutral momentum"
                if market_return(ticker) is not None
                else "Unavailable"
            ),
        }
        for ticker in SECTOR_NAMES
    ]
    market_complete = bool(market) and not (snapshot.get("market") or {}).get(
        "missing_sectors"
    )
    core_complete = bool(snapshot.get("treasury")) and bool(macro) and market_complete
    confidence = "Medium" if core_complete else "Low"
    return {
        "rule_based_score": score,
        "macro_bias": bias,
        "confidence": confidence,
        "bullish_factors": bullish,
        "bearish_factors": bearish,
        "neutral_factors": neutral,
        "headline_flags": headline_flags,
        "headline_category_counts": dict(category_counts),
        "sector_momentum": sectors,
        "interpretation_limit": (
            "This is deterministic screening, not semantic news analysis. "
            "R4 must read the linked articles and write the final weekly interpretation."
        ),
    }


def build_snapshot(as_of: date, headline_limit: int = 30) -> dict[str, Any]:
    """Run every free collector and return a partial-safe weekly snapshot."""
    iso_year, iso_week, week_start, week_end = target_period(as_of)
    status: list[dict[str, Any]] = []

    treasury_url = TREASURY_URL.format(year=iso_year)
    treasury = collect_source(
        status,
        "U.S. Treasury daily par yields",
        treasury_url,
        lambda: parse_treasury_csv(
            fetch_text(treasury_url, timeout=45), week_start, min(as_of, week_end)
        ),
    )

    bls_payload = {
        "seriesid": list(BLS_SERIES.values()),
        # Two prior years keeps a YoY comparison available in January, when the
        # newest published observation can still belong to the previous year.
        "startyear": str(iso_year - 2),
        "endyear": str(iso_year),
    }
    labor_inflation = collect_source(
        status,
        "BLS public timeseries API",
        BLS_API_URL,
        lambda: parse_bls_response(
            fetch_text(BLS_API_URL, payload=bls_payload, timeout=110, attempts=1)
        ),
    )

    claims = collect_source(
        status,
        "U.S. Department of Labor weekly claims",
        DOL_CLAIMS_URL,
        lambda: parse_dol_claims_page(fetch_text(DOL_CLAIMS_URL, timeout=45)),
    )

    market = collect_source(
        status,
        "Yahoo Finance via yfinance",
        "https://finance.yahoo.com/",
        lambda: collect_market_data(week_start, min(as_of, week_end)),
    )
    if market is None:
        fallback_path = BASE / f"market_snapshot_W{iso_week:02d}.json"
        market = collect_source(
            status,
            "Same-week R6 market snapshot fallback",
            str(fallback_path.relative_to(BASE)),
            lambda: load_r6_market_fallback(iso_year, iso_week),
        )

    macro_events = collect_macro_events(as_of, status)
    headlines = collect_headlines(as_of, status, limit=headline_limit)

    skipped = (
        (
            "CME FedWatch",
            "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html",
            "skipped",
            "No stable free public FedWatch API; dynamic dashboard remains a manual R4 check.",
        ),
        (
            "Trading Economics calendar API",
            "https://tradingeconomics.com/calendar",
            "skipped",
            "Reliable API access requires credentials; guest endpoint returns HTTP 410.",
        ),
        (
            "Finviz futures performance",
            "https://finviz.com/futures_performance.ashx?v=12",
            "replaced" if market else "skipped",
            (
                "Direct scraping is fragile; market moves use yfinance or the same-week R6 snapshot."
                if market
                else "Direct scraping is fragile and the attempted yfinance/R6 replacement was unavailable."
            ),
        ),
        (
            "AP News full-article analysis",
            "https://apnews.com/",
            "skipped",
            "No paid/licensed AP API is configured; headline links may appear via news RSS only.",
        ),
        (
            "Earnings Whispers calendar",
            "https://earningswhispers.com/",
            "skipped",
            "No stable free public API; earnings calendar remains a manual check.",
        ),
        (
            "LLM news interpretation",
            "",
            "skipped",
            "No LLM key is required or used; final narrative is intentionally human-reviewed.",
        ),
    )
    for name, url, state, detail in skipped:
        add_status(status, name, url, state, detail)

    snapshot: dict[str, Any] = {
        "meta": {
            "role": "R4 Macro Agent",
            "iso_year": iso_year,
            "iso_week": f"W{iso_week:02d}",
            "as_of_sgt": as_of.isoformat(),
            "target_period_sgt": f"{week_start.isoformat()} to {week_end.isoformat()}",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "schedule": "Saturday",
        },
        "treasury": treasury,
        "labor_inflation": labor_inflation,
        "jobless_claims": claims,
        "market": market,
        "macro_events": macro_events,
        "headlines": headlines,
        "source_status": status,
    }
    snapshot["analysis"] = analyse(snapshot)
    return snapshot


def _fmt(value: Any, decimals: int = 2, suffix: str = "") -> str:
    number = _float(value)
    return "N/A" if number is None else f"{number:.{decimals}f}{suffix}"


def _fmt_signed(value: Any, suffix: str = "%") -> str:
    number = _float(value)
    return "N/A" if number is None else f"{number:+.2f}{suffix}"


def render_report(snapshot: dict[str, Any]) -> str:
    """Render the R4 Markdown hand-off for R8 and the human R4 reviewer."""
    meta = snapshot["meta"]
    treasury = snapshot.get("treasury") or {}
    macro = snapshot.get("labor_inflation") or {}
    claims = snapshot.get("jobless_claims") or {}
    market = (snapshot.get("market") or {}).get("metrics", {})
    analysis = snapshot["analysis"]

    lines = [
        f"# R4 Macro Agent Report — {meta['iso_year']}-{meta['iso_week']}",
        "",
        f"**As of (SGT):** {meta['as_of_sgt']}  ",
        f"**Target period:** {meta['target_period_sgt']}  ",
        f"**Automated schedule:** {meta['schedule']}  ",
        "**Method:** Free/public data + headline collection + transparent rules; no LLM API.",
        "",
        "## Executive Screen",
        "",
        f"- Rule-based macro bias: **{analysis['macro_bias']}**",
        f"- Confidence: **{analysis['confidence']}**",
        f"- Numeric score: **{analysis['rule_based_score']:+d}**",
        f"- Limitation: {analysis['interpretation_limit']}",
        "",
        "## Confirmed Structured Data",
        "",
        "### Inflation and Labour",
        "",
        "| Metric | Period | Latest | Previous comparison |",
        "|---|---:|---:|---:|",
        (
            f"| CPI-U YoY | {(macro.get('cpi_latest') or {}).get('period', 'N/A')} | "
            f"{_fmt((macro.get('cpi_latest') or {}).get('yoy_pct'), suffix='%')} | "
            f"{_fmt((macro.get('cpi_previous') or {}).get('yoy_pct'), suffix='%')} |"
        ),
        (
            f"| Unemployment rate | {(macro.get('unemployment_latest') or {}).get('period', 'N/A')} | "
            f"{_fmt((macro.get('unemployment_latest') or {}).get('value'), suffix='%')} | N/A |"
        ),
        (
            f"| Initial jobless claims (SA) | {claims.get('week_ending', 'N/A')} | "
            f"{claims.get('initial_claims_sa', 'N/A')} | N/A |"
        ),
        "",
        "### U.S. Treasury Yields",
        "",
        "| Date | 2Y | 10Y | 30Y |",
        "|---|---:|---:|---:|",
    ]
    event_lines = [
        "## Key Macro Events — This Week and Next Week",
        "",
        (
            "Times are converted to Singapore time. Official U.S. calendars are preferred; "
            "public-calendar and recurring-schedule fallbacks are clearly labelled. Release schedules "
            "can change, so R4 should recheck high-impact items before the final write-up."
        ),
        "",
    ]
    for period in ("This week", "Next week"):
        event_lines += [
            f"### {period}",
            "",
            "| Date/time (SGT) | Impact | Category | Event | Source / basis |",
            "|---|---|---|---|---|",
        ]
        period_rows = [
            row for row in snapshot.get("macro_events", []) if row.get("period") == period
        ]
        if not period_rows:
            event_lines.append("| — | — | — | No key event collected. Check source status below. | — |")
        for row in period_rows:
            safe_event = row["event"].replace("|", "\\|")
            event_lines.append(
                f"| {row['date_sgt']} {row['time_sgt']} | {row['impact']} | "
                f"{row['category']} | {safe_event} | "
                f"[{row['source']}]({row['source_url']}) |"
            )
        event_lines.append("")
    structured_index = lines.index("## Confirmed Structured Data")
    lines[structured_index:structured_index] = event_lines

    for row in treasury.get("rows", []):
        lines.append(
            f"| {row['date']} | {_fmt(row.get('2y'), suffix='%')} | "
            f"{_fmt(row.get('10y'), suffix='%')} | {_fmt(row.get('30y'), suffix='%')} |"
        )
    changes = treasury.get("changes_bps", {})
    lines += [
        "",
        (
            "Week-to-date change: "
            f"2Y **{_fmt_signed(changes.get('2y_change_bps'), ' bps')}**, "
            f"10Y **{_fmt_signed(changes.get('10y_change_bps'), ' bps')}**, "
            f"30Y **{_fmt_signed(changes.get('30y_change_bps'), ' bps')}**."
        ),
        "",
        "### Cross-Asset Performance",
        "",
        "| Asset | Ticker | Latest date | Latest close | Weekly return |",
        "|---|---:|---:|---:|---:|",
    ]
    for label in ("SPX", "NDX", "IWM", "VIX", "WTI", "BRENT", "DXY"):
        row = market.get(label, {})
        lines.append(
            f"| {label} | {row.get('ticker', 'N/A')} | {row.get('latest_date', 'N/A')} | "
            f"{_fmt(row.get('latest_close'), 4)} | {_fmt_signed(row.get('weekly_return_pct'))} |"
        )

    lines += [
        "",
        "## All 11 S&P Sector ETFs",
        "",
        "| ETF | Sector | Weekly return | Rule-only label |",
        "|---|---|---:|---|",
    ]
    for row in analysis["sector_momentum"]:
        lines.append(
            f"| {row['ticker']} | {row['sector']} | "
            f"{_fmt_signed(row['weekly_return_pct'])} | {row['momentum_label']} |"
        )

    lines += ["", "## Rule-Based Factors", "", "### Bullish"]
    lines.extend(f"- {item}" for item in analysis["bullish_factors"] or ["None triggered."])
    lines += ["", "### Bearish"]
    lines.extend(f"- {item}" for item in analysis["bearish_factors"] or ["None triggered."])
    lines += ["", "### Neutral / Mixed"]
    lines.extend(f"- {item}" for item in analysis["neutral_factors"] or ["None triggered."])

    lines += [
        "",
        "## Weekly Macro Headlines — Human Review Required",
        "",
        "These are headline-level leads only. A headline is not evidence of the article's full meaning.",
        "",
    ]
    lines.extend(f"- {flag}" for flag in analysis["headline_flags"] or ["No relevant headlines collected."])
    lines += ["", "| Published SGT | Categories | Publisher | Headline |", "|---|---|---|---|"]
    for item in snapshot.get("headlines", []):
        safe_title = item["title"].replace("|", "\\|")
        categories = ", ".join(item["categories"])
        lines.append(
            f"| {item['published_sgt']} | {categories} | {item['publisher']} | "
            f"[{safe_title}]({item['link']}) |"
        )

    lines += [
        "",
        "## R4 Manual Interpretation Checklist",
        "",
        "- Read the highest-impact linked stories and verify them against the full article.",
        "- Check CME FedWatch manually and record the next-meeting probabilities.",
        "- Recheck high-impact items in the automated BLS/BEA/Fed event table for schedule changes.",
        "- Use Trading Economics or another public calendar manually only as a cross-check.",
        "- Check AP or another reputable wire for geopolitical developments not captured by the feeds.",
        "- Check Earnings Whispers only if individual earnings are material to the team forecast.",
        "- Replace this checklist with R4's final causal thesis before R8 synthesis.",
        "",
        "## Source Status and Automation Scope",
        "",
        "| Source | Status | Detail |",
        "|---|---|---|",
    ]
    for row in snapshot["source_status"]:
        detail = row["detail"].replace("|", "\\|")
        lines.append(f"| {row['source']} | {row['status']} | {detail} |")
    lines += [
        "",
        "### Implemented",
        "",
        "- Official Treasury yields, BLS CPI/unemployment, DOL claims where available.",
        "- Cross-asset returns and 11-sector ETF collection through yfinance, with same-week R6 fallback.",
        "- Federal Reserve RSS and macro/geopolitical headline-only RSS collection.",
        "- This-week/next-week key event table from official BLS, BEA and Federal Reserve calendars.",
        "- CSV/JSON/Markdown outputs, explicit source health, and rule-based screening.",
        "",
        "### Intentionally Not Automated",
        "",
        "- Paid/licensed or dynamic-dashboard-only data (FedWatch, Trading Economics API, Earnings Whispers).",
        "- Full-article understanding and final news narrative; this remains the human R4 task.",
        "- Any claim that a headline alone proves a market cause.",
        "",
        "_Educational project output; not investment advice._",
        "",
    ]
    return "\n".join(lines)


def write_outputs(snapshot: dict[str, Any]) -> dict[str, Path]:
    """Write weekly JSON/CSV data and the stable docs hand-off report."""
    meta = snapshot["meta"]
    label = f"{meta['iso_year']}-{meta['iso_week']}"
    output_dir = BASE / "data" / "processed" / "r4" / label
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = BASE / "docs" / f"macro_agent_{label}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    snapshot_path = output_dir / "macro_snapshot.json"
    summary_path = output_dir / "macro_summary.json"
    status_path = output_dir / "source_status.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_path.write_text(
        json.dumps(snapshot["analysis"], indent=2, ensure_ascii=False), encoding="utf-8"
    )
    status_path.write_text(
        json.dumps(snapshot["source_status"], indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report_path.write_text(render_report(snapshot), encoding="utf-8")

    with (output_dir / "treasury_yields.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file, fieldnames=["date", "2y", "10y", "30y"], lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows((snapshot.get("treasury") or {}).get("rows", []))

    market_fields = [
        "label",
        "ticker",
        "baseline_date",
        "baseline_close",
        "latest_date",
        "latest_close",
        "weekly_return_pct",
    ]
    with (output_dir / "market_data.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=market_fields, lineterminator="\n")
        writer.writeheader()
        for label_name, row in (snapshot.get("market") or {}).get("metrics", {}).items():
            writer.writerow({"label": label_name, **row})

    with (output_dir / "headlines.csv").open("w", newline="", encoding="utf-8-sig") as file:
        fields = ["published_sgt", "title", "publisher", "feed", "categories", "link"]
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in snapshot.get("headlines", []):
            writer.writerow({**row, "categories": ";".join(row["categories"])})

    with (output_dir / "macro_events.csv").open("w", newline="", encoding="utf-8-sig") as file:
        fields = [
            "period",
            "timing",
            "scheduled_sgt",
            "date_sgt",
            "time_sgt",
            "impact",
            "category",
            "event",
            "source",
            "source_url",
            "schedule_note",
        ]
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in snapshot.get("macro_events", []):
            writer.writerow(row)

    return {
        "report": report_path,
        "snapshot": snapshot_path,
        "summary": summary_path,
        "status": status_path,
        "output_dir": output_dir,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="R4 free weekly macro automation")
    parser.add_argument(
        "--as-of",
        help="Singapore date in YYYY-MM-DD; defaults to today in Asia/Singapore",
    )
    parser.add_argument("--headline-limit", type=int, default=30)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if Treasury, market data or all 11 sectors are incomplete",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 1 <= args.headline_limit <= 100:
        raise SystemExit("--headline-limit must be between 1 and 100")
    try:
        as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(SGT).date()
    except ValueError as exc:
        raise SystemExit("--as-of must use YYYY-MM-DD") from exc

    snapshot = build_snapshot(as_of, headline_limit=args.headline_limit)
    paths = write_outputs(snapshot)
    print(f"R4 report: {paths['report'].relative_to(BASE)}")
    print(f"Structured outputs: {paths['output_dir'].relative_to(BASE)}")
    print(
        f"Rule-based bias: {snapshot['analysis']['macro_bias']} "
        f"({snapshot['analysis']['confidence']} confidence)"
    )
    errors = [row for row in snapshot["source_status"] if row["status"] == "error"]
    print(f"Source errors recorded without fabrication: {len(errors)}")

    if args.strict:
        market = snapshot.get("market") or {}
        if not snapshot.get("treasury") or not market or not market.get("all_11_sectors_complete"):
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
