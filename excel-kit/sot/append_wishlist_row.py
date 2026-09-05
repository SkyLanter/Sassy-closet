#!/usr/bin/env python3
"""Append one Wishlist / Candidates row to Sassy_Closet_SoT.xlsx.

Wishlist is not stock. Stay off Square until Boss confirms bought + Save.
photo_link is optional. Link/source is required if a URL exists — pass
--source/--link, or --no-source when you truly have no reopen link.

Never invents mã (bought finds get a Boss-assigned mã on Official later).

Usage:
  python3 excel-kit/sot/append_wishlist_row.py --source https://... --what-vi "Váy ..."
  python3 excel-kit/sot/append_wishlist_row.py --no-source --what-en "pink bag"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_KIT_DIR = Path(__file__).resolve().parent.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

from schema import (  # noqa: E402
    CANDIDATE_TYPES,
    SOT_WISHLIST_STATUS,
    SQUARE_SOT_SHORT,
    is_valid_ma,
    wishlist_status_or_raise,
)

from sot.workbook import (  # noqa: E402
    WorkbookError,
    add_dry_run_arg,
    add_workbook_path_arg,
    append_mapped_row,
    existing_column_values,
    locate_sot,
    next_numeric_id,
    open_sot,
    require_sheet,
    resolve_header_key,
    sheet_headers,
    today_iso,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Append a Wishlist row. photo_link optional; Link/source required if available.",
    )
    add_workbook_path_arg(parser)
    add_dry_run_arg(parser)
    parser.add_argument("--wish-id", dest="wish_id", default=None, help="default: next WISH001")
    parser.add_argument("--date-added", dest="date_added", default=None)
    parser.add_argument("--prefix", default=None, help="AO/QU/VA/AK/GI/PK/SET hint — not a mã")
    parser.add_argument("--what-vi", dest="what_vi", default=None)
    parser.add_argument("--what-en", dest="what_en", default=None)
    parser.add_argument("--brand", default=None)
    parser.add_argument("--type", dest="item_type", default=None, help=f"Candidates Type {list(CANDIDATE_TYPES)}")
    parser.add_argument("--size", default=None, help="Asia size + cm")
    parser.add_argument("--color", default=None)
    parser.add_argument("--max-cost", dest="max_cost", default=None)
    parser.add_argument("--target-price", dest="target_price", default=None)
    parser.add_argument("--reason", default=None)
    parser.add_argument("--requested-by", dest="requested_by", default=None)
    parser.add_argument(
        "--status",
        default="candidate",
        help=f"{list(SOT_WISHLIST_STATUS)} (default: candidate)",
    )
    parser.add_argument("--source", "--link", dest="source", default=None, help="Taobao / shop URL")
    parser.add_argument(
        "--no-source",
        action="store_true",
        help="confirm no Link/source exists (do not silently drop a URL)",
    )
    parser.add_argument("--photo-link", dest="photo_link", default=None, help="optional OneDrive share URL")
    parser.add_argument("--notes", default=None)
    parser.add_argument("--ma", default=None, help="forbidden on wishlist — bought pieces go Official")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.ma and is_valid_ma(args.ma):
        print(
            "error: do not put a live mã on Wishlist. "
            "Bought finds get a Boss-assigned mã on Official, then Square Save.",
            file=sys.stderr,
        )
        return 2
    if not args.source and not args.no_source:
        print(
            "error: Link/source required if available. "
            "Pass --source URL (Taobao / shop) or --no-source if you truly have no link.",
            file=sys.stderr,
        )
        return 2
    try:
        status = wishlist_status_or_raise(args.status)
        path = locate_sot(args.workbook)
        wb = open_sot(path)
        ws = require_sheet(wb, "wishlist")
        header_row, headers = sheet_headers(ws)
        wish_idx = resolve_header_key(headers, "wish_id")
        if args.wish_id:
            wish_id = str(args.wish_id).strip()
        elif wish_idx is not None:
            existing = existing_column_values(ws, header_row, wish_idx)
            # Candidates uses "#" — keep a numeric-looking id.
            if ws.title == "Candidates":
                wish_id = next_numeric_id(existing, prefix="", width=1) if existing else "1"
            else:
                wish_id = next_numeric_id(existing, prefix="WISH", width=3)
        else:
            wish_id = next_numeric_id([], prefix="WISH", width=3)

        name = args.what_vi or args.what_en or args.brand
        fields: dict[str, object] = {
            "wish_id": wish_id,
            "date_added": args.date_added or today_iso(),
            "date": args.date_added or today_iso(),
            "prefix": args.prefix,
            "what_vi": args.what_vi or name,
            "what_en": args.what_en,
            "item": name,
            "brand": args.brand or name,
            "type": args.item_type,
            "category": args.item_type,
            "size": args.size,
            "color": args.color,
            "max_cost": args.max_cost,
            "cost": args.max_cost,
            "target_price": args.target_price,
            "price": args.target_price,
            "reason": args.reason,
            "requested_by": args.requested_by,
            "status": status,
            "source": args.source,
            "photo_link": args.photo_link,
            "notes": args.notes,
        }
        dest, written = append_mapped_row(ws, fields)
        print(SQUARE_SOT_SHORT)
        print(f"Wishlist append {wish_id} → {ws.title} row {dest} ({status})")
        if args.source:
            print(f"  source: {args.source}")
        else:
            print("  source: none (--no-source)")
        if args.photo_link:
            print(f"  photo_link: {args.photo_link}")
        else:
            print("  photo_link: omitted (optional)")
        print(f"  columns: {', '.join(h for h in written if not h.startswith('(skipped'))}")
        if args.dry_run:
            print("dry-run: not saved")
            return 0
        wb.save(path)
        print(f"saved {path}")
        print("Stay off Square until Boss confirms bought and says Save.")
        return 0
    except (WorkbookError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    finally:
        if "wb" in locals():
            try:
                wb.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
