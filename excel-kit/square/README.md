# Square Free import (Sassy Closet)

Bought / on-hand rows for teammates live in **`Documents/Sassy Closet/Square.xlsx`** (`build_square_finance.py`). That book starts empty. This folder is the **headers-only Square import CSV**, not that tracker.

Headers-only template for Stock. **This file must never grow live inventory rows in git.**

Square Free is the on-hand inventory source of truth. Official Excel is a working copy. Wishlist stays off Square until Boss confirms bought and says **yes** in `#shop-decisions`.

## Standing rules (Boss yes 2026-09-04)

- **Track stock ON** for every item and every variation (Advanced Stock Tracking ON).
- Bots draft / propose only. **No Save** until Boss says yes on that batch.
- SKU = **mã** (`AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + 3 digits). Never invent a mã. Ask Stock to read Dashboard next-mã (`B21:B27`).
- Item Name = `mã` + short name (`AO001 Áo hồng`).
- Variation Name = Asia size + color (`M / đen`). Never quote US sizes to buyers.
- `Stockable` = `Y`. Do not put `No` in `New Quantity [Location]` — that **disables** tracking.
- `New Quantity [Default]` = on-hand count for that variation after a real count. `Current Quantity` is ignored on import.
- `Token` blank for **new** items. Never invent or copy a token from another shop.
- One variation row per size/color. Unique piece = unique mã.

## How Stock uses the template

1. Download a **fresh** blank library from Square Dashboard → Items → Item library → Actions → Export library → Blank import library. Square’s live headers win if they differ (especially location names).
2. Copy columns from `square_import_template.csv` only as a reminder. Replace `[Default]` with the real location name from that export (`Enabled [Sassy Closet]`, `New Quantity [Sassy Closet]`, …).
3. Fill rows **after** Boss assigned mã and confirmed the 8-line intake. Keep the filled file **off git** (OneDrive `Documents/Sassy Closet/square-drafts/`).
4. Post the Save ask in `#shop-decisions`. Wait for **yes**. Then import / Save.
5. After Save, append the Official working-copy row with `excel-kit/sot/append_official_row.py --ma …` (still not a second warehouse).

```bash
# Headers + mã / Track-ON checks on a *local* draft (not committed):
python3 excel-kit/square/validate_import.py path/to/draft.csv
```

`validate_import.py` on this repo’s template must report **headers only**.

## Columns we care about

| Header | Sassy Closet rule |
| --- | --- |
| Token | Blank on create. Do not delete the column. |
| Item Name | `AO001 Áo …` |
| Variation Name | Asia size + color |
| SKU | Exact mã. Unique. Never reuse Sold. |
| Description | Caption draft — Owner posts on Facebook. |
| Category | AO/QU/VA/AK/GI/PK/SET meaning, or Official `category` |
| Price | List $ |
| Sellable | `Y` |
| Stockable | `Y` (Track ON) |
| Default Unit Cost | Von / cost if Boss wants it on the item |
| Enabled [Location] | `Y` |
| New Quantity [Location] | Count. Never `No`. |
| Stock Alert Enabled [Location] | `Y` recommended (alert at 0 or 1) |

Required by Square to import: Item Name, Variation Name, Description, SKU (+ Enabled [Location] when there is more than one location).

## Do not

- Import wishlist / candidate rows.
- Commit a CSV that contains SKUs or quantities.
- Treat a successful import as “Excel is inventory.” Square still wins on-hand.
