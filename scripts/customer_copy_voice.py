"""Flag customer-visible catalog copy the shop treats as ops or stock voice.

Read-only. The sell shop refuses this wording on a shopper payload
(public-safety.ts) and blanks a description that still contains it
(catalog-store.ts). A dropship save also rejects an invented ship price
or a 2-4 week promise (warehouse-voice.ts). This check names the mã,
the field, and the matched phrase. It does not print the rest of the
sentence.

Titles, descriptions, and color names and notes are scanned. The same
four title and description fields are also read as one line, with no
trim, the way the shop decides to blank a description. An invented ship
price or a 2-4 week promise is read only on the two descriptions, with
a line break between them and no trim, the way a save rejects that
lead. A title or a color does not carry that promise. A source link is
not read. The stored phrase
is copied into the flag and is not rewritten. Nothing here writes a
catalog row, a price, a photo, intake, Blob, or data/held.json. S06
stays $25. Held mãs stay held. Pass a local fixture. A URL, held.json,
and the shop catalog are refused.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from held_policy import norm_ma

# JavaScript \b is an ASCII word boundary. JavaScript \d is [0-9].
# JavaScript \s does not include U+0085. Python's versions are wider, so
# the patterns below name the JavaScript set. Ignore-case folds ASCII and
# the phrase's own letters. It does not treat ı as i.
_BEFORE = r"(?<![A-Za-z0-9_])"
_AFTER = r"(?![A-Za-z0-9_])"
_SPACE = r"[ \t\n\v\f\r\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]"
_DIGIT = r"[0-9]"
_DASH = r"[-\u2013]"


def _folded(text: str, ignore_case: bool) -> str:
    """Escape a literal. When ignore_case, fold each letter without ı/i."""
    parts: list[str] = []
    for char in text:
        forms = {char}
        if ignore_case:
            for folded in (char.lower(), char.upper()):
                if len(folded) != 1:
                    continue
                if char.isascii() and not folded.isascii():
                    continue
                forms.add(folded)
            if char.isascii():
                forms = {item for item in forms if item.isascii()}
        if len(forms) == 1:
            parts.append(re.escape(char))
            continue
        parts.append("[" + "".join(re.escape(item) for item in sorted(forms)) + "]")
    return "".join(parts)


def _bound(text: str, ignore_case: bool) -> re.Pattern[str]:
    return re.compile(_BEFORE + _folded(text, ignore_case) + _AFTER)


def _phrase(text: str, ignore_case: bool) -> re.Pattern[str]:
    return re.compile(_folded(text, ignore_case))


# Same phrases and flags as sassy-closet-shop/lib/public-safety.ts and the
# invented-lead pattern in lib/warehouse-voice.ts. Order matches the shop.
_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    ("forbidden_phrase", "Square", _phrase("Square", False)),
    ("forbidden_phrase", "ADMIN_PASSWORD", _phrase("ADMIN_PASSWORD", False)),
    ("forbidden_phrase", "Facebook Send", _phrase("Facebook Send", False)),
    ("forbidden_phrase", "FB Send", _phrase("FB Send", False)),
    ("forbidden_phrase", "Thang Tien Huynh", _phrase("Thang Tien Huynh", False)),
    ("forbidden_phrase", "Shop now", _phrase("Shop now", False)),
    ("forbidden_phrase", "Add to cart", _phrase("Add to cart", False)),
    ("stock_voice", "Hold", _bound("Hold", False)),
    ("stock_voice", "Available", _bound("Available", False)),
    ("stock_voice", "Status:", re.compile("Status:" + _SPACE)),
    ("stock_voice", "on hand", _bound("on hand", True)),
    ("stock_voice", "on-hand", _phrase("on-hand", True)),
    ("stock_voice", "đang có", _phrase("đang có", True)),
    ("stock_voice", "in-stock", _phrase("in-stock", True)),
    ("stock_voice", "In stock", _bound("In stock", True)),
    ("stock_voice", "Tạm giữ", _phrase("Tạm giữ", False)),
    ("ops_voice", "Taobao", _phrase("Taobao", True)),
    ("ops_voice", "Zelle", _bound("Zelle", False)),
    ("ops_voice", "dropship", _phrase("dropship", True)),
    ("ops_voice", "CNY", _bound("CNY", False)),
    ("ops_voice", "source_link", _phrase("source_link", True)),
    ("ops_voice", "we order", _phrase("we order", True)),
    ("ops_voice", "photo-check", _phrase("photo-check", True)),
    ("ops_voice", "no cart", _phrase("no cart", True)),
    ("ops_voice", "flat rate", _phrase("flat rate", True)),
    ("ops_voice", "Message-first", _phrase("Message-first", False)),
    ("ops_voice", "Asia size", _phrase("Asia size", True)),
    ("ops_voice", "size Á châu", _phrase("size Á châu", True)),
    ("ops_voice", "Nhắn tin hỏi giá", _phrase("Nhắn tin hỏi giá", False)),
    ("ops_voice", "sourced after", _phrase("sourced after", True)),
    ("ops_voice", "inbox màu", _phrase("inbox màu", True)),
    ("filler_voice", "unique pieces", _phrase("unique pieces", True)),
    ("filler_voice", "unique piece", _phrase("unique piece", True)),
    ("filler_voice", "unique top", _phrase("unique top", True)),
    ("filler_voice", "curated", _phrase("curated", True)),
    ("filler_voice", "A listed", _phrase("A listed ", True)),
    ("filler_voice", "độc bản", _phrase("độc bản", True)),
    ("filler_voice", "not reserved", _phrase("not reserved", True)),
    (
        "invented_lead",
        "invented lead",
        re.compile(
            "2"
            + _DASH
            + "4"
            + _SPACE
            + "*(?:"
            + _folded("week", True)
            + "|"
            + _folded("tuần", True)
            + ")|"
            + _folded("porch date", True)
            + r"|\$6\.95|"
            + _folded("flat $", True)
            + _DIGIT
        ),
    ),
)

_JOINED_KINDS = frozenset({"stock_voice", "ops_voice", "filler_voice"})
_LEAD_FIELDS = frozenset({"descriptionEn", "descriptionVn"})
_COPY_PATTERNS = tuple(item for item in _PATTERNS if item[0] != "invented_lead")

_COPY_FIELDS = ("titleEn", "titleVn", "descriptionEn", "descriptionVn")


@dataclass(frozen=True)
class CopyField:
    field: str
    index: int | None
    text: str


@dataclass(frozen=True)
class CatalogRow:
    """One catalog row. Price, status, and copy stay as they were passed in."""

    ma: str
    fields: tuple[CopyField, ...]
    price_usd: object
    price_set: bool
    status: str | None


@dataclass(frozen=True)
class VoiceFlag:
    ma: str
    field: str
    index: int | None
    kind: str
    label: str
    stored: str

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "field": self.field,
            "index": self.index,
            "kind": self.kind,
            "label": self.label,
            "stored": self.stored,
        }


def flag_customer_copy(rows: list[CatalogRow]) -> list[VoiceFlag]:
    """Return flags. Leave every CatalogRow as it was passed in."""
    flags: list[VoiceFlag] = []
    for row in rows:
        code = norm_ma(row.ma)
        for field in row.fields:
            patterns = _PATTERNS if field.field in _LEAD_FIELDS else _COPY_PATTERNS
            flags.extend(_scan(code, field.field, field.index, field.text, patterns, None))
        flags.extend(_joined_copy_flags(code, row))
        flags.extend(_joined_lead_flags(code, row))
    return flags


def report_json(rows: list[CatalogRow], flags: list[VoiceFlag]) -> dict[str, object]:
    return {
        "readOnly": True,
        "s06": "stays $25",
        "held": "stay held",
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
                fields=_fields(item, ma),
                price_usd=price,
                price_set=price_set,
                status=_status(item, ma),
            )
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag customer-visible catalog copy the shop treats as ops or stock voice. "
            "Reads a local JSON fixture and prints flags."
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
    if _is_shop_catalog(path):
        print("refusing the shop catalog", file=sys.stderr)
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
        report_json(rows, flag_customer_copy(rows)),
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def _joined_copy_flags(code: str, row: CatalogRow) -> list[VoiceFlag]:
    """Phrases the shop sees on one untrimmed line of the four customer copy fields."""
    parts = [_field_text(row, name) for name in _COPY_FIELDS]
    text, spans = _joined(parts, " ")
    patterns = tuple(item for item in _COPY_PATTERNS if item[0] in _JOINED_KINDS)
    return _scan(code, "joinedCopy", None, text, patterns, spans)


def _joined_lead_flags(code: str, row: CatalogRow) -> list[VoiceFlag]:
    """A lead promise on the two descriptions, joined by the shop's line break. No trim."""
    parts = [_field_text(row, "descriptionEn"), _field_text(row, "descriptionVn")]
    text, spans = _joined(parts, "\n")
    patterns = tuple(item for item in _PATTERNS if item[0] == "invented_lead")
    return _scan(code, "joinedDescriptions", None, text, patterns, spans)


def _scan(
    code: str,
    field: str,
    index: int | None,
    text: str,
    patterns: tuple[tuple[str, str, re.Pattern[str]], ...],
    skip_inside: list[tuple[int, int]] | None,
) -> list[VoiceFlag]:
    flags: list[VoiceFlag] = []
    taken: list[tuple[int, int]] = []
    for kind, label, pattern in patterns:
        for match in pattern.finditer(text):
            start, end = match.span()
            if start == end:
                continue
            if skip_inside is not None and _inside_one(start, end, skip_inside):
                continue
            if any(start < prev_end and end > prev_start for prev_start, prev_end in taken):
                continue
            taken.append((start, end))
            flags.append(
                VoiceFlag(
                    ma=code,
                    field=field,
                    index=index,
                    kind=kind,
                    label=label,
                    stored=match.group(0),
                )
            )
    return flags


def _field_text(row: CatalogRow, name: str) -> str:
    """The stored field. The shop join does not trim it."""
    for field in row.fields:
        if field.field == name and field.index is None:
            return field.text
    return ""


def _joined(parts: list[str], separator: str) -> tuple[str, list[tuple[int, int]]]:
    chunks: list[str] = []
    spans: list[tuple[int, int]] = []
    for index, value in enumerate(parts):
        if index:
            chunks.append(separator)
        start = sum(len(chunk) for chunk in chunks)
        chunks.append(value)
        spans.append((start, start + len(value)))
    return "".join(chunks), spans


def _inside_one(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    return any(start >= left and end <= right for left, right in spans)


def _fields(item: dict[str, object], ma: str) -> tuple[CopyField, ...]:
    fields: list[CopyField] = []
    for name in _COPY_FIELDS:
        if name not in item or item.get(name) is None:
            continue
        raw = item.get(name)
        if not isinstance(raw, str):
            raise ValueError(f"{ma} {name} must be a string")
        fields.append(CopyField(name, None, raw))
    if "colors" in item and item.get("colors") is not None:
        raw_colors = item.get("colors")
        if not isinstance(raw_colors, list):
            raise ValueError(f"{ma} colors must be a list")
        for index, color in enumerate(raw_colors):
            fields.extend(_color_fields(color, ma, index))
    return tuple(fields)


def _color_fields(color: object, ma: str, index: int) -> tuple[CopyField, ...]:
    if isinstance(color, str):
        return (CopyField("colorName", index, color),)
    if not isinstance(color, dict):
        raise ValueError(f"{ma} color {index} must be a string or an object")
    fields: list[CopyField] = []
    for key, field_name in (("name", "colorName"), ("note", "colorNote")):
        if key not in color or color.get(key) is None:
            continue
        raw = color.get(key)
        if not isinstance(raw, str):
            raise ValueError(f"{ma} color {index} {key} must be a string")
        fields.append(CopyField(field_name, index, raw))
    return tuple(fields)


def _product_list(payload: object) -> list[object]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        products = payload.get("products")
        if isinstance(products, list):
            return products
    raise ValueError("catalog fixture must be a product list or a catalog document")


def _price(item: dict[str, object], ma: str) -> tuple[object, bool]:
    if "priceUsd" not in item:
        return None, False
    value = item["priceUsd"]
    if value is None or isinstance(value, str):
        return value, True
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{ma} price must be a number, a string, or blank")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{ma} price must be a finite number")
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


def _is_shop_catalog(path: Path) -> bool:
    root = Path(__file__).resolve().parents[1]
    banned = (root / "sassy-closet-shop" / "data" / "products.json").resolve()
    try:
        return path.resolve() == banned
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
