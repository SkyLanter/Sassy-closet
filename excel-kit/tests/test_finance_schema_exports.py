"""FINANCE_* / SQUARE book exports cannot vanish again."""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import pytest

import schema
from schema import (
    FINANCE_BOOK_EXPORTS,
    FINANCE_CHANNEL,
    FINANCE_EXPENSE_CATEGORY,
    FINANCE_FEE_TYPE,
    FINANCE_FEES,
    FINANCE_PAY_METHOD,
    FINANCE_PAYOUTS,
    FINANCE_SALES,
    FINANCE_SHEETS,
    FINANCE_TAX_CATEGORY,
    FINANCE_TAX_SUMMARY_METRICS,
    FINANCE_TAX_SUMMARY_ROWS,
    LEGACY_SAN_JOSE_SALES_TAX_RATE_NOT_CURRENT,
    SAN_JOSE_SALES_TAX_RATE,
    SAN_JOSE_SALES_TAX_RATE_DISPLAY,
    SQUARE_ON_HAND,
    SQUARE_SOLD_LOG,
    excel_column_letter,
    finance_header_letter,
    finance_net_usd_formula,
    header_index,
    san_jose_sales_tax_usd,
)

KIT = Path(__file__).resolve().parents[1]
BUILDER = KIT / "build_square_finance.py"


def _schema_names_imported_by(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "schema":
            names.extend(alias.name for alias in node.names)
    return names


def test_finance_book_exports_exist() -> None:
    missing = [name for name in FINANCE_BOOK_EXPORTS if not hasattr(schema, name)]
    assert missing == [], f"schema.py dropped finance book exports: {missing}"


def test_builder_import_symbols_exist() -> None:
    imported = _schema_names_imported_by(BUILDER)
    assert imported, "build_square_finance.py must import schema symbols"
    missing = [name for name in imported if not hasattr(schema, name)]
    assert missing == [], f"build_square_finance.py ImportError risk: {missing}"


def test_deleting_finance_channel_would_fail_this_test() -> None:
    # Pin the historical ImportError: schema.py is missing FINANCE_CHANNEL.
    assert hasattr(schema, "FINANCE_CHANNEL")
    assert schema.FINANCE_CHANNEL == ("facebook", "meetup", "website", "other")
    assert "FINANCE_CHANNEL" in FINANCE_BOOK_EXPORTS
    assert "FINANCE_CHANNEL" in _schema_names_imported_by(BUILDER)


@pytest.mark.parametrize(
    "name",
    [
        "FINANCE_SALES",
        "FINANCE_FEES",
        "FINANCE_PAYOUTS",
        "FINANCE_EXPENSES",
        "FINANCE_SHEETS",
        "FINANCE_TAX_SUMMARY_ROWS",
        "FINANCE_CHANNEL",
        "FINANCE_TAX_CATEGORY",
        "SAN_JOSE_SALES_TAX_RATE",
    ],
)
def test_named_finance_symbol_present(name: str) -> None:
    assert hasattr(schema, name), name


def test_headers_match_contract() -> None:
    assert FINANCE_SALES[:14] == (
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
    )
    for extra in ("cogs_usd", "taxable_base_usd", "sales_tax_rate", "sales_tax_usd", "notes"):
        assert extra in FINANCE_SALES
    assert FINANCE_PAY_METHOD == ("zelle", "square", "square_online", "cash", "other")
    assert FINANCE_CHANNEL == ("facebook", "meetup", "website", "other")
    assert FINANCE_TAX_CATEGORY == ("product_sale", "shipping", "other")
    assert FINANCE_FEES == (
        "date",
        "source",
        "amount_usd",
        "fee_type",
        "related_sale_ref",
        "notes",
    )
    assert FINANCE_FEE_TYPE == ("square_processing", "shipping_label", "ads", "other")
    assert FINANCE_PAYOUTS == (
        "date",
        "from_method",
        "to_account_note",
        "amount_usd",
        "confirmation",
        "notes",
    )
    assert FINANCE_EXPENSE_CATEGORY == (
        "inventory_cogs",
        "shipping_supplies",
        "packaging",
        "software",
        "ads",
        "other",
    )
    assert FINANCE_SHEETS == (
        "Sales",
        "Fees",
        "Payouts_Transfers",
        "Expenses",
        "Tax_Summary",
        "Readme",
    )
    assert SQUARE_ON_HAND[0] == "ma"
    assert SQUARE_SOLD_LOG == ("ma", "sold_date", "qty", "finance_ref", "notes")


def test_sales_column_letters_stable_for_tax_summary() -> None:
    assert finance_header_letter(FINANCE_SALES, "gross_usd") == "E"
    assert finance_header_letter(FINANCE_SALES, "ship_usd") == "F"
    assert finance_header_letter(FINANCE_SALES, "discount_usd") == "G"
    assert finance_header_letter(FINANCE_SALES, "net_usd") == "H"
    assert finance_header_letter(FINANCE_SALES, "cogs_usd") == "O"
    assert finance_header_letter(FINANCE_SALES, "taxable_base_usd") == "P"
    assert finance_header_letter(FINANCE_SALES, "sales_tax_usd") == "R"
    assert finance_header_letter(FINANCE_FEES, "amount_usd") == "C"
    assert finance_header_letter(schema.FINANCE_EXPENSES, "amount_usd") == "D"
    assert excel_column_letter(header_index(FINANCE_SALES, "gross_usd") + 1) == "E"


def test_tax_summary_ytd_rows_use_stable_letters() -> None:
    labels = [label for label, _formula in FINANCE_TAX_SUMMARY_ROWS[1:]]
    metric_labels = [label for label, _kind in FINANCE_TAX_SUMMARY_METRICS]
    assert labels == metric_labels
    formulas = dict(FINANCE_TAX_SUMMARY_ROWS)
    assert "Sales!E2:E1001" in formulas["Gross sales (USD)"]
    assert "Sales!F2:F1001" in formulas["Shipping income (USD)"]
    assert "Sales!R2:R1001" in formulas["Sales tax collected (USD, liability — not income)"]
    assert "Fees!C2:C1001" in formulas["Fees (USD)"]
    assert "Sales!O2:O1001" in formulas["COGS (Sales cogs_usd — copy Square.xlsx cost_usd when sold)"]
    assert "Expenses!D2:D1001" in formulas["Expenses (USD)"]


def test_san_jose_rate_is_ten_percent_not_legacy() -> None:
    assert SAN_JOSE_SALES_TAX_RATE == Decimal("0.10")
    assert SAN_JOSE_SALES_TAX_RATE_DISPLAY == "10.000%"
    assert LEGACY_SAN_JOSE_SALES_TAX_RATE_NOT_CURRENT == Decimal("0.09375")
    assert SAN_JOSE_SALES_TAX_RATE != LEGACY_SAN_JOSE_SALES_TAX_RATE_NOT_CURRENT
    assert san_jose_sales_tax_usd(120) == Decimal("12.00")
    assert san_jose_sales_tax_usd(120) != (Decimal("120") * LEGACY_SAN_JOSE_SALES_TAX_RATE_NOT_CURRENT).quantize(
        Decimal("0.01")
    )


def test_net_formula_excludes_sales_tax() -> None:
    formula = finance_net_usd_formula(2)
    assert formula.startswith("=IF(COUNTA(E2,F2,G2)=0")
    assert "N(E2)+N(F2)-N(G2)" in formula
    assert "sales_tax" not in formula.lower()
