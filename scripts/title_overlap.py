"""Flag catalog rows whose titles match or nearly match another mã.

Read-only. The report names both mãs and does not merge rows, rewrite a
title, or change a price. Same-mã pairs are ignored. Nothing here reads
or writes data/held.json. A near title is a normalized match of at least
0.92; equality after that fold is exact.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal
from held_policy import norm_ma

NEAR_RATIO = 0.92
_PUNCT = re.compile(r"[^a-z0-9\s]+")
_SPACE = re.compile(r"\s+")

TitleField = Literal["titleEn", "titleVn"]
TitleKind = Literal["exact", "near"]


@dataclass(frozen=True)
class CatalogRow:
    """One catalog row. The check reads titles and leaves price_usd untouched."""

    ma: str
    title_en: str
    title_vn: str
    price_usd: int | None = None


@dataclass(frozen=True)
class TitleFlag:
    mas: tuple[str, str]
    field: TitleField
    kind: TitleKind
    titles: tuple[str, str]

    def as_json(self) -> dict[str, object]:
        return {
            "mas": [self.mas[0], self.mas[1]],
            "field": self.field,
            "kind": self.kind,
            "titles": [self.titles[0], self.titles[1]],
        }


def normalize_title(title: str) -> str:
    """Fold case, đ, accents, hyphens, and extra spaces. The stored title stays put."""
    text = title.replace("Đ", "D").replace("đ", "d")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("-", " ").replace("/", " ")
    text = _PUNCT.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def flag_title_overlap(rows: list[CatalogRow]) -> list[TitleFlag]:
    """Return title pairs across different mãs. Row objects are not edited."""
    flags: list[TitleFlag] = []
    seen: set[tuple[str, str, TitleField, TitleKind]] = set()
    prepared = [(norm_ma(row.ma), row) for row in rows]
    fields: tuple[TitleField, ...] = ("titleEn", "titleVn")
    for field in fields:
        folded: list[tuple[str, str, str]] = []
        for code, row in prepared:
            raw = _field_text(row, field)
            norm = normalize_title(raw)
            if norm:
                folded.append((code, raw, norm))
        for left in range(len(folded)):
            for right in range(left + 1, len(folded)):
                left_code, left_raw, left_norm = folded[left]
                right_code, right_raw, right_norm = folded[right]
                if left_code == right_code:
                    continue
                kind = _kind(left_norm, right_norm)
                if kind is None:
                    continue
                if left_code < right_code:
                    pair = (left_code, right_code)
                    titles = (left_raw, right_raw)
                else:
                    pair = (right_code, left_code)
                    titles = (right_raw, left_raw)
                key = (pair[0], pair[1], field, kind)
                if key in seen:
                    continue
                seen.add(key)
                flags.append(TitleFlag(pair, field, kind, titles))
    flags.sort(key=lambda flag: (flag.field, flag.mas[0], flag.mas[1], flag.kind))
    return flags


def report_json(rows: list[CatalogRow], flags: list[TitleFlag]) -> dict[str, object]:
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
        rows.append(
            CatalogRow(
                ma,
                _text(item.get("titleEn")),
                _text(item.get("titleVn")),
                _price(item.get("priceUsd")),
            )
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report catalog titles that match or nearly match another mã. Read-only.",
    )
    parser.add_argument("--catalog", required=True, help="Catalog JSON. Read and left unchanged.")
    args = parser.parse_args(argv)
    path = Path(args.catalog)
    try:
        rows = load_catalog(path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    flags = flag_title_overlap(rows)
    print(json.dumps(report_json(rows, flags), ensure_ascii=False, indent=2))
    return 0


def _field_text(row: CatalogRow, field: TitleField) -> str:
    if field == "titleEn":
        return row.title_en
    if field == "titleVn":
        return row.title_vn
    raise AssertionError(field)


def _kind(left: str, right: str) -> TitleKind | None:
    if left == right:
        return "exact"
    if SequenceMatcher(None, left, right).ratio() >= NEAR_RATIO:
        return "near"
    return None


def _text(value: object) -> str:
    if isinstance(value, str):
        return value
    return ""


def _price(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


if __name__ == "__main__":
    raise SystemExit(main())
