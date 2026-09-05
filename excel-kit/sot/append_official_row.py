#!/usr/bin/env python3
"""Append one Official row to Sassy_Closet_SoT.xlsx.

Never invents mã. --ma is required; if you do not have one, ask Stock
to read Dashboard next-mã (B21:B27) and Boss to assign it.

Square Free remains on-hand SoT. qty_on_hand here is a working-copy note,
not a second warehouse. photo_link only — no embeds.

Usage:
  python3 excel-kit/sot/append_official_row.py --ma AO001 --name-vi "Áo ..." --size M
  python3 excel-kit/sot/append_official_row.py --help
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_KIT_DIR = Path(__file__).resolve().parent.parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

from schema import (  # noqa: E402
    ASK_STOCK_MA,
    MissingMaError,
    OFFICIAL_TO_MA_LIST_STATUS,
    SOT_OFFICIAL_STATUS,
    SQUARE_SOT_SHORT,
    official_status_or_raise,
    parse_ma,
    photo_filename_for_ma,
    require_ma,
    resolve_sheet_name,
)

from sot.workbook import (  # noqa: E402
    WorkbookError,
    add_dry_run_arg,
    add_workbook_path_arg,
    append_mapped_row,
    find_existing_ma_row,
    locate_sot,
    open_sot,
    today_iso,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Append an Official row. Never invent mã — require --ma or ask Stock.",
    )
    add_workbook_path_arg(parser)
    add_dry_run_arg(parser)
    parser.add_argument(
        "--ma",
        default=None,
        help="Boss/Stock-assigned mã (AO001). Required. Scripts never mint the next code.",
    )
    parser.add_argument("--date-in", default=None, help="ISO date in (default: today PT)")
    parser.add_argument("--brand", default=None)
    parser.add_argument("--name-vi", dest="name_vi", default=None)
    parser.add_argument("--name-en", dest="name_en", default=None)
    parser.add_argument("--item", default=None, help="fallback display name (Ma_List item)")
    parser.add_argument("--category", default=None)
    parser.add_argument("--size", default=None, help="Asia size + cm (never US)")
    parser.add_argument("--color", default=None)
    parser.add_argument("--condition", default=None)
    parser.add_argument("--qty", dest="qty_on_hand", default=None, help="working-copy qty; Square wins")
    parser.add_argument("--cost", default=None)
    parser.add_argument("--list-price", dest="list_price", default=None)
    parser.add_argument(
        "--status",
        default="Available",
        help=f"Official status {list(SOT_OFFICIAL_STATUS)} (default: Available)",
    )
    parser.add_argument("--photo-file", dest="photo_file", default=None)
    parser.add_argument("--photo-link", dest="photo_link", default=None, help="OneDrive share URL")
    parser.add_argument("--fb-url", dest="fb_url", default=None)
    parser.add_argument("--storage", default=None)
    parser.add_argument("--source", default=None, help="buy link / vendor URL if you still have it")
    parser.add_argument("--bust-chest", dest="bust_chest", default=None)
    parser.add_argument("--waist", default=None)
    parser.add_argument("--length", default=None)
    parser.add_argument("--flaws", default=None)
    parser.add_argument("--reserved-for", dest="reserved_for", default=None)
    parser.add_argument("--square-name", dest="square_name", default=None)
    parser.add_argument("--caption-ready", dest="caption_ready", default=None)
    parser.add_argument("--notes", default=None)
    return parser


def build_fields(args: argparse.Namespace) -> dict[str, object]:
    try:
        ma = require_ma(args.ma)
    except MissingMaError as exc:
        raise WorkbookError(str(exc)) from exc
    parsed = parse_ma(ma)
    assert parsed is not None
    prefix, number = parsed
    status = official_status_or_raise(args.status)
    item = args.item or args.name_vi or args.name_en
    photo_file = args.photo_file or photo_filename_for_ma(ma)
    fields: dict[str, object] = {
        "ma": ma,
        "date_in": args.date_in or today_iso(),
        "brand": args.brand,
        "name_vi": args.name_vi or item,
        "name_en": args.name_en,
        "item": item,
        "category": args.category,
        "size": args.size,
        "sizes_in_stock": args.size,
        "color": args.color,
        "condition": args.condition,
        "qty_on_hand": args.qty_on_hand,
        "on_hand": args.qty_on_hand,
        "cost": args.cost,
        "list_price": args.list_price,
        "price": args.list_price,
        "status": status,
        "photo_file": photo_file,
        "photo_link": args.photo_link,
        "fb_url": args.fb_url,
        "storage": args.storage,
        "source": args.source,
        "bust_chest": args.bust_chest,
        "waist": args.waist,
        "length": args.length,
        "flaws": args.flaws,
        "reserved_for": args.reserved_for,
        "square_name": args.square_name or ma,
        "caption_ready": args.caption_ready,
        "notes": args.notes,
        "last_updated": today_iso(),
        "ma_num": number,
        "prefix": prefix,
    }
    return fields


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.ma is None or str(args.ma).strip() == "":
        print(f"error: --ma is required. {ASK_STOCK_MA}", file=sys.stderr)
        return 2
    try:
        fields = build_fields(args)
        ma = str(fields["ma"])
        path = locate_sot(args.workbook)
        wb = open_sot(path)
    except (WorkbookError, ValueError, MissingMaError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        official_name = resolve_sheet_name(wb.sheetnames, "official")
        if official_name is None:
            print(
                "error: no Official / Ma_List sheet. "
                "Open the ONE desktop book Sassy_Closet_SoT.xlsx.",
                file=sys.stderr,
            )
            return 2
        ws = wb[official_name]
        existing = find_existing_ma_row(ws, ma)
        if existing is not None:
            print(
                f"error: {ma} already on {ws.title} row {existing}. "
                "Do not invent a new mã. Update that row or ask Stock.",
                file=sys.stderr,
            )
            return 2
        # Ma_List uses a shorter status set.
        if ws.title in {"Ma_List", "Ma List"}:
            fields["status"] = OFFICIAL_TO_MA_LIST_STATUS.get(
                str(fields["status"]), "in_stock"
            )
        if args.cost not in (None, "") and args.list_price not in (None, ""):
            # Working-copy math only — Ledger / Square remain the money brains.
            try:
                cost = float(args.cost)
                price = float(args.list_price)
                fields["margin_$"] = round(price - cost, 2)
                fields["margin_pct"] = None if price == 0 else round((price - cost) / price, 4)
            except ValueError:
                pass
        dest, written = append_mapped_row(ws, fields)
        print(SQUARE_SOT_SHORT)
        print(f"Official append {ma} → {ws.title} row {dest}")
        print(f"  columns: {', '.join(h for h in written if not h.startswith('(skipped'))}")
        skipped = [h for h in written if h.startswith("(skipped")]
        for note in skipped:
            print(f"  {note}")
        if args.dry_run:
            print("dry-run: not saved")
            wb.close()
            return 0
        wb.save(path)
        print(f"saved {path}")
        print("Square on-hand still wins. Do not Save in Square from this script.")
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
