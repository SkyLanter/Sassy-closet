#!/usr/bin/env python3
"""Export sassycloset.xlsx All → catalog.v1 JSON (allowlist only; Hold when price empty).

Hard-fails on non-allowlist mãs or invented codes. Hold when sell_usd is
empty or Boss allowlist says Hold. Never writes cost, source_link, or names.

Usage:
  python3 excel-kit/scripts/export_sell_catalog.py \\
    -w "$HOME/OneDrive/Documents/Sassy Closet/sassycloset.xlsx" \\
    --photos-dir "$HOME/OneDrive/Documents/Sassy Closet/Photos" \\
    -o ./out/sell-catalog.v1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_KIT_DIR = Path(__file__).resolve().parent.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

from sell_catalog import (  # noqa: E402
    MISSING_XLSX_STEPS,
    ONEDRIVE_CATALOG,
    CatalogError,
    catalog_envelope,
    dump_catalog_json,
    export_products,
    locate_catalog_xlsx,
    validate_catalog,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "-w",
        "--workbook",
        type=Path,
        default=None,
        help="Path to sassycloset.xlsx (or set SASSY_CATALOG_XLSX)",
    )
    parser.add_argument(
        "--photos-dir",
        type=Path,
        default=None,
        help="OneDrive Photos/ root (Photos/A01/001.jpg). Omit to ship images=[]",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=Path("out/sell-catalog.v1.json"),
        help="Output JSON (default: ./out/sell-catalog.v1.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print JSON to stdout and do not write --out",
    )
    parser.add_argument(
        "--exported-at",
        default=None,
        help="Override exportedAt (ISO-8601). Tests only.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    workbook = locate_catalog_xlsx(args.workbook)
    if workbook is None:
        if args.workbook is not None:
            print(f"error: workbook not found: {args.workbook.expanduser()}", file=sys.stderr)
        print(MISSING_XLSX_STEPS, file=sys.stderr)
        return 2
    photos = args.photos_dir.expanduser() if args.photos_dir else None
    if photos is not None and not photos.is_dir():
        print(f"error: --photos-dir is not a directory: {photos}", file=sys.stderr)
        return 2
    try:
        products, notes = export_products(workbook, photos_dir=photos)
        doc = catalog_envelope(
            products,
            source=ONEDRIVE_CATALOG,
            exported_at=args.exported_at,
        )
        validate_catalog(doc)
    except CatalogError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        for note in notes:
            print(f"# {note}", file=sys.stderr)
        print(f"# dry-run ok · {len(products)} allowlist products · {workbook}", file=sys.stderr)
        return 0
    out = args.out.expanduser()
    dump_catalog_json(doc, out)
    hold = [p["ma"] for p in products if p["status"] == "hold"]
    available = [f"{p['ma']}=${p['priceUsd']}" for p in products if p["status"] == "available"]
    n_images = sum(len(p["images"]) for p in products)
    print(f"OK {out} · catalog.v1 · {len(products)} mãs")
    print(f"  source: {workbook}")
    print(f"  available: {', '.join(available)}")
    print(f"  hold: {', '.join(hold) or '(none)'}")
    print(f"  images: {n_images} (real Photos/ files only; no invented URLs)")
    for note in notes:
        print(f"  note: {note}")
    print("  next: python3 excel-kit/scripts/validate_sell_catalog.py", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
