"""Sell-site catalog.v1 — A01-style mã, allowlist-only, never invent.

Intake / SoT still use excel-kit/schema.py (legacy AO001 parse_ma).
This module is the sell-site lane only. Do not mint mãs. Do not
publish cost, source_link, or customer names.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_ID = "catalog.v1"

# Letter + 2–3 digits. Letters from the live hub (D = đầm).
SELL_MA_LETTERS: tuple[str, ...] = (
    "A",
    "Q",
    "V",
    "K",
    "G",
    "B",
    "P",
    "H",
    "J",
    "S",
    "O",
    "D",
)
SELL_MA_RE = re.compile(rf"^([{''.join(SELL_MA_LETTERS)}])(\d{{2,3}})$")

# First-ten sell-test mãs. Scripts refuse anything else.
SELL_ALLOWLIST: tuple[str, ...] = (
    "A01",
    "S01",
    "P01",
    "P02",
    "P03",
    "P04",
    "P05",
    "K01",
    "H01",
    "A02",
)

# Boss-approved USD. None = Hold · Inbox for price. Never invent a substitute.
SELL_ALLOWLIST_PRICE_USD: dict[str, int | None] = {
    "A01": 25,
    "S01": 28,
    "P01": 5,
    "P02": None,
    "P03": 18,
    "P04": 13,
    "P05": None,
    "K01": 37,
    "H01": 8,
    "A02": 22,
}

# Live sell-test types for the two thermos Holds (kind letter is still P).
THERMOS_MAS: frozenset[str] = frozenset({"P02", "P05"})

KIND_TO_TYPE: dict[str, str] = {
    "A": "top",
    "Q": "pants",
    "V": "skirt",
    "D": "dress",
    "K": "jacket",
    "G": "shoes",
    "B": "bag",
    "P": "accessory",
    "H": "hair",
    "J": "jewelry",
    "S": "set",
    "O": "other",
}

TYPE_LABEL_EN: dict[str, str] = {
    "top": "Top",
    "pants": "Pants",
    "skirt": "Skirt",
    "dress": "Dress",
    "jacket": "Jacket",
    "shoes": "Shoes",
    "bag": "Bag",
    "accessory": "Accessory",
    "thermos": "Thermos",
    "hair": "Hair",
    "jewelry": "Jewelry",
    "set": "Set",
    "other": "Other",
}

TYPE_LABEL_VN: dict[str, str] = {
    "top": "Áo",
    "pants": "Quần",
    "skirt": "Váy",
    "dress": "Đầm",
    "jacket": "Áo khoác",
    "shoes": "Giày",
    "bag": "Túi",
    "accessory": "Phụ kiện",
    "thermos": "Bình giữ nhiệt",
    "hair": "Tóc",
    "jewelry": "Trang sức",
    "set": "Set đồ",
    "other": "Khác",
}

XLSX_ALL_SHEET = "All"
XLSX_REQUIRED_HEADERS: tuple[str, ...] = ("ma",)

ONEDRIVE_CATALOG = "Documents/Sassy Closet/sassycloset.xlsx"
ONEDRIVE_PHOTOS = "Documents/Sassy Closet/Photos"
ENV_CATALOG = "SASSY_CATALOG_XLSX"
ENV_CATALOG_ALT = "SASSYCLOSET_XLSX"

PRODUCT_KEYS: tuple[str, ...] = (
    "ma",
    "titleEn",
    "titleVn",
    "descriptionEn",
    "descriptionVn",
    "type",
    "status",
    "priceUsd",
    "qty",
    "colors",
    "images",
)
COLOR_KEYS: frozenset[str] = frozenset({"id", "name", "hex"})
IMAGE_KEYS: frozenset[str] = frozenset({"src", "url", "colorId", "order"})
IMAGE_SUFFIXES: frozenset[str] = frozenset({".jpg", ".jpeg", ".png", ".webp"})
SKIP_IMAGE_PREFIXES: tuple[str, ...] = (".", "_")

HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "ma": ("ma", "mã", "Ma"),
    "source_link": ("source_link", "source", "link"),
    "kind": ("kind", "type", "category", "prefix"),
    "colors": ("colors", "color", "mau", "màu"),
    "sell_usd": (
        "sell_usd",
        "price",
        "list_price",
        "price_usd",
        "priceUsd",
        "sell $",
        "gia ban $",
    ),
    "status": ("status", "Status"),
    "flag": ("flag", "flags", "notes"),
    "photo_folder": ("photo_folder", "photo_link", "photos"),
    "title_en": ("title_en", "titleEn", "name_en", "title en"),
    "title_vn": ("title_vn", "titleVn", "name_vi", "title vn"),
    "description_en": ("description_en", "descriptionEn", "blurb_en", "desc_en"),
    "description_vn": ("description_vn", "descriptionVn", "blurb_vn", "desc_vn"),
}

MISSING_XLSX_STEPS = """sassycloset.xlsx was not found. Do not invent rows.

Boss / Kit run (laptop with OneDrive):

  pip install -r requirements.txt
  python3 excel-kit/scripts/export_sell_catalog.py \\
    -w "$HOME/OneDrive/Documents/Sassy Closet/sassycloset.xlsx" \\
    --photos-dir "$HOME/OneDrive/Documents/Sassy Closet/Photos" \\
    -o ./out/sell-catalog.v1.json
  python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json

Or set SASSY_CATALOG_XLSX to that workbook path.

Allowlist only: A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
Hold when sell_usd is empty or Boss allowlist says Hold (P02, P05).
Never invent mã / stock / prices. No Square Save. No Facebook Post/Send.
"""


class CatalogError(ValueError):
    """Hard-fail: non-allowlist, invent, or schema mismatch."""


def parse_sell_ma(value: object) -> tuple[str, int] | None:
    """Return (letter, number) for an A01-style mã; else None. Never invent."""
    if value is None:
        return None
    text = str(value).strip().upper()
    match = SELL_MA_RE.fullmatch(text)
    if not match:
        return None
    letter, digits = match.group(1), match.group(2)
    if letter not in SELL_MA_LETTERS:
        return None
    number = int(digits)
    if number < 1 or number > 999:
        return None
    if number < 100 and len(digits) != 2:
        return None
    if number >= 100 and len(digits) != 3:
        return None
    return letter, number


def format_sell_ma(letter: str, number: int) -> str:
    key = letter.strip().upper()
    if key not in SELL_MA_LETTERS:
        raise CatalogError(f"unknown sell-site mã letter: {letter!r}")
    if number < 1 or number > 999:
        raise CatalogError(f"mã number out of range: {number}")
    digits = f"{number:02d}" if number < 100 else str(number)
    return f"{key}{digits}"


def normalize_sell_ma(value: object) -> str | None:
    parsed = parse_sell_ma(value)
    if parsed is None:
        return None
    return format_sell_ma(*parsed)


def is_allowlisted_ma(value: object) -> bool:
    ma = normalize_sell_ma(value)
    return ma is not None and ma in SELL_ALLOWLIST


def sell_type_for_ma(ma: str, kind: str | None = None) -> str:
    if ma in THERMOS_MAS:
        return "thermos"
    letter = (kind or ma[:1]).strip().upper()
    if letter not in KIND_TO_TYPE:
        raise CatalogError(f"{ma}: unknown kind letter {letter!r} — do not invent a type")
    return KIND_TO_TYPE[letter]


def _norm_header(name: object) -> str:
    return "" if name is None else str(name).strip().lower()


def _header_index(headers: Sequence[str], logical: str) -> int | None:
    aliases = HEADER_ALIASES.get(logical, (logical,))
    wanted = {_norm_header(a) for a in aliases}
    for i, header in enumerate(headers):
        if _norm_header(header) in wanted:
            return i
    return None


def _cell_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_price_usd(value: object) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise CatalogError(f"sell_usd cannot be boolean: {value!r}")
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            return float(value)
        return int(value)
    text = str(value).strip()
    if not text or text.lower() in {"hold", "inbox", "n/a", "na", "-"}:
        return None
    cleaned = text.replace("$", "").replace(",", "").strip()
    try:
        number = float(cleaned)
    except ValueError as exc:
        raise CatalogError(f"sell_usd is not a number: {value!r}") from exc
    if not number.is_integer():
        return number
    return int(number)


def _slug_color_id(name: str, used: set[str]) -> str:
    folded = name.replace("đ", "d").replace("Đ", "d")
    decomposed = unicodedata.normalize("NFKD", folded)
    ascii_only = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    if not slug:
        slug = "color"
    base = slug
    n = 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


def parse_colors_text(raw: object) -> list[dict[str, str]]:
    """Customer colors are text-only. Do not invent hex."""
    text = _cell_text(raw)
    if not text:
        return []
    parts = [p.strip() for p in re.split(r"[,;/|]+", text) if p.strip()]
    used: set[str] = set()
    colors: list[dict[str, str]] = []
    for part in parts:
        colors.append({"id": _slug_color_id(part, used), "name": part})
    return colors


def _is_real_photo_name(name: str) -> bool:
    stem = Path(name).name
    if not stem or stem.startswith(SKIP_IMAGE_PREFIXES):
        return False
    return Path(stem).suffix.lower() in IMAGE_SUFFIXES


def list_photo_files(photos_dir: Path, ma: str) -> list[str]:
    folder = photos_dir / ma
    if not folder.is_dir():
        return []
    names = [p.name for p in folder.iterdir() if p.is_file() and _is_real_photo_name(p.name)]
    names.sort()
    return names


def _photo_folder_text(raw: object, ma: str) -> str:
    text = _cell_text(raw).rstrip("/")
    if text:
        return text
    return f"{ONEDRIVE_PHOTOS}/{ma}"


def product_images(ma: str, photo_folder: str, filenames: Sequence[str]) -> list[dict[str, Any]]:
    images: list[dict[str, Any]] = []
    for order, name in enumerate(filenames, start=1):
        images.append(
            {
                "src": f"{photo_folder.rstrip('/')}/{name}",
                "colorId": None,
                "order": order,
            }
        )
    return images


def resolve_sell_status_and_price(
    ma: str,
    xlsx_price: int | float | None,
) -> tuple[str, int | float | None, list[str]]:
    """Boss allowlist wins. Empty xlsx price → Hold. Never invent a USD amount."""
    notes: list[str] = []
    allowed = SELL_ALLOWLIST_PRICE_USD[ma]
    if allowed is None:
        if xlsx_price is not None:
            notes.append(
                f"{ma}: xlsx sell_usd={xlsx_price} ignored — Boss allowlist is Hold"
            )
        return "hold", None, notes
    if xlsx_price is None:
        notes.append(f"{ma}: xlsx sell_usd empty; using Boss allowlist ${allowed}")
        return "available", allowed, notes
    if float(xlsx_price) != float(allowed):
        raise CatalogError(
            f"{ma}: xlsx sell_usd={xlsx_price} disagrees with Boss allowlist ${allowed}. "
            "Do not invent or override a live price."
        )
    return "available", allowed, notes


def empty_product(ma: str) -> dict[str, Any]:
    kind = ma[:1]
    return {
        "ma": ma,
        "titleEn": "",
        "titleVn": "",
        "descriptionEn": "",
        "descriptionVn": "",
        "type": sell_type_for_ma(ma, kind),
        "status": "hold",
        "priceUsd": None,
        "qty": 1,
        "colors": [],
        "images": [],
    }


def catalog_envelope(
    products: Sequence[Mapping[str, Any]],
    *,
    source: str = ONEDRIVE_CATALOG,
    exported_at: str | None = None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA_ID,
        "source": source,
        "exportedAt": exported_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "allowlist": list(SELL_ALLOWLIST),
        "products": [dict(p) for p in products],
    }


def candidate_catalog_paths(explicit: Path | None = None) -> list[Path]:
    found: list[Path] = []
    if explicit is not None:
        found.append(Path(explicit).expanduser())
    for key in (ENV_CATALOG, ENV_CATALOG_ALT):
        env = os.environ.get(key)
        if env:
            found.append(Path(env).expanduser())
    home = Path.home()
    extras = [
        home / "OneDrive" / ONEDRIVE_CATALOG,
        home / "OneDrive - Personal" / ONEDRIVE_CATALOG,
        home / "Library/CloudStorage/OneDrive-Personal" / ONEDRIVE_CATALOG,
        Path.cwd() / "sassycloset.xlsx",
        Path.cwd() / "Documents/Sassy Closet/sassycloset.xlsx",
        Path.cwd() / "out" / "sassycloset.xlsx",
    ]
    found.extend(extras)
    # De-dupe while keeping order.
    seen: set[str] = set()
    unique: list[Path] = []
    for path in found:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def locate_catalog_xlsx(explicit: Path | None = None) -> Path | None:
    for path in candidate_catalog_paths(explicit):
        if path.is_file():
            return path
    return None


def _row_get(headers: Sequence[str], values: Sequence[object], logical: str) -> object:
    idx = _header_index(headers, logical)
    if idx is None or idx >= len(values):
        return None
    return values[idx]


def read_all_sheet_rows(workbook_path: Path) -> tuple[list[str], list[list[object]]]:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:  # pragma: no cover — --help does not import this
        raise CatalogError(
            "openpyxl is required to read xlsx. pip install -r requirements.txt"
        ) from exc

    wb = load_workbook(workbook_path, data_only=True, read_only=True)
    try:
        if XLSX_ALL_SHEET not in wb.sheetnames:
            raise CatalogError(
                f"{workbook_path}: missing {XLSX_ALL_SHEET!r} sheet. "
                "Do not invent rows from kind tabs."
            )
        ws = wb[XLSX_ALL_SHEET]
        rows = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()
    if not rows:
        raise CatalogError(f"{workbook_path}: {XLSX_ALL_SHEET} is empty")
    headers = [_cell_text(h) for h in rows[0]]
    while headers and headers[-1] == "":
        headers.pop()
    if _header_index(headers, "ma") is None:
        raise CatalogError(
            f"{workbook_path}: {XLSX_ALL_SHEET} has no ma column, got {headers!r}"
        )
    data: list[list[object]] = []
    for raw in rows[1:]:
        values = list(raw[: len(headers)])
        if all(_cell_text(v) == "" for v in values):
            continue
        data.append(values)
    return headers, data


def row_to_product(
    headers: Sequence[str],
    values: Sequence[object],
    *,
    photos_dir: Path | None = None,
) -> tuple[dict[str, Any], list[str]]:
    raw_ma = _row_get(headers, values, "ma")
    ma = normalize_sell_ma(raw_ma)
    if ma is None:
        raise CatalogError(
            f"invalid or invented mã {raw_ma!r}. "
            f"Sell-site mã is letter+2–3 digits from {list(SELL_MA_LETTERS)}. "
            f"This export allowlist is {list(SELL_ALLOWLIST)}."
        )
    if ma not in SELL_ALLOWLIST:
        raise CatalogError(
            f"{ma} is not on the sell-test allowlist {list(SELL_ALLOWLIST)}. "
            "Hard-fail — do not invent extra shop rows."
        )
    kind_raw = _cell_text(_row_get(headers, values, "kind")).upper()
    if kind_raw and kind_raw != ma[:1]:
        raise CatalogError(f"{ma}: kind {kind_raw!r} does not match mã letter {ma[:1]}")
    xlsx_price = _parse_price_usd(_row_get(headers, values, "sell_usd"))
    status, price, notes = resolve_sell_status_and_price(ma, xlsx_price)
    photo_folder = _photo_folder_text(_row_get(headers, values, "photo_folder"), ma)
    filenames = list_photo_files(photos_dir, ma) if photos_dir is not None else []
    product = {
        "ma": ma,
        "titleEn": _cell_text(_row_get(headers, values, "title_en")),
        "titleVn": _cell_text(_row_get(headers, values, "title_vn")),
        "descriptionEn": _cell_text(_row_get(headers, values, "description_en")),
        "descriptionVn": _cell_text(_row_get(headers, values, "description_vn")),
        "type": sell_type_for_ma(ma, kind_raw or ma[:1]),
        "status": status,
        "priceUsd": price,
        "qty": 1,
        "colors": parse_colors_text(_row_get(headers, values, "colors")),
        "images": product_images(ma, photo_folder, filenames),
    }
    return product, notes


def export_products(
    workbook_path: Path,
    *,
    photos_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    headers, rows = read_all_sheet_rows(workbook_path)
    by_ma: dict[str, dict[str, Any]] = {}
    notes: list[str] = []
    for values in rows:
        product, row_notes = row_to_product(headers, values, photos_dir=photos_dir)
        ma = product["ma"]
        if ma in by_ma:
            raise CatalogError(f"duplicate mã on All sheet: {ma}")
        by_ma[ma] = product
        notes.extend(row_notes)
    missing = [ma for ma in SELL_ALLOWLIST if ma not in by_ma]
    if missing:
        raise CatalogError(
            f"All sheet is missing allowlist mã(s) {missing}. Never invent the gaps."
        )
    extra = [ma for ma in by_ma if ma not in SELL_ALLOWLIST]
    if extra:
        raise CatalogError(f"All sheet has non-allowlist mã(s) {extra}")
    ordered = [by_ma[ma] for ma in SELL_ALLOWLIST]
    return ordered, notes


def _require_str(product: Mapping[str, Any], key: str, ma: str) -> str:
    value = product.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise CatalogError(f"{ma}.{key} must be a string")
    return value


def validate_product(product: Mapping[str, Any], *, expect_ma: str | None = None) -> None:
    unknown = [k for k in product if k not in PRODUCT_KEYS]
    if unknown:
        raise CatalogError(
            f"{product.get('ma')}: extra keys {unknown} (cost/source/PII must not ship)"
        )
    ma = normalize_sell_ma(product.get("ma"))
    if ma is None:
        raise CatalogError(f"product.ma invalid: {product.get('ma')!r}")
    if ma not in SELL_ALLOWLIST:
        raise CatalogError(f"{ma} is not allowlisted")
    if expect_ma is not None and ma != expect_ma:
        raise CatalogError(f"expected {expect_ma} in this slot, got {ma}")
    for key in ("titleEn", "titleVn", "descriptionEn", "descriptionVn"):
        _require_str(product, key, ma)
    typ = product.get("type")
    if typ not in TYPE_LABEL_EN:
        raise CatalogError(f"{ma}.type {typ!r} is not a known sell-site type")
    expected_type = sell_type_for_ma(ma)
    if typ != expected_type:
        raise CatalogError(f"{ma}.type {typ!r} != {expected_type!r} for this mã")
    status = product.get("status")
    if status not in {"hold", "available"}:
        raise CatalogError(f"{ma}.status must be hold|available, got {status!r}")
    price = product.get("priceUsd")
    allowed = SELL_ALLOWLIST_PRICE_USD[ma]
    if status == "hold":
        if price is not None:
            raise CatalogError(f"{ma} is Hold — priceUsd must be null")
        if allowed is not None:
            raise CatalogError(f"{ma} allowlist has ${allowed} — status cannot be hold")
    else:
        if price is None:
            raise CatalogError(f"{ma} is available — priceUsd required")
        if not isinstance(price, (int, float)) or isinstance(price, bool):
            raise CatalogError(f"{ma}.priceUsd must be a number")
        if allowed is None:
            raise CatalogError(f"{ma} allowlist is Hold — cannot be available")
        if float(price) != float(allowed):
            raise CatalogError(f"{ma}.priceUsd {price} != allowlist ${allowed}")
    qty = product.get("qty")
    if qty != 1:
        raise CatalogError(f"{ma}.qty must be 1 (unique piece), got {qty!r}")
    colors = product.get("colors")
    if not isinstance(colors, list):
        raise CatalogError(f"{ma}.colors must be an array")
    seen_color_ids: set[str] = set()
    for color in colors:
        if not isinstance(color, dict):
            raise CatalogError(f"{ma}.colors entries must be objects")
        extra = [k for k in color if k not in COLOR_KEYS]
        if extra:
            raise CatalogError(f"{ma} color extra keys {extra}")
        cid = color.get("id")
        if not isinstance(cid, str) or not cid.strip():
            raise CatalogError(f"{ma} color.id required")
        if cid in seen_color_ids:
            raise CatalogError(f"{ma} duplicate color.id {cid!r}")
        seen_color_ids.add(cid)
        if "name" in color and color["name"] is not None and not isinstance(color["name"], str):
            raise CatalogError(f"{ma} color.name must be text")
        if "hex" in color and color["hex"] not in (None, "") and not isinstance(color["hex"], str):
            raise CatalogError(f"{ma} color.hex must be text if present")
    images = product.get("images")
    if not isinstance(images, list):
        raise CatalogError(f"{ma}.images must be an array")
    for image in images:
        if not isinstance(image, dict):
            raise CatalogError(f"{ma}.images entries must be objects")
        extra = [k for k in image if k not in IMAGE_KEYS]
        if extra:
            raise CatalogError(f"{ma} image extra keys {extra}")
        src = image.get("src") or image.get("url")
        if not isinstance(src, str) or not src.strip():
            raise CatalogError(f"{ma} image needs src or url")
        if src.startswith("blob:"):
            raise CatalogError(f"{ma} image src is a local blob: URL — not importable")
        color_id = image.get("colorId", None)
        if color_id is not None and color_id not in seen_color_ids:
            raise CatalogError(f"{ma} image.colorId {color_id!r} is not a product color")
        order = image.get("order")
        if order is not None and (not isinstance(order, int) or order < 1):
            raise CatalogError(f"{ma} image.order must be a positive int")


def validate_catalog(doc: Mapping[str, Any]) -> None:
    if doc.get("schema") != SCHEMA_ID:
        raise CatalogError(f"schema must be {SCHEMA_ID!r}, got {doc.get('schema')!r}")
    products = doc.get("products")
    if not isinstance(products, list):
        raise CatalogError("products must be an array")
    if len(products) != len(SELL_ALLOWLIST):
        raise CatalogError(
            f"expected exactly {len(SELL_ALLOWLIST)} allowlist products, got {len(products)}"
        )
    seen: list[str] = []
    for i, product in enumerate(products):
        if not isinstance(product, dict):
            raise CatalogError(f"products[{i}] must be an object")
        expect = SELL_ALLOWLIST[i]
        validate_product(product, expect_ma=expect)
        seen.append(str(product["ma"]))
    if seen != list(SELL_ALLOWLIST):
        raise CatalogError(f"product order must be {list(SELL_ALLOWLIST)}, got {seen}")


def load_catalog_json(path: Path) -> dict[str, Any]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(f"{path}: invalid JSON ({exc})") from exc
    if not isinstance(doc, dict):
        raise CatalogError(f"{path}: catalog root must be an object")
    return doc


def dump_catalog_json(doc: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def write_xlsx_fixture(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    """Test helper: All-sheet workbook. Never a live Official book."""
    from openpyxl import Workbook

    headers = [
        "ma",
        "source_link",
        "kind",
        "colors",
        "sell_usd",
        "cost",
        "currency",
        "square",
        "status",
        "flag",
        "photo_folder",
        "title_en",
        "title_vn",
        "description_en",
        "description_vn",
    ]
    wb = Workbook()
    ws = wb.active
    ws.title = XLSX_ALL_SHEET
    ws.append(headers)
    for row in rows:
        ws.append([row.get(h, "") for h in headers])
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    wb.close()


def allowlist_fixture_rows() -> list[dict[str, object]]:
    """Minimal real-shaped rows for the 10 known mãs. Prices match Boss table."""
    colors = {
        "A01": "Kem, Xanh",
        "S01": "Kem",
        "P01": "Hoa",
        "P02": "Đỏ",
        "P03": "Đen, Đỏ",
        "P04": "Kem",
        "P05": "Hồng, Đỏ, Xanh",
        "K01": "",
        "H01": "",
        "A02": "Chấm bi",
    }
    flags = {
        "P02": "thermos kind hold",
        "P05": "thermos kind hold",
    }
    rows: list[dict[str, object]] = []
    for ma in SELL_ALLOWLIST:
        price = SELL_ALLOWLIST_PRICE_USD[ma]
        rows.append(
            {
                "ma": ma,
                "kind": ma[:1],
                "colors": colors[ma],
                "sell_usd": "" if price is None else price,
                "status": "staged",
                "flag": flags.get(ma, ""),
                "photo_folder": f"{ONEDRIVE_PHOTOS}/{ma}/",
            }
        )
    return rows
