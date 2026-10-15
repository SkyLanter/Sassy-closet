"""Flag a fixture hex which is not # plus 3 or 6 hex digits.

Read-only. The stored hex is copied into the flag and is not rewritten.
A blank hex stays blank: missing, null, empty, and whitespace-only stay
as they were, and nothing fills one in from a name, a note, or a color id.
A short #rgb is not expanded, and letter case is left as stored.
Nothing here writes a catalog row, a price, or data/held.json.
S06 stays $25.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Hash, then exactly three or exactly six hex digits. No spaces, no extra marks.
_HEX_SHAPE = re.compile(r"^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")
_BAD_HEX = "bad_hex"


@dataclass(frozen=True)
class FixtureColor:
    """One stored color. hex is the fixture text, not a corrected value."""

    hex: str | None
    hex_set: bool
    name: str | None
    color_id: str | None


@dataclass(frozen=True)
class CatalogRow:
    """One catalog row. Price and colors stay as they were passed in."""

    ma: str
    colors: tuple[FixtureColor, ...]
    price_usd: object
    price_set: bool
    status: str | None


@dataclass(frozen=True)
class HexShapeFlag:
    ma: str
    index: int
    kind: str
    stored: str
    color_id: str

    def as_json(self) -> dict[str, str | int]:
        return {
            "ma": self.ma,
            "index": self.index,
            "kind": self.kind,
            "stored": self.stored,
            "colorId": self.color_id,
        }


def flag_hex_shapes(rows: list[CatalogRow]) -> list[HexShapeFlag]:
    """Return flags. Leave every hex as it was passed in."""
    flags: list[HexShapeFlag] = []
    for row in rows:
        code = row.ma.strip().upper()
        for index, color in enumerate(row.colors):
            stored = color.hex
            if _is_blank_hex(stored) or _matches_shape(stored):
                continue
            flags.append(
                HexShapeFlag(
                    ma=code,
                    index=index,
                    kind=_BAD_HEX,
                    stored=stored,
                    color_id=color.color_id or "",
                )
            )
    return flags


def report_json(rows: list[CatalogRow], flags: list[HexShapeFlag]) -> dict[str, object]:
    return {
        "readOnly": True,
        "s06": "stays $25",
        "rows": [_row_json(row) for row in rows],
        "flagCount": len(flags),
        "flags": [flag.as_json() for flag in flags],
    }


def rows_from_payload(payload: object) -> list[CatalogRow]:
    """Copy catalog rows out of a fixture. Does not write the payload."""
    products = _product_list(payload)
    rows: list[CatalogRow] = []
    for index, item in enumerate(products):
        if not isinstance(item, dict):
            raise ValueError(f"catalog row {index} must be an object")
        ma = item.get("ma")
        if not isinstance(ma, str) or not ma.strip():
            raise ValueError(f"catalog row {index} needs a mã")
        price, price_set = _price(item, ma)
        rows.append(
            CatalogRow(
                ma=ma,
                colors=_colors(item, ma),
                price_usd=price,
                price_set=price_set,
                status=_status(item, ma),
            )
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag a fixture hex which is not # plus 3 or 6 hex digits. "
            "Reads JSON and prints flags."
        ),
    )
    parser.add_argument("--fixture", required=True, help="Local JSON fixture. Not a live catalog URL.")
    args = parser.parse_args(argv)
    path_text = str(args.fixture).strip()
    lowered = path_text.casefold()
    if lowered.startswith("http://") or lowered.startswith("https://"):
        print("refusing a live catalog URL", file=sys.stderr)
        return 2
    path = Path(path_text)
    if _is_held_path(path):
        print("refusing to open held.json", file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"fixture not found: {path}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = rows_from_payload(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    json.dump(
        report_json(rows, flag_hex_shapes(rows)),
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def _is_blank_hex(value: str | None) -> bool:
    """Missing, null, empty, and whitespace-only hexes are blank."""
    if value is None:
        return True
    return value.strip() == ""


def _matches_shape(value: str | None) -> bool:
    if value is None:
        return False
    return _HEX_SHAPE.fullmatch(value) is not None


def _product_list(payload: object) -> list[object]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        products = payload.get("products")
        if isinstance(products, list):
            return products
    raise ValueError("catalog fixture must be a product list or a catalog document")


def _colors(item: dict[str, object], ma: str) -> tuple[FixtureColor, ...]:
    if "colors" not in item or item.get("colors") is None:
        return ()
    raw = item.get("colors")
    if not isinstance(raw, list):
        raise ValueError(f"{ma} colors must be a list")
    return tuple(_one_color(color, ma, index) for index, color in enumerate(raw))


def _one_color(color: object, ma: str, index: int) -> FixtureColor:
    if isinstance(color, str):
        return FixtureColor(hex=None, hex_set=False, name=color, color_id=None)
    if not isinstance(color, dict):
        raise ValueError(f"{ma} color {index} must be a string or an object")
    stored, hex_set = _hex_text(color, ma, index)
    return FixtureColor(
        hex=stored,
        hex_set=hex_set,
        name=_name_text(color, ma, index),
        color_id=_color_id(color, ma, index),
    )


def _hex_text(color: dict[str, object], ma: str, index: int) -> tuple[str | None, bool]:
    if "hex" not in color:
        return None, False
    raw = color.get("hex")
    if raw is None:
        return None, True
    if not isinstance(raw, str):
        raise ValueError(f"{ma} color {index} hex must be a string")
    return raw, True


def _name_text(color: dict[str, object], ma: str, index: int) -> str | None:
    if "name" not in color or color.get("name") is None:
        return None
    raw = color.get("name")
    if not isinstance(raw, str):
        raise ValueError(f"{ma} color {index} name must be a string")
    return raw


def _color_id(color: dict[str, object], ma: str, index: int) -> str | None:
    if "id" not in color or color.get("id") is None:
        return None
    raw = color.get("id")
    if not isinstance(raw, str):
        raise ValueError(f"{ma} color {index} id must be a string")
    return raw


def _price(item: dict[str, object], ma: str) -> tuple[object, bool]:
    if "priceUsd" not in item:
        return None, False
    value = item["priceUsd"]
    if value is None or isinstance(value, str):
        return value, True
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{ma} price must be a number, a string, or blank")
    return value, True


def _status(item: dict[str, object], ma: str) -> str | None:
    if "status" not in item or item.get("status") is None:
        return None
    value = item.get("status")
    if not isinstance(value, str):
        raise ValueError(f"{ma} status must be a string")
    return value


def _row_json(row: CatalogRow) -> dict[str, object]:
    body: dict[str, object] = {"ma": row.ma.strip().upper()}
    if row.price_set and _price_is_copyable(row.price_usd):
        body["priceUsd"] = row.price_usd
    if row.status is not None:
        body["status"] = row.status
    body["colors"] = [
        {"index": index, "hex": color.hex} for index, color in enumerate(row.colors)
    ]
    return body


def _price_is_copyable(value: object) -> bool:
    if value is None or isinstance(value, str):
        return True
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float))


def _is_held_path(path: Path) -> bool:
    if path.name.casefold() == "held.json":
        return True
    try:
        return path.resolve().name.casefold() == "held.json"
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
