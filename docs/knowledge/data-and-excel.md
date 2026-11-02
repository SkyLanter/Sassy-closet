# Data files and the Excel schema

Column meanings below come from names and comments in the repo. A header with no comment is listed as the header text only. The live OneDrive SoT file is not in git. See [proof-and-hub-snapshot.md](proof-and-hub-snapshot.md).

Headers from the scrubbed snapshot are in [snapshot-excel.md](snapshot-excel.md). Those headers are not `excel-kit/schema.py`. The snapshot's own meaning cell for them is `unknown (header only: …)`. Builders for a floor tracker, a `sassycloset.xlsx` hub, and Square / Finance books are still open PRs (#7, #8, #10, #11, #43), not files on `main`. `Sassy_Closet_SoT.xlsx` is not in the export. Which Taobao pull copy is canonical, and whether `sassycloset.xlsx` is the hub, are UNKNOWN there.

## Excel kit sheets on main

Defined in `excel-kit/schema.py`.

### SoT workbook sheets

`SOT_SHEETS`: `START HERE`, `TOMORROW`, `BOT PROMPT`, `Lists`, `Official`, `Wishlist`, `Orders`, `Dashboard`, `Bot_Activity`. `Bot_Activity` is optional on the SoT book and required on the lean Official desktop book.

Official / Wishlist / Orders data headers are on row 4. `Bot_Activity`, `Ma_List`, and `Candidates` use row 1 (`SOT_DATA_SHEETS`).

### Official columns (`SOT_OFFICIAL`)

| Column | Meaning in repo |
| --- | --- |
| `ma` | Official mã (`AO001` style). Aliases include `mã`. |
| `date_in` | Header only. No further definition in `schema.py`. |
| `brand` | Header only. Alias `Brand + name`. |
| `name_vi` | Vietnamese name. Aliases `what_vi`, `item`. |
| `name_en` | English name. |
| `category` | Alias `Type`, `kind_vi`. |
| `size` | Alias `sizes_in_stock`, `Size Asia + cm`. |
| `color` | Alias `Color`. |
| `condition` | One of `SOT_CONDITION`: New, Like new, Good, Fair, As-is. |
| `qty_on_hand` | Working-copy quantity. Square still wins on-hand (`SQUARE_SOT_LINE`). |
| `cost` | Cost. Alias `Cost ¥`. Do not commit live cost rows (`README.md`). |
| `list_price` | Sell / list dollar. Aliases include `price`, `Sell $`, `Gia ban $`. The freshness parser also accepts a header `sell_usd` when `list_price` is absent (`scripts/freshness_check.py`). |
| `margin_$` | Header only. |
| `margin_pct` | Header only. |
| `status` | One of `SOT_OFFICIAL_STATUS`: Available, Reserved, Sold, Hold, Damaged, Donated. |
| `photo_file` | Header only. |
| `photo_link` | Link only. Never an embedded image (`PHOTO_RULE`). |
| `fb_url` | Header only. |
| `storage` | Header only. |
| `source` | Header only on Official. Aliases `link`, `Link (reopen)`, `Link/source`, `Link` (`HEADER_ALIASES`). The "required if available" comment in `schema.py` sits on `SOT_WISHLIST`, not on `SOT_OFFICIAL`. |
| `bust_chest`, `waist`, `length` | Header only. |
| `flaws` | Header only. |
| `reserved_for` | Header only. |
| `days_in` | Header only. |
| `square_name` | Header only. |
| `caption_ready` | Header only. |
| `notes` | Header only. |
| `last_updated` | Header only. |
| `ma_num` | Numeric part used by Dashboard next-mã formulas. |
| `prefix` | `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET`. |

Status map into the lean Ma_List (`OFFICIAL_TO_MA_LIST_STATUS`): Available → `in_stock`, Reserved and Hold → `held`, Sold → `sold`, Damaged and Donated → `archived`.

### Wishlist columns (`SOT_WISHLIST`)

`wish_id`, `date_added`, `prefix`, `what_vi`, `what_en`, `size`, `color`, `max_cost`, `target_price`, `reason`, `requested_by`, `status`, `source`, `notes`, `photo_link`.

`photo_link` is last. The comment above `SOT_WISHLIST` says `source` is "Link/source (Taobao / shop URL) — required if available." Status values: `candidate`, `watching`, `skip`, `bought` (`SOT_WISHLIST_STATUS`). Bought stays off Square until Boss confirms received and says Save (`STAY_OFF_SQUARE`).

### Orders columns (`SOT_ORDERS`)

`order_id`, `date`, `channel`, `buyer`, `fb_handle`, `ma`, `snapshot`, `qty`, `agreed_price`, `ship_fee`, `net`, `order_status`, `pay_method`, `fulfill`, `meetup_or_ship`, `thread_note`, `last_touch`.

`order_status`: Inquiry, Reserved, Paid, Shipped, Picked up, Cancelled. Channels: Facebook, IG, Walk-in, Friend, Other. Pay: Zelle, Cash, Venmo, Other, Unpaid. Fulfill: Ship, Local pickup, Hold, TBD.

### Lean desktop books

`MA_LIST`: `ma`, `item`, `sizes_in_stock`, `color`, `cost`, `price`, `on_hand`, `status`, `notes`, `photo_link`. Status: `in_stock`, `held`, `sold`, `archived`.

`ORDERS` (lean): `date`, `buyer`, `ma`, `size`, `color`, `channel`, `status`, `pay`, `ship_or_local`, `agreed_price`, `notes`.

`BOT_ACTIVITY`: `Date`, `Time PT`, `Bot`, `Ma`, `Action`, `Summary`, `Status`.

`CANDIDATES`: `#`, `Date`, `Status`, `Type`, `Brand + name`, `Size Asia + cm`, `Color`, `Cost ¥`, `Sell $`, `Link (reopen)`, `Photos / notes`, `photo_link`. Status: `candidate`, `watching`, `skip`, `bought`. Types include Dress, Top, Skirt, Bag, Shoes, Other, SET.

### Dashboard

Morning brief is cell `B43` (`SOT_DASHBOARD_BRIEF_CELL`). Rows 5–18 are counts. Rows 21–27 are next-mã formulas. The note on `SOT_DASHBOARD_BRIEF_NOTE` says openpyxl cannot calculate formulas, so Boss copies `B43` from Excel when the script prints a formula.

### Square import

`SQUARE_IMPORT_HEADERS` is the headers-only catalog import. `SQUARE_SKU_IS_MA` says SKU is the mã (`AO001`), Item Name is mã plus a short name, Variation Name is Asia size plus color, and Stockable is Y. The template in `excel-kit/square/` must stay headers-only (`README.md`).

### Intake CSV headers

`INTAKE_CSV_HEADERS` in `schema.py`: `ma`, `kind`, `kind_vi`, `size`, `color`, `color_note`, `color_pieces`, `blurb`, `cost_cny`, `cost_usd`, `cost_currency`, `sell_cny`, `sell_usd`, `sell_currency`, `source_link`, `status`, `square`, `created_at`, `updated_at`, `photo_link`, `size_options`.

## JSON and other data files

### `data/held.json`

`heldIncomplete` (string list) and `neverList` (string list). Meanings: [shop.md](shop.md). This is the list the shop and `publishBlock` import. Do not fork a second copy in a component.

### `data/approved-held-gia.json`

`_note` says the values are Giá already shown on FB and IG for held mãs, dual-checked 2026-10, reference only, not a sell price. Object `approvedGia` maps mã to a number.

### `data/privacy-allowlist.json` and `data/run-gaps.json`

Present in `data/`. This page does not restate their keys. Read the file and the script that loads it (`scripts/privacy_scan.py`, `scripts/run_gap_check.py`) before describing a key.

### `shared/live-price-snapshot.json`

Header fields include `readOnly`, `writesCatalog`, `blobUrl`, `blobSha256`, `blobUpdatedAt`, `intakeUrl`, `readAt`, `fx`, `liveCount`, and `rows`. Each row has `ma`, `kind`, `liveUsd`, `deboxUsd`, `flat25Usd`, `wouldBeUsd`, `applied`, `note`. `costCny`, `costUsd`, `costSource`, and `landedUsd` are null after PR #207. Do not print or restore the old cost values.

### Sell seed `sassy-closet-shop/data/products.json`

`schema` `catalog.v1`. Top-level `allowlist` is the ten `KNOWN_SEED_MAS` (`sassy-closet-shop/lib/catalog-contract.ts`). Product fields in `sassy-closet-shop/lib/types.ts`:

| Field | Meaning |
| --- | --- |
| `ma` | Intake-style mã. |
| `type` | Kind letter. |
| `titleVn`, `titleEn` | Titles. |
| `priceUsd` | Public USD, or null. |
| `qty` | Typed as the literal `1`. |
| `status` | `available`, `hold`, or `sold`. |
| `colors[]` | `id`, `hex`, `name`, `note`. |
| `images[]` | `src`, `colorId`, `order`. |
| `sizes` | Shop sizes. |
| `fitCm` | `bustChestCm`, `waistCm`, `lengthCm` (null allowed in the seed sample). |
| `descriptionVn`, `descriptionEn` | Copy. |
| `fulfillment` | `dropship` or `on_hand` (`lib/fulfillment.ts`). |
| `sourceLink` | Taobao or shop URL, or null. |
| `fbRank`, `fbViews`, `fbEngagement`, `fbPosts` | Optional. Comment says they are not persisted in the catalog Blob. |

`sassy-closet-shop/data/popular-order.json` is the popular-order list. `sassy-closet-shop/lib/popular-rank.ts` imports it as `@/data/popular-order.json` and reads its `order` and `scores` keys. `sassy-closet-shop/lib/products.ts` sorts visible looks with `sortByPopular` from that module. `fb-ma-rank.json`, `intake-extras.json`, `local-product-files.json`, and `taobao_confirm_seed.json` also sit in `sassy-closet-shop/data/`. A second `taobao_confirm_seed.json` is in `sassy-closet-shop/public/data/`. Treat them as data the shop bundle ships. Do not guess a field that the type does not name.

### Fixtures

`data/fixtures/` and `docs/fixtures/` are test inputs (caption lint, meta inventory, seed-vs-live sell dollars, OneDrive mirror comparison, price drift). `data/price-drift/` holds a committed report and an observed-sell JSON. They are not the live catalog.

## Catalog read order

Blob, then KV, then local file, then seed. Corrupt JSON does not fall through. Details: [pitfalls.md](pitfalls.md) and `sassy-closet-shop/lib/catalog-store.ts`.
