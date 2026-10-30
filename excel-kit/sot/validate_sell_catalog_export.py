#!/usr/bin/env python3
"""Validate a sell-test catalog export before CLONE_TO_OFFICIAL.

Kit lane. Merges with the catalog-export agent — this script does not
write Official Excel, does not Save Square, does not Send Facebook,
does not mint mã, and does not ask for passwords.

Accepts JSON (list or {items: [...]}) or CSV. Every row.ma must be one of
A01 S01 P01–P05 K01 H01 A02. Extra mãs fail. Missing allowlist mãs fail
under --strict-complete (default on).

Usage:
  python3 excel-kit/sot/validate_sell_catalog_export.py --help
  python3 excel-kit/sot/validate_sell_catalog_export.py path/to/export.json
  python3 excel-kit/sot/validate_sell_catalog_export.py path/to/export.csv --no-strict-complete
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
if str(KIT) not in sys.path:
    sys.path.insert(0, str(KIT))

from sell_test_allowlist import (  # noqa: E402
    HOLD_MAS,
    SELL_TEST_KIND,
    SELL_TEST_MAS,
    SELL_TEST_PRICE_USD,
    SELL_TEST_SHOP_URL,
    is_allowed_sell_ma,
    refuse_invented_ma,
)

REQUIRED_FIELDS = ("ma",)
RECOMMENDED_FIELDS = (
    "kind",
    "title_en",
    "title_vn",
    "description_en",
    "description_vn",
    "status",
    "price_usd",
    "inbox_for_price",
    "cover",
    "colors",
    "images",
)

ALLOWED_STATUS = {"Available", "Hold", "available", "hold"}
THERMOS_TYPES = {"THERMOS", "BÌNH", "BINH"}


def _load_rows(path: Path) -> list[dict[str, object]]:
    raw = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            rows = parsed
        elif isinstance(parsed, dict):
            items = (
                parsed.get("items")
                or parsed.get("products")
                or parsed.get("catalog")
            )
            if not isinstance(items, list):
                raise ValueError(
                    "JSON object needs items / products / catalog array "
                    "(catalog.v1 uses products[])"
                )
            rows = items
        else:
            raise ValueError("JSON must be a list or an object with items[]")
        out: list[dict[str, object]] = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("each catalog item must be an object")
            out.append(row)
        return out
    if suffix in {".csv", ".tsv"}:
        dialect = csv.excel_tab if suffix == ".tsv" else csv.excel
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle, dialect=dialect))
    raise ValueError(f"unsupported export type {suffix!r} — use .json / .csv / .tsv")


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text in {"1", "true", "yes", "y"}


def validate_rows(
    rows: list[dict[str, object]],
    *,
    strict_complete: bool,
) -> list[str]:
    errors: list[str] = []
    seen: list[str] = []
    for i, row in enumerate(rows, start=1):
        keys = {str(k).strip().lower(): k for k in row}
        ma_key = keys.get("ma") or keys.get("mã") or keys.get("code")
        if ma_key is None:
            errors.append(f"row {i}: missing ma")
            continue
        raw_ma = row[ma_key]
        try:
            ma = refuse_invented_ma(raw_ma)
        except ValueError as exc:
            errors.append(f"row {i}: {exc}")
            continue
        if ma in seen:
            errors.append(f"row {i}: mã collision — {ma} already in this export")
            continue
        seen.append(ma)

        kind_key = keys.get("kind") or keys.get("type")
        if kind_key is not None and str(row[kind_key] or "").strip():
            kind = str(row[kind_key]).strip().upper()
            expected = SELL_TEST_KIND[ma]
            thermos_ok = ma in HOLD_MAS and kind in THERMOS_TYPES
            # Letter (A) or shop word (TOP / SET / …) — first letter must match.
            # catalog.v1 uses type=thermos for P02/P05 (letter is still P).
            if (
                kind != expected
                and not thermos_ok
                and (not kind or kind[0] != expected)
            ):
                errors.append(
                    f"row {i} {ma}: kind {kind!r} does not match allowlist letter {expected}"
                )

        status_key = keys.get("status")
        status = ""
        if status_key is not None and str(row[status_key] or "").strip():
            status = str(row[status_key]).strip()
            if status not in ALLOWED_STATUS:
                errors.append(
                    f"row {i} {ma}: status {status!r} — sell-test uses Available | Hold only"
                )

        price_key = (
            keys.get("price_usd")
            or keys.get("priceusd")
            or keys.get("price")
            or keys.get("sell_usd")
        )
        inbox_key = keys.get("inbox_for_price")
        inbox = _as_bool(row[inbox_key]) if inbox_key is not None else False
        if status.lower() == "hold":
            inbox = True
        raw_price = None if price_key is None else row[price_key]
        if raw_price is None:
            price = ""
        else:
            price = str(raw_price).strip()
            if price.lower() in {"none", "null"}:
                price = ""
        if inbox and price and price not in {"0", "0.00"}:
            errors.append(
                f"row {i} {ma}: Hold / Inbox for price must not carry a USD sell price"
            )
        expected_price = SELL_TEST_PRICE_USD.get(ma)
        if expected_price is None and price and not inbox:
            errors.append(f"row {i} {ma}: allowlist is Hold — do not publish a USD price")
        if expected_price is not None and price:
            try:
                published = float(price)
            except ValueError:
                errors.append(f"row {i} {ma}: price {price!r} is not a number")
            else:
                if published != float(expected_price):
                    errors.append(
                        f"row {i} {ma}: price {price!r} disagrees with Boss table ${expected_price}"
                    )

    extra = [ma for ma in seen if not is_allowed_sell_ma(ma)]
    if extra:
        errors.append(f"invented mã in export: {', '.join(extra)}")

    if strict_complete:
        missing = [ma for ma in SELL_TEST_MAS if ma not in seen]
        if missing:
            errors.append(
                "export missing allowlist mãs (seed drift): " + ", ".join(missing)
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a sell-test catalog export. Never invents mã. "
            "Does not write Official, Square, or Facebook."
        )
    )
    parser.add_argument("export", nargs="?", help="path to export.json or export.csv")
    parser.add_argument(
        "--strict-complete",
        dest="strict_complete",
        action="store_true",
        default=True,
        help="require all 10 allowlist mãs (default)",
    )
    parser.add_argument(
        "--no-strict-complete",
        dest="strict_complete",
        action="store_false",
        help="allow a partial export (still refuse invented mã)",
    )
    args = parser.parse_args(argv)
    if not args.export:
        parser.print_help()
        print(
            f"\nAllowlist ({len(SELL_TEST_MAS)}): {', '.join(SELL_TEST_MAS)}\n"
            f"Shop: {SELL_TEST_SHOP_URL}\n"
            "CLONE_TO_OFFICIAL: map these mãs onto Official only after Boss/Stock "
            "confirms. Square Free still wins on-hand. No Square Save. No FB Send."
        )
        return 0

    path = Path(args.export)
    if not path.is_file():
        print(f"error: export not found: {path}", file=sys.stderr)
        return 2
    try:
        rows = _load_rows(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: cannot read export: {exc}", file=sys.stderr)
        return 2

    errors = validate_rows(rows, strict_complete=args.strict_complete)
    print(f"export: {path}")
    print(f"rows: {len(rows)}")
    print(f"allowlist: {', '.join(SELL_TEST_MAS)}")
    print(f"shop: {SELL_TEST_SHOP_URL}")
    print("hard stops: no invent mã · no Square Save · no FB Send · no passwords")
    if errors:
        print("FAIL:")
        for line in errors:
            print(f"  - {line}")
        return 2
    print("OK — export mãs match the sell-test allowlist. Ready for CLONE_TO_OFFICIAL review.")
    print("Next: Official Excel is a working copy, not a second stock. ASK STOCK before any new mã.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
