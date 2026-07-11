from __future__ import annotations

import re
from bs4 import BeautifulSoup

from .common import CollectorResult, fail_with_cache, finish, get

SOURCE = "Finviz Futures Performance"
URL = "https://finviz.com/futures_performance.ashx?v=12"
PCT = re.compile(r"^[+-]?\d+(?:\.\d+)?%$")


def collect() -> CollectorResult:
    try:
        html = get(URL, headers={"Referer": "https://finviz.com/"}).text
        soup = BeautifulSoup(html, "lxml")
        items = []
        # Finviz changes markup periodically. Parse rows semantically instead of relying on one CSS class.
        for tr in soup.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
            if len(cells) < 2:
                continue
            pct_values = [x for x in cells if PCT.match(x.replace(" ", ""))]
            if not pct_values:
                continue
            label = next((x for x in cells if x and not PCT.match(x.replace(" ", "")) and len(x) < 80), None)
            if label:
                items.append({"asset": label, "performance": pct_values[-1]})
        # Fallback: links/tile text used by the current heatmap-like view.
        if not items:
            texts = [x.strip() for x in soup.stripped_strings]
            for i, t in enumerate(texts):
                if PCT.match(t.replace(" ", "")) and i > 0:
                    label = texts[i - 1]
                    if 0 < len(label) < 80:
                        items.append({"asset": label, "performance": t})
        dedup = []
        seen = set()
        for x in items:
            k = (x["asset"], x["performance"])
            if k not in seen:
                seen.add(k); dedup.append(x)
        if not dedup:
            raise ValueError("Finviz page loaded but no futures performance values were recognized")
        return finish(SOURCE, dedup[:50], "HTML semantic parser")
    except Exception as exc:
        return fail_with_cache(SOURCE, "HTML semantic parser", exc)
