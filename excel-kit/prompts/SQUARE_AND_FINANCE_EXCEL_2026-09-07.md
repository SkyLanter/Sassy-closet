# Square.xlsx + Finance.xlsx — Boss 2026-09-07 ~11:30 PM PT

Recreated in-kit. This is the locked contract. Website staged mãs are **not** bought.

## Outcome

Two plain books on the existing OneDrive shop folder:

```
Documents/Sassy Closet/
  Square.xlsx      bought / on-hand team tracker (NOT the website staged list)
  Finance.xlsx     tax-ready Sales / Fees / Payouts_Transfers / Expenses / Tax_Summary
  Photos/{ma}/     photo folder path only — never embed
```

Square Free Dashboard remains on-hand inventory **source of truth**. Excel is the **team tracker**. Cute / pink / embeds are retired.

## Square.xlsx — bought / on-hand tracker

**Not** the website staged list. **Not** `sassycloset.xlsx` All. **Not** `Sassy_Closet_Track.xlsx`.

Sheets (this order):

1. **On_Hand** — header + empty runway. Staged website mãs are not bought; do **not** copy live `/api/export` rows here.
2. **Sold_Log** — optional archive of sold pieces (header + empty runway).
3. **Readme** — shop law for teammates.

### On_Hand columns (exact)

`ma, kind, colors, size, qty_on_hand, costs, buy_date, source_link, photo_folder, square_item_name, track_on, status, sold_date, notes`

| Field | Rule |
| --- | --- |
| `ma` | Boss / Stock assigned. Never invent. Never reuse a sold mã. |
| `kind` | Letter / type as assigned (A áo …). Do not infer a live staged row. |
| `colors` | As bought |
| `size` | Asia size + cm. Never quote US sizes to buyers. |
| `qty_on_hand` | Team count. Square Free Dashboard still wins if they disagree. |
| `costs` | What was paid. Empty until a real buy. Do not invent $. |
| `buy_date` | Date received / bought. Empty until real. |
| `source_link` | Taobao / e.tb.cn / shop URL. Keep forever if you have it. |
| `photo_folder` | `Documents/Sassy Closet/Photos/{ma}/` |
| `square_item_name` | Name on Square Item library after Boss Save. Blank until then. |
| `track_on` | `Y` \| `N`. Standing rule is Track stock ON (`Y`) when the piece is on Square. |
| `status` | `on_hand` \| `reserved` \| `sold` \| `dead` |
| `sold_date` | Set when `status=sold`. |
| `notes` | Captions / flaws. Not a picture. |

Start **On_Hand empty**. Headers + short blank runway only.

### Sold_Log columns (exact)

`sold_date, ma, kind, colors, size, qty, costs, buy_date, source_link, square_item_name, notes`

Optional. Copy a sold On_Hand row here if the team wants a log. The required pair is still: On_Hand qty 0 + Finance Sales row.

### Sold rule (both books)

When a piece sells:

1. Square.xlsx On_Hand: `qty_on_hand = 0`, `status = sold`, `sold_date` filled.
2. Finance.xlsx Sales: one new row. `square_xlsx_ma` = that On_Hand `ma`.
3. Square Free Dashboard: Boss / Stock adjusts the live count. **No Square Save from this kit.**

## Finance.xlsx — tax-ready

Empty templates. **No invented sales. No invented $. No invented mã.**

Sheets (this order):

1. **Sales**
2. **Fees**
3. **Payouts_Transfers**
4. **Expenses**
5. **Tax_Summary** — formulas only (YTD + monthly). `0` means no rows yet.
6. **Readme**

### Sales columns (exact)

`date, ma, description, qty, gross_usd, ship_usd, discount_usd, net_usd, pay_method, pay_ref, customer_note, channel, square_xlsx_ma, tax_category, notes`

| Field | Rule |
| --- | --- |
| `date` | Sale date (Pacific). |
| `ma` | Same mã as Square.xlsx when it is a shop piece. |
| `description` | Short item / sale note. |
| `qty` | Units sold. |
| `gross_usd` | Merchandise $ before ship / discount. |
| `ship_usd` | Shipping collected (0 if meetup). |
| `discount_usd` | Discount given. |
| `net_usd` | Cash in for the sale (`gross + ship − discount`). Type it from the real payment. Do not invent. |
| `pay_method` | `zelle` \| `square` \| `square_online` \| `cash` \| `other` |
| `pay_ref` | Zelle memo / Square receipt / last-4. Not a password. |
| `customer_note` | Short note. Do not dump customer PII into git. |
| `channel` | `Facebook` \| `IG` \| `Walk-in` \| `Friend` \| `Square Online` \| `Other` |
| `square_xlsx_ma` | Must match Square.xlsx On_Hand `ma` for that sold piece. |
| `tax_category` | `clothing` \| `shipping` \| `other` |
| `notes` | Anything else |

### Fees columns (exact)

`date, source, fee_type, amount_usd, pay_ref, notes`

- `source`: `square` \| `square_online` \| `other`
- `fee_type`: `processing` \| `payout` \| `chargeback` \| `other`

### Payouts_Transfers columns (exact)

`date, direction, from_account, to_account, amount_usd, pay_ref, notes`

- `direction`: `in` \| `out`
- These are **cash movement, not income**. Do not add them into net sales.

### Expenses columns (exact)

`date, vendor, category, amount_usd, pay_method, receipt_ref, tax_category, notes`

- `category`: `inventory` \| `shipping_supplies` \| `packaging` \| `ads` \| `other`
- `pay_method`: same list as Sales
- `tax_category`: `cogs` \| `opex` \| `other`

### Tax_Summary

Plain header row. No cute title art.

| metric | ytd | 2026-01 … 2026-12 |
| --- | --- | --- |
| `gross_usd` | `SUMIFS` Sales `gross_usd` | monthly `SUMIFS` |
| `ship_usd` | Sales `ship_usd` | monthly |
| `discount_usd` | Sales `discount_usd` | monthly |
| `net_usd` | Sales `net_usd` | monthly |
| `fees_usd` | Fees `amount_usd` | monthly |
| `expenses_usd` | Expenses `amount_usd` | monthly |
| `net_after_fees_expenses` | `net_usd − fees − expenses` | same per column |
| `payouts_transfers_usd` | Payouts_Transfers `amount_usd` (not income) | monthly |

- **YTD** = calendar year of `TODAY()` through `TODAY()`.
- **Monthly** columns are tax year **2026** (`DATE(2026,n,1)`).
- Formulas ship even when Sales/Fees/Expenses are empty. Excel shows `0` until real rows exist. That is not invented revenue.
- openpyxl cannot calculate. Boss opens Excel / OneDrive.

## Style

- Plain only. Calibri 11 / 11 bold. No fills. No emoji. No merges. No embeds.
- Freeze header row (`A2`) on data sheets + Tax_Summary.
- AutoFilter on data sheets (header + runway).
- No sheet protection.
- Retired cute RGB (`F7C6D5`, `C43B6E`, `FFF7FA`, `F3E6EE`, `FFF3B0`) is a failed build.
- Font size > 14 is title-art — fail.

## Builder

```
python3 excel-kit/build_square_finance.py --out-dir ./out
```

Writes `out/Square.xlsx` and `out/Finance.xlsx`. Does **not** fetch the website export. Does **not** Save in Square.

## Hard stops

- No invent mã.
- No invent $.
- No Square Save.
- No Facebook Post.
- No passwords.
- No cute.
- Do not copy staged website mãs onto On_Hand.
- Do not delete other OneDrive files (`sassycloset.xlsx`, SoT, Photos, From GF).

## Success

- Spec file present (this document)
- `out/Square.xlsx` + `out/Finance.xlsx`
- On_Hand empty. Sales/Fees/Payouts_Transfers/Expenses empty.
- Tax_Summary has YTD + monthly formulas
- KIT.md note
- `unzip -t` + openpyxl sanity
- PR
