from __future__ import annotations

import os
from typing import Any

from .common import CollectorResult, fail_with_cache, finish, get

SOURCE = "CME FedWatch"


def _flatten(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return [x if isinstance(x, dict) else {"value": x} for x in payload]
    if isinstance(payload, dict):
        for key in ("data", "results", "probabilities", "meetings"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x if isinstance(x, dict) else {"value": x} for x in value]
        return [payload]
    return [{"value": payload}]


def collect() -> CollectorResult:
    api_url = os.getenv("CME_FEDWATCH_API_URL", "").strip()
    api_key = os.getenv("CME_FEDWATCH_API_KEY", "").strip()
    if not api_url or not api_key:
        return fail_with_cache(
            SOURCE,
            "official subscribed REST API",
            RuntimeError("CME_FEDWATCH_API_URL and CME_FEDWATCH_API_KEY are not configured"),
        )
    try:
        # CME subscription setups may use either x-api-key or bearer tokens. Sending both is harmless
        # for most gateways; remove one in .env-backed deployment if your CME onboarding specifies it.
        headers = {"x-api-key": api_key, "Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        payload = get(api_url, headers=headers).json()
        rows = _flatten(payload)
        if not rows:
            raise ValueError("CME FedWatch API returned no rows")
        return finish(SOURCE, rows, "official subscribed REST API")
    except Exception as exc:
        return fail_with_cache(SOURCE, "official subscribed REST API", exc)
