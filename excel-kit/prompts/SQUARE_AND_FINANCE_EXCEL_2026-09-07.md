# Square.xlsx + Finance.xlsx — Boss 2026-09-07 ~11:30 PM PT

## Outcome
Under OneDrive `Documents/Sassy Closet/` (beside sassycloset.xlsx + Photos/):

1. **Square.xlsx** — bought / on-hand inventory tracker (Excel working copy)
2. **Finance.xlsx** — payments + tax-ready ledger (Zelle + Square + future Square Online)

Plain English headers. No cute/pink. Freeze + autofilter. No embeds.

## Relationship
- **sassycloset.xlsx** = website staged mirror (all intake mãs + source_link) — already exists. Do not overwrite.
- **Square.xlsx** = only **bought / on-hand** pieces (Boss bought/received). Square Free Dashboard remains legal on-hand SoT; this Excel tracks for the team. Never invent on-hand.
- When an item **sells**: update Square.xlsx (on-hand → 0 / status Sold) AND append a Finance.xlsx sale row (required).
- Hard stops: no Square Save click, no invent mã/stock/$, bots draft only.

## Square.xlsx sheets

### On_Hand
Columns:
`ma, kind, colors, size, qty_on_hand, cost_cny, cost_usd, cost_currency, buy_date, source_link, photo_folder, square_item_name, track_on, status, sold_date, notes`

status enum: `on_hand, reserved, sold, dead`
qty_on_hand: unique piece default 1; sold → 0
photo_folder: `Documents/Sassy Closet/Photos/{ma}/`
Empty template + 20 blank rows if no bought stock yet (shop may still be staged-only).
Staged site mãs are NOT bought.

### Sold_Log (optional thin)
`ma, sold_date, qty, finance_ref, notes` — or leave blank template

### Readme
5 lines: purpose; Square Free = SoT; Excel = team tracker; sold → Finance; never invent.

## Finance.xlsx sheets (tax-ready detail)

### Sales
`date, ma, description, qty, gross_usd, ship_usd, discount_usd, net_usd, pay_method, pay_ref, customer_note, channel, square_xlsx_ma, tax_category, notes`
pay_method: `zelle, square, square_online, cash, other`
channel: `facebook, meetup, website, other`
tax_category: `product_sale, shipping, other`

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
Monthly / YTD totals: gross sales, shipping income, fees, COGS (from Square cost when linked), expenses, net — English labels suitable for accountant / US Schedule C style summary (not legal advice; columns for 1099-K / Zelle notes).

### Readme
Rules: every sold on-hand item must create a Sales row; never invent $; Boss confirms money moves.
Cap logs a sale on Sales after Boss confirms money. Boss uses Tax_Summary for filing (accountant-friendly, not legal advice).

## Seed
Do NOT invent sales. On_Hand starts empty OR only rows Boss has confirmed bought (currently staged A01/P01/S01/P02… are NOT bought — leave On_Hand empty with headers).

## Kit
`excel-kit/build_square_finance.py` + short KIT.md note. Artifacts: `out/Square.xlsx`, `out/Finance.xlsx`.

## Success
- Both xlsx unzip-t clean, openpyxl sanity
- Headers match spec; empty On_Hand OK
- Land path documented Documents/Sassy Closet/Square.xlsx and Documents/Sassy Closet/Finance.xlsx
- No Square Save
- PR

Model: grok-4.6 xhigh Fast ON
