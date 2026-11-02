# Excel columns from the scrubbed snapshot

Source: `/cursor/stores/bot/knowledge-snapshot/INDEX.md` (workbook table and Gaps), checked against `excel/_sheets.json` and the header tables in `excel/*.md`, on 2026-11-02. The snapshot says it is read-only, PII-scrubbed, and rechecked. Example rows are not copied. Dollar amounts and supplier links from those rows are not copied.

Every meaning cell in the export is the snapshot's own `unknown (header only: <header>)`. There is no data dictionary. The tables below list the headers so the schema is in git. They do not add a meaning the snapshot did not write.

`INDEX.md`'s workbook table names **11 exported files**. It does not name a twelfth exported workbook.

The table writes paths with an underscore (`Documents/Sassy_Closet/`, `Sassy_Closet/`). The Gaps section writes the same two Taobao files with a space (`Documents/Sassy Closet/`, `Sassy Closet/`). `ONEDRIVE_SHOP_DIR` in `excel-kit/schema.py` is `Documents/Sassy Closet`. This page does not treat the underscore form and the space form as proven to be the same directory. Row counts are what tie the two Taobao strings to the two exports.

## Workbooks in the export

Non-empty row counts are the INDEX table (same counts as `_sheets.json`).

| Workbook in the INDEX table | Sheets (non-empty rows, columns) |
| --- | --- |
| `Documents/Sassy_Closet/Finance.xlsx` | Sales 0×19, Fees 0×6, Payouts_Transfers 0×6, Expenses 0×7, Tax_Summary 19×15, Readme 6×1 |
| `Documents/Sassy_Closet/PHOTO_COMPLETENESS_2026-09-18.xlsx` | PHOTO_COMPLETENESS 40×11 |
| `Documents/Sassy_Closet/Photo_Color_Map.xlsx` | Photo Color Map 71×12 |
| `Documents/Sassy_Closet/Size_Report_2026-09-18.xlsx` | Size Report 40×16, SizeChart Detail 40×6 |
| `Documents/Sassy_Closet/Size_Report_BuyResearch_2026-09-18.xlsx` | Size Report BuyResearch 40×10 |
| `Documents/Sassy_Closet/Square.xlsx` | On_Hand 0×16, Sold_Log 0×5, Readme 4×1 |
| `Documents/Sassy_Closet/TAOBAO_PULL_MASTER.xlsx` | Items 40×31, Colors 110×8, Sizes 82×3, Photos 231×11, Prices 35×16, Missing 0×8, Notes 14×2 |
| `Documents/Sassy_Closet/Taobao_Audit_2026-09-18.xlsx` | Taobao Audit 40×19 |
| `Documents/Sassy_Closet/sassycloset.xlsx` | Official 62×20 |
| `Sassy_Closet/TAOBAO_PULL_MASTER.xlsx` | Items 35×31, Colors 110×8, Sizes 82×3, Photos 231×11, Prices 35×16, Missing 5×8, Notes 14×2 |
| `root/Book.xlsx` | Sheet1 0×0 (empty) |

Empty data sheets named by INDEX: Finance Sales, Fees, Payouts_Transfers, Expenses; Square On_Hand and Sold_Log; Documents `TAOBAO_PULL_MASTER` Missing; `Book.xlsx` Sheet1.

## UNKNOWN, from INDEX Gaps

- `Sassy_Closet_Order_Log.xlsx` and `Sassy_Closet_Wishlist.xlsx` sit at the OneDrive drive root. INDEX says both fail zip CRC/inflate, a re-download was byte-identical, and the stored files are damaged. They were not exported. Their columns are UNKNOWN.
- Which `TAOBAO_PULL_MASTER.xlsx` is canonical is UNKNOWN. INDEX: `Sassy Closet/` has Items 35 and Missing 5 (modified 2026-09-23 PT); `Documents/Sassy Closet/` has Items 40 and Missing 0.
- Whether `Documents/Sassy Closet/sassycloset.xlsx` is the hub is UNKNOWN. INDEX says that is an assumption (sheet `Official`, 62 rows) and that no note confirms it.
- `Sassy_Closet_SoT.xlsx` is not in the export. Live SoT columns stay the ones in `excel-kit/schema.py`. Cell values on the live file are UNKNOWN.
- `Sassy_Closet_Official_desktop.xlsx` and `Sassy_Closet_Wishlist_desktop.xlsx` are named in `schema.py` and are not in this export. The drive-root `Sassy_Closet_Wishlist.xlsx` above is a different filename.
- No exported file is named as a floor tracker. Open PR #7's title names `Sassy_Closet_Data.xlsx`. That file is not in the export.
- Not exported, so not schema here: `tb_verify/2026-09-23/`, Photos, and non-xlsx files INDEX names (`TAOBAO_PULL_MASTER.csv`, `intake-export-now.csv`, briefs).

## Readme lines that are not column meanings

These are the snapshot's own Readme sentences, not inventory rows. Column meanings above them stay header-only.

- Finance Readme header: the book is tax-ready for San Jose, California, and Sales / Fees / Payouts_Transfers / Expenses start empty. A later line says a Square sale becomes one Sales row (`square_xlsx_ma` plus `Sold_Log.finance_ref`) and that Square `cost_usd` is copied into `cogs_usd`. Another line states San Jose combined sales tax as 10.000% (CDTFA, effective 2026-04-01) and separates sales tax on the sell price from income tax on profit. The snapshot also has a numeric example shape. Those numbers are not copied.
- Square Readme header: the book tracks bought / on-hand pieces; On_Hand starts empty; staged site mãs are not bought. Later lines say the Square Free Dashboard is the on-hand source of truth and this workbook is the team tracker, not a second warehouse. A sale sets `qty_on_hand` to 0, `status` to sold, and `sold_date`, and writes Sold_Log plus a Finance Sales row. `photo_folder` in that line is `Documents/Sassy Closet/Photos/{ma}/` (space, not underscore).

## Documents/Sassy_Closet/Finance.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__Finance.md`.

### Sheet `Sales`

Header row 1. Non-empty data rows: 0. Dims: A1:S21.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `date` | unknown (header only: date) |
| 2 | `ma` | unknown (header only: ma) |
| 3 | `description` | unknown (header only: description) |
| 4 | `qty` | unknown (header only: qty) |
| 5 | `gross_usd` | unknown (header only: gross_usd) |
| 6 | `ship_usd` | unknown (header only: ship_usd) |
| 7 | `discount_usd` | unknown (header only: discount_usd) |
| 8 | `net_usd` | unknown (header only: net_usd) |
| 9 | `pay_method` | unknown (header only: pay_method) |
| 10 | `pay_ref` | unknown (header only: pay_ref) |
| 11 | `customer_note` | unknown (header only: customer_note) |
| 12 | `channel` | unknown (header only: channel) |
| 13 | `square_xlsx_ma` | unknown (header only: square_xlsx_ma) |
| 14 | `tax_category` | unknown (header only: tax_category) |
| 15 | `cogs_usd` | unknown (header only: cogs_usd) |
| 16 | `taxable_base_usd` | unknown (header only: taxable_base_usd) |
| 17 | `sales_tax_rate` | unknown (header only: sales_tax_rate) |
| 18 | `sales_tax_usd` | unknown (header only: sales_tax_usd) |
| 19 | `notes` | unknown (header only: notes) |

### Sheet `Fees`

Header row 1. Non-empty data rows: 0. Dims: A1:F21.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `date` | unknown (header only: date) |
| 2 | `source` | unknown (header only: source) |
| 3 | `amount_usd` | unknown (header only: amount_usd) |
| 4 | `fee_type` | unknown (header only: fee_type) |
| 5 | `related_sale_ref` | unknown (header only: related_sale_ref) |
| 6 | `notes` | unknown (header only: notes) |

### Sheet `Payouts_Transfers`

Header row 1. Non-empty data rows: 0. Dims: A1:F21.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `date` | unknown (header only: date) |
| 2 | `from_method` | unknown (header only: from_method) |
| 3 | `to_account_note` | unknown (header only: to_account_note) |
| 4 | `amount_usd` | unknown (header only: amount_usd) |
| 5 | `confirmation` | unknown (header only: confirmation) |
| 6 | `notes` | unknown (header only: notes) |

### Sheet `Expenses`

Header row 1. Non-empty data rows: 0. Dims: A1:G21.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `date` | unknown (header only: date) |
| 2 | `vendor` | unknown (header only: vendor) |
| 3 | `category` | unknown (header only: category) |
| 4 | `amount_usd` | unknown (header only: amount_usd) |
| 5 | `payment_method` | unknown (header only: payment_method) |
| 6 | `receipt_note` | unknown (header only: receipt_note) |
| 7 | `notes` | unknown (header only: notes) |

### Sheet `Tax_Summary`

Header row 1. Non-empty data rows: 19. Dims: A1:O20.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `metric` | unknown (header only: metric) |
| 2 | `2026-01` | unknown (header only: 2026-01) |
| 3 | `2026-02` | unknown (header only: 2026-02) |
| 4 | `2026-03` | unknown (header only: 2026-03) |
| 5 | `2026-04` | unknown (header only: 2026-04) |
| 6 | `2026-05` | unknown (header only: 2026-05) |
| 7 | `2026-06` | unknown (header only: 2026-06) |
| 8 | `2026-07` | unknown (header only: 2026-07) |
| 9 | `2026-08` | unknown (header only: 2026-08) |
| 10 | `2026-09` | unknown (header only: 2026-09) |
| 11 | `2026-10` | unknown (header only: 2026-10) |
| 12 | `2026-11` | unknown (header only: 2026-11) |
| 13 | `2026-12` | unknown (header only: 2026-12) |
| 14 | `YTD` | unknown (header only: YTD) |
| 15 | `accountant_note` | unknown (header only: accountant_note) |

### Sheet `Readme`

Header row 1. Non-empty data rows: 6. Dims: A1:A7.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `Finance.xlsx is tax-ready for San Jose, California. Sales / Fees / Payouts_Transfers / Expenses start empty — no invented sales or $.` | unknown (header only: Finance.xlsx is tax-ready for San Jose, California. Sales / Fees / Payouts_Transfers / Expenses start empty — no invented sales or $.) |

## Documents/Sassy_Closet/PHOTO_COMPLETENESS_2026-09-18.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__PHOTO_COMPLETENESS_2026-09-18.md`.

### Sheet `PHOTO_COMPLETENESS`

Header row 1. Non-empty data rows: 40. Dims: A1:K41.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `photo_count_before` | unknown (header only: photo_count_before) |
| 3 | `photo_count_after` | unknown (header only: photo_count_after) |
| 4 | `urls_found` | unknown (header only: urls_found) |
| 5 | `downloaded` | unknown (header only: downloaded) |
| 6 | `colors_detected` | unknown (header only: colors_detected) |
| 7 | `sizes_visible` | unknown (header only: sizes_visible) |
| 8 | `public_preselect` | unknown (header only: public_preselect) |
| 9 | `gaps` | unknown (header only: gaps) |
| 10 | `sku_colors_cn` | unknown (header only: sku_colors_cn) |
| 11 | `hub_colors` | unknown (header only: hub_colors) |

## Documents/Sassy_Closet/Photo_Color_Map.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__Photo_Color_Map.md`.

### Sheet `Photo Color Map`

Header row 1. Non-empty data rows: 71. Dims: A1:L72.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `MA` | unknown (header only: MA) |
| 2 | `File` | unknown (header only: File) |
| 3 | `Rel Path` | unknown (header only: Rel Path) |
| 4 | `Detected VI` | unknown (header only: Detected VI) |
| 5 | `CN Hint (listing)` | unknown (header only: CN Hint (listing)) |
| 6 | `Confidence` | unknown (header only: Confidence) |
| 7 | `R` | unknown (header only: R) |
| 8 | `G` | unknown (header only: G) |
| 9 | `B` | unknown (header only: B) |
| 10 | `SKU Colors Listing` | unknown (header only: SKU Colors Listing) |
| 11 | `colorId` | unknown (header only: colorId) |
| 12 | `shared` | unknown (header only: shared) |

## Documents/Sassy_Closet/Size_Report_2026-09-18.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__Size_Report_2026-09-18.md`.

### Sheet `Size Report`

Header row 1. Non-empty data rows: 40. Dims: A1:P41.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `MA` | unknown (header only: MA) |
| 2 | `Kind` | unknown (header only: Kind) |
| 3 | `Title CN` | unknown (header only: Title CN) |
| 4 | `Hub Size` | unknown (header only: Hub Size) |
| 5 | `Hub Sizes Parsed` | unknown (header only: Hub Sizes Parsed) |
| 6 | `Sizes SKU Public` | unknown (header only: Sizes SKU Public) |
| 7 | `Capacity ml` | unknown (header only: Capacity ml) |
| 8 | `Size Chart cm` | unknown (header only: Size Chart cm) |
| 9 | `Size Note` | unknown (header only: Size Note) |
| 10 | `Sizes Source` | unknown (header only: Sizes Source) |
| 11 | `Hub Color` | unknown (header only: Hub Color) |
| 12 | `SKU Colors CN` | unknown (header only: SKU Colors CN) |
| 13 | `Flags` | unknown (header only: Flags) |
| 14 | `Hub Color Note` | unknown (header only: Hub Color Note) |
| 15 | `Item ID` | unknown (header only: Item ID) |
| 16 | `SKU Infos Raw` | unknown (header only: SKU Infos Raw) |

### Sheet `SizeChart Detail`

Header row 1. Non-empty data rows: 40. Dims: A1:F41.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `MA` | unknown (header only: MA) |
| 2 | `size_chart_cm` | unknown (header only: size_chart_cm) |
| 3 | `size_note` | unknown (header only: size_note) |
| 4 | `sizes_sku_public` | unknown (header only: sizes_sku_public) |
| 5 | `capacity_ml` | unknown (header only: capacity_ml) |
| 6 | `notes` | unknown (header only: notes) |

## Documents/Sassy_Closet/Size_Report_BuyResearch_2026-09-18.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__Size_Report_BuyResearch_2026-09-18.md`.

### Sheet `Size Report BuyResearch`

Header row 1. Non-empty data rows: 40. Dims: A1:J41.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `kind_vi` | unknown (header only: kind_vi) |
| 3 | `hub_size` | unknown (header only: hub_size) |
| 4 | `live_size_skus` | unknown (header only: live_size_skus) |
| 5 | `chart_present` | unknown (header only: chart_present) |
| 6 | `chart_text_or_json` | unknown (header only: chart_text_or_json) |
| 7 | `capacity_ml` | unknown (header only: capacity_ml) |
| 8 | `mismatch_flags` | unknown (header only: mismatch_flags) |
| 9 | `source_urls` | unknown (header only: source_urls) |
| 10 | `pulled_at_pt` | unknown (header only: pulled_at_pt) |

## Documents/Sassy_Closet/Square.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__Square.md`.

### Sheet `On_Hand`

Header row 1. Non-empty data rows: 0. Dims: A1:P21.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `kind` | unknown (header only: kind) |
| 3 | `colors` | unknown (header only: colors) |
| 4 | `size` | unknown (header only: size) |
| 5 | `qty_on_hand` | unknown (header only: qty_on_hand) |
| 6 | `cost_cny` | unknown (header only: cost_cny) |
| 7 | `cost_usd` | unknown (header only: cost_usd) |
| 8 | `cost_currency` | unknown (header only: cost_currency) |
| 9 | `buy_date` | unknown (header only: buy_date) |
| 10 | `source_link` | unknown (header only: source_link) |
| 11 | `photo_folder` | unknown (header only: photo_folder) |
| 12 | `square_item_name` | unknown (header only: square_item_name) |
| 13 | `track_on` | unknown (header only: track_on) |
| 14 | `status` | unknown (header only: status) |
| 15 | `sold_date` | unknown (header only: sold_date) |
| 16 | `notes` | unknown (header only: notes) |

### Sheet `Sold_Log`

Header row 1. Non-empty data rows: 0. Dims: A1:E21.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `sold_date` | unknown (header only: sold_date) |
| 3 | `qty` | unknown (header only: qty) |
| 4 | `finance_ref` | unknown (header only: finance_ref) |
| 5 | `notes` | unknown (header only: notes) |

### Sheet `Readme`

Header row 1. Non-empty data rows: 4. Dims: A1:A5.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `Square.xlsx tracks bought / on-hand pieces for the team. On_Hand starts empty — staged site mãs are not bought.` | unknown (header only: Square.xlsx tracks bought / on-hand pieces for the team. On_Hand starts empty — staged site mãs are not bought.) |

## Documents/Sassy_Closet/TAOBAO_PULL_MASTER.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__TAOBAO_PULL_MASTER.md`.

### Sheet `Items`

Header row 1. Non-empty data rows: 40. Dims: A1:AE41.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `status_pull` | unknown (header only: status_pull) |
| 3 | `title` | unknown (header only: title) |
| 4 | `item_id` | unknown (header only: item_id) |
| 5 | `source_link` | unknown (header only: source_link) |
| 6 | `world_url` | unknown (header only: world_url) |
| 7 | `opened_url` | unknown (header only: opened_url) |
| 8 | `logged_in_account` | unknown (header only: logged_in_account) |
| 9 | `colors_cn` | unknown (header only: colors_cn) |
| 10 | `colors_en` | unknown (header only: colors_en) |
| 11 | `sizes` | unknown (header only: sizes) |
| 12 | `coupon_after_yuan` | unknown (header only: coupon_after_yuan) |
| 13 | `before_yuan` | unknown (header only: before_yuan) |
| 14 | `yuan_used` | unknown (header only: yuan_used) |
| 15 | `yuan_source` | unknown (header only: yuan_source) |
| 16 | `fx_cny_per_usd` | unknown (header only: fx_cny_per_usd) |
| 17 | `cost_usd` | unknown (header only: cost_usd) |
| 18 | `ship_est_usd` | unknown (header only: ship_est_usd) |
| 19 | `ship_range_usd` | unknown (header only: ship_range_usd) |
| 20 | `ship_note` | unknown (header only: ship_note) |
| 21 | `landed_usd` | unknown (header only: landed_usd) |
| 22 | `margin_target` | unknown (header only: margin_target) |
| 23 | `sell_raw` | unknown (header only: sell_raw) |
| 24 | `recommend_price_usd` | unknown (header only: recommend_price_usd) |
| 25 | `photo_count` | unknown (header only: photo_count) |
| 26 | `public_default_photos_preselected` | unknown (header only: public_default_photos_preselected) |
| 27 | `confirm_preselect` | unknown (header only: confirm_preselect) |
| 28 | `status_suggestion` | unknown (header only: status_suggestion) |
| 29 | `preserve_live_available` | unknown (header only: preserve_live_available) |
| 30 | `captured_at` | unknown (header only: captured_at) |
| 31 | `notes` | unknown (header only: notes) |

### Sheet `Colors`

Header row 1. Non-empty data rows: 110. Dims: A1:H111.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `color_cn` | unknown (header only: color_cn) |
| 3 | `color_en` | unknown (header only: color_en) |
| 4 | `chip_image` | unknown (header only: chip_image) |
| 5 | `photo_redirect_files` | unknown (header only: photo_redirect_files) |
| 6 | `photo_redirect` | unknown (header only: photo_redirect) |
| 7 | `preselected_in_confirm` | unknown (header only: preselected_in_confirm) |
| 8 | `translate_how` | unknown (header only: translate_how) |

### Sheet `Sizes`

Header row 1. Non-empty data rows: 82. Dims: A1:C83.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `size` | unknown (header only: size) |
| 3 | `preselected_in_confirm` | unknown (header only: preselected_in_confirm) |

### Sheet `Photos`

Header row 1. Non-empty data rows: 231. Dims: A1:K232.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `file` | unknown (header only: file) |
| 3 | `url` | unknown (header only: url) |
| 4 | `bytes` | unknown (header only: bytes) |
| 5 | `index` | unknown (header only: index) |
| 6 | `public_default_preselected` | unknown (header only: public_default_preselected) |
| 7 | `public_default_candidate` | unknown (header only: public_default_candidate) |
| 8 | `mapped_color_cn` | unknown (header only: mapped_color_cn) |
| 9 | `mapped_color_en` | unknown (header only: mapped_color_en) |
| 10 | `local_path` | unknown (header only: local_path) |
| 11 | `boss_note` | unknown (header only: boss_note) |

### Sheet `Prices`

Header row 1. Non-empty data rows: 35. Dims: A1:P36.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `title` | unknown (header only: title) |
| 3 | `coupon_after_yuan` | unknown (header only: coupon_after_yuan) |
| 4 | `before_yuan` | unknown (header only: before_yuan) |
| 5 | `yuan_used` | unknown (header only: yuan_used) |
| 6 | `yuan_source` | unknown (header only: yuan_source) |
| 7 | `fx_cny_per_usd` | unknown (header only: fx_cny_per_usd) |
| 8 | `cost_usd` | unknown (header only: cost_usd) |
| 9 | `ship_est_usd` | unknown (header only: ship_est_usd) |
| 10 | `ship_range_usd` | unknown (header only: ship_range_usd) |
| 11 | `landed_usd` | unknown (header only: landed_usd) |
| 12 | `gm_target` | unknown (header only: gm_target) |
| 13 | `sell_raw` | unknown (header only: sell_raw) |
| 14 | `recommend_price_usd` | unknown (header only: recommend_price_usd) |
| 15 | `boss_confirm_required` | unknown (header only: boss_confirm_required) |
| 16 | `note` | unknown (header only: note) |

### Sheet `Missing`

Header row 1. Non-empty data rows: 0. Dims: A1:H1.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `status` | unknown (header only: status) |
| 3 | `item_id` | unknown (header only: item_id) |
| 4 | `title_cn` | unknown (header only: title_cn) |
| 5 | `note` | unknown (header only: note) |
| 6 | `queries` | unknown (header only: queries) |
| 7 | `source_link` | unknown (header only: source_link) |
| 8 | `world_url` | unknown (header only: world_url) |

### Sheet `Notes`

Header row 1. Non-empty data rows: 14. Dims: A1:B15.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `Field` | unknown (header only: Field) |
| 2 | `Value` | unknown (header only: Value) |

## Documents/Sassy_Closet/Taobao_Audit_2026-09-18.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__Taobao_Audit_2026-09-18.md`.

### Sheet `Taobao Audit`

Header row 1. Non-empty data rows: 40. Dims: A1:S41.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `MA` | unknown (header only: MA) |
| 2 | `Source Link (short)` | unknown (header only: Source Link (short)) |
| 3 | `Item ID` | unknown (header only: Item ID) |
| 4 | `Title CN` | unknown (header only: Title CN) |
| 5 | `Shop` | unknown (header only: Shop) |
| 6 | `Live Share CNY (price=)` | unknown (header only: Live Share CNY (price=)) |
| 7 | `Live World CNY (promotionPrice)` | unknown (header only: Live World CNY (promotionPrice)) |
| 8 | `Live Price Note` | unknown (header only: Live Price Note) |
| 9 | `Colors SKU CN` | unknown (header only: Colors SKU CN) |
| 10 | `Colors VN Note` | unknown (header only: Colors VN Note) |
| 11 | `Sizes SKU` | unknown (header only: Sizes SKU) |
| 12 | `Photo Count` | unknown (header only: Photo Count) |
| 13 | `Photo Dir` | unknown (header only: Photo Dir) |
| 14 | `Hub Color` | unknown (header only: Hub Color) |
| 15 | `Hub Cost CNY` | unknown (header only: Hub Cost CNY) |
| 16 | `Hub Cost USD` | unknown (header only: Hub Cost USD) |
| 17 | `Mismatch Flags` | unknown (header only: Mismatch Flags) |
| 18 | `Pulled At PT` | unknown (header only: Pulled At PT) |
| 19 | `World URL` | unknown (header only: World URL) |

## Documents/Sassy_Closet/sassycloset.xlsx

Snapshot file: `excel/Documents__Sassy_Closet__sassycloset.md`.

### Sheet `Official`

Header row 1. Non-empty data rows: 62. Dims: A1:T63.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `status` | unknown (header only: status) |
| 3 | `cost_usd` | unknown (header only: cost_usd) |
| 4 | `source_link` | unknown (header only: source_link) |
| 5 | `photo_link` | unknown (header only: photo_link) |
| 6 | `created_at` | unknown (header only: created_at) |
| 7 | `updated_at` | unknown (header only: updated_at) |
| 8 | `kind` | unknown (header only: kind) |
| 9 | `kind_vi` | unknown (header only: kind_vi) |
| 10 | `size` | unknown (header only: size) |
| 11 | `color` | unknown (header only: color) |
| 12 | `color_note` | unknown (header only: color_note) |
| 13 | `color_pieces` | unknown (header only: color_pieces) |
| 14 | `blurb` | unknown (header only: blurb) |
| 15 | `cost_cny` | unknown (header only: cost_cny) |
| 16 | `cost_currency` | unknown (header only: cost_currency) |
| 17 | `sell_cny` | unknown (header only: sell_cny) |
| 18 | `sell_usd` | unknown (header only: sell_usd) |
| 19 | `sell_currency` | unknown (header only: sell_currency) |
| 20 | `square` | unknown (header only: square) |

## Sassy_Closet/TAOBAO_PULL_MASTER.xlsx

Snapshot file: `excel/Sassy_Closet__TAOBAO_PULL_MASTER.md`.

### Sheet `Items`

Header row 1. Non-empty data rows: 35. Dims: A1:AE36.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `status_pull` | unknown (header only: status_pull) |
| 3 | `title` | unknown (header only: title) |
| 4 | `item_id` | unknown (header only: item_id) |
| 5 | `source_link` | unknown (header only: source_link) |
| 6 | `world_url` | unknown (header only: world_url) |
| 7 | `opened_url` | unknown (header only: opened_url) |
| 8 | `logged_in_account` | unknown (header only: logged_in_account) |
| 9 | `colors_cn` | unknown (header only: colors_cn) |
| 10 | `colors_en` | unknown (header only: colors_en) |
| 11 | `sizes` | unknown (header only: sizes) |
| 12 | `coupon_after_yuan` | unknown (header only: coupon_after_yuan) |
| 13 | `before_yuan` | unknown (header only: before_yuan) |
| 14 | `yuan_used` | unknown (header only: yuan_used) |
| 15 | `yuan_source` | unknown (header only: yuan_source) |
| 16 | `fx_cny_per_usd` | unknown (header only: fx_cny_per_usd) |
| 17 | `cost_usd` | unknown (header only: cost_usd) |
| 18 | `ship_est_usd` | unknown (header only: ship_est_usd) |
| 19 | `ship_range_usd` | unknown (header only: ship_range_usd) |
| 20 | `ship_note` | unknown (header only: ship_note) |
| 21 | `landed_usd` | unknown (header only: landed_usd) |
| 22 | `margin_target` | unknown (header only: margin_target) |
| 23 | `sell_raw` | unknown (header only: sell_raw) |
| 24 | `recommend_price_usd` | unknown (header only: recommend_price_usd) |
| 25 | `photo_count` | unknown (header only: photo_count) |
| 26 | `public_default_photos_preselected` | unknown (header only: public_default_photos_preselected) |
| 27 | `confirm_preselect` | unknown (header only: confirm_preselect) |
| 28 | `status_suggestion` | unknown (header only: status_suggestion) |
| 29 | `preserve_live_available` | unknown (header only: preserve_live_available) |
| 30 | `captured_at` | unknown (header only: captured_at) |
| 31 | `notes` | unknown (header only: notes) |

### Sheet `Colors`

Header row 1. Non-empty data rows: 110. Dims: A1:H111.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `color_cn` | unknown (header only: color_cn) |
| 3 | `color_en` | unknown (header only: color_en) |
| 4 | `chip_image` | unknown (header only: chip_image) |
| 5 | `photo_redirect_files` | unknown (header only: photo_redirect_files) |
| 6 | `photo_redirect` | unknown (header only: photo_redirect) |
| 7 | `preselected_in_confirm` | unknown (header only: preselected_in_confirm) |
| 8 | `translate_how` | unknown (header only: translate_how) |

### Sheet `Sizes`

Header row 1. Non-empty data rows: 82. Dims: A1:C83.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `size` | unknown (header only: size) |
| 3 | `preselected_in_confirm` | unknown (header only: preselected_in_confirm) |

### Sheet `Photos`

Header row 1. Non-empty data rows: 231. Dims: A1:K232.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `file` | unknown (header only: file) |
| 3 | `url` | unknown (header only: url) |
| 4 | `bytes` | unknown (header only: bytes) |
| 5 | `index` | unknown (header only: index) |
| 6 | `public_default_preselected` | unknown (header only: public_default_preselected) |
| 7 | `public_default_candidate` | unknown (header only: public_default_candidate) |
| 8 | `mapped_color_cn` | unknown (header only: mapped_color_cn) |
| 9 | `mapped_color_en` | unknown (header only: mapped_color_en) |
| 10 | `local_path` | unknown (header only: local_path) |
| 11 | `boss_note` | unknown (header only: boss_note) |

### Sheet `Prices`

Header row 1. Non-empty data rows: 35. Dims: A1:P36.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `title` | unknown (header only: title) |
| 3 | `coupon_after_yuan` | unknown (header only: coupon_after_yuan) |
| 4 | `before_yuan` | unknown (header only: before_yuan) |
| 5 | `yuan_used` | unknown (header only: yuan_used) |
| 6 | `yuan_source` | unknown (header only: yuan_source) |
| 7 | `fx_cny_per_usd` | unknown (header only: fx_cny_per_usd) |
| 8 | `cost_usd` | unknown (header only: cost_usd) |
| 9 | `ship_est_usd` | unknown (header only: ship_est_usd) |
| 10 | `ship_range_usd` | unknown (header only: ship_range_usd) |
| 11 | `landed_usd` | unknown (header only: landed_usd) |
| 12 | `gm_target` | unknown (header only: gm_target) |
| 13 | `sell_raw` | unknown (header only: sell_raw) |
| 14 | `recommend_price_usd` | unknown (header only: recommend_price_usd) |
| 15 | `boss_confirm_required` | unknown (header only: boss_confirm_required) |
| 16 | `note` | unknown (header only: note) |

### Sheet `Missing`

Header row 1. Non-empty data rows: 5. Dims: A1:H6.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `ma` | unknown (header only: ma) |
| 2 | `status` | unknown (header only: status) |
| 3 | `item_id` | unknown (header only: item_id) |
| 4 | `title_cn` | unknown (header only: title_cn) |
| 5 | `note` | unknown (header only: note) |
| 6 | `queries` | unknown (header only: queries) |
| 7 | `source_link` | unknown (header only: source_link) |
| 8 | `world_url` | unknown (header only: world_url) |

### Sheet `Notes`

Header row 1. Non-empty data rows: 14. Dims: A1:B15.

| # | Header | Meaning in the snapshot |
| --- | --- | --- |
| 1 | `Field` | unknown (header only: Field) |
| 2 | `Value` | unknown (header only: Value) |

## root/Book.xlsx

Snapshot file: `excel/root__Book.md`.

### Sheet `Sheet1`

The snapshot markdown says this sheet is empty. `_sheets.json` lists 0 non-empty rows and 0 columns. No headers.

