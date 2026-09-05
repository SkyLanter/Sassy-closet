#!/usr/bin/env python3
"""Append one Orders row to Sassy_Closet_SoT.xlsx.

Statuses (exact): Inquiry | Reserved | Paid | Shipped | Picked up | Cancelled

Facebook inbox is the store. This sheet is the working log — not Square.
If --ma is set it must already be a real mã (never invent one).

Usage:
  python3 excel-kit/sot/append_order_row.py --status Inquiry --ma AO001 --channel Facebook
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
    ORDER_STATUS,
    SQUARE_SOT_SHORT,
    order_status_or_raise,
    require_ma,
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
        description=(
            "Append an Orders row. Status must be "
            "Inquiry|Reserved|Paid|Shipped|Picked up|Cancelled."
        ),
    )
    add_workbook_path_arg(parser)
    add_dry_run_arg(parser)
    parser.add_argument("--order-id", dest="order_id", default=None, help="default: next ORD001")
    parser.add_argument("--date", default=None, help="ISO date (default: today PT)")
    parser.add_argument("--channel", default="Facebook")
    parser.add_argument("--buyer", default=None, help="omit rather than invent a name")
    parser.add_argument("--fb-handle", dest="fb_handle", default=None)
    parser.add_argument("--ma", default=None, help="existing mã only — never invent")
    parser.add_argument("--snapshot", default=None, help="size / color snapshot at inquiry")
    parser.add_argument("--size", default=None)
    parser.add_argument("--color", default=None)
    parser.add_argument("--qty", default="1")
    parser.add_argument("--agreed-price", dest="agreed_price", default=None)
    parser.add_argument("--ship-fee", dest="ship_fee", default=None)
    parser.add_argument(
        "--status",
        "--order-status",
        dest="status",
        required=True,
        help="Inquiry|Reserved|Paid|Shipped|Picked up|Cancelled",
    )
    parser.add_argument("--pay-method", dest="pay_method", default=None)
    parser.add_argument("--fulfill", default=None, help="Ship / Local pickup / Hold / TBD")
    parser.add_argument("--meetup-or-ship", dest="meetup_or_ship", default=None)
    parser.add_argument("--thread-note", dest="thread_note", default=None)
    parser.add_argument("--notes", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        status = order_status_or_raise(args.status)
        ma = None
        if args.ma not in (None, ""):
            try:
                ma = require_ma(args.ma)
            except MissingMaError as exc:
                print(f"error: {exc}", file=sys.stderr)
                print(ASK_STOCK_MA, file=sys.stderr)
                return 2
        path = locate_sot(args.workbook)
        wb = open_sot(path)
        ws = require_sheet(wb, "orders")
        header_row, headers = sheet_headers(ws)
        oid_idx = resolve_header_key(headers, "order_id")
        if args.order_id:
            order_id = str(args.order_id).strip()
        elif oid_idx is not None:
            existing = existing_column_values(ws, header_row, oid_idx)
            order_id = next_numeric_id(existing, prefix="ORD", width=3)
        else:
            order_id = None

        snapshot = args.snapshot or " / ".join(
            part for part in (args.size, args.color) if part
        )
        net = None
        if args.agreed_price not in (None, ""):
            try:
                price = float(args.agreed_price)
                fee = float(args.ship_fee) if args.ship_fee not in (None, "") else 0.0
                net = round(price + fee, 2)
            except ValueError:
                net = None

        fields: dict[str, object] = {
            "order_id": order_id,
            "date": args.date or today_iso(),
            "channel": args.channel,
            "buyer": args.buyer,
            "fb_handle": args.fb_handle,
            "ma": ma,
            "snapshot": snapshot or None,
            "size": args.size,
            "color": args.color,
            "qty": args.qty,
            "agreed_price": args.agreed_price,
            "ship_fee": args.ship_fee,
            "net": net,
            "order_status": status,
            "status": status,
            "pay_method": args.pay_method,
            "pay": args.pay_method,
            "fulfill": args.fulfill,
            "ship_or_local": args.fulfill or args.meetup_or_ship,
            "meetup_or_ship": args.meetup_or_ship or args.fulfill,
            "thread_note": args.thread_note or args.notes,
            "notes": args.notes or args.thread_note,
            "last_touch": today_iso(),
        }
        dest, written = append_mapped_row(ws, fields)
        print(SQUARE_SOT_SHORT)
        print(f"Orders append {order_id or '(no order_id col)'} → {ws.title} row {dest}")
        print(f"  status: {status}")
        if ma:
            print(f"  ma: {ma}")
        print(f"  allowed: {' | '.join(ORDER_STATUS)}")
        print(f"  columns: {', '.join(h for h in written if not h.startswith('(skipped'))}")
        if args.dry_run:
            print("dry-run: not saved")
            return 0
        wb.save(path)
        print(f"saved {path}")
        print("Bots draft only. Owner sends, takes Zelle, taps Square Save.")
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
