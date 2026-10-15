"""Flag fixture sell prices that are not a whole dollar.

Read-only. A fixture catalog is read and left unchanged. A price such as
25.50 is copied into the flag with its original digits and is not rounded
to 25 or 26. S06 at 25 stays clean. Nothing here writes data/held.json,
a price, or a catalog row. Held mãs stay held.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import load_held_policy

_FRACTION = re.compile(r"\d+\.(\d+)")


@dataclass(frozen=True)
class CatalogRow:
    """One catalog row. price_usd stays as it was passed in."""

    ma: str
    price_usd: object
    price_set: bool


@dataclass(frozen=True)
class NonWholeDollarFlag:
    ma: str
    stored: str
    held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "field": "priceUsd",
            "kind": "non_whole_dollar",
            "stored": self.stored,
            "held": self.held,
        }


def flag_non_whole_dollars(
    rows: list[CatalogRow],
    held: frozenset[str] = frozenset(),
) -> list[NonWholeDollarFlag]:
    """Return flags for fractional sell prices. Row objects are not edited."""
    flags: list[NonWholeDollarFlag] = []
    for row in rows:
        if not _is_non_whole_dollar(row.price_usd):
            continue
        code = row.ma.strip().upper()
        flags.append(NonWholeDollarFlag(code, _stored(row.price_usd), code in held))
    return flags


def report_json(
    rows: list[CatalogRow],
    flags: list[NonWholeDollarFlag],
    held: frozenset[str],
) -> dict[str, object]:
    return {
        "readOnly": True,
        "s06": "stays $25",
        "heldMas": "stay held",
        "rows": [_row_json(row, held) for row in rows],
        "flagCount": len(flags),
        "flags": [flag.as_json() for flag in flags],
    }


def load_catalog(path: Path) -> list[CatalogRow]:
    payload = json.loads(path.read_text(encoding="utf-8"), parse_float=_keep_decimal_token)
    products = payload.get("products") if isinstance(payload, dict) else payload
    if not isinstance(products, list):
        raise ValueError("catalog must be a list of rows or an object with products")
    rows: list[CatalogRow] = []
    for item in products:
        if not isinstance(item, dict):
            raise ValueError("each catalog row must be an object")
        ma = item.get("ma")
        if not isinstance(ma, str) or not ma.strip():
            raise ValueError("each catalog row needs a mã")
        rows.append(CatalogRow(ma, item.get("priceUsd"), "priceUsd" in item))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag fixture sell prices that are not a whole dollar. Read-only. Does not round."
    )
    parser.add_argument("--catalog", required=True, help="Fixture catalog JSON. Read and left unchanged.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json. Not written.")
    args = parser.parse_args(argv)
    if _is_live_target(args.catalog) or _is_live_target(args.held):
        print("Catalog fixtures only. Live catalogs are not read.", file=sys.stderr)
        return 2
    path = Path(args.catalog)
    if not path.is_file():
        print(f"Fixture not found: {path}", file=sys.stderr)
        return 2
    held_path = Path(args.held) if args.held else None
    if held_path is not None and not held_path.is_file():
        print(f"Held list not found: {held_path}", file=sys.stderr)
        return 2
    try:
        rows = load_catalog(path)
        policy = load_held_policy(held_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    held = frozenset(policy.held)
    flags = flag_non_whole_dollars(rows, held)
    print(json.dumps(report_json(rows, flags, held), ensure_ascii=False, indent=2))
    return 1 if flags else 0


def _keep_decimal_token(token: str) -> str:
    """Keep the JSON digits, so 25.50 stays 25.50 instead of a binary float."""
    return token


def _is_non_whole_dollar(value: object) -> bool:
    token = _amount_token(value)
    if token is None:
        return False
    match = _FRACTION.fullmatch(token)
    if match is None:
        return False
    return any(digit != "0" for digit in match.group(1))


def _amount_token(value: object) -> str | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(Decimal(str(value)), "f")
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return None
        return stripped
    if isinstance(value, Decimal):
        return format(value, "f")
    return None


def _stored(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, float):
        return format(Decimal(str(value)), "f")
    return str(value)


def _row_json(row: CatalogRow, held: frozenset[str]) -> dict[str, object]:
    code = row.ma.strip().upper()
    body: dict[str, object] = {"ma": code, "held": code in held}
    if row.price_set:
        body["priceUsd"] = row.price_usd
    return body


def _is_live_target(value: str) -> bool:
    text = value.strip().casefold()
    return text.startswith("http://") or text.startswith("https://")


if __name__ == "__main__":
    raise SystemExit(main())
