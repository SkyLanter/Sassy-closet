"""Flag a catalog row whose mã letter does not match its type.

Read-only. A dress stored under A, or a top stored under D, is a flag.
The report copies the stored mã and type. It does not rename a mã or
change a price. Nothing here reads or writes data/held.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from held_policy import norm_ma

LETTERS = "AQVDKGBPHJSO"
MA_RE = re.compile(rf"^([{LETTERS}])(\d+)$")
_PUNCT = re.compile(r"[^a-z0-9\s]+")
_SPACE = re.compile(r"\s+")

# Shop type words and intake labels. Longer phrases win by exact match
# before a token split, so "áo khoác" stays a jacket and "áo" stays a top.
TYPE_WORDS: dict[str, str] = {
    "top": "A",
    "tops": "A",
    "ao": "A",
    "pants": "Q",
    "quan": "Q",
    "skirt": "V",
    "skirts": "V",
    "vay": "V",
    "dress": "D",
    "dresses": "D",
    "dam": "D",
    "dam dress": "D",
    "jacket": "K",
    "jackets": "K",
    "ao khoac": "K",
    "khoac": "K",
    "shoes": "G",
    "shoe": "G",
    "giay": "G",
    "cao got": "G",
    "giay cao got": "G",
    "bag": "B",
    "bags": "B",
    "tui": "B",
    "accessory": "P",
    "accessories": "P",
    "phu kien": "P",
    "thermos": "P",
    "hair": "H",
    "toc": "H",
    "phu kien toc": "H",
    "hair accessories": "H",
    "phu kien toc hair accessories": "H",
    "jewelry": "J",
    "trang suc": "J",
    "trang suc jewelry": "J",
    "set": "S",
    "sets": "S",
    "set do": "S",
    "other": "O",
    "khac": "O",
    "khac other": "O",
}

FlagKind = Literal["mismatch", "unrecognized"]


@dataclass(frozen=True)
class CatalogRow:
    """One catalog row. The check reads mã and type and leaves price_usd untouched."""

    ma: str
    stored_type: str
    price_usd: int | None = None


@dataclass(frozen=True)
class LetterTypeFlag:
    ma: str
    letter: str
    stored_type: str
    type_letter: str | None
    kind: FlagKind

    def as_json(self) -> dict[str, str | None]:
        return {
            "ma": self.ma,
            "letter": self.letter,
            "type": self.stored_type,
            "typeLetter": self.type_letter,
            "kind": self.kind,
        }


def normalize_type(value: str) -> str:
    """Fold case, đ, accents, slashes, and extra spaces. The stored type stays put."""
    text = value.replace("Đ", "D").replace("đ", "d")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("-", " ").replace("/", " ")
    text = _PUNCT.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def type_to_letter(stored: str) -> str | None:
    """Map a type word or letter onto a mã letter. Unknown text maps to None."""
    folded = normalize_type(stored)
    if not folded:
        return None
    exact = TYPE_WORDS.get(folded)
    if exact is not None:
        return exact
    if len(folded) == 1 and folded.upper() in LETTERS:
        return folded.upper()
    letters: list[str] = []
    for part in folded.split(" "):
        letter = TYPE_WORDS.get(part)
        if letter is None and len(part) == 1 and part.upper() in LETTERS:
            letter = part.upper()
        if letter is None:
            return None
        letters.append(letter)
    if letters and len(set(letters)) == 1:
        return letters[0]
    return None


def catalog_letter(ma: str) -> str | None:
    match = MA_RE.fullmatch(ma.strip().upper())
    if match is None:
        return None
    return match.group(1)


def flag_letter_type(rows: list[CatalogRow]) -> list[LetterTypeFlag]:
    """Return rows whose type letter disagrees with the mã letter.

    Blank types are left alone: the catalog treats a missing type as the
    mã letter. Row objects are not edited.
    """
    flags: list[LetterTypeFlag] = []
    for row in rows:
        code = norm_ma(row.ma)
        letter = catalog_letter(code)
        if letter is None:
            continue
        stored = row.stored_type
        if stored.strip() == "":
            continue
        type_letter = type_to_letter(stored)
        if type_letter == letter:
            continue
        kind: FlagKind = "mismatch" if type_letter is not None else "unrecognized"
        flags.append(LetterTypeFlag(code, letter, stored, type_letter, kind))
    flags.sort(key=lambda flag: (flag.ma, flag.stored_type, flag.kind))
    return flags


def report_json(rows: list[CatalogRow], flags: list[LetterTypeFlag]) -> dict[str, object]:
    return {
        "readOnly": True,
        "rows": len(rows),
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
        if "type" in item and item["type"] is not None and not isinstance(item["type"], str):
            raise ValueError(f"mã {norm_ma(ma)} type must be a string")
        stored = item.get("type")
        rows.append(CatalogRow(ma, stored if isinstance(stored, str) else "", _price(item.get("priceUsd"))))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report catalog rows whose mã letter does not match the type. Read-only.",
    )
    parser.add_argument("--catalog", required=True, help="Catalog JSON. Read and left unchanged.")
    args = parser.parse_args(argv)
    path = Path(args.catalog)
    try:
        rows = load_catalog(path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    flags = flag_letter_type(rows)
    print(json.dumps(report_json(rows, flags), ensure_ascii=False, indent=2))
    return 0


def _price(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


if __name__ == "__main__":
    raise SystemExit(main())
