from __future__ import annotations

import feedparser

from .common import CollectorResult, fail_with_cache, finish, get

SOURCE = "Associated Press News"
FEEDS = [
    "https://apnews.com/index.rss",
    "https://apnews.com/hub/business?output=rss",
    "https://apnews.com/hub/world-news?output=rss",
]


def collect() -> CollectorResult:
    try:
        seen, items = set(), []
        errors = []
        for url in FEEDS:
            try:
                content = get(url).content
                parsed = feedparser.parse(content)
                for e in parsed.entries:
                    link = e.get("link", "")
                    title = e.get("title", "").strip()
                    key = link or title
                    if not title or key in seen:
                        continue
                    seen.add(key)
                    items.append({
                        "title": title,
                        "published": e.get("published") or e.get("updated"),
                        "summary": e.get("summary", ""),
                        "url": link,
                    })
            except Exception as e:
                errors.append(str(e))
        if not items:
            raise RuntimeError("; ".join(errors) or "No AP RSS entries found")
        return finish(SOURCE, items[:30], "public RSS feeds")
    except Exception as exc:
        return fail_with_cache(SOURCE, "public RSS feeds", exc)
