"""Flag catalog titles that are only the mã.

Read-only. A fixture catalog is read and left unchanged. The stored title
is copied into the flag and is not replaced. After trim, a title that
equals that row's mã ignoring case is flagged. A real title that contains the
mã stays quiet. Blank titles stay quiet. Nothing here writes
data/held.json, a price, or a catalog row. S06 stays $25. Held mãs stay held.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from held_policy import load_held_policy

TitleField = Literal["titleEn", "titleVn"]


@dataclass(frozen=True)
class CatalogRow:
    """One catalog row. Titles and price_usd stay as they were passed in."""

    ma: str
    title_en: object
    title_vn: object
    title_en_set: bool
    title_vn_set: bool
    price_usd: object
    price_set: bool


@dataclass(frozen=True)
class MaOnlyFlag:
    ma: str
    field: TitleField
    stored: str
    held: bool

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "field": self.field,
            "kind": "ma_only",
            "stored": self.stored,
            "held": self.held,
        }


def flag_ma_only_titles(rows: list[CatalogRow], held: frozenset[str] = frozenset()) -> list[MaOnlyFlag]:
    """Return mã-only title flags. Row objects are not edited."""
    flags: list[MaOnlyFlag] = []
    for row in rows:
        code = row.ma.strip().upper()
        is_held = code in held
        fields: tuple[TitleField, ...] = ("titleEn", "titleVn")
        for field in fields:
            value, present = _field_value(row, field)
            stored = _only_ma_text(value, present, code)
            if stored is None:
                continue
            flags.append(MaOnlyFlag(code, field, stored, is_held))
    return flags


def report_json(rows: list[CatalogRow], flags: list[MaOnlyFlag], held: frozenset[str]) -> dict[str, object]:
    return {
        "readOnly": True,
        "s06": "stays $25",
        "heldMas": "stay held",
        "rows": [_row_json(row, held) for row in rows],
        "flagCount": len(flags),
        "flags": [flag.as_json() for flag in flags],
    }


def load_catalog(path: Path) -> list[CatalogRow]:
    payload = json.loads(path.read_text(encoding="utf-8"))
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
        rows.append(
            CatalogRow(
                ma,
                item.get("titleEn"),
                item.get("titleVn"),
                "titleEn" in item,
                "titleVn" in item,
                item.get("priceUsd"),
                "priceUsd" in item,
            )
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag catalog titles that are only the mã. Read-only. Fixtures only.",
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
    flags = flag_ma_only_titles(rows, held)
    print(json.dumps(report_json(rows, flags, held), ensure_ascii=False, indent=2))
    return 1 if flags else 0


def _field_value(row: CatalogRow, field: TitleField) -> tuple[object, bool]:
    if field == "titleEn":
        return row.title_en, row.title_en_set
    if field == "titleVn":
        return row.title_vn, row.title_vn_set
    raise AssertionError(field)


def _only_ma_text(value: object, present: bool, code: str) -> str | None:
    if not present or not isinstance(value, str) or code == "":
        return None
    if value.strip().upper() != code:
        return None
    return value


def _row_json(row: CatalogRow, held: frozenset[str]) -> dict[str, object]:
    body: dict[str, object] = {
        "ma": row.ma.strip().upper(),
        "held": row.ma.strip().upper() in held,
    }
    if row.price_set and _price_is_copyable(row.price_usd):
        body["priceUsd"] = row.price_usd
    return body


def _price_is_copyable(value: object) -> bool:
    if value is None or isinstance(value, str):
        return True
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float))


def _is_live_target(value: str) -> bool:
    text = value.strip().casefold()
    return text.startswith("http://") or text.startswith("https://")


if __name__ == "__main__":
    raise SystemExit(main())
