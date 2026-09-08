# Kit

Square.xlsx + Finance.xlsx land on OneDrive `Documents/Sassy Closet/` (Boss 2026-09-07 ~11:30 PM PT).

- **Square.xlsx** = bought / on-hand team tracker. **Not** the website staged list. On_Hand starts empty.
- **Finance.xlsx** = tax-ready Sales / Fees / Payouts_Transfers / Expenses / Tax_Summary. Empty templates — no invented sales.
- Square Free Dashboard remains inventory SoT. Excel is the team tracker.
- Sold item → Square `qty_on_hand` 0 + one Finance Sales row (`square_xlsx_ma`).
- Cute Excel is retired. Do not delete other OneDrive files.

```bash
python3 excel-kit/build_square_finance.py --out-dir ./out
unzip -t out/Square.xlsx
unzip -t out/Finance.xlsx
```

Kit copies into `Documents/Sassy Closet/` only if that folder already exists. Contract: `prompts/SQUARE_AND_FINANCE_EXCEL_2026-09-07.md`.
