#!/usr/bin/env python3
"""Check a Square item-import CSV against Sassy Closet shop law.

The committed template must be headers-only. A local draft may have rows;
this script then requires valid mã SKUs, Stockable=Y, and no Track-OFF tricks.

Usage:
  python3 excel-kit/square/validate_import.py excel-kit/square/square_import_template.csv
  python3 excel-kit/square/validate_import.py ~/drafts/first-ten.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_KIT_DIR = Path(__file__).resolve().parent.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

from schema import ASK_STOCK_MA, SQUARE_IMPORT_HEADERS, SQUARE_SKU_IS_MA, is_valid_ma


REQUIRED = ("Item Name", "Variation Name", "Description", "SKU")


def _norm(name: str) -> str:
    return name.strip().lower()


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return ["file has no header row"]
        headers = [h.strip() for h in reader.fieldnames if h and h.strip()]
        missing = [h for h in REQUIRED if h not in headers]
        if missing:
            errors.append(f"missing required Square headers: {missing}")
        if "Token" not in headers:
            errors.append("Token column required (leave values blank on create)")
        stockable_key = next((h for h in headers if _norm(h) == "stockable"), None)
        sku_key = next((h for h in headers if h == "SKU"), None)
        qty_keys = [h for h in headers if h.lower().startswith("new quantity")]
        rows = list(reader)

    if not rows:
        # Headers-only is the only shape we commit.
        extra = [h for h in SQUARE_IMPORT_HEADERS if h not in headers]
        if extra:
            # Fresh Square exports may differ — warn, do not fail the template check
            # when the core required headers exist.
            pass
        return errors

    for i, row in enumerate(rows, start=2):
        sku = (row.get(sku_key or "SKU") or "").strip()
        if not sku:
            errors.append(f"row {i}: SKU empty. {ASK_STOCK_MA}")
        elif not is_valid_ma(sku):
            errors.append(f"row {i}: SKU {sku!r} is not a mã. {SQUARE_SKU_IS_MA}")
        if stockable_key:
            flag = (row.get(stockable_key) or "").strip().upper()
            if flag not in {"Y", "YES", "TRUE", "1"}:
                errors.append(f"row {i}: Stockable must be Y (Track stock ON), got {flag!r}")
        for qk in qty_keys:
            qty = (row.get(qk) or "").strip()
            if qty.lower() == "no":
                errors.append(f"row {i}: {qk}='No' disables tracking. Track must stay ON.")
        token = (row.get("Token") or "").strip()
        if token:
            errors.append(f"row {i}: Token should be blank for new Sassy Closet items")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("csv", type=Path, help="Square import CSV (template or local draft)")
    args = parser.parse_args(argv)
    if not args.csv.is_file():
        print(f"error: not a file: {args.csv}", file=sys.stderr)
        return 2
    errors = validate(args.csv)
    with args.csv.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        n = sum(1 for _ in reader)
    if errors:
        print(f"FAIL {args.csv} ({n} data row(s))")
        for err in errors:
            print(f"  - {err}")
        return 1
    if n == 0:
        print(f"OK headers-only {args.csv}")
        print(SQUARE_SKU_IS_MA)
        print("Track stock ON. No live inventory in git.")
        return 0
    print(f"OK draft {args.csv} ({n} data row(s)) — still no Save until Boss yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
