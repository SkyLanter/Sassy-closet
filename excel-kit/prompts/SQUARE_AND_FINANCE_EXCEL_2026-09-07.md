# Square.xlsx + Finance.xlsx — Boss 2026-09-07 ~11:30 PM PT

## Outcome
Under OneDrive `Documents/Sassy Closet/` (beside sassycloset.xlsx + Photos/):

1. **Square.xlsx** — bought / on-hand inventory tracker (Excel working copy)
2. **Finance.xlsx** — payments + tax-ready ledger (Zelle + Square + future Square Online)

Plain English headers. No cute/pink. Freeze + autofilter. No embeds.

## Relationship
- **sassycloset.xlsx** = website staged mirror (all intake mãs + source_link) — already exists
- **Square.xlsx** = only **bought / on-hand** pieces (Boss bought/received). Square Free Dashboard remains legal on-hand SoT; this Excel tracks for the team. Never invent on-hand.
- When an item **sells**: update Square.xlsx (on-hand → 0 / status Sold) AND append a Finance.xlsx sale row (required). Sold_Log.finance_ref points at that Sales row / pay_ref.
- Hard stops: no Square Save click, no invent mã/stock/$, bots draft only.

## Square.xlsx sheets

### On_Hand
Columns:
`ma, kind, colors, size, qty_on_hand, cost_cny, cost_usd, cost_currency, buy_date, source_link, photo_folder, square_item_name, track_on, status, sold_date, notes`

status enum: `on_hand, reserved, sold, dead`
qty_on_hand: unique piece default 1; sold → 0
photo_folder: `Documents/Sassy Closet/Photos/{ma}/`
Empty template + 20 blank rows if no bought stock yet (shop may still be staged-only).

### Sold_Log (optional thin)
`ma, sold_date, qty, finance_ref, notes` — or leave blank template

### Readme
5 lines: purpose; Square Free = SoT; Excel = team tracker; sold → Finance; never invent.

## Finance.xlsx sheets (tax-ready detail)

### Sales
`date, ma, description, qty, gross_usd, ship_usd, discount_usd, net_usd, pay_method, pay_ref, customer_note, channel, square_xlsx_ma, tax_category, cogs_usd, taxable_base_usd, sales_tax_rate, sales_tax_usd, notes`

pay_method: `zelle, square, square_online, cash, other`
channel: `facebook, meetup, website, other`
tax_category: `product_sale, shipping, other`

`net_usd` = gross + ship − discount (formula). Sales tax is **not** in net.
`cogs_usd` = Square.xlsx On_Hand cost_usd copied when the piece sells (do not invent a sell price).
`taxable_base_usd` / `sales_tax_rate` / `sales_tax_usd` record San Jose combined sales tax on the taxable sell price, collected separately.

### Fees
`date, source, amount_usd, fee_type, related_sale_ref, notes`
fee_type: `square_processing, shipping_label, ads, other`

### Payouts_Transfers
`date, from_method, to_account_note, amount_usd, confirmation, notes`
(Zelle display customers see: Thang Tien Huynh — note only, never store bank passwords)

### Expenses
`date, vendor, category, amount_usd, payment_method, receipt_note, notes`
category: `inventory_cogs, shipping_supplies, packaging, software, ads, other`

### Tax_Summary (formulas OK)
Monthly / YTD totals: gross sales, shipping income, fees, COGS (from Square cost when linked via Sales cogs_usd), expenses, net — English labels suitable for accountant / US Schedule C style summary (not legal advice; columns for 1099-K / Zelle notes).

San Jose, California helper: combined sales tax rate **10.000%** (CDTFA, effective Apr 1, 2026). Do not use 9.375% as current. Sales tax collected is a liability, not income. Income tax is on profit, not COGS.

### Readme
Rules: every sold on-hand item must create a Sales row; never invent $; Boss confirms money moves. Tax on sell price / income tax on profit. Empty until real sales.

## Seed
Do NOT invent sales. On_Hand starts empty OR only rows Boss has confirmed bought (currently staged A01/P01/S01/P02… are NOT bought — leave On_Hand empty with headers).

## Kit
`excel-kit/build_square_finance.py` + short KIT.md note. Artifacts: `out/Square.xlsx`, `out/Finance.xlsx`.

```bash
python3 excel-kit/build_square_finance.py --out-dir ./out
./excel-kit/kit.sh square    # same as: kit.sh finance | kit.sh books
python3 -m pytest excel-kit/tests/test_finance_schema_exports.py excel-kit/tests/test_square_finance_builder.py excel-kit/tests/test_finance_formulas.py
```

## Success
- Both xlsx unzip-t clean, openpyxl sanity
- Headers match spec; empty On_Hand OK
- Land path documented Documents/Sassy Closet/Square.xlsx and Documents/Sassy Closet/Finance.xlsx
- PR

Model: grok-4.6 xhigh Fast ON
