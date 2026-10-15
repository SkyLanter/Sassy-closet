"""Flag catalog mãs with fewer than 2 photos.

Reads a catalog JSON fixture and writes a report. Photo files stay
untouched. S06 stays $25. Held mãs stay held. This module does not upload
photos, and it does not write catalog rows, prices, or data/held.json.

A photo is one image entry with a non-blank src. A repeated src counts
again. Blank srcs do not count.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from held_policy import HeldPolicy, load_held_policy

MIN_PHOTOS = 2
S06 = "S06"
S06_USD = "25"
MA_RE = re.compile(r"^[A-Z][0-9]{2}$")
ROOT = Path(__file__).resolve().parents[1]
_LIVE_CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
_HELD_PATH = ROOT / "data" / "held.json"
_BLOCKED_OUT_ROOTS = (
    ROOT / "data",
    ROOT / "sassy-closet-shop" / "data",
    ROOT / "sassy-closet" / "data",
)


@dataclass(frozen=True)
class CatalogPhotoRow:
    ma: str
    photos: tuple[str, ...]
    held: bool
    price_usd: str | None
    status: str | None

    @property
    def photo_count(self) -> int:
        return len(self.photos)

    @property
    def thin(self) -> bool:
        return self.photo_count < MIN_PHOTOS

    def as_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "photoCount": self.photo_count,
            "photos": list(self.photos),
            "held": self.held,
            "priceUsd": self.price_usd,
            "status": self.status,
        }

    def flag_json(self) -> dict[str, object]:
        return {
            "ma": self.ma,
            "kind": "few_photos",
            "photoCount": self.photo_count,
            "held": self.held,
            "priceUsd": self.price_usd,
            "status": self.status,
        }


@dataclass(frozen=True)
class CatalogPhotoReport:
    rows: tuple[CatalogPhotoRow, ...]

    @property
    def flags(self) -> tuple[CatalogPhotoRow, ...]:
        return tuple(sorted((row for row in self.rows if row.thin), key=lambda row: row.ma))

    @property
    def flag_count(self) -> int:
        return len(self.flags)

    @property
    def s06_usd(self) -> str | None:
        for row in self.rows:
            if row.ma == S06:
                return row.price_usd
        return None


def photo_srcs(images: object) -> tuple[str, ...]:
    """Non-blank image srcs, in order. A repeated src counts again."""
    if not isinstance(images, list):
        return ()
    found: list[str] = []
    for item in images:
        src = _src(item)
        if src is not None:
            found.append(src)
    return tuple(found)


def flag_catalog(payload: object, policy: HeldPolicy) -> CatalogPhotoReport:
    """Return thin-gallery rows. Leave the payload as it was passed in."""
    products = _products(payload)
    rows: list[CatalogPhotoRow] = []
    seen: set[str] = set()
    for item in products:
        row = _row(item, policy)
        if row.ma in seen:
            raise ValueError(f"catalog fixture repeats {row.ma}")
        seen.add(row.ma)
        rows.append(row)
    return CatalogPhotoReport(tuple(rows))


def render_markdown(report: CatalogPhotoReport) -> str:
    lines = [
        "# Catalog photo count",
        "",
        "Read-only catalog photo check. Photo files stay untouched.",
        "S06 stays $25. Held mãs stay held.",
        "",
        f"Rows: {len(report.rows)}",
        f"Thin galleries: {report.flag_count}",
        f"Minimum photos: {MIN_PHOTOS}",
        "",
        "## Thin galleries",
        "",
    ]
    if not report.flags:
        lines.append("None.")
    else:
        lines.extend(_flag_line(row) for row in report.flags)
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "mã | photos | held | price | status | flag",
            "--- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_table_row(row) for row in report.rows)
    lines.extend(["", "## S06", ""])
    if report.s06_usd is None:
        lines.append("S06 was not in this catalog. No price was written.")
    elif report.s06_usd == S06_USD:
        lines.append("S06 stays $25.")
    else:
        lines.append(f"S06 stored price is {_md(report.s06_usd)}. No price was written.")
    lines.extend(
        [
            "",
            "## Left alone",
            "",
            "Catalog rows, prices, and data/held.json were not written.",
            "Photo files were not uploaded.",
            "",
        ]
    )
    return "\n".join(lines)


def report_json(report: CatalogPhotoReport) -> dict[str, object]:
    return {
        "readOnly": True,
        "photoBytes": "untouched",
        "minPhotos": MIN_PHOTOS,
        "s06": "stays $25",
        "s06Usd": report.s06_usd,
        "heldMas": "stay held",
        "writes": [],
        "rows": len(report.rows),
        "flagCount": report.flag_count,
        "flags": [row.flag_json() for row in report.flags],
        "catalog": [row.as_json() for row in report.rows],
    }


def write_report(report: CatalogPhotoReport, out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "catalog-photo-count.md"
    json_path = out_dir / "catalog-photo-count.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    body = json.dumps(report_json(report), ensure_ascii=False, indent=2) + "\n"
    json_path.write_text(body, encoding="utf-8")
    return markdown_path, json_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flag catalog mãs with fewer than 2 photos. Writes a report only.",
    )
    parser.add_argument("--fixture", required=True, help="Catalog JSON fixture. Read and left unchanged.")
    parser.add_argument("--out", required=True, help="Directory for the markdown report and JSON sibling.")
    parser.add_argument("--held", default="", help="Held-list JSON to read. Defaults to data/held.json.")
    args = parser.parse_args(argv)
    if _is_remote(args.fixture) or (args.held != "" and _is_remote(args.held)):
        print("Catalog photo count reads local fixtures only.", file=sys.stderr)
        return 2
    fixture = Path(args.fixture)
    out = Path(args.out)
    try:
        _refuse_live_catalog(fixture)
        _refuse_out(out)
        if not fixture.is_file():
            raise ValueError(f"Fixture not found: {fixture}")
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        policy = load_held_policy(Path(args.held) if args.held else None)
        report = flag_catalog(payload, policy)
        markdown_path, _json_path = write_report(report, out)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(_error_text(error, fixture), file=sys.stderr)
        return 2
    print(f"Catalog photo flags: {report.flag_count}")
    print(f"report: {markdown_path}")
    return 1 if report.flag_count else 0


def _products(payload: object) -> list[object]:
    if not isinstance(payload, dict):
        raise ValueError("catalog fixture must be a JSON object")
    schema = payload.get("schema")
    if schema is not None and schema != "catalog.v1":
        raise ValueError("catalog fixture schema must be catalog.v1")
    version = payload.get("version")
    if version is not None and version != 1:
        raise ValueError("catalog fixture version must be 1")
    products = payload.get("products")
    if not isinstance(products, list):
        raise ValueError("catalog fixture needs a products list")
    return products


def _row(item: object, policy: HeldPolicy) -> CatalogPhotoRow:
    if not isinstance(item, dict):
        raise ValueError("catalog product must be an object")
    ma = _ma(item.get("ma"))
    return CatalogPhotoRow(
        ma,
        _photos(item),
        policy.skip_reason(ma) == "held",
        _price(item, ma),
        _status(item, ma),
    )


def _photos(item: dict[str, object]) -> tuple[str, ...]:
    if "images" not in item or item.get("images") is None:
        return ()
    return photo_srcs(item.get("images"))


def _src(item: object) -> str | None:
    if isinstance(item, str):
        text = item.strip()
        return text or None
    if isinstance(item, dict):
        raw = item.get("src")
        if isinstance(raw, str):
            text = raw.strip()
            return text or None
    return None


def _ma(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("catalog product needs a mã")
    code = value.strip().upper()
    if MA_RE.fullmatch(code) is None:
        raise ValueError(f"catalog product has an invalid mã {value!r}")
    return code


def _price(item: dict[str, object], ma: str) -> str | None:
    if "priceUsd" not in item:
        return None
    value = item.get("priceUsd")
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{ma} priceUsd must be a number, a string, or null")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError(f"{ma} priceUsd must be a number, a string, or null")
        return str(value)
    if isinstance(value, str):
        return value
    raise ValueError(f"{ma} priceUsd must be a number, a string, or null")


def _status(item: dict[str, object], ma: str) -> str | None:
    if "status" not in item:
        return None
    value = item.get("status")
    if value is None:
        return None
    if isinstance(value, str):
        return value
    raise ValueError(f"{ma} status must be a string or null")


def _flag_line(row: CatalogPhotoRow) -> str:
    price = "—" if row.price_usd is None else _md(row.price_usd)
    status = "—" if row.status is None else _md(row.status)
    hold = " stays held" if row.held else ""
    return f"- {row.ma} few_photos photos {row.photo_count} price {price} status {status}{hold}"


def _table_row(row: CatalogPhotoRow) -> str:
    price = "—" if row.price_usd is None else _md(row.price_usd)
    status = "—" if row.status is None else _md(row.status)
    flag = "few_photos" if row.thin else "—"
    held = "true" if row.held else "false"
    return f"{row.ma} | {row.photo_count} | {held} | {price} | {status} | {flag}"


def _md(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def _is_remote(value: str) -> bool:
    text = value.strip().casefold()
    return "://" in text or text.startswith("blob:") or text.startswith("http")


def _refuse_live_catalog(path: Path) -> None:
    resolved = path.resolve()
    if resolved in {_LIVE_CATALOG.resolve(), _HELD_PATH.resolve()}:
        raise ValueError("Catalog photo count reads local fixtures only.")


def _refuse_out(path: Path) -> None:
    resolved = path.resolve()
    for root in _BLOCKED_OUT_ROOTS:
        base = root.resolve()
        if resolved == base or base in resolved.parents:
            raise ValueError("catalog photo count does not write catalog or held files")


def _error_text(error: Exception, fixture: Path) -> str:
    if isinstance(error, json.JSONDecodeError):
        return f"{fixture} is not catalog JSON"
    return str(error)


if __name__ == "__main__":
    raise SystemExit(main())
