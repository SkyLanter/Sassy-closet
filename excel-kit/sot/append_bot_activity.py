#!/usr/bin/env python3
"""Append one Bot_Activity row if the sheet exists; otherwise skip with a note.

The ONE SoT book may omit Bot_Activity (lean Official desktop always has it).
Bots draft only — this log is not a Square Save and not a Facebook send.

Times are Pacific. Usage:
  python3 excel-kit/sot/append_bot_activity.py --bot Stock --action draft --summary "..."
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
    BOTS_DRAFT_ONLY,
    MissingMaError,
    require_ma,
)

from sot.workbook import (  # noqa: E402
    WorkbookError,
    add_dry_run_arg,
    add_workbook_path_arg,
    append_mapped_row,
    locate_sot,
    now_pt,
    open_sot,
    optional_sheet,
)


SKIP_NOTE = (
    "note: Bot_Activity sheet not in this workbook — skipped. "
    "The ONE desktop SoT book (Sassy_Closet_SoT.xlsx) may omit it; "
    "the lean Official desktop book always has Bot_Activity. "
    "No row written. Bots still draft only."
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Append Bot_Activity if the sheet exists; else skip with a note.",
    )
    add_workbook_path_arg(parser)
    add_dry_run_arg(parser)
    parser.add_argument("--bot", required=True, help="Stock / Scout / Guide / Quill / Ledger / Mini Boss")
    parser.add_argument("--action", required=True, help="draft / propose / log / skip")
    parser.add_argument("--summary", required=True, help="one-line what happened (no customer secrets)")
    parser.add_argument("--ma", default=None, help="existing mã only, if the draft is about a piece")
    parser.add_argument("--status", default="draft", help="default: draft (never 'saved')")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (default: today PT)")
    parser.add_argument("--time-pt", dest="time_pt", default=None, help="HH:MM PT (default: now PT)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if str(args.status).strip().lower() in {"saved", "save", "posted", "sent", "zelle"}:
        print(
            f"error: Bot_Activity status {args.status!r} is not allowed. {BOTS_DRAFT_ONLY}",
            file=sys.stderr,
        )
        return 2
    ma = None
    if args.ma not in (None, ""):
        try:
            ma = require_ma(args.ma)
        except MissingMaError as exc:
            print(f"error: {exc}", file=sys.stderr)
            print(ASK_STOCK_MA, file=sys.stderr)
            return 2
    try:
        path = locate_sot(args.workbook)
        wb = open_sot(path)
    except WorkbookError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        ws = optional_sheet(wb, "bot_activity")
        if ws is None:
            print(SKIP_NOTE)
            print(f"  workbook: {path}")
            print(f"  sheets: {', '.join(wb.sheetnames)}")
            return 0
        stamp = now_pt()
        fields = {
            "Date": args.date or stamp.date().isoformat(),
            "Time PT": args.time_pt or stamp.strftime("%H:%M"),
            "Bot": args.bot,
            "Ma": ma,
            "Action": args.action,
            "Summary": args.summary,
            "Status": args.status,
            # logical aliases in case a future book uses lowercase headers
            "date": args.date or stamp.date().isoformat(),
            "ma": ma,
            "status": args.status,
            "notes": args.summary,
        }
        dest, written = append_mapped_row(ws, fields)
        print(BOTS_DRAFT_ONLY)
        print(f"Bot_Activity append → {ws.title} row {dest} ({args.bot} / {args.action})")
        print(f"  columns: {', '.join(h for h in written if not h.startswith('(skipped'))}")
        if args.dry_run:
            print("dry-run: not saved")
            return 0
        wb.save(path)
        print(f"saved {path}")
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
