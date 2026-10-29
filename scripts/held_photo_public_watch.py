#!/usr/bin/env python3
"""Held photo public watch (piece 46): READ-ONLY, WARN-only.

Lists held mãs from the SHARED held list (sassy-closet-shop/lib/held-incomplete.ts
-> the JSON it imports; --held overrides) whose photos are still publicly
reachable on Blob. Known case: S14 / A24 / A25.

Reuses held_photo_check (piece 30) for URL collection and HEAD probing and
emits the same held-photos/v1 schema, plus `watch` metadata.

Modes:
  live     HEAD only (urllib, method=HEAD), rate <= 2 req/s. Never GET/PUT/DELETE.
  offline  --fixture STATUS_JSON: {"<url or products/MA/file>": 200|404|"error: X"}.
           No network at all; unknown URLs report "error: not-in-fixture".
Deleting or changing Blob objects is Boss's call; this script never does it.
Exit: 0 none exposed, 1 some exposed (WARN), 2 usage/input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import held_photo_check as hpc

ROOT = Path(__file__).resolve().parents[1]
HELD_TS = ROOT / "sassy-closet-shop" / "lib" / "held-incomplete.ts"
KNOWN_EXPOSED = ("S14", "A24", "A25")


def shared_held(held: Path | None = None, held_ts: Path = HELD_TS) -> tuple[list[str], str]:
    if held is not None:
        return hpc.load_held(held), str(held)
    from too_cheap_check import held_json_from_ts
    p = held_json_from_ts(held_ts)
    return hpc.load_held(p), str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)


def fixture_head(fixture: dict, prefix: str = hpc.DEFAULT_PREFIX):
    def head(url: str):
        if url in fixture:
            return fixture[url]
        tail = url.split("/" + prefix, 1)[-1] if ("/" + prefix) in url else url
        for k in (tail, tail.split("products/", 1)[-1]):
            if k in fixture:
                return fixture[k]
        return "error: not-in-fixture"
    return head


def run(held: list[str], sources: dict[str, list[str]], *, fixture: dict | None = None,
        blob_base: str = hpc.DEFAULT_BLOB, prefix: str = hpc.DEFAULT_PREFIX,
        probe_default: bool = True, rate: float = 2.0, head=None, sleep=None,
        held_source: str = "") -> dict:
    if not 0 < rate <= 2:
        raise ValueError("rate must be in (0, 2]")
    urls = hpc.collect(held, sources, blob_base, prefix, probe_default)
    if fixture is not None:
        head, sleep = fixture_head(fixture, prefix), (lambda s: None)
    rows = hpc.check(urls, head=head, rate=rate, sleep=sleep)
    rep = hpc.report(held, rows)
    rep["watch"] = {
        "piece": 46, "mode": "offline" if fixture is not None else "live",
        "heldSource": held_source, "knownExposed": list(KNOWN_EXPOSED),
        "stillExposedKnown": [m for m in KNOWN_EXPOSED if m in rep["exposedMas"]],
        "newlyExposed": [m for m in rep["exposedMas"] if m not in KNOWN_EXPOSED],
        "note": "WARN only; Blob delete is Boss's call",
    }
    return rep


def load_sources(catalog=(), health=(), files=()) -> dict[str, list[str]]:
    s: dict[str, list[str]] = {}
    for f in catalog:
        s.setdefault("catalog", []).extend(hpc.paths_from_catalog(json.loads(Path(f).read_text(encoding="utf-8"))))
    for f in health:
        s.setdefault("health-listing", []).extend(hpc.paths_from_health(json.loads(Path(f).read_text(encoding="utf-8"))))
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        s.setdefault("product-files", []).extend(x for x in d if isinstance(x, str))
    return s


def summary_line(rep: dict) -> str:
    w = rep["watch"]
    s = f"held {len(rep['held'])} · {rep['checked']} URLs HEAD ({w['mode']}) · exposed mã: {', '.join(rep['exposedMas']) or 'none'}"
    if w["newlyExposed"]:
        s += f" · NEW: {', '.join(w['newlyExposed'])}"
    return s


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--held", type=Path, help="held JSON (default: shared list via held-incomplete.ts)")
    p.add_argument("--held-ts", type=Path, default=HELD_TS)
    p.add_argument("--catalog", type=Path, action="append", default=[])
    p.add_argument("--health", type=Path, action="append", default=[])
    p.add_argument("--files", type=Path, action="append", default=[])
    p.add_argument("--no-probe-default", action="store_true")
    p.add_argument("--fixture", type=Path, help="offline status JSON (no network)")
    p.add_argument("--blob-base", default=hpc.DEFAULT_BLOB)
    p.add_argument("--prefix", default=hpc.DEFAULT_PREFIX)
    p.add_argument("--rate", type=float, default=2.0)
    p.add_argument("--out-json", type=Path)
    a = p.parse_args(argv)
    if not 0 < a.rate <= 2:
        p.error("--rate must be in (0, 2]")
    try:
        held, src = shared_held(a.held, a.held_ts)
        sources = load_sources(a.catalog, a.health, a.files)
        fixture = json.loads(a.fixture.read_text(encoding="utf-8")) if a.fixture else None
        if fixture is not None and not isinstance(fixture, dict):
            raise ValueError("fixture must be a JSON object")
    except (OSError, ValueError) as e:
        print(f"input error: {e}", file=sys.stderr)
        return 2
    rep = run(held, sources, fixture=fixture, blob_base=a.blob_base, prefix=a.prefix,
              probe_default=not a.no_probe_default, rate=a.rate, held_source=src)
    if a.out_json:
        a.out_json.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    print(summary_line(rep))
    return 1 if rep["exposed"] else 0


if __name__ == "__main__":
    sys.exit(main())
