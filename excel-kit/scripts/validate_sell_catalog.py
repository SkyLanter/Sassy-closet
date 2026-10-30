#!/usr/bin/env python3
"""Validate a catalog.v1 JSON against schema + the first-ten allowlist.

Usage:
  python3 excel-kit/scripts/validate_sell_catalog.py out/sell-catalog.v1.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_KIT_DIR = Path(__file__).resolve().parent.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

from sell_catalog import (  # noqa: E402
    SCHEMA_ID,
    SELL_ALLOWLIST,
    SELL_ALLOWLIST_PRICE_USD,
    CatalogError,
    load_catalog_json,
    validate_catalog,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("json", type=Path, help="catalog.v1 JSON path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    path = args.json.expanduser()
    if not path.is_file():
        print(f"error: not a file: {path}", file=sys.stderr)
        return 2
    try:
        doc = load_catalog_json(path)
        validate_catalog(doc)
    except CatalogError as exc:
        print(f"FAIL {path}")
        print(f"  - {exc}")
        return 1
    products = doc["products"]
    hold = [p["ma"] for p in products if p["status"] == "hold"]
    print(f"PASS {path}")
    print(f"  schema: {SCHEMA_ID}")
    print(f"  allowlist: {' '.join(SELL_ALLOWLIST)}")
    print(f"  hold (priceUsd=null): {' '.join(hold)}")
    priced = [
        f"{ma}=${price}"
        for ma, price in SELL_ALLOWLIST_PRICE_USD.items()
        if price is not None
    ]
    print(f"  priced: {', '.join(priced)}")
    print("  qty=1 · no invented mã · no cost/source/PII keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
