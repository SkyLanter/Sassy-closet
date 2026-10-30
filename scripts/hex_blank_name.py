"""Flag a fixture color that has a hex and a blank name.

Read-only. The stored name is copied into the flag. A hex is not turned
into a name, and a color id or note is not written in as the name.
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
from typing import Literal
from held_policy import norm_ma

_HEX = re.compile(r"^#?(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")
Reason = Literal["missing", "null", "blank"]


@dataclass(frozen=True)
class FixtureColor:
    hex: str | None
    name: str | None
    name_set: bool
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
class HexNameFlag:
    ma: str
    index: int
    kind: str
    reason: Reason
    stored: str
    hex: str
    color_id: str

    def as_json(self) -> dict[str, str | int]:
        return {
            "ma": self.ma,
            "index": self.index,
            "kind": self.kind,
            "reason": self.reason,
            "stored": self.stored,
            "hex": self.hex,
            "colorId": self.color_id,
        }


def flag_hex_blank_names(rows: list[CatalogRow]) -> list[HexNameFlag]:
    """Return flags. Leave every CatalogRow as it was passed in."""
    flags: list[HexNameFlag] = []
    for row in rows:
        code = norm_ma(row.ma)
        for index, color in enumerate(row.colors):
            if color.hex is None or not _is_hex(color.hex):
                continue
            reason = _blank_reason(color)
            if reason is None:
                continue
            flags.append(
                HexNameFlag(
                    ma=code,
                    index=index,
                    kind="blank_name",
                    reason=reason,
                    stored=_stored_name(color, reason),
                    hex=color.hex,
                    color_id=color.color_id or "",
                )
            )
    return flags


def report_json(rows: list[CatalogRow], flags: list[HexNameFlag]) -> dict[str, object]:
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
        description="Flag a fixture color that has a hex and a blank name. Reads JSON and prints flags.",
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
        report_json(rows, flag_hex_blank_names(rows)),
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def _is_hex(value: str) -> bool:
    return _HEX.fullmatch(value.strip()) is not None


def _blank_reason(color: FixtureColor) -> Reason | None:
    if not color.name_set:
        return "missing"
    if color.name is None:
        return "null"
    if color.name.strip() == "":
        return "blank"
    return None


def _stored_name(color: FixtureColor, reason: Reason) -> str:
    if reason == "blank":
        if color.name is None:
            return ""
        return color.name
    if reason == "missing" or reason == "null":
        return ""
    raise AssertionError(reason)


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
        return FixtureColor(hex=None, name=color, name_set=True, color_id=None)
    if not isinstance(color, dict):
        raise ValueError(f"{ma} color {index} must be a string or an object")
    return FixtureColor(
        hex=_hex_text(color, ma, index),
        name=_name_text(color, ma, index),
        name_set="name" in color,
        color_id=_color_id(color, ma, index),
    )


def _hex_text(color: dict[str, object], ma: str, index: int) -> str | None:
    if "hex" not in color or color.get("hex") is None:
        return None
    raw = color.get("hex")
    if not isinstance(raw, str):
        raise ValueError(f"{ma} color {index} hex must be a string")
    return raw


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
    body: dict[str, object] = {"ma": norm_ma(row.ma)}
    if row.price_set and _price_is_copyable(row.price_usd):
        body["priceUsd"] = row.price_usd
    if row.status is not None:
        body["status"] = row.status
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
