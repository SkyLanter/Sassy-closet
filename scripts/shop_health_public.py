#!/usr/bin/env python3
"""Classify shop GET /api/health JSON for the read-only unblock and privacy checks.

Prints one line: "<reading> <True|False> <yes|no>".
reading is blob, kv, local, seed, or "?". The middle flag is blob.readable.
The last flag is yes when the body is outside the public shape from #205:
blob keys other than configured and readable, a secret key name, or the
words token / vercel_blob. The body itself is never printed.
"""
from __future__ import annotations

import json
import sys

READINGS = frozenset({"blob", "kv", "local", "seed"})
BLOB_KEYS = frozenset({"configured", "readable"})
SECRET_KEYS = frozenset({
    "path",
    "prefix",
    "listed",
    "token",
    "sourcelink",
    "sourcelinks",
    "catalogsiteid",
})


def _secret_key(value: object) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in SECRET_KEYS or _secret_key(child):
                return True
        return False
    if isinstance(value, list):
        return any(_secret_key(item) for item in value)
    return False


def shop_health_verdict(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return "? False yes"
    if not isinstance(data, dict):
        return "? False yes"
    blob = data.get("blob") if isinstance(data.get("blob"), dict) else {}
    reading = data.get("reading")
    reading_text = reading if isinstance(reading, str) and reading in READINGS else "?"
    readable = blob.get("readable") is True
    low = raw.lower()
    leak = (
        set(blob) != BLOB_KEYS
        or blob.get("configured") is not True
        or "token" in low
        or "vercel_blob" in low
        or _secret_key(data)
    )
    return f"{reading_text} {readable} {'yes' if leak else 'no'}"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    line = "? False yes"
    try:
        if len(args) == 1:
            with open(args[0], encoding="utf-8") as handle:
                line = shop_health_verdict(handle.read())
    except (OSError, UnicodeError):
        line = "? False yes"
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
