"""Flag a fixture photo path that has no image extension.

Read-only. A path ending in .jpg, .jpeg, .png, or .webp stays quiet. Any
other photo path is named in the report and left as stored. This script
does not rename a file, rewrite a path, or change a price. Nothing here
reads or writes data/held.json. Pass a fixture file. A URL and the shop
catalog are refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

_PHOTO_KEYS = ("images", "photos", "gallery", "gallery_urls")
_URL_KEYS = ("src", "url", "path")
_IMAGE_EXTS = (".jpeg", ".jpg", ".png", ".webp")
_KIND = "no_image_extension"


@dataclass(frozen=True)
class CatalogPhotoRow:
    """One catalog row. The check reads each photo path and leaves the row as it was."""

    ma: str
    photos: tuple[str, ...]
    price_usd: int | None = None
    held: bool = False
    status: str | None = None


@dataclass(frozen=True)
class PhotoExtFlag:
    ma: str
    path: str
    index: int
    kind: str

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "path": self.path,
            "index": self.index,
            "kind": self.kind,
        }


def image_extension(path: str) -> str | None:
    """Return .jpg, .jpeg, .png, or .webp, or None when the path has no image extension.

    The match ignores letter case and ignores a query or fragment. The stored
    path is not rewritten.
    """
    folded = _path_body(path).casefold()
    for ext in _IMAGE_EXTS:
        if folded.endswith(ext):
            return ext
    return None


def flag_photo_extensions(rows: list[CatalogPhotoRow]) -> list[PhotoExtFlag]:
    """Return one flag per photo path that has no image extension. Rows stay as passed in."""
    flags: list[PhotoExtFlag] = []
    for row in rows:
        code = row.ma.strip().upper()
        for index, path in enumerate(row.photos):
            if image_extension(path) is not None:
                continue
            flags.append(PhotoExtFlag(code, path, index, _KIND))
    return flags


def report_json(rows: list[CatalogPhotoRow], flags: list[PhotoExtFlag]) -> dict[str, object]:
    return {
        "readOnly": True,
        "rows": len(rows),
        "flags": [flag.as_json() for flag in flags],
    }


def load_catalog(path: Path) -> list[CatalogPhotoRow]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    products = payload.get("products") if isinstance(payload, dict) else payload
    if not isinstance(products, list):
        raise ValueError("catalog must be a list of rows or an object with products")
    rows: list[CatalogPhotoRow] = []
    for item in products:
        if not isinstance(item, dict):
            raise ValueError("each catalog row must be an object")
        ma = item.get("ma")
        if not isinstance(ma, str) or not ma.strip():
            raise ValueError("each catalog row needs a mã")
        rows.append(
            CatalogPhotoRow(
                ma,
                _photo_list(item),
                _price(item.get("priceUsd")),
                _held(item),
                _status(item.get("status")),
            )
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag a fixture photo path that has no image extension. Read-only.",
    )
    parser.add_argument("--catalog", required=True, help="Fixture catalog JSON. Read and left unchanged.")
    args = parser.parse_args(argv)
    try:
        _reject_live(args.catalog)
        rows = load_catalog(Path(args.catalog))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    flags = flag_photo_extensions(rows)
    print(json.dumps(report_json(rows, flags), ensure_ascii=False, indent=2))
    return 1 if flags else 0


def _path_body(path: str) -> str:
    """Path text before a query or fragment. The caller still reports the stored path."""
    cut = len(path)
    for mark in ("?", "#"):
        index = path.find(mark)
        if index != -1 and index < cut:
            cut = index
    return path[:cut]


def _photo_list(item: dict[str, object]) -> tuple[str, ...]:
    for key in _PHOTO_KEYS:
        if key not in item:
            continue
        raw = item[key]
        if not isinstance(raw, list):
            raise ValueError(f"{key} must be a list")
        return tuple(_photo_path(entry) for entry in raw)
    return ()


def _photo_path(entry: object) -> str:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        for key in _URL_KEYS:
            if key in entry:
                value = entry[key]
                if value is None:
                    return ""
                if not isinstance(value, str):
                    raise ValueError("photo path must be a string")
                return value
        raise ValueError("photo object needs a src")
    raise ValueError("photo entry must be a path string or an object with src")


def _price(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _status(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _held(item: dict[str, object]) -> bool:
    if item.get("held") is True:
        return True
    status = item.get("status")
    if isinstance(status, str) and status.strip().lower() in {"hold", "held"}:
        return True
    return False


def _reject_live(raw: str) -> None:
    if "://" in raw:
        raise ValueError("fixtures only; refusing a URL")
    path = Path(raw).resolve()
    root = Path(__file__).resolve().parents[1]
    banned = {
        (root / "sassy-closet-shop" / "data" / "products.json").resolve(),
        (root / "data" / "held.json").resolve(),
    }
    if path in banned:
        raise ValueError("fixtures only; refusing the shop catalog and held list")


if __name__ == "__main__":
    raise SystemExit(main())
