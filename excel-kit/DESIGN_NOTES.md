# Design notes

Why the kit looks the way it does.

## ONE hub (Boss 2026-09-07 ~10:33 PM PT)

`sassycloset.xlsx` is the teammate hub: **All** plus category sheets filtered by kind letter, a blank **Orders** log, and a **Readme**. Photos stay on disk at `Documents/sassycloset/Photos/{MA}/001.jpg` — Excel stores `photo_folder` only. `kit.sh save` (= `run`) fetches the live site export and syncs those folders. Square Free still wins on-hand. A02 is retired (renamed to P02, not P05). Plain workbook — no pink, no embeds.

## Two Excel layers, one stock brain

| Layer | File | Job |
| --- | --- | --- |
| Square Free | Square Item library | On-hand count. Track stock ON. Boss Save only. |
| SoT book | `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` | Working copy / mã index / captions / photos. Official + Wishlist + Orders + Dashboard. |
| Desktop lean | `Sassy_Closet_Official_desktop.xlsx` + `Sassy_Closet_Wishlist_desktop.xlsx` | Filter/sort on a computer. Same shop law, fewer columns. |

SoT Official columns (`ma`, `name_vi`, `qty_on_hand`, `square_name`, …) answer “còn AO015 size M không?”. Desktop `MA_LIST` is the daily index (`ma`, `item`, `sizes_in_stock`, `on_hand`, `status`, `notes`, `photo_link`). They are not a second warehouse.

## Headers the builders lock

Defined in `schema.py`:

- **MA_LIST** — `ma` … `photo_link` (last)
- **ORDERS** — Facebook hello → pay / ship (no photo column)
- **BOT_ACTIVITY** — Date, Time PT, Bot, Ma, Action, Summary, Status
- **CANDIDATES** — `#` … `photo_link` (last)
- **SOT_WISHLIST** — `wish_id` … `source` … `notes` … `photo_link` (last). Link/source required if available.
- **SOT_OFFICIAL** — richer working-copy columns (`ma_num`, `prefix`, `square_name`, measurements). `photo_link` is not last here on purpose so live SoT books do not shuffle; append scripts map by header name.

`photo_link` is last on Ma_List, Candidates, and SoT Wishlist so a phone can ignore it and a desktop can still AutoFilter it. Never add a picture column.

## SoT automation (`excel-kit/sot/`)

Append scripts refuse to mint mã. Official requires `--ma` or prints ASK STOCK. Wishlist demands `--source` or `--no-source`. Orders accept only `Inquiry|Reserved|Paid|Shipped|Picked up|Cancelled`. `append_bot_activity.py` no-ops with a note when `Bot_Activity` is missing. `dashboard_brief.py` reads cached Dashboard values; if Excel has not calculated yet, Boss copies `Dashboard!B43`. `gf_intake_apply.py` stages a From GF packet (photos + template) onto Wishlist or Official without Square Save — contract `prompts/GF_CLOTHES_INTAKE.md`.

## Mã

`AO` áo, `QU` quần, `VA` váy, `AK` áo khoác, `GI` giày, `PK` phụ kiện, `SET` set — plus three digits (`AO001`). Unique piece = unique mã. Sold mã stays retired. Scripts validate with `MA_RE`; they never mint the next code. Next-mã math lives on the SoT Dashboard (`MAXIFS` on `Official[ma_num]` + prefix) for Stock to read, not for bots to invent.

## Photos

```
Documents/Sassy Closet/Photos/
  AO001.jpg      owned piece (and AO001_2.jpg)
  #001.jpg       wishlist find (and #001_2.jpg)
```

Excel cells hold the OneDrive **share URL** in `photo_link`. Captions live in `notes` / `Photos / notes`. Drawings and floating images are stripped by the builders and by `clean_sot_demo.py`.

## Status dropdowns (desktop)

- Ma_List: `in_stock`, `held`, `sold`, `archived`
- Orders: `Inquiry`, `Reserved`, `Paid`, `Shipped`, `Picked up`, `Cancelled`
- Candidates: `candidate`, `watching`, `skip`, `bought` plus Type `Dress` / `Top` / `Skirt` / `Bag` / `Shoes` / `Other` / `SET`

SoT Official uses a different status set (`Available` → `Reserved` → `Sold`, plus Hold / Damaged / Donated). Do not mix the two in one sheet.

## Pink, not locked

Deep rose / blush headers, yellow meaning “type here” on the SoT book, no sheet protection. A locked-feeling preview is a failed build. Freeze the header row only so a phone can still reach size and price.

## What we refuse to ship

- Fake live inventory rows (“~25 sample Official lines”)
- Customer PII in git
- Google Sheets as SoT
- Shopify
- Bots that Save in Square, post to Facebook, or move Zelle
- US sizes quoted to customers (Asia size + cm only)

## Cleaner

`clean_sot_demo.py` looks for kit-seeded demo tokens (`demo`, `sample`, `AO999`, …), optional `--wipe-data`, Square wording patches, and embedded images. It does not invent replacement stock.
