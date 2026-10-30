"""Report fixture mãs that are not one letter plus two digits.

A valid mã is one uppercase letter and two digits, such as Q02 or S06.
A1, AA01, and a01 are flagged. The report copies each stored mã and the
stored S06 dollar. Shop files stay on disk as they were.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

SHAPE_LABEL = "one letter plus two digits"
SHAPE_RE = re.compile(r"^[A-Z][0-9]{2}$")
FlagKind = Literal["wrong_shape"]
_FORBIDDEN_NAMES = frozenset(
    {
        "held.json",
        "products.json",
        "catalog.v1.json",
        "submissions.json",
        "taobao_confirm_seed.json",
    }
)


@dataclass(frozen=True)
class FixtureMa:
    """One fixture mã. price_usd is copied through and stays as passed in."""

    ma: str
    price_usd: int | None = None


@dataclass(frozen=True)
class ShapeFlag:
    ma: str
    kind: FlagKind = "wrong_shape"

    def as_json(self) -> dict[str, str]:
        return {"ma": self.ma, "kind": self.kind}


def stored_code(ma: str) -> str:
    """Strip surrounding space. Leave letter case and digits as stored."""
    return ma.strip()


def is_valid_shape(ma: str) -> bool:
    return SHAPE_RE.fullmatch(stored_code(ma)) is not None


def flag_wrong_shapes(rows: list[FixtureMa]) -> list[ShapeFlag]:
    """Return fixture mãs that are not one uppercase letter plus two digits.

    Row objects stay as they were passed in.
    """
    flags: list[ShapeFlag] = []
    for row in rows:
        code = stored_code(row.ma)
        if is_valid_shape(code):
            continue
        flags.append(ShapeFlag(code))
    flags.sort(key=lambda flag: flag.ma)
    return flags


def report_json(rows: list[FixtureMa], flags: list[ShapeFlag]) -> dict[str, object]:
    return {
        "readOnly": True,
        "shape": SHAPE_LABEL,
        "rows": len(rows),
        "checked": [stored_code(row.ma) for row in rows],
        "q02": _q02_state(rows, flags),
        "s06PriceUsd": _s06_price(rows),
        "flags": [flag.as_json() for flag in flags],
        "writes": [],
    }


def load_fixture(payload: object) -> list[FixtureMa]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("products"), list):
        rows = payload["products"]
    else:
        raise ValueError("fixture must be a list of mãs or an object with products")
    return [_row(item) for item in rows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag a fixture mã that is not one letter plus two digits. Read-only.",
    )
    parser.add_argument("--fixture", required=True, help="JSON fixture. Read and left unchanged.")
    args = parser.parse_args(argv)
    refused = _refuse_reason(args.fixture)
    if refused:
        print(refused, file=sys.stderr)
        return 2
    path = Path(args.fixture)
    if not path.is_file():
        print(f"Fixture not found: {path}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = load_fixture(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    flags = flag_wrong_shapes(rows)
    print(json.dumps(report_json(rows, flags), ensure_ascii=False, indent=2))
    return 0


def _row(item: object) -> FixtureMa:
    if isinstance(item, str):
        if not item.strip():
            raise ValueError("fixture mã is blank")
        return FixtureMa(item)
    if not isinstance(item, dict):
        raise ValueError("fixture mã must be a string or an object")
    ma = item.get("ma")
    if not isinstance(ma, str) or not ma.strip():
        raise ValueError("fixture row needs a mã")
    price = _price(item.get("priceUsd"), ma) if "priceUsd" in item else None
    return FixtureMa(ma, price)


def _price(value: object, ma: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"mã {stored_code(ma)} priceUsd must be a whole dollar amount")
    return value


def _q02_state(rows: list[FixtureMa], flags: list[ShapeFlag]) -> str:
    present = any(stored_code(row.ma) == "Q02" for row in rows)
    if not present:
        return "absent"
    if any(flag.ma == "Q02" for flag in flags):
        return "flagged"
    return "valid"


def _s06_price(rows: list[FixtureMa]) -> int | None:
    for row in rows:
        if stored_code(row.ma) == "S06":
            return row.price_usd
    return None


def _refuse_reason(fixture: str) -> str | None:
    text = fixture.strip().casefold()
    if "://" in text or text.startswith("//") or text.startswith("blob:"):
        return "Shape checks read a fixture file. Live catalogs are not read."
    path = Path(fixture)
    if _is_protected(path):
        return "Shape checks read a fixture file. Shop catalog files are not read."
    return None


def _is_protected(path: Path) -> bool:
    if path.name.casefold() in _FORBIDDEN_NAMES:
        return True
    resolved = path.expanduser().resolve()
    if resolved.name.casefold() in _FORBIDDEN_NAMES:
        return True
    repo = Path(__file__).resolve().parents[1]
    protected = (
        repo / "data",
        repo / "sassy-closet" / "data",
        repo / "sassy-closet-shop" / "data",
        repo / "sassy-closet-shop" / "public" / "data",
    )
    for folder in protected:
        root = folder.resolve()
        if resolved == root or root in resolved.parents:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
