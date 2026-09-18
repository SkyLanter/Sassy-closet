# DONE — Finance.xlsx tax-ready (San Jose 10%)

## What was fixed
- Restored `FINANCE_*` / Square book exports on `excel-kit/schema.py` so `build_square_finance.py` cannot `ImportError` (`FINANCE_CHANNEL`, `FINANCE_SALES`, …).
- Pinned the export list as `FINANCE_BOOK_EXPORTS` plus pytest that fails if any symbol is deleted.
- Builder writes empty `out/Square.xlsx` + `out/Finance.xlsx` (contract headers, freeze, AutoFilter, no cute, no invented sales).
- San Jose, CA combined sales tax **10.000%** (`SAN_JOSE_SALES_TAX_RATE`, CDTFA effective 2026-04-01). Not 9.375%.
- Sales columns: `cogs_usd`, `taxable_base_usd`, `sales_tax_rate`, `sales_tax_usd`. Tax is on sell price; income tax is on profit.
- Tax_Summary: monthly + YTD Schedule C-style formulas. Sold path: `Sold_Log.finance_ref` → `Sales.square_xlsx_ma`.

## Tests
```bash
python3 excel-kit/build_square_finance.py --out-dir ./out
./excel-kit/kit.sh square
python3 -m pytest excel-kit/tests/test_finance_schema_exports.py \
  excel-kit/tests/test_square_finance_builder.py \
  excel-kit/tests/test_finance_formulas.py -q
python3 excel-kit/tests/run_checks.py
```

Counts and sha256 are filled after the rebuild in CI / this agent run.

## Land path (document only — Mini Boss / Build & Files after PR review)
`Documents/Sassy Closet/Finance.xlsx` beside `Square.xlsx` + `sassycloset.xlsx`.
This VM does not overwrite OneDrive.

## Open questions (Cap / accountant)
- CDTFA seller permit
- Nexus outside San Jose / California
- Tax-included vs +tax pricing (book default is +tax: tax not stuffed into profit)
- Customer flat ship $ (TBD — never invent a rate)
- Whether CA treats collected shipping as taxable (taxable_base defaults to gross − discount only)

Not legal advice. Empty until real sales. No bot invents sales.
