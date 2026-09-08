# Square.xlsx + Finance.xlsx — Boss 2026-09-07 ~11:30 PM PT

## Outcome

Two plain books on the existing OneDrive shop folder (not `Documents/sassycloset/`):

```
Documents/Sassy Closet/Square.xlsx
Documents/Sassy Closet/Finance.xlsx
```

`Square.xlsx` is the **bought / on-hand tracker**. `Finance.xlsx` is **tax-ready**.  
Website https://sassy-closet.vercel.app = GF intake. **Staged site mãs are NOT bought.**  
**Square Free = on-hand source of truth.** These books do not win a stock argument with Square.  
Cute / pink / emoji / embeds / phone art are retired. Freeze + AutoFilter only.

## Square.xlsx — bought / on-hand

Sheets: **On_Hand** · **Sold_Log** · **Readme**

### On_Hand columns (exact)

`ma, kind, colors, size, qty_on_hand, cost_cny, cost_usd, cost_currency, buy_date, source_link, photo_folder, square_item_name, track_on, status, sold_date, notes`

| Field | Rule |
| --- | --- |
| `photo_folder` | `Documents/Sassy Closet/Photos/{ma}/` (formula from `ma`; empty until a real mã is typed) |
| `status` | `on_hand` \| `reserved` \| `sold` \| `dead` |
| `track_on` | `Y` \| `N` — Track stock ON when the piece is actually in Square |
| `cost_currency` | `CNY` \| `USD` — write the cost Boss paid; do not convert or invent $ |

**Start On_Hand EMPTY.** Do not copy live `/api/export` rows. Staged site mãs (A01, P01, …) are not bought.

### Sold_Log columns (exact)

`sold_date, ma, kind, colors, size, qty, square_item_name, notes`

Header + empty runway. Money lives on Finance Sales, not here.

### Sold rule

When a piece sells:

1. On_Hand: `qty_on_hand` = **0**, `status` = `sold`, fill `sold_date`
2. Sold_Log: one row
3. Finance **Sales**: one row (`square_xlsx_ma` = that mã)
4. Square Free still wins — Boss sets Square qty 0. **No Square Save from kit.**

`dead` = write-off, qty 0, **no** Finance Sales row.

## Finance.xlsx — tax-ready

Sheets: **Sales** · **Fees** · **Payouts_Transfers** · **Expenses** · **Tax_Summary** · **Readme**  
**Empty — no invented sales or $.**

### Sales columns (exact)

`date, ma, description, qty, gross_usd, ship_usd, discount_usd, net_usd, pay_method, pay_ref, customer_note, channel, square_xlsx_ma, tax_category, notes`

| Field | Rule |
| --- | --- |
| `pay_method` | `zelle` \| `square` \| `square_online` \| `cash` \| `other` |
| `channel` | `facebook` \| `meetup` \| `website` \| `other` |
| `tax_category` | `product_sale` \| `shipping` \| `other` |
| `square_xlsx_ma` | same mã as Square.xlsx On_Hand |
| `net_usd` | formula `gross + ship − discount` when those cells have numbers; blank if all three are blank |

### Fees

`date, source, fee_type, amount_usd, pay_ref, related_ma, notes`  
`source`: `square` \| `square_online` \| `bank` \| `other`  
`fee_type`: `processing` \| `payout` \| `chargeback` \| `other`

### Payouts_Transfers

`date, kind, from_account, to_account, amount_usd, pay_ref, notes`  
`kind`: `square_payout` \| `zelle` \| `bank` \| `other`  
Not income. Tax_Summary lists the total separately.

### Expenses

`date, vendor, category, amount_usd, pay_method, pay_ref, ma, notes`  
`category`: `inventory` \| `shipping_supply` \| `ads` \| `software` \| `meetup` \| `other`  
`pay_method`: `zelle` \| `square` \| `cash` \| `other`

### Tax_Summary

Formulas only (open in Excel). Empty books total **0** — that is correct.

- Gross / ship / discount / net from Sales
- SUMIF by `tax_category`
- Fees, Expenses, Payouts / transfers
- Net after fees and expenses = net sales − fees − expenses

## Build

```
python3 excel-kit/build_square_finance.py --out-dir ./out
./excel-kit/kit.sh square
```

Writes `out/Square.xlsx` + `out/Finance.xlsx`. Kit copies into `Documents/Sassy Closet/` only if that folder already exists. No deletes.

## Hard stops

- No invent mã.
- No invent $.
- No Square Save.
- No Facebook Post.
- No passwords.
- No cute.
- Do not treat staged site mãs as On_Hand.

## Success

- Both books empty of stock and sales
- Freeze + AutoFilter on data sheets
- `unzip -t` + openpyxl sanity
- PR + KIT note
