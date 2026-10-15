"""Count how many fixture catalog mãs use each color name.

Read-only. Each stored name counts once per mã. A blank palette, a blank
name, and a blank piece color count as blank. They are not filled from a
hex, a color id, a note, a sibling color field, or a suggested label.
Nothing here writes a catalog row, a price, or data/held.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CatalogColor:
    name: str | None
    color_id: str | None = None
    hex: str | None = None


@dataclass(frozen=True)
class CatalogPiece:
    piece_id: str
    color: str | None


@dataclass(frozen=True)
class CatalogRow:
    ma: str
    colors: tuple[CatalogColor, ...] | None
    pieces: tuple[CatalogPiece, ...] = ()
    price_usd: int | float | str | None = None
    status: str | None = None


@dataclass(frozen=True)
class ColorCount:
    name: str
    count: int
    codes: tuple[str, ...]

    @property
    def blank(self) -> bool:
        return self.name == ""

    def as_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "blank": self.blank,
            "count": self.count,
            "codes": list(self.codes),
        }


def count_color_names(rows: list[CatalogRow]) -> list[ColorCount]:
    """Return one tally per stored color name. Leave every row as it was passed in."""
    used: dict[str, set[str]] = {}
    for row in rows:
        code = row.ma.strip().upper()
        if not code:
            raise ValueError("catalog row needs a mã")
        used.setdefault(code, set()).update(_names_used(row))
    tally: dict[str, list[str]] = {}
    for code, names in used.items():
        for name in names:
            tally.setdefault(name, []).append(code)
    counts: list[ColorCount] = []
    for name in sorted(tally):
        codes = tuple(sorted(tally[name]))
        counts.append(ColorCount(name, len(codes), codes))
    return counts


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
        rows.append(
            CatalogRow(
                ma=ma,
                colors=_colors_from_row(item, ma),
                pieces=_pieces_from_row(item, ma),
                price_usd=_price(item, ma),
                status=_status(item, ma),
            )
        )
    return rows


def _names_used(row: CatalogRow) -> set[str]:
    names: set[str] = set()
    if not row.colors:
        names.add("")
    else:
        for color in row.colors:
            names.add(_color_name(color.name))
    for piece in row.pieces:
        names.add(_color_name(piece.color))
    return names


def _color_name(value: str | None) -> str:
    if value is None or value.strip() == "":
        return ""
    return value


def _product_list(payload: object) -> list[object]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        products = payload.get("products")
        if isinstance(products, list):
            return products
    raise ValueError("catalog fixture must be a product list or a catalog document")


def _colors_from_row(item: dict[str, object], ma: str) -> tuple[CatalogColor, ...] | None:
    if "colors" in item:
        raw = item["colors"]
        if raw is None:
            return None
        if not isinstance(raw, list):
            raise ValueError(f"{ma} colors must be a list")
        return tuple(_one_color(color, ma, index) for index, color in enumerate(raw))
    if "color" in item:
        raw = item["color"]
        if raw is None:
            return None
        if not isinstance(raw, str):
            raise ValueError(f"{ma} color must be a string")
        return (CatalogColor(raw),)
    return None


def _one_color(color: object, ma: str, index: int) -> CatalogColor:
    if isinstance(color, str):
        return CatalogColor(color)
    if not isinstance(color, dict):
        raise ValueError(f"{ma} color {index} must be a string or an object")
    if "name" not in color or color.get("name") is None:
        name: str | None = None
    else:
        raw_name = color.get("name")
        if not isinstance(raw_name, str):
            raise ValueError(f"{ma} color {index} name must be a string")
        name = raw_name
    raw_id = color.get("id")
    raw_hex = color.get("hex")
    return CatalogColor(
        name,
        raw_id if isinstance(raw_id, str) else None,
        raw_hex if isinstance(raw_hex, str) else None,
    )


def _pieces_from_row(item: dict[str, object], ma: str) -> tuple[CatalogPiece, ...]:
    if "pieces" not in item or item.get("pieces") is None:
        return ()
    raw = item.get("pieces")
    if not isinstance(raw, list):
        raise ValueError(f"{ma} pieces must be a list")
    pieces: list[CatalogPiece] = []
    for index, piece in enumerate(raw):
        if not isinstance(piece, dict):
            raise ValueError(f"{ma} piece {index} must be an object")
        raw_id = piece.get("id")
        piece_id = raw_id if isinstance(raw_id, str) else ""
        if "color" not in piece or piece.get("color") is None:
            color: str | None = None
        else:
            raw_color = piece.get("color")
            if not isinstance(raw_color, str):
                raise ValueError(f"{ma} piece {index} color must be a string")
            color = raw_color
        pieces.append(CatalogPiece(piece_id, color))
    return tuple(pieces)


def _price(item: dict[str, object], ma: str) -> int | float | str | None:
    if "priceUsd" in item:
        key = "priceUsd"
    elif "price_usd" in item:
        key = "price_usd"
    else:
        return None
    value = item[key]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{ma} price must be a number, a string, or blank")
    return value


def _status(item: dict[str, object], ma: str) -> str | None:
    if "status" not in item or item.get("status") is None:
        return None
    value = item.get("status")
    if not isinstance(value, str):
        raise ValueError(f"{ma} status must be a string")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Count fixture catalog mãs per color name. Reads a JSON fixture and prints counts.",
    )
    parser.add_argument("--fixture", required=True, help="Local JSON fixture. Not a live catalog URL.")
    args = parser.parse_args(argv)
    path_text = str(args.fixture).strip()
    if path_text.startswith("http://") or path_text.startswith("https://"):
        print("refusing a live catalog URL", file=sys.stderr)
        return 2
    path = Path(path_text)
    if path.name == "held.json":
        print("refusing to open held.json", file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"fixture not found: {path}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = rows_from_payload(payload)
    except (json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    json.dump(
        [item.as_json() for item in count_color_names(rows)],
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
