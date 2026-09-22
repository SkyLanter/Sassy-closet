"""Formula fixtures: San Jose 10%, profit vs tax, edge cases."""

from __future__ import annotations

import random
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from schema import (
    FINANCE_EXPENSES,
    FINANCE_FEES,
    FINANCE_SALES,
    FINANCE_TAX_SUMMARY_METRICS,
    FINANCE_TAX_YEAR,
    SQUARE_ON_HAND,
    SQUARE_SOLD_LOG,
    finance_net_usd_amount,
    finance_profit_usd,
    finance_sales_tax_usd_formula,
    finance_taxable_base_amount,
    header_index,
    san_jose_sales_tax_usd,
)
from build_square_finance import build

BOSS_EXAMPLE_COST = Decimal("100.00")
BOSS_EXAMPLE_GROSS = Decimal("120.00")
BOSS_EXAMPLE_TAX = Decimal("12.00")
BOSS_EXAMPLE_PROFIT = Decimal("20.00")


def _set(ws: Worksheet, headers: tuple[str, ...], row: int, **values: object) -> None:
    for name, value in values.items():
        ws.cell(row, header_index(headers, name) + 1, value)


def _num(value: object) -> Decimal:
    if value is None or value == "":
        return Decimal("0.00")
    if isinstance(value, str) and value.startswith("="):
        raise AssertionError(f"expected a computed number, got formula {value!r}")
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _eval_sales_row(ws: Worksheet, row: int) -> dict[str, Decimal]:
    """Mirror Sales formulas in Python (openpyxl does not calculate)."""
    def get(name: str) -> object:
        return ws.cell(row, header_index(FINANCE_SALES, name) + 1).value

    gross = get("gross_usd")
    ship = get("ship_usd")
    discount = get("discount_usd")
    typed_taxable = get("taxable_base_usd")
    typed_rate = get("sales_tax_rate")
    typed_tax = get("sales_tax_usd")
    cogs = get("cogs_usd")

    if all(v in (None, "") for v in (gross, ship, discount)):
        net = Decimal("0.00")
    else:
        net = finance_net_usd_amount(gross or 0, ship or 0, discount or 0)

    if isinstance(typed_taxable, str) and typed_taxable.startswith("="):
        taxable = (
            Decimal("0.00")
            if all(v in (None, "") for v in (gross, discount))
            else finance_taxable_base_amount(gross or 0, discount or 0)
        )
    else:
        taxable = _num(typed_taxable)

    if isinstance(typed_rate, str) and typed_rate.startswith("="):
        rate = Decimal("0.10") if taxable != 0 or gross not in (None, "") else Decimal("0")
        if all(v in (None, "") for v in (gross, discount)):
            rate = Decimal("0")
    else:
        rate = Decimal(str(typed_rate or 0))

    if isinstance(typed_tax, str) and typed_tax.startswith("="):
        tax = Decimal("0.00") if rate == 0 and taxable == 0 and gross in (None, "") else san_jose_sales_tax_usd(taxable)
        if all(v in (None, "") for v in (gross, discount)):
            tax = Decimal("0.00")
        elif rate != Decimal("0.10") and rate != 0:
            tax = (taxable * rate).quantize(Decimal("0.01"))
    else:
        tax = _num(typed_tax)

    return {
        "gross": _num(gross),
        "ship": _num(ship),
        "discount": _num(discount),
        "net": net,
        "cogs": _num(cogs),
        "taxable": taxable,
        "tax": tax,
    }


def _sum_sheet(ws: Worksheet, headers: tuple[str, ...], header: str, year: int | None = None, month: int | None = None) -> Decimal:
    idx = header_index(headers, header) + 1
    date_idx = header_index(headers, "date") + 1 if "date" in headers else None
    total = Decimal("0.00")
    for row in range(2, (ws.max_row or 1) + 1):
        value = ws.cell(row, idx).value
        if isinstance(value, str) and value.startswith("="):
            if header in {"net_usd", "taxable_base_usd", "sales_tax_usd"} and ws.title == "Sales":
                computed = _eval_sales_row(ws, row)
                mapping = {
                    "net_usd": "net",
                    "taxable_base_usd": "taxable",
                    "sales_tax_usd": "tax",
                }
                amount = computed[mapping[header]]
            else:
                continue
        elif value in (None, ""):
            continue
        else:
            amount = _num(value)
        if year is not None and month is not None and date_idx is not None:
            raw = ws.cell(row, date_idx).value
            if raw in (None, ""):
                continue
            if isinstance(raw, datetime):
                dt = raw.date()
            elif isinstance(raw, date):
                dt = raw
            else:
                dt = date.fromisoformat(str(raw)[:10])
            if dt.year != year or dt.month != month:
                continue
        total += amount
    return total


def _tax_summary_totals(finance_ws: dict[str, Worksheet], year: int | None = None, month: int | None = None) -> dict[str, Decimal]:
    sales = finance_ws["Sales"]
    fees = finance_ws["Fees"]
    expenses = finance_ws["Expenses"]
    gross = _sum_sheet(sales, FINANCE_SALES, "gross_usd", year, month)
    ship = _sum_sheet(sales, FINANCE_SALES, "ship_usd", year, month)
    discount = _sum_sheet(sales, FINANCE_SALES, "discount_usd", year, month)
    net = _sum_sheet(sales, FINANCE_SALES, "net_usd", year, month)
    taxable = _sum_sheet(sales, FINANCE_SALES, "taxable_base_usd", year, month)
    tax = _sum_sheet(sales, FINANCE_SALES, "sales_tax_usd", year, month)
    fee_total = _sum_sheet(fees, FINANCE_FEES, "amount_usd", year, month)
    cogs = _sum_sheet(sales, FINANCE_SALES, "cogs_usd", year, month)
    expense_total = _sum_sheet(expenses, FINANCE_EXPENSES, "amount_usd", year, month)
    profit = finance_profit_usd(
        gross_usd=gross,
        ship_usd=ship,
        discount_usd=discount,
        fees_usd=fee_total,
        cogs_usd=cogs,
        expenses_usd=expense_total,
    )
    return {
        "gross": gross,
        "shipping": ship,
        "discount": discount,
        "net": net,
        "taxable_base": taxable,
        "sales_tax": tax,
        "fees": fee_total,
        "cogs": cogs,
        "expenses": expense_total,
        "profit": profit,
    }


@pytest.fixture()
def books(tmp_path: Path):
    square_path, finance_path = build(tmp_path)
    square = load_workbook(square_path)
    finance = load_workbook(finance_path)
    try:
        yield square, finance, square_path, finance_path
    finally:
        square.close()
        finance.close()


def test_zero_sales_tax_summary_is_zero(books) -> None:
    _square, finance, _sp, _fp = books
    sheets = {name: finance[name] for name in finance.sheetnames}
    totals = _tax_summary_totals(sheets)
    assert totals["gross"] == Decimal("0.00")
    assert totals["sales_tax"] == Decimal("0.00")
    assert totals["profit"] == Decimal("0.00")
    assert totals["shipping"] == Decimal("0.00")


def test_boss_example_cost_100_sell_120_tax_12(books) -> None:
    square, finance, _sp, _fp = books
    sales = finance["Sales"]
    sold = square["Sold_Log"]
    on_hand = square["On_Hand"]

    _set(
        on_hand,
        SQUARE_ON_HAND,
        2,
        ma="A01",
        qty_on_hand=0,
        cost_usd=float(BOSS_EXAMPLE_COST),
        status="sold",
        sold_date=date(FINANCE_TAX_YEAR, 4, 15),
    )
    _set(
        sold,
        SQUARE_SOLD_LOG,
        2,
        ma="A01",
        sold_date=date(FINANCE_TAX_YEAR, 4, 15),
        qty=1,
        finance_ref="Sales!A2",
        notes="fixture — sold Square row → finance_ref path",
    )
    _set(
        sales,
        FINANCE_SALES,
        2,
        date=date(FINANCE_TAX_YEAR, 4, 15),
        ma="A01",
        description="Boss example fixture",
        qty=1,
        gross_usd=float(BOSS_EXAMPLE_GROSS),
        ship_usd=0,
        discount_usd=0,
        pay_method="zelle",
        pay_ref="fixture-zelle",
        channel="facebook",
        square_xlsx_ma="A01",
        tax_category="product_sale",
        cogs_usd=float(BOSS_EXAMPLE_COST),
    )
    computed = _eval_sales_row(sales, 2)
    assert computed["net"] == BOSS_EXAMPLE_GROSS
    assert computed["taxable"] == BOSS_EXAMPLE_GROSS
    assert computed["tax"] == BOSS_EXAMPLE_TAX
    assert computed["tax"] == san_jose_sales_tax_usd(BOSS_EXAMPLE_GROSS)

    totals = _tax_summary_totals({name: finance[name] for name in finance.sheetnames})
    assert totals["gross"] == BOSS_EXAMPLE_GROSS
    assert totals["sales_tax"] == BOSS_EXAMPLE_TAX
    assert totals["cogs"] == BOSS_EXAMPLE_COST
    assert totals["profit"] == BOSS_EXAMPLE_PROFIT
    assert totals["profit"] == finance_profit_usd(
        gross_usd=BOSS_EXAMPLE_GROSS,
        cogs_usd=BOSS_EXAMPLE_COST,
    )
    # Sales tax is collected separately — not stuffed into profit.
    assert totals["profit"] != BOSS_EXAMPLE_GROSS - BOSS_EXAMPLE_TAX
    assert sold.cell(2, header_index(SQUARE_SOLD_LOG, "finance_ref") + 1).value == "Sales!A2"
    assert sales.cell(2, header_index(FINANCE_SALES, "square_xlsx_ma") + 1).value == "A01"

    apr = _tax_summary_totals({name: finance[name] for name in finance.sheetnames}, FINANCE_TAX_YEAR, 4)
    jan = _tax_summary_totals({name: finance[name] for name in finance.sheetnames}, FINANCE_TAX_YEAR, 1)
    assert apr["gross"] == BOSS_EXAMPLE_GROSS
    assert jan["gross"] == Decimal("0.00")


def test_discount_reduces_taxable_base(books) -> None:
    _square, finance, _sp, _fp = books
    sales = finance["Sales"]
    _set(
        sales,
        FINANCE_SALES,
        2,
        date=date(FINANCE_TAX_YEAR, 5, 1),
        gross_usd=120,
        discount_usd=20,
        tax_category="product_sale",
    )
    computed = _eval_sales_row(sales, 2)
    assert computed["net"] == Decimal("100.00")
    assert computed["taxable"] == Decimal("100.00")
    assert computed["tax"] == Decimal("10.00")


def test_shipping_income_separate_from_product(books) -> None:
    _square, finance, _sp, _fp = books
    sales = finance["Sales"]
    _set(
        sales,
        FINANCE_SALES,
        2,
        date=date(FINANCE_TAX_YEAR, 6, 2),
        gross_usd=120,
        ship_usd=8,
        discount_usd=0,
        tax_category="product_sale",
        cogs_usd=100,
    )
    computed = _eval_sales_row(sales, 2)
    assert computed["net"] == Decimal("128.00")
    assert computed["taxable"] == Decimal("120.00")
    assert computed["tax"] == Decimal("12.00")
    totals = _tax_summary_totals({name: finance[name] for name in finance.sheetnames})
    assert totals["shipping"] == Decimal("8.00")
    assert totals["gross"] == Decimal("120.00")
    assert totals["profit"] == Decimal("28.00")


def test_fee_row_linked_and_expense_cogs(books) -> None:
    _square, finance, _sp, _fp = books
    sales = finance["Sales"]
    fees = finance["Fees"]
    expenses = finance["Expenses"]
    _set(
        sales,
        FINANCE_SALES,
        2,
        date=date(FINANCE_TAX_YEAR, 7, 3),
        ma="P01",
        gross_usd=120,
        pay_ref="sale-001",
        square_xlsx_ma="P01",
        tax_category="product_sale",
    )
    _set(
        fees,
        FINANCE_FEES,
        2,
        date=date(FINANCE_TAX_YEAR, 7, 3),
        source="square",
        amount_usd=3.50,
        fee_type="square_processing",
        related_sale_ref="sale-001",
    )
    _set(
        expenses,
        FINANCE_EXPENSES,
        2,
        date=date(FINANCE_TAX_YEAR, 7, 3),
        vendor="supplier",
        category="inventory_cogs",
        amount_usd=100,
        payment_method="zelle",
        receipt_note="fixture COGS via Expenses",
    )
    totals = _tax_summary_totals({name: finance[name] for name in finance.sheetnames})
    assert totals["fees"] == Decimal("3.50")
    assert totals["expenses"] == Decimal("100.00")
    assert totals["cogs"] == Decimal("0.00")
    assert totals["profit"] == Decimal("16.50")
    assert fees.cell(2, header_index(FINANCE_FEES, "related_sale_ref") + 1).value == "sale-001"


def test_sales_tax_formula_string_uses_sj_rate() -> None:
    formula = finance_sales_tax_usd_formula(2)
    assert formula.startswith("=")
    assert "ROUND(" in formula
    assert "P2" in formula
    assert "Q2" in formula


@pytest.mark.parametrize("gross", [Decimal("0.01"), Decimal("1.00"), Decimal("19.99"), Decimal("120"), Decimal("333.33"), Decimal("1000")])
def test_sj_tax_is_ten_percent_rounded(gross: Decimal) -> None:
    assert san_jose_sales_tax_usd(gross) == (gross * Decimal("0.10")).quantize(Decimal("0.01"))


@pytest.mark.parametrize("seed", range(15))
def test_property_random_positive_gross_sj_tax(seed: int) -> None:
    rng = random.Random(seed)
    cents = rng.randint(1, 500_000)
    gross = (Decimal(cents) / Decimal("100")).quantize(Decimal("0.01"))
    assert san_jose_sales_tax_usd(gross) == (gross * Decimal("0.10")).quantize(Decimal("0.01"))


def test_tax_summary_metric_kinds_cover_profit() -> None:
    kinds = [kind for _label, kind in FINANCE_TAX_SUMMARY_METRICS]
    assert kinds[-1] == "profit"
    assert "sales_tax" in kinds
    assert "cogs" in kinds
