"""Sassy Closet Excel kit — shared headers, mã rules, and workbook helpers.

Desktop Official / Wishlist use MA_LIST, ORDERS, BOT_ACTIVITY, CANDIDATES.
The OneDrive SoT workbook (Sassy_Closet_SoT.xlsx) uses the richer Official /
Wishlist / Orders column sets. Square Free remains on-hand inventory SoT;
these sheets are a working copy / mã index / captions — not a second stock.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Sequence

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.styles.numbers import FORMAT_TEXT
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.worksheet import Worksheet

# ---------------------------------------------------------------------------
# Shop paths (OneDrive). Kit syncs generated files here; this repo is code.
# ---------------------------------------------------------------------------

ONEDRIVE_SHOP_DIR = "Documents/Sassy Closet"
ONEDRIVE_SOT = f"{ONEDRIVE_SHOP_DIR}/Sassy_Closet_SoT.xlsx"
ONEDRIVE_PHOTOS = f"{ONEDRIVE_SHOP_DIR}/Photos"
ONEDRIVE_OFFICIAL_DESKTOP = f"{ONEDRIVE_SHOP_DIR}/Sassy_Closet_Official_desktop.xlsx"
ONEDRIVE_WISHLIST_DESKTOP = f"{ONEDRIVE_SHOP_DIR}/Sassy_Closet_Wishlist_desktop.xlsx"

# ---------------------------------------------------------------------------
# Mã
# ---------------------------------------------------------------------------

MA_PREFIXES: tuple[str, ...] = ("AO", "QU", "VA", "AK", "GI", "PK", "SET")
MA_PREFIX_MEANS: dict[str, str] = {
    "AO": "Áo / tops",
    "QU": "Quần / bottoms",
    "VA": "Váy / dresses",
    "AK": "Áo khoác / jackets",
    "GI": "Giày / shoes",
    "PK": "Phụ kiện / accessories",
    "SET": "Set",
}
MA_RE = re.compile(r"^(AO|QU|VA|AK|GI|PK|SET)(\d{3})$")

# ---------------------------------------------------------------------------
# Desktop kit headers — photo_link is last on Ma_List and Candidates
# ---------------------------------------------------------------------------

MA_LIST: tuple[str, ...] = (
    "ma",
    "item",
    "sizes_in_stock",
    "color",
    "cost",
    "price",
    "on_hand",
    "status",
    "notes",
    "photo_link",
)

ORDERS: tuple[str, ...] = (
    "date",
    "buyer",
    "ma",
    "size",
    "color",
    "channel",
    "status",
    "pay",
    "ship_or_local",
    "agreed_price",
    "notes",
)

BOT_ACTIVITY: tuple[str, ...] = (
    "Date",
    "Time PT",
    "Bot",
    "Ma",
    "Action",
    "Summary",
    "Status",
)

CANDIDATES: tuple[str, ...] = (
    "#",
    "Date",
    "Status",
    "Type",
    "Brand + name",
    "Size Asia + cm",
    "Color",
    "Cost ¥",
    "Sell $",
    "Link (reopen)",
    "Photos / notes",
    "photo_link",
)

MA_LIST_STATUS: tuple[str, ...] = ("in_stock", "held", "sold", "archived")
ORDER_STATUS: tuple[str, ...] = (
    "Inquiry",
    "Reserved",
    "Paid",
    "Shipped",
    "Picked up",
    "Cancelled",
)
CANDIDATE_STATUS: tuple[str, ...] = ("candidate", "watching", "skip", "bought")
CANDIDATE_TYPES: tuple[str, ...] = (
    "Dress",
    "Top",
    "Skirt",
    "Bag",
    "Shoes",
    "Other",
    "SET",
)

# ---------------------------------------------------------------------------
# SoT workbook (pink stock book) — used by clean_sot_demo.py
# ---------------------------------------------------------------------------

SOT_SHEETS: tuple[str, ...] = (
    "START HERE",
    "TOMORROW",
    "BOT PROMPT",
    "Lists",
    "Official",
    "Wishlist",
    "Orders",
    "Dashboard",
)

SOT_OFFICIAL: tuple[str, ...] = (
    "ma",
    "date_in",
    "brand",
    "name_vi",
    "name_en",
    "category",
    "size",
    "color",
    "condition",
    "qty_on_hand",
    "cost",
    "list_price",
    "margin_$",
    "margin_pct",
    "status",
    "photo_file",
    "photo_link",
    "fb_url",
    "storage",
    "source",
    "bust_chest",
    "waist",
    "length",
    "flaws",
    "reserved_for",
    "days_in",
    "square_name",
    "caption_ready",
    "notes",
    "last_updated",
    "ma_num",
    "prefix",
)

SOT_WISHLIST: tuple[str, ...] = (
    "wish_id",
    "date_added",
    "prefix",
    "what_vi",
    "what_en",
    "size",
    "color",
    "max_cost",
    "target_price",
    "reason",
    "requested_by",
    "status",
    "photo_link",
    "notes",
)

SOT_ORDERS: tuple[str, ...] = (
    "order_id",
    "date",
    "channel",
    "buyer",
    "fb_handle",
    "ma",
    "snapshot",
    "qty",
    "agreed_price",
    "ship_fee",
    "net",
    "order_status",
    "pay_method",
    "fulfill",
    "meetup_or_ship",
    "thread_note",
    "last_touch",
)

SOT_OFFICIAL_STATUS: tuple[str, ...] = (
    "Available",
    "Reserved",
    "Sold",
    "Hold",
    "Damaged",
    "Donated",
)

# Sheets whose data rows may hold kit-seeded demo stock / fake buyers.
SOT_DATA_SHEETS: dict[str, dict[str, object]] = {
    "Official": {"header_row": 4, "table": "Official"},
    "Wishlist": {"header_row": 4, "table": "Wishlist"},
    "Orders": {"header_row": 4, "table": "Orders"},
    "Ma_List": {"header_row": 1, "table": None},
    "Candidates": {"header_row": 1, "table": None},
    "Ma List": {"header_row": 1, "table": None},
}

# ---------------------------------------------------------------------------
# Standing copy
# ---------------------------------------------------------------------------

SQUARE_SOT_LINE = (
    "Square Free = on-hand inventory source of truth. "
    "Desktop SoT Excel is a working copy / mã index / captions — "
    "NOT a second inventory."
)

SQUARE_SOT_SHORT = (
    "Square Free = on-hand source of truth. "
    "Official Excel = working copy / mã index / captions / photos — "
    "not a second inventory brain. Wishlist ≠ stock. Bots draft only."
)

BOTS_DRAFT_ONLY = (
    "Bots draft only. Owner posts on Facebook, sends the message, "
    "takes Zelle, and taps Save in Square."
)

PHOTO_RULE = (
    f"Photos live in {ONEDRIVE_PHOTOS}/ named #001.jpg / AO001.jpg. "
    "Excel stores photo_link only — never embed images."
)

# Outdated phrases → current shop law. Applied cell-by-cell; skip cells
# that already state Square Free is on-hand SoT.
SQUARE_WORDING_PATCHES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"(?i)\bgoogle (?:drive|sheets) is (?:the )?source of truth\b"
        ),
        SQUARE_SOT_LINE,
    ),
    (
        re.compile(
            r"(?i)\b(?:this )?(?:excel|workbook|spreadsheet|sheet) is "
            r"(?:the )?(?:on-hand )?source of truth\b"
        ),
        SQUARE_SOT_LINE,
    ),
    (
        re.compile(r"(?i)\bexcel is (?:the )?inventory\b"),
        (
            "Square Free is on-hand inventory; "
            "Excel is a working copy / mã index / captions"
        ),
    ),
    (
        re.compile(r"(?i)\blive inventory (?:lives|is) in (?:this )?excel\b"),
        SQUARE_SOT_LINE,
    ),
)

# Tokens that mark kit-seeded demo / example rows (never real stock).
DEMO_ROW_TOKENS: tuple[str, ...] = (
    "demo",
    "sample",
    "example",
    "placeholder",
    "lorem",
    "fake stock",
    "test buyer",
    "demo buyer",
    "ao999",
    "qu999",
    "va999",
    "ak999",
    "gi999",
    "pk999",
    "set999",
    "ao000",
)

# ---------------------------------------------------------------------------
# Pink boutique theme (matches desktop books already on OneDrive)
# ---------------------------------------------------------------------------

ROSE = "C43B6E"
BLUSH = "F7C6D5"
BLUSH_ROW = "FFF7FA"
SECTION = "F3E6EE"
INK = "4A3038"
MUTED = "8B6B75"
YELLOW_INPUT = "FFF3B0"
THIN = Border(
    left=Side(style="thin", color="E8C4D0"),
    right=Side(style="thin", color="E8C4D0"),
    top=Side(style="thin", color="E8C4D0"),
    bottom=Side(style="thin", color="E8C4D0"),
)
HEADER_FILL = PatternFill("solid", fgColor=BLUSH)
HEADER_FONT = Font(name="Calibri", size=10, bold=True, color=INK, underline="single")
HEADER_FONT_PLAIN = Font(name="Calibri", size=10, bold=True, color=INK)
BODY_FONT = Font(name="Calibri", size=10, color=INK)
TITLE_FONT = Font(name="Calibri", size=17, bold=True, color=INK)
SUB_FONT = Font(name="Calibri", size=11, color=MUTED)
SECTION_FONT = Font(name="Calibri", size=11, bold=True, color=INK)
LINK_FONT = Font(name="Calibri", size=10, color="2B6CB0", underline="single")

MA_LIST_WIDTHS = {
    "A": 10,
    "B": 22,
    "C": 16,
    "D": 12,
    "E": 10,
    "F": 10,
    "G": 10,
    "H": 12,
    "I": 22,
    "J": 36,
}
ORDERS_WIDTHS = {
    "A": 12,
    "B": 16,
    "C": 10,
    "D": 12,
    "E": 12,
    "F": 12,
    "G": 14,
    "H": 12,
    "I": 14,
    "J": 14,
    "K": 22,
}
BOT_ACTIVITY_WIDTHS = {
    "A": 12,
    "B": 12,
    "C": 12,
    "D": 10,
    "E": 16,
    "F": 28,
    "G": 12,
}
CANDIDATES_WIDTHS = {
    "A": 6,
    "B": 12,
    "C": 12,
    "D": 12,
    "E": 22,
    "F": 16,
    "G": 12,
    "H": 10,
    "I": 10,
    "J": 36,
    "K": 22,
    "L": 36,
}

# ---------------------------------------------------------------------------
# Mã / photo helpers
# ---------------------------------------------------------------------------


def parse_ma(value: object) -> tuple[str, int] | None:
    """Return (prefix, number) for a valid mã; else None. Never invent one."""
    if value is None:
        return None
    text = str(value).strip().upper()
    match = MA_RE.fullmatch(text)
    if not match:
        return None
    return match.group(1), int(match.group(2))


def is_valid_ma(value: object) -> bool:
    return parse_ma(value) is not None


def photo_filename_for_ma(ma: str, extra: int | None = None) -> str:
    parsed = parse_ma(ma)
    if parsed is None:
        raise ValueError(f"not a valid mã: {ma!r} — never invent stock")
    prefix, num = parsed
    stem = f"{prefix}{num:03d}"
    return f"{stem}_{extra}.jpg" if extra else f"{stem}.jpg"


def photo_filename_for_wish(number: int, extra: int | None = None) -> str:
    if number < 1 or number > 999:
        raise ValueError("wishlist photo numbers are #001–#999")
    stem = f"#{number:03d}"
    return f"{stem}_{extra}.jpg" if extra else f"{stem}.jpg"


def looks_like_demo_row(values: Iterable[object]) -> bool:
    """True when a data row is kit-seeded demo, not a real piece or buyer."""
    blob = " ".join("" if v is None else str(v) for v in values).strip().lower()
    if not blob:
        return False
    return any(token in blob for token in DEMO_ROW_TOKENS)


def is_photo_link_header(name: str) -> bool:
    return name.strip().lower() == "photo_link"


# ---------------------------------------------------------------------------
# openpyxl helpers — freeze, filter, dropdowns, no embeds
# ---------------------------------------------------------------------------


def style_header_row(
    ws: Worksheet,
    headers: Sequence[str],
    row: int = 1,
    *,
    underline_photo_link: bool = True,
) -> None:
    for col, name in enumerate(headers, start=1):
        cell = ws.cell(row, col, name)
        font = HEADER_FONT if (underline_photo_link and is_photo_link_header(name)) else HEADER_FONT_PLAIN
        cell.font = font
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN
        cell.number_format = FORMAT_TEXT
    ws.row_dimensions[row].height = 22
    ws.auto_filter.ref = f"A{row}:{get_column_letter(len(headers))}{row}"
    ws.freeze_panes = f"A{row + 1}"


def apply_widths(ws: Worksheet, widths: dict[str, float]) -> None:
    for letter, width in widths.items():
        ws.column_dimensions[letter].width = width


def paint_tab(ws: Worksheet, color: str = BLUSH) -> None:
    ws.sheet_properties.tabColor = color


def add_list_dropdown(
    ws: Worksheet,
    col: int,
    choices: Sequence[str],
    *,
    start_row: int = 2,
    end_row: int = 200,
    prompt: str | None = None,
) -> DataValidation:
    letter = get_column_letter(col)
    # Quoted comma list — no hidden Lists sheet needed for the lean desktop books.
    formula = '"' + ",".join(choices) + '"'
    dv = DataValidation(
        type="list",
        formula1=formula,
        allow_blank=True,
        showDropDown=False,
        showErrorMessage=True,
        error="Pick a value from the list.",
        errorTitle="status",
        prompt=prompt,
        showInputMessage=bool(prompt),
    )
    dv.add(f"{letter}{start_row}:{letter}{end_row}")
    ws.add_data_validation(dv)
    return dv


def strip_embedded_images(ws: Worksheet) -> int:
    """Remove worksheet drawings. Excel stores photo_link only."""
    images = getattr(ws, "_images", None)
    if not images:
        return 0
    count = len(images)
    images.clear()
    return count


def strip_workbook_images(wb: Workbook) -> int:
    return sum(strip_embedded_images(ws) for ws in wb.worksheets)


def apply_photo_link_style(cell, value: object) -> None:
    """Store a URL as text + hyperlink. Never add a picture."""
    if value is None or str(value).strip() == "":
        cell.value = None
        cell.hyperlink = None
        return
    text = str(value).strip()
    cell.value = text
    if text.startswith(("http://", "https://")):
        cell.hyperlink = text
        cell.font = LINK_FONT
    else:
        # OneDrive path or file name — keep as text, owner pastes the share URL.
        cell.font = BODY_FONT


def header_index(headers: Sequence[str], name: str) -> int:
    needle = name.strip().lower()
    for i, header in enumerate(headers):
        if header.strip().lower() == needle:
            return i
    raise KeyError(name)


def assert_photo_link_last(headers: Sequence[str], sheet_label: str) -> None:
    if not headers or headers[-1] != "photo_link":
        raise AssertionError(f"{sheet_label}: photo_link must be the last column, got {headers!r}")


assert_photo_link_last(MA_LIST, "MA_LIST")
assert_photo_link_last(CANDIDATES, "CANDIDATES")


def new_boutique_workbook() -> Workbook:
    wb = Workbook()
    wb.properties.creator = "Sassy Closet excel-kit"
    return wb


def write_how_to_use(ws: Worksheet, lines: Sequence[tuple[str, str]]) -> None:
    """lines: (role, text) where role is title|sub|rule|section|body|divider|foot."""
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 72
    ws.column_dimensions["B"].width = 28
    fills = {
        "title": PatternFill("solid", fgColor=BLUSH),
        "sub": PatternFill("solid", fgColor=BLUSH_ROW),
        "rule": PatternFill("solid", fgColor=BLUSH_ROW),
        "section": PatternFill("solid", fgColor=SECTION),
        "body": PatternFill("solid", fgColor=BLUSH_ROW),
        "divider": PatternFill("solid", fgColor=BLUSH_ROW),
        "foot": PatternFill("solid", fgColor=BLUSH),
    }
    fonts = {
        "title": TITLE_FONT,
        "sub": SUB_FONT,
        "rule": BODY_FONT,
        "section": SECTION_FONT,
        "body": BODY_FONT,
        "divider": Font(name="Calibri", size=10, color=MUTED),
        "foot": Font(name="Calibri", size=10, italic=True, color=INK),
    }
    for row, (role, text) in enumerate(lines, start=1):
        cell = ws.cell(row, 1, text)
        cell.font = fonts[role]
        cell.fill = fills[role]
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        ws.row_dimensions[row].height = 22 if role != "title" else 26
    paint_tab(ws)


def default_out_dir() -> Path:
    return Path.cwd() / "out"
