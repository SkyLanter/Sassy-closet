"""Flag a catalog photo src that is not a site path.

Read-only. A site path starts with /products/, such as
/products/S06/cover.jpg. A full http URL, a data URL, a blank, and a src
that does not start with /products/ (images/a01.jpg, /etc/passwd) are
named in the report with the stored src. This script does not rewrite a
src, change a price, or write data/held.json. Pass a fixture file. A URL
and the shop catalog are refused.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

_PHOTO_KEYS = ("images", "photos", "gallery", "gallery_urls")
_URL_KEYS = ("src", "url", "path")
_HTTP_PREFIXES = ("http://", "https://")
_SITE_PREFIX = "/products/"


@dataclass(frozen=True)
class CatalogPhotoRow:
    """One catalog row. The check reads each photo src and leaves the row as it was."""

    ma: str
    photos: tuple[str, ...]
    price_usd: int | None = None
    held: bool = False
    status: str | None = None


@dataclass(frozen=True)
class PhotoSrcFlag:
    ma: str
    src: str
    index: int
    kind: str

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "src": self.src,
            "index": self.index,
            "kind": self.kind,
        }


def src_kind(src: str) -> str | None:
    """Return a flag kind, or None when the stored src is already a site path.

    The stored text is classified and is not trimmed or replaced.
    """
    stripped = src.strip()
    if stripped == "":
        return "blank"
    folded = stripped.casefold()
    if folded.startswith(_HTTP_PREFIXES):
        return "http_url"
    if folded.startswith("data:"):
        return "data_url"
    if _is_site_path(src):
        return None
    return "not_site_path"


def flag_photo_src_paths(rows: list[CatalogPhotoRow]) -> list[PhotoSrcFlag]:
    """Return one flag per photo src that is not a site path. Rows stay as passed in."""
    flags: list[PhotoSrcFlag] = []
    for row in rows:
        code = row.ma.strip().upper()
        for index, src in enumerate(row.photos):
            kind = src_kind(src)
            if kind is None:
                continue
            flags.append(PhotoSrcFlag(code, src, index, kind))
    flags.sort(key=lambda flag: (flag.ma, flag.index, flag.kind, flag.src))
    return flags


def report_json(rows: list[CatalogPhotoRow], flags: list[PhotoSrcFlag]) -> dict[str, object]:
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
        description="Flag a catalog photo src that is not a site path. Read-only.",
    )
    parser.add_argument("--catalog", required=True, help="Fixture catalog JSON. Read and left unchanged.")
    args = parser.parse_args(argv)
    try:
        _reject_live(args.catalog)
        rows = load_catalog(Path(args.catalog))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    flags = flag_photo_src_paths(rows)
    print(json.dumps(report_json(rows, flags), ensure_ascii=False, indent=2))
    return 1 if flags else 0


def _is_site_path(src: str) -> bool:
    """True when the stored src starts with /products/, such as /products/S06/cover.jpg."""
    if src != src.strip() or not src.startswith(_SITE_PREFIX) or src.endswith("/"):
        return False
    if any(char.isspace() or char in {"\\", "\x00", ":"} for char in src) or "//" in src:
        return False
    parts = src.split("/")
    return all(part not in {"", ".", ".."} for part in parts[1:])


def _photo_list(item: dict[str, object]) -> tuple[str, ...]:
    for key in _PHOTO_KEYS:
        if key not in item:
            continue
        raw = item[key]
        if not isinstance(raw, list):
            raise ValueError(f"{key} must be a list")
        return tuple(_photo_url(entry) for entry in raw)
    return ()


def _photo_url(entry: object) -> str:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        for key in _URL_KEYS:
            if key in entry:
                value = entry[key]
                if value is None:
                    return ""
                if not isinstance(value, str):
                    raise ValueError("photo src must be a string")
                return value
        raise ValueError("photo object needs a src")
    raise ValueError("photo entry must be a src string or an object with src")


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
