#!/usr/bin/env python3
"""Build empty Square.xlsx + Finance.xlsx team trackers.

Square.xlsx = bought / on-hand tracker (NOT the website staged list).
Finance.xlsx = tax-ready Sales / Fees / Payouts_Transfers / Expenses / Tax_Summary.
On_Hand and money sheets ship empty — no invented mã or $.
Square Free Dashboard remains inventory SoT. No Square Save.

Usage:
  python3 excel-kit/build_square_finance.py --out-dir ./out
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.styles.numbers import FORMAT_TEXT
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

_KIT_DIR = Path(__file__).resolve().parent
if str(_KIT_DIR) not in sys.path:
    sys.path.insert(0, str(_KIT_DIR))

from schema import (
    FINANCE_EXPENSE_CATEGORY,
    FINANCE_EXPENSE_TAX_CATEGORY,
    FINANCE_EXPENSES,
    FINANCE_FEE_SOURCE,
    FINANCE_FEE_TYPE,
    FINANCE_FEES,
    FINANCE_PAY_METHOD,
    FINANCE_PAYOUT_DIRECTION,
    FINANCE_PAYOUTS,
    FINANCE_README_LINES,
    FINANCE_SALES,
    FINANCE_SALES_CHANNEL,
    FINANCE_SALES_TAX_CATEGORY,
    FINANCE_SHEETS,
    FINANCE_TAX_SUMMARY_HEADERS,
    FINANCE_TAX_SUMMARY_METRICS,
    FINANCE_XLSX_NAME,
    ONEDRIVE_FINANCE,
    ONEDRIVE_PHOTOS,
    ONEDRIVE_SQUARE,
    SQUARE_FINANCE_TAX_YEAR,
    SQUARE_FINANCE_TEMPLATE_ROWS,
    SQUARE_ON_HAND,
    SQUARE_ON_HAND_STATUS,
    SQUARE_SOLD_LOG,
    SQUARE_TRACK_ON,
    SQUARE_XLSX_NAME,
    SQUARE_XLSX_README_LINES,
    SQUARE_XLSX_SHEETS,
    add_list_dropdown,
    header_index,
    strip_workbook_images,
)

PLAIN_FONT = Font(name="Calibri", size=11)
PLAIN_HEADER_FONT = Font(name="Calibri", size=11, bold=True)
RETIRED_FILL_RGB = frozenset({"F7C6D5", "C43B6E", "FFF7FA", "F3E6EE", "FFF3B0"})
CUTE_EMOJI = "🎀♡💗✨"
FORBIDDEN_SHEETS = frozenset(
    {
        "Dashboard",
        "Bot_Activity",
        "Wishlist",
        "START HERE",
        "How_to_use",
        "Candidates",
        "Inventory",
        "Track",
        "All",
    }
)

ON_HAND_WIDTHS = {
    "ma": 10,
    "kind": 8,
    "colors": 16,
    "size": 12,
    "qty_on_hand": 12,
    "costs": 12,
    "buy_date": 12,
    "source_link": 36,
    "photo_folder": 40,
    "square_item_name": 22,
    "track_on": 10,
    "status": 12,
    "sold_date": 12,
    "notes": 24,
}
SOLD_LOG_WIDTHS = {
    "sold_date": 12,
    "ma": 10,
    "kind": 8,
    "colors": 16,
    "size": 12,
    "qty": 8,
    "costs": 12,
    "buy_date": 12,
    "source_link": 36,
    "square_item_name": 22,
    "notes": 24,
}
SALES_WIDTHS = {
    "date": 12,
    "ma": 10,
    "description": 22,
    "qty": 8,
    "gross_usd": 12,
    "ship_usd": 12,
    "discount_usd": 12,
    "net_usd": 12,
    "pay_method": 14,
    "pay_ref": 16,
    "customer_note": 18,
    "channel": 14,
    "square_xlsx_ma": 14,
    "tax_category": 12,
    "notes": 22,
}
FEES_WIDTHS = {
    "date": 12,
    "source": 14,
    "fee_type": 14,
    "amount_usd": 12,
    "pay_ref": 16,
    "notes": 24,
}
PAYOUTS_WIDTHS = {
    "date": 12,
    "direction": 10,
    "from_account": 16,
    "to_account": 16,
    "amount_usd": 12,
    "pay_ref": 16,
    "notes": 24,
}
EXPENSES_WIDTHS = {
    "date": 12,
    "vendor": 18,
    "category": 16,
    "amount_usd": 12,
    "pay_method": 14,
    "receipt_ref": 16,
    "tax_category": 12,
    "notes": 22,
}
MONEY_HEADERS = frozenset(
    {
        "costs",
        "qty_on_hand",
        "qty",
        "gross_usd",
        "ship_usd",
        "discount_usd",
        "net_usd",
        "amount_usd",
    }
)
DATE_HEADERS = frozenset({"date", "buy_date", "sold_date"})


def style_plain_header(ws: Worksheet, headers: tuple[str, ...], last_row: int) -> None:
    for col, name in enumerate(headers, start=1):
        cell = ws.cell(1, col, name)
        cell.font = PLAIN_HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.number_format = FORMAT_TEXT
    ws.row_dimensions[1].height = 18
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{last_row}"


def apply_named_widths(ws: Worksheet, headers: tuple[str, ...], widths: dict[str, float]) -> None:
    for index, name in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(index)].width = widths.get(name, 12)


def write_empty_grid(
    ws: Worksheet,
    title: str,
    headers: tuple[str, ...],
    widths: dict[str, float],
    dropdowns: tuple[tuple[str, tuple[str, ...]], ...] = (),
) -> None:
    ws.title = title
    last = SQUARE_FINANCE_TEMPLATE_ROWS + 1
    for col, name in enumerate(headers, start=1):
        ws.cell(1, col, name)
    for row in range(2, last + 1):
        for col, name in enumerate(headers, start=1):
            cell = ws.cell(row, col, None)
            cell.font = PLAIN_FONT
            cell.alignment = Alignment(vertical="center")
            if name in DATE_HEADERS:
                cell.number_format = "YYYY-MM-DD"
            elif name in MONEY_HEADERS:
                cell.number_format = "0.00"
    style_plain_header(ws, headers, last)
    apply_named_widths(ws, headers, widths)
    for field, choices in dropdowns:
        add_list_dropdown(
            ws,
            header_index(headers, field) + 1,
            choices,
            start_row=2,
            end_row=last,
            prompt=field,
        )


def write_readme(ws: Worksheet, title: str, lines: tuple[str, ...]) -> None:
    ws.title = title
    ws.column_dimensions["A"].width = 96
    for row, line in enumerate(lines, start=1):
        cell = ws.cell(row, 1, line)
        cell.font = PLAIN_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        ws.row_dimensions[row].height = 18


def ytd_sumifs(sheet: str, col: str) -> str:
    return (
        f'=SUMIFS({sheet}!{col}:{col},{sheet}!A:A,">="&DATE(YEAR(TODAY()),1,1),'
        f'{sheet}!A:A,"<="&TODAY())'
    )


def month_sumifs(sheet: str, col: str, year: int, month: int) -> str:
    if month == 12:
        end = f"DATE({year + 1},1,1)"
    else:
        end = f"DATE({year},{month + 1},1)"
    return (
        f'=SUMIFS({sheet}!{col}:{col},{sheet}!A:A,">="&DATE({year},{month},1),'
        f'{sheet}!A:A,"<"&{end})'
    )


def tax_formula(metric: str, year: int, month: int | None) -> str:
    mapping = {
        "gross_usd": ("Sales", "E"),
        "ship_usd": ("Sales", "F"),
        "discount_usd": ("Sales", "G"),
        "net_usd": ("Sales", "H"),
        "fees_usd": ("Fees", "D"),
        "expenses_usd": ("Expenses", "D"),
        "payouts_transfers_usd": ("Payouts_Transfers", "E"),
    }
    if metric not in mapping:
        raise ValueError(f"no SUMIFS source for metric {metric!r}")
    sheet, col = mapping[metric]
    if month is None:
        return ytd_sumifs(sheet, col)
    return month_sumifs(sheet, col, year, month)


def write_tax_summary(ws: Worksheet) -> None:
    ws.title = "Tax_Summary"
    headers = FINANCE_TAX_SUMMARY_HEADERS
    last = 1 + len(FINANCE_TAX_SUMMARY_METRICS)
    for col, name in enumerate(headers, start=1):
        ws.cell(1, col, name)
    year = SQUARE_FINANCE_TAX_YEAR
    net_row = FINANCE_TAX_SUMMARY_METRICS.index("net_after_fees_expenses") + 2
    net_src = FINANCE_TAX_SUMMARY_METRICS.index("net_usd") + 2
    fees_row = FINANCE_TAX_SUMMARY_METRICS.index("fees_usd") + 2
    exp_row = FINANCE_TAX_SUMMARY_METRICS.index("expenses_usd") + 2
    for row, metric in enumerate(FINANCE_TAX_SUMMARY_METRICS, start=2):
        name_cell = ws.cell(row, 1, metric)
        name_cell.font = PLAIN_FONT
        name_cell.number_format = FORMAT_TEXT
        for col in range(2, len(headers) + 1):
            cell = ws.cell(row, col)
            cell.font = PLAIN_FONT
            cell.number_format = "0.00"
            letter = get_column_letter(col)
            if metric == "net_after_fees_expenses":
                cell.value = f"={letter}{net_src}-{letter}{fees_row}-{letter}{exp_row}"
                continue
            month = None if col == 2 else col - 2
            cell.value = tax_formula(metric, year, month)
    note = ws.cell(
        last + 2,
        1,
        "0 means no rows yet. Open in Excel so formulas calculate. "
        "payouts_transfers_usd is cash movement, not income.",
    )
    note.font = PLAIN_FONT
    note.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[last + 2].height = 18
    style_plain_header(ws, headers, last)
    ws.column_dimensions["A"].width = 28
    for col in range(2, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 12
    # net_after row uses B5-style refs — keep them aligned with metric order.
    if net_row != 8 or net_src != 5 or fees_row != 6 or exp_row != 7:
        raise AssertionError("Tax_Summary metric order drifted — fix net_after formula rows")


def new_plain_workbook(title: str) -> Workbook:
    workbook = Workbook()
    workbook.properties.creator = "Sassy Closet excel-kit"
    workbook.properties.title = title
    return workbook


def build_square_workbook() -> Workbook:
    workbook = new_plain_workbook("Sassy Closet Square")
    write_empty_grid(
        workbook.active,
        "On_Hand",
        SQUARE_ON_HAND,
        ON_HAND_WIDTHS,
        (
            ("track_on", SQUARE_TRACK_ON),
            ("status", SQUARE_ON_HAND_STATUS),
        ),
    )
    write_empty_grid(
        workbook.create_sheet("Sold_Log"),
        "Sold_Log",
        SQUARE_SOLD_LOG,
        SOLD_LOG_WIDTHS,
    )
    write_readme(workbook.create_sheet("Readme"), "Readme", SQUARE_XLSX_README_LINES)
    for index, name in enumerate(SQUARE_XLSX_SHEETS):
        workbook.move_sheet(name, offset=index - workbook.sheetnames.index(name))
    strip_workbook_images(workbook)
    return workbook


def build_finance_workbook() -> Workbook:
    workbook = new_plain_workbook("Sassy Closet Finance")
    write_empty_grid(
        workbook.active,
        "Sales",
        FINANCE_SALES,
        SALES_WIDTHS,
        (
            ("pay_method", FINANCE_PAY_METHOD),
            ("channel", FINANCE_SALES_CHANNEL),
            ("tax_category", FINANCE_SALES_TAX_CATEGORY),
        ),
    )
    write_empty_grid(
        workbook.create_sheet("Fees"),
        "Fees",
        FINANCE_FEES,
        FEES_WIDTHS,
        (
            ("source", FINANCE_FEE_SOURCE),
            ("fee_type", FINANCE_FEE_TYPE),
        ),
    )
    write_empty_grid(
        workbook.create_sheet("Payouts_Transfers"),
        "Payouts_Transfers",
        FINANCE_PAYOUTS,
        PAYOUTS_WIDTHS,
        (("direction", FINANCE_PAYOUT_DIRECTION),),
    )
    write_empty_grid(
        workbook.create_sheet("Expenses"),
        "Expenses",
        FINANCE_EXPENSES,
        EXPENSES_WIDTHS,
        (
            ("pay_method", FINANCE_PAY_METHOD),
            ("category", FINANCE_EXPENSE_CATEGORY),
            ("tax_category", FINANCE_EXPENSE_TAX_CATEGORY),
        ),
    )
    write_tax_summary(workbook.create_sheet("Tax_Summary"))
    write_readme(workbook.create_sheet("Readme"), "Readme", FINANCE_README_LINES)
    for index, name in enumerate(FINANCE_SHEETS):
        workbook.move_sheet(name, offset=index - workbook.sheetnames.index(name))
    strip_workbook_images(workbook)
    return workbook


def unzip_test(path: Path) -> None:
    proc = subprocess.run(
        ["unzip", "-t", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(f"unzip -t failed:\n{proc.stdout}\n{proc.stderr}")
    if "No errors detected" not in proc.stdout:
        raise AssertionError(f"unzip -t did not confirm a clean zip:\n{proc.stdout}")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    media = [
        name
        for name in names
        if "/media/" in name.lower() or name.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]
    if media:
        raise AssertionError(f"embedded media in xlsx zip: {media}")


def _fill_rgb(fill: object) -> str | None:
    if fill is None:
        return None
    if getattr(fill, "patternType", None) in (None, "none"):
        return None
    fg = getattr(fill, "fgColor", None)
    if fg is None:
        return None
    rgb = getattr(fg, "rgb", None)
    if not rgb:
        return None
    text = str(rgb).upper()
    if len(text) == 8:
        text = text[2:]
    return text


def nonempty_row_count(ws: Worksheet, headers: tuple[str, ...], header_row: int = 1) -> int:
    count = 0
    for row in range(header_row + 1, (ws.max_row or header_row) + 1):
        values = [ws.cell(row, col).value for col in range(1, len(headers) + 1)]
        if any(value is not None and str(value).strip() != "" for value in values):
            count += 1
    return count


def _assert_plain_sheet(ws: Worksheet) -> None:
    if getattr(ws, "_images", None):
        raise AssertionError(f"{ws.title}: embedded images forbidden")
    if ws.merged_cells.ranges:
        raise AssertionError(f"{ws.title}: merged title art is retired")
    for row in ws.iter_rows(max_row=min(ws.max_row or 1, 40), max_col=ws.max_column or 1):
        for cell in row:
            rgb = _fill_rgb(cell.fill)
            if rgb and rgb in RETIRED_FILL_RGB:
                raise AssertionError(f"{ws.title}!{cell.coordinate} uses retired cute fill {rgb}")
            font = cell.font
            if font and font.size and font.size > 14:
                raise AssertionError(f"{ws.title}!{cell.coordinate} title-art font size {font.size}")


def _assert_readme(ws: Worksheet, needles: tuple[str, ...]) -> None:
    lines = [
        str(ws.cell(row, 1).value).strip()
        for row in range(1, 10)
        if ws.cell(row, 1).value and str(ws.cell(row, 1).value).strip()
    ]
    if not (4 <= len(lines) <= 6):
        raise AssertionError(f"{ws.title} must be 4–6 lines, got {len(lines)}: {lines}")
    blob = " ".join(lines).lower()
    for needle in needles:
        if needle.lower() not in blob:
            raise AssertionError(f"{ws.title} should mention {needle!r}")
    if any(ch in "".join(lines) for ch in CUTE_EMOJI):
        raise AssertionError(f"{ws.title} must stay plain (no cute emoji)")


def _assert_data_sheet(
    ws: Worksheet,
    title: str,
    headers: tuple[str, ...],
    *,
    min_dropdowns: int = 0,
) -> None:
    got = [ws.cell(1, col).value for col in range(1, len(headers) + 1)]
    if got != list(headers):
        raise AssertionError(f"{title} headers drifted: {got}")
    if ws.freeze_panes != "A2":
        raise AssertionError(f"{title} freeze_panes={ws.freeze_panes}")
    if not ws.auto_filter.ref or not str(ws.auto_filter.ref).startswith("A1:"):
        raise AssertionError(f"{title} autofilter={ws.auto_filter.ref}")
    if nonempty_row_count(ws, headers) != 0:
        raise AssertionError(f"{title} must ship empty (no invented mã / $)")
    if min_dropdowns and len(ws.data_validations.dataValidation) < min_dropdowns:
        raise AssertionError(f"{title} missing dropdowns")


def _assert_no_forbidden(workbook: Workbook) -> None:
    extra = FORBIDDEN_SHEETS.intersection(workbook.sheetnames)
    if extra:
        raise AssertionError(f"retired/forbidden sheets present: {sorted(extra)}")


def verify_square_book(path: Path) -> list[str]:
    unzip_test(path)
    workbook = load_workbook(path)
    notes: list[str] = []
    try:
        if list(workbook.sheetnames) != list(SQUARE_XLSX_SHEETS):
            raise AssertionError(f"Square sheets must be {list(SQUARE_XLSX_SHEETS)}, got {workbook.sheetnames}")
        _assert_no_forbidden(workbook)
        _assert_data_sheet(workbook["On_Hand"], "On_Hand", SQUARE_ON_HAND, min_dropdowns=2)
        _assert_data_sheet(workbook["Sold_Log"], "Sold_Log", SQUARE_SOLD_LOG)
        _assert_readme(
            workbook["Readme"],
            ("bought", "staged", "Square Free", "sold", "invent", "Save", "Photos"),
        )
        for sheet in workbook.worksheets:
            _assert_plain_sheet(sheet)
        notes.append("On_Hand empty")
        notes.append("Sold_Log empty")
        notes.append(f"photo_root {ONEDRIVE_PHOTOS}/{{ma}}/")
    finally:
        workbook.close()
    return notes


def verify_finance_book(path: Path) -> list[str]:
    unzip_test(path)
    workbook = load_workbook(path, data_only=False)
    notes: list[str] = []
    try:
        if list(workbook.sheetnames) != list(FINANCE_SHEETS):
            raise AssertionError(f"Finance sheets must be {list(FINANCE_SHEETS)}, got {workbook.sheetnames}")
        _assert_no_forbidden(workbook)
        _assert_data_sheet(workbook["Sales"], "Sales", FINANCE_SALES, min_dropdowns=3)
        _assert_data_sheet(workbook["Fees"], "Fees", FINANCE_FEES, min_dropdowns=2)
        _assert_data_sheet(
            workbook["Payouts_Transfers"],
            "Payouts_Transfers",
            FINANCE_PAYOUTS,
            min_dropdowns=1,
        )
        _assert_data_sheet(workbook["Expenses"], "Expenses", FINANCE_EXPENSES, min_dropdowns=3)
        summary = workbook["Tax_Summary"]
        headers = [summary.cell(1, col).value for col in range(1, len(FINANCE_TAX_SUMMARY_HEADERS) + 1)]
        if headers != list(FINANCE_TAX_SUMMARY_HEADERS):
            raise AssertionError(f"Tax_Summary headers drifted: {headers}")
        if summary.freeze_panes != "A2":
            raise AssertionError(f"Tax_Summary freeze_panes={summary.freeze_panes}")
        metrics = [
            summary.cell(row, 1).value
            for row in range(2, 2 + len(FINANCE_TAX_SUMMARY_METRICS))
        ]
        if metrics != list(FINANCE_TAX_SUMMARY_METRICS):
            raise AssertionError(f"Tax_Summary metrics drifted: {metrics}")
        for row in range(2, 2 + len(FINANCE_TAX_SUMMARY_METRICS)):
            for col in range(2, len(FINANCE_TAX_SUMMARY_HEADERS) + 1):
                value = summary.cell(row, col).value
                if not isinstance(value, str) or not value.startswith("="):
                    raise AssertionError(
                        f"Tax_Summary!{get_column_letter(col)}{row} must be a formula, got {value!r}"
                    )
                if any(token in value.lower() for token in ("ao999", "demo", "sample sale")):
                    raise AssertionError(f"Tax_Summary invented token in {value!r}")
        ytd_gross = summary.cell(2, 2).value
        if not isinstance(ytd_gross, str) or "SUMIFS" not in ytd_gross or "TODAY()" not in ytd_gross:
            raise AssertionError(f"YTD gross must be SUMIFS/TODAY, got {ytd_gross!r}")
        jan_gross = summary.cell(2, 3).value
        if not isinstance(jan_gross, str) or f"DATE({SQUARE_FINANCE_TAX_YEAR},1,1)" not in jan_gross:
            raise AssertionError(f"Jan gross must target {SQUARE_FINANCE_TAX_YEAR}-01, got {jan_gross!r}")
        net_after = summary.cell(8, 2).value
        if net_after != "=B5-B6-B7":
            raise AssertionError(f"YTD net_after must be =B5-B6-B7, got {net_after!r}")
        _assert_readme(
            workbook["Readme"],
            ("tax", "invent", "Sales", "Square.xlsx", "Payouts", "Save"),
        )
        for sheet in workbook.worksheets:
            _assert_plain_sheet(sheet)
        notes.append("Sales/Fees/Payouts/Expenses empty")
        notes.append(f"Tax_Summary YTD + monthly {SQUARE_FINANCE_TAX_YEAR}")
    finally:
        workbook.close()
    return notes


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    square_path = out_dir / SQUARE_XLSX_NAME
    finance_path = out_dir / FINANCE_XLSX_NAME

    square = build_square_workbook()
    square.save(square_path)
    square.close()
    square_notes = verify_square_book(square_path)

    finance = build_finance_workbook()
    finance.save(finance_path)
    finance.close()
    finance_notes = verify_finance_book(finance_path)

    print(f"wrote {square_path}")
    print(f"sha256 {sha256_file(square_path)}")
    print(f"wrote {finance_path}")
    print(f"sha256 {sha256_file(finance_path)}")
    print("On_Hand empty on purpose — staged website mãs are not bought")
    print("Finance templates empty on purpose — no invented sales")
    print(f"sync target: OneDrive {ONEDRIVE_SQUARE}")
    print(f"sync target: OneDrive {ONEDRIVE_FINANCE}")
    for note in square_notes + finance_notes:
        print(f"ok {note}")
    return square_path, finance_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("out"),
        help="folder for Square.xlsx + Finance.xlsx (default: ./out)",
    )
    parser.add_argument(
        "--verify-only",
        nargs=2,
        metavar=("SQUARE", "FINANCE"),
        help="verify two existing books instead of rebuilding",
    )
    args = parser.parse_args(argv)
    if args.verify_only:
        square, finance = (Path(p) for p in args.verify_only)
        for note in verify_square_book(square):
            print(f"ok {note}")
        for note in verify_finance_book(finance):
            print(f"ok {note}")
        print(f"verified {square}")
        print(f"verified {finance}")
        return 0
    build(args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
