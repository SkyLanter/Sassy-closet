"""Flag a photo colorId that the shop reel will not attach to its color.

Read-only. The sell shop matches image.colorId to color.id with exact
equality (gallery-reel.ts). A typo, extra space, or id from another mã
leaves that chip without its slide. A null colorId stays an untagged
shared photo and is not a flag. A color with no exact slide is a flag
only when some other color on the same mã already has one, which is the
missed-tag case. Consistent binds, including a padded id that matches
its photos exactly, stay quiet.

The stored id is copied into the flag and is not rewritten. A photo in
another hub mã's `/products/` folder does not count as a slide: the shop
reel drops those files (`srcBelongsToMa`). The folder is the canonical
mã, so `a01` and `A001` are A01. Another mã's held folder does not count
either. This mã's own folder still counts, including a held mã's own
photos. Other paths, including `/uploads/` and a folder that is not a hub
mã and is not held, still count. The held list is read and not written.
Nothing here writes a catalog row, a price, a photo, intake, Blob, or
data/held.json. S06 stays $25. Held mãs stay held. Pass a local fixture.
A URL, held.json, and the shop catalog are refused.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from held_policy import HeldPolicy, load_held_policy, norm_ma

# Same list as sassy-closet-shop/lib/catalog-contract.ts KNOWN_SEED_MAS.
# srcBelongsToMa drops /products/{these}/ when the folder is not this mã.
_KNOWN_SEED_FOLDERS = (
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
_SEED_FOLDERS = frozenset(_KNOWN_SEED_FOLDERS)
# ASCII case fold, like the shop's /products/ regex. Unicode case fold would
# treat U+017F as "s" and match a different folder than the reel.
_PRODUCT_FOLDER = re.compile(r"/products/([^/]+)/", re.IGNORECASE | re.ASCII)
# JavaScript String.prototype.trim: Unicode space separators, plus these.
# Python strip also removes U+0085 and U+001C–U+001F, and it leaves U+FEFF.
_JS_TRIM_EXTRA = frozenset("\t\v\f\n\r\u00a0\u2028\u2029\ufeff")
# ASCII digits only. Python \d also matches fullwidth ０-９, and the shop regex does not.
_JS_MA = re.compile(r"^([A-Z])([0-9]+)$")

_BLANK_COLOR_ID = "blank_color_id"
_DUPLICATE_COLOR_ID = "duplicate_color_id"
_BLANK_BIND = "blank_bind"
_PADDED_BIND = "padded_bind"
_ORPHAN_BIND = "orphan_bind"
_COLOR_WITHOUT_SLIDE = "color_without_slide"


@dataclass(frozen=True)
class FixtureColor:
    """One stored color. id is the fixture text, not a corrected value."""

    id: str | None


@dataclass(frozen=True)
class FixtureImage:
    """One stored photo. color_id null means untagged."""

    src: str | None
    color_id: str | None


@dataclass(frozen=True)
class CatalogRow:
    """One catalog row. Price, status, colors, and images stay as passed in."""

    ma: str
    colors: tuple[FixtureColor, ...]
    images: tuple[FixtureImage, ...]
    price_usd: object
    price_set: bool
    status: str | None


@dataclass(frozen=True)
class BindFlag:
    ma: str
    kind: str
    index: int
    stored: str
    also_on: tuple[str, ...] = ()

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": self.kind,
            "index": self.index,
            "stored": self.stored,
            "alsoOn": list(self.also_on),
        }


def flag_color_binds(rows: list[CatalogRow]) -> list[BindFlag]:
    """Return flags. Leave every CatalogRow as it was passed in."""
    policy = load_held_policy()
    flags: list[BindFlag] = []
    for row in rows:
        code = norm_ma(row.ma)
        flags.extend(_color_id_flags(code, row))
        flags.extend(_image_flags(code, row, rows, policy))
        flags.extend(_missing_slide_flags(code, row, policy))
    return flags


def report_json(rows: list[CatalogRow], flags: list[BindFlag]) -> dict[str, object]:
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
                colors=_colors(item, ma),
                images=_images(item, ma),
                price_usd=price,
                price_set=price_set,
                status=_status(item, ma),
            )
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Flag a photo colorId the shop reel will not attach to its color. "
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
        report_json(rows, flag_color_binds(rows)),
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def _color_id_flags(code: str, row: CatalogRow) -> list[BindFlag]:
    flags: list[BindFlag] = []
    seen: set[str] = set()
    for index, color in enumerate(row.colors):
        stored = color.id
        if stored is None:
            continue
        if stored.strip() == "":
            flags.append(BindFlag(code, _BLANK_COLOR_ID, index, stored))
            continue
        if stored != stored.strip():
            continue
        if stored in seen:
            flags.append(BindFlag(code, _DUPLICATE_COLOR_ID, index, stored))
            continue
        seen.add(stored)
    return flags


def _image_flags(
    code: str, row: CatalogRow, rows: list[CatalogRow], policy: HeldPolicy
) -> list[BindFlag]:
    flags: list[BindFlag] = []
    for index, image in enumerate(row.images):
        if not _counts_for_ma(image.src, row.ma, policy):
            continue
        stored = image.color_id
        if stored is None:
            continue
        if any(color.id == stored for color in row.colors):
            continue
        if stored.strip() == "":
            flags.append(BindFlag(code, _BLANK_BIND, index, stored))
            continue
        if _strip_matches_color(row, stored):
            flags.append(BindFlag(code, _PADDED_BIND, index, stored))
            continue
        flags.append(BindFlag(code, _ORPHAN_BIND, index, stored, _also_on(rows, code, stored)))
    return flags


def _missing_slide_flags(code: str, row: CatalogRow, policy: HeldPolicy) -> list[BindFlag]:
    matched = _ids_with_slide(row, policy)
    if not matched:
        return []
    flags: list[BindFlag] = []
    for index, color in enumerate(row.colors):
        stored = color.id
        if stored is None or stored.strip() == "":
            continue
        if stored in matched:
            continue
        flags.append(BindFlag(code, _COLOR_WITHOUT_SLIDE, index, stored))
    return flags


def _ids_with_slide(row: CatalogRow, policy: HeldPolicy) -> set[str]:
    found: set[str] = set()
    for image in row.images:
        if not _counts_for_ma(image.src, row.ma, policy) or image.color_id is None:
            continue
        for color in row.colors:
            if color.id is not None and color.id == image.color_id:
                found.add(color.id)
    return found


def _strip_matches_color(row: CatalogRow, stored: str) -> bool:
    wanted = stored.strip()
    if wanted == "":
        return False
    for color in row.colors:
        if color.id is None:
            continue
        if color.id.strip() == wanted:
            return True
    return False


def _also_on(rows: list[CatalogRow], code: str, stored: str) -> tuple[str, ...]:
    """Other mãs whose color id is this stored text, or its trimmed text."""
    wanted = {stored}
    trimmed = stored.strip()
    if trimmed != "":
        wanted.add(trimmed)
    found: set[str] = set()
    for row in rows:
        other = norm_ma(row.ma)
        if other == code:
            continue
        for color in row.colors:
            if color.id in wanted:
                found.add(other)
    return tuple(sorted(found))


def _js_trim_char(char: str) -> bool:
    return char in _JS_TRIM_EXTRA or unicodedata.category(char) == "Zs"


def _js_trim(value: str) -> str:
    """Trim the way JavaScript does. Leaves U+0085 and U+001C–U+001F."""
    start = 0
    end = len(value)
    while start < end and _js_trim_char(value[start]):
        start += 1
    while end > start and _js_trim_char(value[end - 1]):
        end -= 1
    return value[start:end]


def _js_canonical(value: str) -> str:
    """Shop canonicalMaSpelling: JS trim, upper, then one letter and digits."""
    code = _js_trim(value).upper()
    match = _JS_MA.match(code)
    if match is None:
        return code
    return f"{match.group(1)}{int(match.group(2)):02d}"


def _counts_for_ma(src: str | None, ma: str, policy: HeldPolicy) -> bool:
    """True when this branch's shop reel can show this src on this mã.

    Blank src is dropped. Trim matches JavaScript, so a BOM-only src is
    blank and U+0085 is not. A `/products/{folder}/` file is dropped when
    the folder is another mã and that mã is held or a known hub mã. The
    match is ASCII case-insensitive, like the shop regex. Folder and mã
    use the shop canonical spelling, so `a01` and `A001` are A01. This
    mã's own folder still counts. The query string is ignored.
    """
    if src is None:
        return False
    trimmed = _js_trim(src)
    if trimmed == "":
        return False
    path = trimmed.split("?", 1)[0]
    match = _PRODUCT_FOLDER.search(path)
    if match is None:
        return True
    folder_code = _js_canonical(match.group(1))
    if folder_code == _js_canonical(ma):
        return True
    if folder_code in policy.held or folder_code in policy.never_list:
        return False
    return folder_code not in _SEED_FOLDERS


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
        return FixtureColor(id=None)
    if not isinstance(color, dict):
        raise ValueError(f"{ma} color {index} must be a string or an object")
    return FixtureColor(id=_color_id(color, ma, index))


def _color_id(color: dict[str, object], ma: str, index: int) -> str | None:
    if "id" not in color or color.get("id") is None:
        return None
    raw = color.get("id")
    if not isinstance(raw, str):
        raise ValueError(f"{ma} color {index} id must be a string")
    return raw


def _images(item: dict[str, object], ma: str) -> tuple[FixtureImage, ...]:
    if "images" not in item or item.get("images") is None:
        return ()
    raw = item.get("images")
    if not isinstance(raw, list):
        raise ValueError(f"{ma} images must be a list")
    return tuple(_one_image(image, ma, index) for index, image in enumerate(raw))


def _one_image(image: object, ma: str, index: int) -> FixtureImage:
    if isinstance(image, str):
        return FixtureImage(src=image, color_id=None)
    if not isinstance(image, dict):
        raise ValueError(f"{ma} image {index} must be a string or an object")
    return FixtureImage(src=_src(image, ma, index), color_id=_image_color_id(image, ma, index))


def _src(image: dict[str, object], ma: str, index: int) -> str | None:
    if "src" not in image or image.get("src") is None:
        return None
    raw = image.get("src")
    if not isinstance(raw, str):
        raise ValueError(f"{ma} image {index} src must be a string")
    return raw


def _image_color_id(image: dict[str, object], ma: str, index: int) -> str | None:
    if "colorId" not in image or image.get("colorId") is None:
        return None
    raw = image.get("colorId")
    if not isinstance(raw, str):
        raise ValueError(f"{ma} image {index} colorId must be a string")
    return raw


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
    body["colorIds"] = [{"index": index, "id": color.id} for index, color in enumerate(row.colors)]
    body["imageBinds"] = [
        {"index": index, "colorId": image.color_id} for index, image in enumerate(row.images)
    ]
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
