"""Flag a fixture catalog row whose sell price is 0.

Read-only. The fixture is read and left unchanged. A stored 0 stays 0.
A missing, null, or blank price is not this flag. S06 at $25 stays clean.
Nothing here writes data/held.json, a price, or a catalog row.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Never

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import default_held_path, load_held_policy

_ROOT = _SCRIPTS.parent
SHOP_CATALOG = _ROOT / "sassy-closet-shop" / "data" / "products.json"
SHOP_CATALOG_NAMES = frozenset({"products.json", "catalog.v1.json"})
_ZERO_TEXT = re.compile(r"[+-]?(?:0+(?:\.0*)?|\.0+)")

PriceShape = Literal["missing", "null", "blank", "zero", "priced"]


@dataclass(frozen=True)
class CatalogRow:
    """One catalog row. price_usd stays as it was passed in."""

    ma: str
    price_usd: object
    price_set: bool


@dataclass(frozen=True)
class ZeroSellPriceFlag:
    ma: str
    stored: object
    held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "field": "priceUsd",
            "kind": "zero_sell_price",
            "stored": self.stored,
            "held": self.held,
        }


def flag_zero_sell_prices(
    rows: list[CatalogRow],
    held: frozenset[str] = frozenset(),
) -> list[ZeroSellPriceFlag]:
    """Return zero-price flags. Row objects are not edited."""
    flags: list[ZeroSellPriceFlag] = []
    for row in rows:
        code = row.ma.strip().upper()
        shape = _shape(row.price_usd, row.price_set)
        if not _is_zero_flag(shape):
            continue
        flags.append(ZeroSellPriceFlag(code, row.price_usd, code in held))
    return flags


def report_json(
    rows: list[CatalogRow],
    flags: list[ZeroSellPriceFlag],
    held: frozenset[str],
) -> dict[str, object]:
    return {
        "readOnly": True,
        "s06": "stays $25",
        "heldMas": "stay held",
        "rows": [_row_json(row, held) for row in rows],
        "flagCount": len(flags),
        "flags": [flag.as_json() for flag in flags],
        "writes": [],
    }


def load_catalog(path: str | Path) -> list[CatalogRow]:
    fixture = _local_catalog(path)
    payload = json.loads(fixture.read_text(encoding="utf-8"))
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
        description="Flag a fixture sell price of 0. Read-only. The stored 0 is not replaced."
    )
    parser.add_argument("--catalog", required=True, help="Fixture catalog JSON. Read and left unchanged.")
    parser.add_argument(
        "--held",
        default="",
        help="Held-list JSON to read. Defaults to data/held.json. Not written.",
    )
    args = parser.parse_args(argv)
    try:
        rows = load_catalog(args.catalog)
        held_path = _held_path(args.held)
        policy = load_held_policy(held_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    held = frozenset(policy.held)
    flags = flag_zero_sell_prices(rows, held)
    print(json.dumps(report_json(rows, flags, held), ensure_ascii=False, indent=2))
    return 1 if flags else 0


def _shape(value: object, present: bool) -> PriceShape:
    if not present:
        return "missing"
    if value is None:
        return "null"
    if isinstance(value, str) and value.strip() == "":
        return "blank"
    if _is_zero_price(value):
        return "zero"
    return "priced"


def _is_zero_flag(shape: PriceShape) -> bool:
    if shape == "zero":
        return True
    if shape == "missing" or shape == "null" or shape == "blank" or shape == "priced":
        return False
    unexpected: Never = shape
    raise AssertionError(unexpected)


def _is_zero_price(value: object) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value == 0
    if isinstance(value, float):
        if value != value:
            return False
        return value == 0.0
    if isinstance(value, str):
        return _ZERO_TEXT.fullmatch(value.strip()) is not None
    return False


def _row_json(row: CatalogRow, held: frozenset[str]) -> dict[str, object]:
    code = row.ma.strip().upper()
    body: dict[str, object] = {"ma": code, "held": code in held}
    if row.price_set:
        body["priceUsd"] = row.price_usd
    return body


def _held_path(value: str) -> Path | None:
    if not value:
        return None
    if _is_remote(value):
        raise ValueError("Held-list fixtures only. Live lists are not read.")
    file = Path(value)
    if not file.is_file():
        raise ValueError(f"Held list not found: {file}")
    return file


def _local_catalog(path: str | Path) -> Path:
    text = str(path).strip()
    if _is_remote(text):
        raise ValueError("Catalog fixtures only. Live catalogs are not read.")
    file = Path(text)
    if not file.is_file():
        raise ValueError(f"Fixture not found: {file}")
    resolved = file.resolve()
    if resolved == default_held_path().resolve():
        raise ValueError("Catalog fixtures only. data/held.json is not read as a catalog.")
    if resolved == SHOP_CATALOG.resolve() or resolved.name.casefold() in SHOP_CATALOG_NAMES:
        raise ValueError("Catalog fixtures only. Shop catalog files are not read.")
    return resolved


def _is_remote(value: str) -> bool:
    text = value.strip()
    return "://" in text or text.startswith("//") or text.startswith("http:") or text.startswith("https:")


if __name__ == "__main__":
    raise SystemExit(main())
