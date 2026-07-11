from __future__ import annotations

import asyncio
import os
import re
from datetime import date

from .common import CollectorResult, fail_with_cache, finish

SOURCE = "Earnings Whispers"
URLS = ["https://www.earningswhispers.com/calendar", "https://www.earningswhispers.com/"]
TICKER = re.compile(r"^[A-Z][A-Z0-9.\-]{0,7}$")


async def _browser_collect() -> list[dict]:
    from playwright.async_api import async_playwright

    headless = os.getenv("HEADLESS", "true").lower() != "false"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            viewport={"width": 1440, "height": 1000},
        )
        page = await context.new_page()
        last_error = None
        for url in URLS:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(4000)
                body = await page.locator("body").inner_text()
                links = await page.locator("a").evaluate_all(
                    "els => els.map(a => ({text:(a.innerText||'').trim(), href:a.href, title:a.title||''}))"
                )
                if "access denied" in body.lower() or "captcha" in body.lower():
                    raise RuntimeError("Site presented an access challenge")
                items = []
                for a in links:
                    text = a["text"].strip()
                    title = a["title"].strip()
                    href = a["href"]
                    candidates = re.findall(r"\b[A-Z][A-Z0-9.\-]{0,7}\b", f"{text} {title}")
                    ticker = next((c for c in candidates if TICKER.match(c) and c not in {"AM", "PM", "EPS", "CEO", "EST"}), None)
                    if ticker and ("earn" in href.lower() or "ticker" in href.lower() or "calendar" in href.lower()):
                        items.append({"ticker": ticker, "company_or_label": text or title, "url": href, "retrieved_date": date.today().isoformat()})
                dedup, seen = [], set()
                for x in items:
                    key = (x["ticker"], x["url"])
                    if key not in seen:
                        seen.add(key); dedup.append(x)
                if dedup:
                    await browser.close()
                    return dedup[:100]
                last_error = RuntimeError("Page loaded but earnings links were not recognized")
            except Exception as exc:
                last_error = exc
        await browser.close()
        raise last_error or RuntimeError("No Earnings Whispers page could be loaded")


def collect() -> CollectorResult:
    try:
        data = asyncio.run(_browser_collect())
        return finish(SOURCE, data, "Playwright browser parser")
    except Exception as exc:
        return fail_with_cache(SOURCE, "Playwright browser parser", exc)
