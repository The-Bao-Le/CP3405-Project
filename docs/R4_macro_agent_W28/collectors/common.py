from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class CollectorResult:
    source: str
    ok: bool
    data: list[dict[str, Any]]
    fetched_at: str
    method: str
    error: str | None = None
    stale_cache: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "ok": self.ok,
            "data": self.data,
            "fetched_at": self.fetched_at,
            "method": self.method,
            "error": self.error,
            "stale_cache": self.stale_cache,
        }


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36 CP3405-R4/1.0"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
    })
    return s


@retry(
    retry=retry_if_exception_type((requests.RequestException, TimeoutError)),
    stop=stop_after_attempt(4),
    wait=wait_exponential_jitter(initial=1, max=12),
    reraise=True,
)
def get(url: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> requests.Response:
    timeout = env_int("HTTP_TIMEOUT", 30)
    r = session().get(url, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r


def _cache_path(source: str) -> Path:
    digest = hashlib.sha256(source.encode()).hexdigest()[:12]
    return CACHE_DIR / f"{digest}.json"


def save_cache(source: str, payload: dict[str, Any]) -> None:
    p = _cache_path(source)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def load_cache(source: str, max_age_hours: int | None = None) -> dict[str, Any] | None:
    p = _cache_path(source)
    if not p.exists():
        return None
    if max_age_hours is not None:
        age_hours = (time.time() - p.stat().st_mtime) / 3600
        if age_hours > max_age_hours:
            return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def finish(source: str, data: list[dict[str, Any]], method: str) -> CollectorResult:
    result = CollectorResult(source, True, data, now_iso(), method)
    save_cache(source, result.as_dict())
    return result


def fail_with_cache(source: str, method: str, exc: Exception) -> CollectorResult:
    cached = load_cache(source)
    if cached and cached.get("data"):
        return CollectorResult(
            source=source,
            ok=False,
            data=cached["data"],
            fetched_at=cached.get("fetched_at", now_iso()),
            method=method,
            error=f"Live fetch failed; returned last successful cache: {type(exc).__name__}: {exc}",
            stale_cache=True,
        )
    return CollectorResult(source, False, [], now_iso(), method, f"{type(exc).__name__}: {exc}")
