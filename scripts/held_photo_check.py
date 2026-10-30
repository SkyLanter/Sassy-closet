#!/usr/bin/env python3
"""Read-only held-photo exposure check (report only).

For every mã in data/held.json, collect photo URLs that reference it from
local catalog/product data and report which ones still answer HTTP 200.

URL sources (all local files, any combination):
  --catalog    catalog JSON (products[].images[].src, e.g. /products/S14/cover.jpg)
  --health     saved health JSON that still has blob.listed object paths.
               Public /api/health no longer returns those paths.
  --files      local-product-files.json style list ("S14/cover.jpg")
  --probe-default  also probe <mã>/cover.jpg and <mã>/photo-2.jpg per held mã
Paths are turned into URLs under --blob-base (+ --prefix for relative paths).

Network: HEAD requests only, rate-limited (--rate req/s, default 2). Never
GET, PUT, DELETE or any write. Deleting exposed objects is Boss's call.

Output JSON (schema held-photos/v1) is read by daily_shop_check.py
(--held-photos) as section `held_photos`: WARN when any exposed, never FAIL.
Exit: 0 none exposed, 1 some exposed, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from held_policy import norm_ma

DEFAULT_BLOB = "https://efsi0jejsfy7j058.public.blob.vercel-storage.com"
DEFAULT_PREFIX = "sassy-closet-shop/"
SCHEMA = "held-photos/v1"
MA_RE = re.compile(r"(?:^|/)products/([A-Z]\d{2})/|^([A-Z]\d{2})/")


def load_held(path: Path) -> list[str]:
    d = json.loads(path.read_text(encoding="utf-8"))
    held = d.get("heldIncomplete") if isinstance(d, dict) else None
    if not isinstance(held, list):
        raise ValueError(f"{path.name}: no heldIncomplete list")
    return [c for c in (norm_ma(m) for m in held) if c]


def ma_of(path: str) -> str | None:
    m = MA_RE.search(path)
    return (m.group(1) or m.group(2)) if m else None


def paths_from_catalog(d: dict) -> list[str]:
    out = []
    for p in d.get("products", []) if isinstance(d, dict) else []:
        for im in p.get("images", []) or []:
            src = im.get("src") if isinstance(im, dict) else im
            if isinstance(src, str):
                out.append(src)
    return out


def paths_from_health(d: dict) -> list[str]:
    listed = (d.get("blob") or {}).get("listed") if isinstance(d, dict) else None
    return [x for x in listed if isinstance(x, str)] if isinstance(listed, list) else []


def to_url(path: str, blob_base: str, prefix: str) -> str:
    if path.startswith(("http://", "https://")):
        return path
    p = path.lstrip("/")
    if not p.startswith(prefix):
        p = prefix + (p if p.startswith("products/") else "products/" + p)
    return blob_base.rstrip("/") + "/" + p


def collect(held: list[str], sources: dict[str, list[str]], blob_base: str, prefix: str,
            probe_default: bool) -> dict[str, dict]:
    """Return {url: {"ma", "sources"}} for held mãs only."""
    hs = set(held)
    urls: dict[str, dict] = {}
    for src, paths in sources.items():
        for p in paths:
            ma = ma_of(p.split("://", 1)[-1].split("/", 1)[-1] if "://" in p else p)
            if ma in hs:
                u = to_url(p, blob_base, prefix)
                urls.setdefault(u, {"ma": ma, "sources": []})["sources"].append(src)
    if probe_default:
        for ma in held:
            for f in ("cover.jpg", "photo-2.jpg"):
                u = to_url(f"products/{ma}/{f}", blob_base, prefix)
                urls.setdefault(u, {"ma": ma, "sources": []})["sources"].append("probe-default")
    return urls


def head_status(url: str, timeout: float = 15.0) -> int | str:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "sassy-closet-held-photo-check/1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001
        return f"error: {type(e).__name__}"


def check(urls: dict[str, dict], head=None, rate: float = 2.0, sleep=None) -> list[dict]:
    head = head or head_status
    sleep = sleep or time.sleep
    rows, gap = [], (1.0 / rate if rate > 0 else 0.0)
    for i, (u, meta) in enumerate(sorted(urls.items(), key=lambda kv: (kv[1]["ma"], kv[0]))):
        if i and gap:
            sleep(gap)
        st = head(u)
        rows.append({"ma": meta["ma"], "url": u, "sources": sorted(set(meta["sources"])),
                     "status": st, "exposed": st == 200})
    return rows


def report(held: list[str], rows: list[dict]) -> dict:
    exposed = [r for r in rows if r["exposed"]]
    errors = [r for r in rows if not isinstance(r["status"], int)]
    return {
        "schema": SCHEMA,
        "checkedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "held": held, "checked": len(rows),
        "exposed": [{"ma": r["ma"], "url": r["url"]} for r in exposed],
        "exposedMas": sorted({r["ma"] for r in exposed}),
        "errors": [{"ma": r["ma"], "url": r["url"], "status": r["status"]} for r in errors],
        "rows": rows, "method": "HEAD", "writes": "none",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--held", type=Path, default=Path("data/held.json"))
    p.add_argument("--catalog", type=Path, action="append", default=[])
    p.add_argument("--health", type=Path, action="append", default=[])
    p.add_argument("--files", type=Path, action="append", default=[])
    p.add_argument("--probe-default", action="store_true")
    p.add_argument("--blob-base", default=DEFAULT_BLOB)
    p.add_argument("--prefix", default=DEFAULT_PREFIX)
    p.add_argument("--rate", type=float, default=2.0, help="max HEAD requests per second (cap 2)")
    p.add_argument("--out-json", type=Path)
    a = p.parse_args(argv)
    if a.rate <= 0 or a.rate > 2:
        p.error("--rate must be in (0, 2]")
    try:
        held = load_held(a.held)
        sources: dict[str, list[str]] = {}
        for f in a.catalog:
            sources.setdefault("catalog", []).extend(paths_from_catalog(json.loads(f.read_text(encoding="utf-8"))))
        for f in a.health:
            sources.setdefault("health-listing", []).extend(paths_from_health(json.loads(f.read_text(encoding="utf-8"))))
        for f in a.files:
            d = json.loads(f.read_text(encoding="utf-8"))
            sources.setdefault("product-files", []).extend(x for x in d if isinstance(x, str))
    except (OSError, ValueError) as e:
        print(f"input error: {e}", file=sys.stderr)
        return 2
    rows = check(collect(held, sources, a.blob_base, a.prefix, a.probe_default), rate=a.rate)
    rep = report(held, rows)
    if a.out_json:
        a.out_json.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    print(f"held {len(held)} · checked {rep['checked']} URLs · exposed {len(rep['exposed'])}"
          + (": " + ", ".join(e["url"].split("/products/", 1)[-1] for e in rep["exposed"]) if rep["exposed"] else ""))
    return 1 if rep["exposed"] else 0


if __name__ == "__main__":
    sys.exit(main())
