"""Sell-test mã allowlist — never invent beyond this set.

Live shop snapshot target: https://sassy-closet-shop.vercel.app
Kit lane only. Do not fight Origin shop main. Intake is untouched.

HARD STOPS: no Square Save, no Facebook Send, no passwords, no minted mã.
"""

from __future__ import annotations

# Exact public catalog on the sell-test shop as of 2026-09-09.
# Order matches the Featured collection grid (left-to-right, top-to-bottom).
SELL_TEST_MAS: tuple[str, ...] = (
    "A01",
    "S01",
    "P01",
    "P02",
    "P03",
    "P04",
    "P05",
    "K01",
    "H01",
    "A02",
)

# Letter on the mã is the kind. Do not invent Q01 / V01 / D01 / A03 / …
SELL_TEST_KIND: dict[str, str] = {
    "A01": "A",
    "S01": "S",
    "P01": "P",
    "P02": "P",
    "P03": "P",
    "P04": "P",
    "P05": "P",
    "K01": "K",
    "H01": "H",
    "A02": "A",
}

# Public sell-test category slugs (Origin shop). Not intake kinds.
SELL_TEST_CATEGORY_SLUG: dict[str, str] = {
    "A01": "ao",
    "S01": "set",
    "P01": "phu-kien",
    "P02": "phu-kien",
    "P03": "phu-kien",
    "P04": "phu-kien",
    "P05": "phu-kien",
    "K01": "ao-khoac",
    "H01": "toc",
    "A02": "ao",
}

SELL_TEST_SHOP_URL = "https://sassy-closet-shop.vercel.app"
SELL_TEST_ADMIN_URL = f"{SELL_TEST_SHOP_URL}/admin"
SELL_TEST_FB_PAGE = "https://www.facebook.com/profile.php?id=61594312648057"

# Boss-approved USD on sell-test (2026-09-09). None = Hold · Inbox for price.
# Same table as excel-kit/sell_catalog.py on the catalog-export branch.
SELL_TEST_PRICE_USD: dict[str, int | None] = {
    "A01": 25,
    "S01": 28,
    "P01": 5,
    "P02": None,
    "P03": 18,
    "P04": 13,
    "P05": None,
    "K01": 37,
    "H01": 8,
    "A02": 22,
}

HOLD_MAS: frozenset[str] = frozenset(
    ma for ma, price in SELL_TEST_PRICE_USD.items() if price is None
)

# Sibling kit agent (catalog export + CLONE_TO_OFFICIAL) — merge, don't fork.
CATALOG_EXPORT_SIBLING_AGENT = "bc-8eb42dad-c793-4dc5-92b1-c63df4375ad2"
CATALOG_EXPORT_SIBLING_BRANCH = "cursor/catalog-export-clone-official-5ad2"


def normalize_sell_ma(raw: object) -> str:
    return "" if raw is None else str(raw).strip().upper()


def is_allowed_sell_ma(raw: object) -> bool:
    return normalize_sell_ma(raw) in SELL_TEST_MAS


def refuse_invented_ma(raw: object) -> str:
    """Return a known sell-test mã or raise. Never mint a replacement."""
    ma = normalize_sell_ma(raw)
    if ma in SELL_TEST_MAS:
        return ma
    raise ValueError(
        f"mã {ma or '(empty)'} is not on the sell-test allowlist "
        f"({', '.join(SELL_TEST_MAS)}). Never invent mã. ASK STOCK / Boss."
    )
