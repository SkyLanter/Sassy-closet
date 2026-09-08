"""Sassy Closet Excel kit — shared headers, mã rules, and workbook helpers.

Desktop Official / Wishlist use MA_LIST, ORDERS, BOT_ACTIVITY, CANDIDATES.
The OneDrive SoT workbook (Sassy_Closet_SoT.xlsx) is the ONE desktop working
copy: Official / Wishlist / Orders / Dashboard (plus Bot_Activity when present).
Square Free remains on-hand inventory SoT; Official Excel is a working copy /
mã index / captions — not a second stock. Never embed images. photo_link last
on Ma_List, Candidates, and SoT Wishlist.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Sequence

# openpyxl is required to *write* Excel. Constant / mã helpers used by
# append_official_row --help must import without it (local bugcheck).
try:
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.styles.numbers import FORMAT_TEXT
    from openpyxl.utils import get_column_letter
    from openpyxl.workbook import Workbook
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.worksheet.worksheet import Worksheet
except ImportError as exc:  # pragma: no cover — --help / smoke imports
    _OPENPYXL_IMPORT_ERROR: ImportError | None = exc
    Alignment = Border = Font = PatternFill = Side = None  # type: ignore[misc, assignment]
    FORMAT_TEXT = "@"
    get_column_letter = None  # type: ignore[assignment]
    Workbook = None  # type: ignore[misc, assignment]
    DataValidation = None  # type: ignore[misc, assignment]
    Worksheet = None  # type: ignore[misc, assignment]
else:
    _OPENPYXL_IMPORT_ERROR = None

# ---------------------------------------------------------------------------
# Shop paths (OneDrive). Kit syncs generated files here; this repo is code.
# ---------------------------------------------------------------------------

ONEDRIVE_SHOP_DIR = "Documents/Sassy Closet"
ONEDRIVE_SOT = f"{ONEDRIVE_SHOP_DIR}/Sassy_Closet_SoT.xlsx"
ONEDRIVE_PHOTOS = f"{ONEDRIVE_SHOP_DIR}/Photos"
ONEDRIVE_FROM_GF = f"{ONEDRIVE_SHOP_DIR}/From GF"
ONEDRIVE_OFFICIAL_DESKTOP = f"{ONEDRIVE_SHOP_DIR}/Sassy_Closet_Official_desktop.xlsx"
ONEDRIVE_WISHLIST_DESKTOP = f"{ONEDRIVE_SHOP_DIR}/Sassy_Closet_Wishlist_desktop.xlsx"
ONEDRIVE_SQUARE = f"{ONEDRIVE_SHOP_DIR}/Square.xlsx"
ONEDRIVE_FINANCE = f"{ONEDRIVE_SHOP_DIR}/Finance.xlsx"

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
    "Bot_Activity",
)

# Optional on the SoT book; required on the lean Official desktop book.
SOT_OPTIONAL_SHEETS: tuple[str, ...] = ("Bot_Activity",)

SHEET_ALIASES: dict[str, tuple[str, ...]] = {
    "official": ("Official", "Ma_List", "Ma List"),
    "wishlist": ("Wishlist", "Candidates"),
    "orders": ("Orders",),
    "bot_activity": ("Bot_Activity", "Bot Activity", "BOT_ACTIVITY"),
    "dashboard": ("Dashboard",),
    "lists": ("Lists",),
    "start_here": ("START HERE", "How_to_use"),
    "on_hand": ("On_Hand",),
    "sold_log": ("Sold_Log",),
    "sales": ("Sales",),
    "fees": ("Fees",),
    "payouts_transfers": ("Payouts_Transfers",),
    "expenses": ("Expenses",),
    "tax_summary": ("Tax_Summary",),
}

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

# photo_link is last. source = Link/source (Taobao / shop URL) — required if available.
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
    "source",
    "notes",
    "photo_link",
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

SOT_WISHLIST_STATUS: tuple[str, ...] = ("candidate", "watching", "skip", "bought")
SOT_ORDER_STATUS: tuple[str, ...] = ORDER_STATUS
SOT_CONDITION: tuple[str, ...] = ("New", "Like new", "Good", "Fair", "As-is")
SOT_CHANNELS: tuple[str, ...] = ("Facebook", "IG", "Walk-in", "Friend", "Other")
SOT_PAY: tuple[str, ...] = ("Zelle", "Cash", "Venmo", "Other", "Unpaid")
SOT_FULFILL: tuple[str, ...] = ("Ship", "Local pickup", "Hold", "TBD")

# Official working-copy status → lean Ma_List status (Square still wins on-hand).
OFFICIAL_TO_MA_LIST_STATUS: dict[str, str] = {
    "Available": "in_stock",
    "Reserved": "held",
    "Sold": "sold",
    "Hold": "held",
    "Damaged": "archived",
    "Donated": "archived",
}

# Header aliases so append scripts work on both SoT and lean desktop books.
HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "ma": ("ma", "mã", "Ma"),
    "item": ("item", "name_vi", "Brand + name", "what_vi"),
    "name_vi": ("name_vi", "what_vi", "item", "Brand + name"),
    "name_en": ("name_en", "what_en"),
    "what_vi": ("what_vi", "name_vi", "Brand + name", "item"),
    "what_en": ("what_en", "name_en"),
    "size": ("size", "sizes_in_stock", "Size Asia + cm"),
    "sizes_in_stock": ("sizes_in_stock", "size", "Size Asia + cm"),
    "color": ("color", "Color", "mau", "Mau"),
    "cost": ("cost", "Cost ¥", "max_cost", "Von Y"),
    "list_price": ("list_price", "price", "Sell $", "Gia ban $", "target_price", "agreed_price"),
    "price": ("price", "list_price", "Sell $", "Gia ban $"),
    "qty_on_hand": ("qty_on_hand", "on_hand", "qty"),
    "on_hand": ("on_hand", "qty_on_hand", "qty"),
    "status": ("status", "Status", "order_status"),
    "order_status": ("order_status", "status", "Status"),
    "notes": ("notes", "Photos / notes", "thread_note"),
    "photo_link": ("photo_link",),
    "source": (
        "source",
        "link",
        "Link (reopen)",
        "Link/source",
        "link_source",
        "Link",
    ),
    "date": ("date", "Date", "date_in", "date_added"),
    "date_in": ("date_in", "date", "Date"),
    "date_added": ("date_added", "date", "Date"),
    "buyer": ("buyer",),
    "channel": ("channel",),
    "pay": ("pay", "pay_method"),
    "pay_method": ("pay_method", "pay"),
    "ship_or_local": ("ship_or_local", "fulfill", "meetup_or_ship"),
    "agreed_price": ("agreed_price", "price", "list_price"),
    "wish_id": ("wish_id", "#"),
    "order_id": ("order_id",),
    "brand": ("brand", "Brand + name"),
    "prefix": ("prefix",),
    "requested_by": ("requested_by",),
    "reason": ("reason",),
    "max_cost": ("max_cost", "cost", "Cost ¥"),
    "target_price": ("target_price", "Sell $", "list_price", "price"),
    "type": ("Type", "type", "category"),
    "category": ("category", "Type", "type"),
    "photo_file": ("photo_file",),
    "square_name": ("square_name",),
    "caption_ready": ("caption_ready",),
    "fb_handle": ("fb_handle",),
    "snapshot": ("snapshot",),
    "qty": ("qty", "qty_on_hand", "on_hand"),
    "ship_fee": ("ship_fee",),
    "net": ("net",),
    "fulfill": ("fulfill", "ship_or_local"),
    "meetup_or_ship": ("meetup_or_ship", "ship_or_local"),
    "thread_note": ("thread_note", "notes"),
    "last_touch": ("last_touch", "last_updated"),
    "last_updated": ("last_updated", "last_touch"),
    "reserved_for": ("reserved_for",),
    "condition": ("condition",),
    "storage": ("storage",),
    "fb_url": ("fb_url",),
    "costs": ("costs", "cost"),
    "buy_date": ("buy_date",),
    "sold_date": ("sold_date",),
    "photo_folder": ("photo_folder",),
    "square_item_name": ("square_item_name", "square_name"),
    "track_on": ("track_on",),
    "gross_usd": ("gross_usd",),
    "ship_usd": ("ship_usd", "ship_fee"),
    "discount_usd": ("discount_usd",),
    "net_usd": ("net_usd", "net"),
    "pay_ref": ("pay_ref",),
    "customer_note": ("customer_note",),
    "square_xlsx_ma": ("square_xlsx_ma",),
    "tax_category": ("tax_category",),
    "fee_type": ("fee_type",),
    "direction": ("direction",),
    "from_account": ("from_account",),
    "to_account": ("to_account",),
    "vendor": ("vendor",),
    "receipt_ref": ("receipt_ref",),
}

# Sheets whose data rows may hold kit-seeded demo stock / fake buyers.
SOT_DATA_SHEETS: dict[str, dict[str, object]] = {
    "Official": {"header_row": 4, "table": "Official"},
    "Wishlist": {"header_row": 4, "table": "Wishlist"},
    "Orders": {"header_row": 4, "table": "Orders"},
    "Bot_Activity": {"header_row": 1, "table": None},
    "Ma_List": {"header_row": 1, "table": None},
    "Candidates": {"header_row": 1, "table": None},
    "Ma List": {"header_row": 1, "table": None},
    "Bot Activity": {"header_row": 1, "table": None},
}

# ---------------------------------------------------------------------------
# Dashboard — morning brief. Boss copies Dashboard!B43 when formulas are live.
# ---------------------------------------------------------------------------

SOT_DASHBOARD_BRIEF_CELL = "B43"
SOT_DASHBOARD_BRIEF_LABEL_CELL = "A43"

# row -> (A-label, B-formula-or-kind). Formulas use Excel table names.
SOT_DASHBOARD_ROWS: dict[int, tuple[str, str]] = {
    5: ("Official pieces (ma rows)", '=COUNTA(Official[ma])'),
    6: ("Available", '=COUNTIF(Official[status],"Available")'),
    7: ("Reserved (Official)", '=COUNTIF(Official[status],"Reserved")'),
    8: ("Sold", '=COUNTIF(Official[status],"Sold")'),
    9: (
        "Other Official (Hold / Damaged / Donated)",
        '=COUNTIF(Official[status],"Hold")+COUNTIF(Official[status],"Damaged")+COUNTIF(Official[status],"Donated")',
    ),
    10: (
        "Qty on hand (Available rows — working copy)",
        '=SUMIF(Official[status],"Available",Official[qty_on_hand])',
    ),
    11: (
        "Wishlist open (candidate + watching)",
        '=COUNTIF(Wishlist[status],"candidate")+COUNTIF(Wishlist[status],"watching")',
    ),
    12: ("Wishlist bought (not Square until Boss Save)", '=COUNTIF(Wishlist[status],"bought")'),
    13: ("Orders Inquiry", '=COUNTIF(Orders[order_status],"Inquiry")'),
    14: ("Orders Reserved", '=COUNTIF(Orders[order_status],"Reserved")'),
    15: ("Orders Paid", '=COUNTIF(Orders[order_status],"Paid")'),
    16: ("Orders Shipped", '=COUNTIF(Orders[order_status],"Shipped")'),
    17: ("Orders Picked up", '=COUNTIF(Orders[order_status],"Picked up")'),
    18: ("Orders Cancelled", '=COUNTIF(Orders[order_status],"Cancelled")'),
    21: ("Next AO (Stock reads — bots do not mint)", '="AO"&TEXT(MAXIFS(Official[ma_num],Official[prefix],"AO")+1,"000")'),
    22: ("Next QU (Stock reads — bots do not mint)", '="QU"&TEXT(MAXIFS(Official[ma_num],Official[prefix],"QU")+1,"000")'),
    23: ("Next VA (Stock reads — bots do not mint)", '="VA"&TEXT(MAXIFS(Official[ma_num],Official[prefix],"VA")+1,"000")'),
    24: ("Next AK (Stock reads — bots do not mint)", '="AK"&TEXT(MAXIFS(Official[ma_num],Official[prefix],"AK")+1,"000")'),
    25: ("Next GI (Stock reads — bots do not mint)", '="GI"&TEXT(MAXIFS(Official[ma_num],Official[prefix],"GI")+1,"000")'),
    26: ("Next PK (Stock reads — bots do not mint)", '="PK"&TEXT(MAXIFS(Official[ma_num],Official[prefix],"PK")+1,"000")'),
    27: ("Next SET (Stock reads — bots do not mint)", '="SET"&TEXT(MAXIFS(Official[ma_num],Official[prefix],"SET")+1,"000")'),
}

SOT_DASHBOARD_BRIEF_FORMULA = (
    '="Morning brief · Official "&TEXT(B5,"0")'
    '&" · Available "&TEXT(B6,"0")'
    '&" · Reserved "&TEXT(B7,"0")'
    '&" · on-hand "&TEXT(B10,"0")'
    '&" · wishlist open "&TEXT(B11,"0")'
    '&" · inquiry "&TEXT(B13,"0")'
    '&" · reserved orders "&TEXT(B14,"0")'
    '&" · paid "&TEXT(B15,"0")'
    '&" · next AO "&B21'
)

SOT_DASHBOARD_BRIEF_NOTE = (
    "If this script prints a formula instead of numbers, Excel has not cached "
    "values yet. Boss: open Sassy_Closet_SoT.xlsx → Dashboard → copy B43 "
    "(morning brief). Paste that text to Mini Boss / Slack. "
    "openpyxl cannot calculate Excel formulas."
)

# ---------------------------------------------------------------------------
# Square Free catalog import (headers only in git — never live stock rows)
# ---------------------------------------------------------------------------

# Stable Square item-library columns Stock maps in Dashboard → Import library.
# Location-specific headers use [Default]; Stock replaces Default with the
# live Square location name from a fresh export before any Boss-approved Save.
SQUARE_IMPORT_HEADERS: tuple[str, ...] = (
    "Token",
    "Item Name",
    "Variation Name",
    "SKU",
    "Description",
    "Category",
    "Reporting Category",
    "SEO Title",
    "SEO Description",
    "Permalink",
    "GTIN",
    "Square Online Item Visibility",
    "Item Type",
    "Weight",
    "Price",
    "Online Sale Price",
    "Archived",
    "Sellable",
    "Stockable",
    "Skip Detail Screen in POS",
    "Option Name 1",
    "Option Value 1",
    "Default Unit Cost",
    "Enabled [Default]",
    "Current Quantity [Default]",
    "New Quantity [Default]",
    "Stock Alert Enabled [Default]",
    "Stock Alert Count [Default]",
)

SQUARE_SKU_IS_MA = (
    "SKU = mã (AO001). Item Name = mã + short name. "
    "Variation Name = Asia size + color (M / đen). "
    "Stockable = Y (Track stock ON). Never put No in New Quantity to kill tracking."
)

# ---------------------------------------------------------------------------
# Square.xlsx + Finance.xlsx (Boss 2026-09-07 ~11:30 PM PT)
# Bought / on-hand team tracker + tax-ready books. Not the website staged list.
# Square Free Dashboard remains inventory SoT. Empty templates — no invented $.
# ---------------------------------------------------------------------------

SQUARE_XLSX_NAME = "Square.xlsx"
FINANCE_XLSX_NAME = "Finance.xlsx"
SQUARE_FINANCE_TEMPLATE_ROWS = 20
SQUARE_FINANCE_TAX_YEAR = 2026

SQUARE_ON_HAND: tuple[str, ...] = (
    "ma",
    "kind",
    "colors",
    "size",
    "qty_on_hand",
    "costs",
    "buy_date",
    "source_link",
    "photo_folder",
    "square_item_name",
    "track_on",
    "status",
    "sold_date",
    "notes",
)

SQUARE_SOLD_LOG: tuple[str, ...] = (
    "sold_date",
    "ma",
    "kind",
    "colors",
    "size",
    "qty",
    "costs",
    "buy_date",
    "source_link",
    "square_item_name",
    "notes",
)

SQUARE_ON_HAND_STATUS: tuple[str, ...] = ("on_hand", "reserved", "sold", "dead")
SQUARE_TRACK_ON: tuple[str, ...] = ("Y", "N")
SQUARE_XLSX_SHEETS: tuple[str, ...] = ("On_Hand", "Sold_Log", "Readme")

SQUARE_XLSX_README_LINES: tuple[str, ...] = (
    "Square.xlsx is the bought / on-hand team tracker. It is NOT the website staged list.",
    "Square Free Dashboard remains on-hand inventory source of truth. Excel is a team tracker.",
    "On_Hand starts empty. Staged website mãs are not bought — do not copy them here.",
    "Sold item: qty_on_hand 0, status=sold, sold_date, and one Finance.xlsx Sales row (square_xlsx_ma).",
    "photo_folder = Documents/Sassy Closet/Photos/{ma}/. Never invent mã. Never Square Save. No cute.",
)

FINANCE_SALES: tuple[str, ...] = (
    "date",
    "ma",
    "description",
    "qty",
    "gross_usd",
    "ship_usd",
    "discount_usd",
    "net_usd",
    "pay_method",
    "pay_ref",
    "customer_note",
    "channel",
    "square_xlsx_ma",
    "tax_category",
    "notes",
)

FINANCE_FEES: tuple[str, ...] = (
    "date",
    "source",
    "fee_type",
    "amount_usd",
    "pay_ref",
    "notes",
)

FINANCE_PAYOUTS: tuple[str, ...] = (
    "date",
    "direction",
    "from_account",
    "to_account",
    "amount_usd",
    "pay_ref",
    "notes",
)

FINANCE_EXPENSES: tuple[str, ...] = (
    "date",
    "vendor",
    "category",
    "amount_usd",
    "pay_method",
    "receipt_ref",
    "tax_category",
    "notes",
)

FINANCE_PAY_METHOD: tuple[str, ...] = (
    "zelle",
    "square",
    "square_online",
    "cash",
    "other",
)
FINANCE_SALES_CHANNEL: tuple[str, ...] = (
    "Facebook",
    "IG",
    "Walk-in",
    "Friend",
    "Square Online",
    "Other",
)
FINANCE_SALES_TAX_CATEGORY: tuple[str, ...] = ("clothing", "shipping", "other")
FINANCE_FEE_SOURCE: tuple[str, ...] = ("square", "square_online", "other")
FINANCE_FEE_TYPE: tuple[str, ...] = ("processing", "payout", "chargeback", "other")
FINANCE_PAYOUT_DIRECTION: tuple[str, ...] = ("in", "out")
FINANCE_EXPENSE_CATEGORY: tuple[str, ...] = (
    "inventory",
    "shipping_supplies",
    "packaging",
    "ads",
    "other",
)
FINANCE_EXPENSE_TAX_CATEGORY: tuple[str, ...] = ("cogs", "opex", "other")

FINANCE_SHEETS: tuple[str, ...] = (
    "Sales",
    "Fees",
    "Payouts_Transfers",
    "Expenses",
    "Tax_Summary",
    "Readme",
)

FINANCE_TAX_SUMMARY_HEADERS: tuple[str, ...] = (
    "metric",
    "ytd",
    *(f"{SQUARE_FINANCE_TAX_YEAR}-{month:02d}" for month in range(1, 13)),
)

FINANCE_TAX_SUMMARY_METRICS: tuple[str, ...] = (
    "gross_usd",
    "ship_usd",
    "discount_usd",
    "net_usd",
    "fees_usd",
    "expenses_usd",
    "net_after_fees_expenses",
    "payouts_transfers_usd",
)

FINANCE_README_LINES: tuple[str, ...] = (
    "Finance.xlsx is tax-ready. Empty templates are correct — do not invent sales or dollar amounts.",
    "Sold item → Square.xlsx On_Hand qty_on_hand 0 + one Sales row. square_xlsx_ma must match that mã.",
    "Tax_Summary is formulas (YTD + monthly 2026). Open in Excel. 0 means no rows yet, not invented revenue.",
    "Payouts_Transfers are cash movement, not income. Fees and Expenses are not sales.",
    "Never invent mã or $. Never Square Save. customer_note is a short note — no PII in git. No cute.",
)

# ---------------------------------------------------------------------------
# Standing copy
# ---------------------------------------------------------------------------

SQUARE_SOT_LINE = (
    "Square Free = on-hand inventory source of truth. "
    "Official Excel (Sassy_Closet_SoT.xlsx) is a working copy / mã index / captions — "
    "NOT a second inventory."
)

SQUARE_SOT_SHORT = (
    "Square Free = on-hand source of truth. "
    "Official Excel = working copy / mã index / captions / photos — "
    "not a second inventory brain. Wishlist ≠ stock. Bots draft only."
)

ASK_STOCK_MA = (
    "Never invent a mã. Ask Stock to read Dashboard next-mã "
    "(MAXIFS on Official[ma_num] + prefix, cells B21:B27) and Boss to assign it. "
    "Do not reuse a Sold mã."
)

STAY_OFF_SQUARE = (
    "Stay off Square until Boss confirms bought/received AND says Save. "
    "Approvals live in Slack #shop-decisions. Scripts never Square Save. "
    "Wishlist / candidates are not on-hand."
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
            r"(?:the )?(?:on-hand )?source of truth"
            r"(?:\s+for(?:\s+the)?(?:\s+on-hand)?\s+inventory)?[.]?"
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
if _OPENPYXL_IMPORT_ERROR is None:
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
else:  # pragma: no cover — constants still import; Excel helpers need openpyxl
    THIN = HEADER_FILL = HEADER_FONT = HEADER_FONT_PLAIN = None
    BODY_FONT = TITLE_FONT = SUB_FONT = SECTION_FONT = LINK_FONT = None

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
# Live site still uses legacy AO001-style (MA_RE). Do not migrate parse_ma
# to A01 here — that is a separate handoff (bc-43bc86e1).
# ---------------------------------------------------------------------------


def _require_openpyxl() -> None:
    """Excel builders need openpyxl; SoT helper constants do not."""
    if _OPENPYXL_IMPORT_ERROR is not None:
        raise ImportError(
            "openpyxl is required for Excel helpers. pip install -r requirements.txt"
        ) from _OPENPYXL_IMPORT_ERROR


def parse_ma(value: object) -> tuple[str, int] | None:
    """Return (prefix, number) for a valid mã; else None. Never invent one.

    Legacy AO001-style until the A01 handoff. Never invent a mã.
    """
    if value is None:
        return None
    text = str(value).strip().upper()
    match = MA_RE.fullmatch(text)
    if not match:
        return None
    return match.group(1), int(match.group(2))


def is_valid_ma(value: object) -> bool:
    return parse_ma(value) is not None


def format_ma(prefix: str, number: int) -> str:
    """Format a Boss/Stock-assigned prefix+number. Does not pick the next code."""
    key = prefix.strip().upper()
    if key not in MA_PREFIX_MEANS:
        raise ValueError(f"unknown mã prefix: {prefix!r}")
    if number < 1 or number > 999:
        raise ValueError(f"mã number out of range: {number}")
    return f"{key}{number:03d}"


class MissingMaError(ValueError):
    """Raised when a script would have to invent a mã — ask Stock instead."""


def require_ma(value: object) -> str:
    """Return a normalized mã or raise MissingMaError (never invent)."""
    parsed = parse_ma(value)
    if parsed is None:
        given = "" if value is None else str(value).strip()
        hint = f" got {given!r}." if given else ""
        raise MissingMaError(f"mã required.{hint} {ASK_STOCK_MA}")
    prefix, number = parsed
    return format_ma(prefix, number)


def normalize_header(name: object) -> str:
    return "" if name is None else str(name).strip().lower()


def resolve_header_key(headers: Sequence[str], logical: str) -> int | None:
    """Column index (0-based) for a logical field, using HEADER_ALIASES."""
    aliases = HEADER_ALIASES.get(logical, (logical,))
    wanted = {normalize_header(a) for a in aliases}
    for i, header in enumerate(headers):
        if normalize_header(header) in wanted:
            return i
    return None


def read_headers(ws: Worksheet, header_row: int) -> list[str]:
    max_col = max(ws.max_column or 1, 1)
    values = [ws.cell(header_row, col).value for col in range(1, max_col + 1)]
    # Trim trailing empty headers.
    while values and (values[-1] is None or str(values[-1]).strip() == ""):
        values.pop()
    return ["" if v is None else str(v).strip() for v in values]


def header_row_for_sheet(title: str) -> int:
    meta = SOT_DATA_SHEETS.get(title, {})
    configured = meta.get("header_row")
    return configured if isinstance(configured, int) else 1


def table_name_for_sheet(title: str) -> str | None:
    meta = SOT_DATA_SHEETS.get(title, {})
    name = meta.get("table")
    return name if isinstance(name, str) and name else None


def resolve_sheet_name(sheetnames: Sequence[str], logical: str) -> str | None:
    aliases = SHEET_ALIASES.get(logical, (logical,))
    wanted = {a.strip().lower() for a in aliases}
    for name in sheetnames:
        if name.strip().lower() in wanted:
            return name
    return None


def photo_folder_for_ma(ma: str) -> str:
    """Folder path only. Requires a real mã — never invent one to name a folder."""
    text = "" if ma is None else str(ma).strip()
    if not text:
        raise ValueError("mã required for photo_folder — never invent one")
    return f"{ONEDRIVE_PHOTOS}/{text}/"


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
    _require_openpyxl()
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
assert_photo_link_last(SOT_WISHLIST, "SOT_WISHLIST")


def photo_link_col_index(headers: Sequence[str]) -> int | None:
    """0-based index of photo_link, if present."""
    return resolve_header_key(headers, "photo_link")


def official_status_or_raise(value: object) -> str:
    text = "" if value is None else str(value).strip()
    for allowed in SOT_OFFICIAL_STATUS:
        if text.lower() == allowed.lower():
            return allowed
    raise ValueError(
        f"Official status must be one of {list(SOT_OFFICIAL_STATUS)}, got {text!r}"
    )


# Keep these names importable from schema through the A01 cutover (bc-43bc86e1)
# and any site↔Wishlist slimming. Re-export is fine; dropping them breaks
# excel-kit/sot/append_official_row.py.
APPEND_OFFICIAL_ROW_EXPORTS: tuple[str, ...] = (
    "ASK_STOCK_MA",
    "MissingMaError",
    "OFFICIAL_TO_MA_LIST_STATUS",
    "SOT_OFFICIAL_STATUS",
    "SQUARE_SOT_SHORT",
    "official_status_or_raise",
    "parse_ma",
    "photo_filename_for_ma",
    "require_ma",
    "resolve_sheet_name",
)


def order_status_or_raise(value: object) -> str:
    text = "" if value is None else str(value).strip()
    for allowed in ORDER_STATUS:
        if text.lower() == allowed.lower():
            return allowed
    raise ValueError(
        f"order status must be one of {list(ORDER_STATUS)}, got {text!r}"
    )


def wishlist_status_or_raise(value: object) -> str:
    text = "" if value is None else str(value).strip()
    for allowed in SOT_WISHLIST_STATUS:
        if text.lower() == allowed.lower():
            return allowed
    raise ValueError(
        f"wishlist status must be one of {list(SOT_WISHLIST_STATUS)}, got {text!r}"
    )


def new_boutique_workbook() -> Workbook:
    _require_openpyxl()
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
