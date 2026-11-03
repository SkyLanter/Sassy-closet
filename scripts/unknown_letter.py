"""Report fixture mãs whose letter sits outside the shop's known letters.

Known letters are A, B, D, G, H, J, K, O, P, Q, S, V.
The report copies the stored mã and the stored S06 dollar.
Shop files stay on disk as they were.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

KNOWN_LETTERS = ("A", "B", "D", "G", "H", "J", "K", "O", "P", "Q", "S", "V")
_KNOWN = frozenset(KNOWN_LETTERS)
MA_RE = re.compile(r"^([A-Z])(\d+)$")
FlagKind = Literal["unknown_letter"]
_FORBIDDEN_NAMES = frozenset(
    {"held.json", "products.json", "catalog.v1.json", "submissions.json"}
)


@dataclass(frozen=True)
class FixtureMa:
    """One fixture mã. price_usd is copied through and never rewritten."""

    ma: str
    price_usd: int | None = None


@dataclass(frozen=True)
class UnknownLetterFlag:
    ma: str
    letter: str
    kind: FlagKind = "unknown_letter"

    def as_json(self) -> dict[str, str]:
        return {"ma": self.ma, "letter": self.letter, "kind": self.kind}


def ma_letter(ma: str) -> str | None:
    """Return the leading letter when the mã is one letter plus digits."""
    match = MA_RE.fullmatch(ma.strip().upper())
    if match is None:
        return None
    return match.group(1)


def flag_unknown_letters(rows: list[FixtureMa]) -> list[UnknownLetterFlag]:
    """Return fixture mãs whose letter is outside the known set.

    Row objects stay as they were passed in.
    """
    flags: list[UnknownLetterFlag] = []
    for row in rows:
        code = row.ma.strip().upper()
        letter = ma_letter(code)
        if letter is None or letter in _KNOWN:
            continue
        flags.append(UnknownLetterFlag(code, letter))
    flags.sort(key=_flag_sort)
    return flags


def report_json(rows: list[FixtureMa], flags: list[UnknownLetterFlag]) -> dict[str, object]:
    return {
        "readOnly": True,
        "knownLetters": list(KNOWN_LETTERS),
        "rows": len(rows),
        "checked": [row.ma.strip().upper() for row in rows],
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
    loaded: list[FixtureMa] = []
    for item in rows:
        loaded.append(_row(item))
    return loaded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag a fixture mã whose letter is outside the shop's known letters. Read-only.",
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
    flags = flag_unknown_letters(rows)
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
        raise ValueError(f"mã {ma.strip().upper()} priceUsd must be a whole dollar amount")
    return value


def _q02_state(rows: list[FixtureMa], flags: list[UnknownLetterFlag]) -> str:
    present = any(row.ma.strip().upper() == "Q02" for row in rows)
    if not present:
        return "absent"
    if any(flag.ma == "Q02" for flag in flags):
        return "flagged"
    return "known"


def _s06_price(rows: list[FixtureMa]) -> int | None:
    for row in rows:
        if row.ma.strip().upper() == "S06":
            return row.price_usd
    return None


def _flag_sort(flag: UnknownLetterFlag) -> tuple[str, int, str]:
    match = MA_RE.fullmatch(flag.ma)
    number = int(match.group(2)) if match else 0
    return (flag.letter, number, flag.ma)


def _refuse_reason(fixture: str) -> str | None:
    text = fixture.strip().casefold()
    if "://" in text or text.startswith("//") or text.startswith("blob:"):
        return "Unknown-letter checks read a fixture file. Live catalogs are not read."
    path = Path(fixture)
    if _is_protected(path):
        return "Unknown-letter checks read a fixture file. Shop catalog files are not read."
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
    )
    for folder in protected:
        root = folder.resolve()
        if resolved == root or root in resolved.parents:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
