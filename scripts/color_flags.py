"""Flag catalog rows with a blank color.

Read-only. A blank palette, a blank color name, and a blank piece color are
flags. The stored text is copied into the flag and is not rewritten. Hex,
color id, and a piece's suggested label are not turned into a color name.
Nothing here writes a catalog row or data/held.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from held_policy import norm_ma


@dataclass(frozen=True)
class CatalogColor:
    name: str | None
    color_id: str | None = None


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
class ColorFlag:
    ma: str
    kind: str
    stored: str
    index: int | None = None
    piece: str | None = None

    def as_json(self) -> dict[str, str | int | None]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "stored": self.stored,
            "index": self.index,
            "piece": self.piece,
        }


def flag_blank_colors(rows: list[CatalogRow]) -> list[ColorFlag]:
    """Return flags. Leave every CatalogRow as it was passed in."""
    flags: list[ColorFlag] = []
    for row in rows:
        code = norm_ma(row.ma)
        colors = row.colors
        if not colors:
            flags.append(ColorFlag(code, "blank_color", ""))
        else:
            for index, color in enumerate(colors):
                stored = "" if color.name is None else color.name
                if stored.strip() == "":
                    flags.append(ColorFlag(code, "blank_color", stored, index))
        for index, piece in enumerate(row.pieces):
            stored = "" if piece.color is None else piece.color
            if stored.strip() == "":
                flags.append(ColorFlag(code, "blank_color", stored, index, piece.piece_id))
    return flags


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
        colors: list[CatalogColor] = []
        for index, color in enumerate(raw):
            colors.append(_one_color(color, ma, index))
        return tuple(colors)
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
    color_id = raw_id if isinstance(raw_id, str) else None
    return CatalogColor(name, color_id)


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
        description="Flag catalog rows with a blank color. Reads a JSON fixture and prints flags.",
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
        [flag.as_json() for flag in flag_blank_colors(rows)],
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
