"""Polite, cached HTTP for all collectors."""

from __future__ import annotations
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from typing import Any
import requests
from .paths import CACHE

DEFAULT_UA = "software-substitution-research/0.1 (academic research)"
_last_call: dict[str, float] = {}


def _key(url: str, params: dict | None) -> str:
    blob = url + "?" + json.dumps(params or {}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:32]


def github_token() -> str | None:
    """GITHUB_TOKEN env var, else the token from an authenticated `gh` CLI."""
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    try:
        out = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=20
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def get(
    url: str,
    params: dict | None = None,
    *,
    namespace: str = "misc",
    headers: dict | None = None,
    min_interval: float = 1.0,
    as_json: bool = True,
    refresh: bool = False,
    retries: int = 5,
) -> Any:
    """GET with on-disk cache, per-namespace rate limiting and retry/backoff."""
    folder = CACHE / namespace
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{_key(url, params)}.json"
    if path.exists() and (not refresh):
        return json.loads(path.read_text(encoding="utf-8"))["body"]
    hdrs = {"User-Agent": DEFAULT_UA}
    hdrs.update(headers or {})
    for attempt in range(retries):
        wait = min_interval - (time.time() - _last_call.get(namespace, 0))
        if wait > 0:
            time.sleep(wait)
        _last_call[namespace] = time.time()
        resp = requests.get(url, params=params, headers=hdrs, timeout=60)
        if resp.status_code == 200:
            body = resp.json() if as_json else resp.text
            path.write_text(
                json.dumps(
                    {
                        "url": url,
                        "params": params,
                        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                        "body": body,
                    }
                ),
                encoding="utf-8",
            )
            return body
        if resp.status_code in (403, 429, 500, 502, 503, 504):
            reset = resp.headers.get("x-ratelimit-reset")
            retry_after = resp.headers.get("retry-after")
            if retry_after:
                delay = float(retry_after)
            elif reset and resp.headers.get("x-ratelimit-remaining") == "0":
                delay = max(1.0, float(reset) - time.time() + 1)
            else:
                delay = 2**attempt * 2
            time.sleep(min(delay, 120))
            continue
        resp.raise_for_status()
    raise RuntimeError(f"GET failed after {retries} attempts: {url} {params}")
