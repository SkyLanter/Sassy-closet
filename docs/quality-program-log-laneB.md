# Lane B quality log

## 2026-11-02 pass 1

Read-only checker: `scripts/parity_check.py` (probes `scripts/parity_probe_intake.ts` and `scripts/parity_probe_shop.ts`). No catalog price was edited. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 14.

A named cost currency on `wouldBeLiveUsd` now follows intake. Omitting the field still prefers the yen figure when both cost fields are set. On A04 the omitted quote is 23 and the blank-currency intake quote is 16. Nothing was stored.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shoe windows disagree: autolist 33–46, shop parse 34–42, intake and Excel 35–41. Autolist treats O as a shoe; intake keeps clothing sizes for O.
- Official Excel prefixes do not cover intake letters D, B, H, J, and O.
- A $3 sell on a $1 landed cost clears the 35% caption floor and fails the tier quote. Caption copy was not changed.
- `wouldBeLiveUsd` rejects A1. `norm_ma` maps A1 to A01. The shop test locks the rejection.
- Shop `normalizeMa` does not collapse K003 to K03. Shop debox stays null off V, Q, and D.

Tier quotes, flat 25% quotes, clothing ladders, and the canonical mã helpers matched.

Hard recheck: PASS against origin/main after npm ci in both apps. pytest 2123 passed. Privacy CLEAN. Intake and shop test suites and tsc passed. held.json unchanged. No recheck step was SKIP.

## 2026-11-02 pass 2

Shop `parseAsiaSizes` now treats a single trailing `.0` as the two-digit EU size. `40.0` and `34.0` stay `40` and `34`. `34.00`, `34.5`, and strings such as `36 -37` stay dropped. Shop EU sizes stay 34–42. No catalog file was edited. `data/held.json` was not edited. No stored size in products or the Taobao seed was a trailing `.0`, so listed sizes on the page stay the same.

Checker: code fails 0, Boss notes 15. New Boss note `shoe-decimal-window`: autolist keeps `33.0` as 33 and `46.0` as 46; the shop window still drops both.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shoe windows disagree: autolist 33–46, shop parse 34–42, intake and Excel 35–41. Autolist treats O as a shoe; intake keeps clothing sizes for O.
- Official Excel prefixes do not cover intake letters D, B, H, J, and O.
- A $3 sell on a $1 landed cost clears the 35% caption floor and fails the tier quote. Caption copy was not changed.
- `wouldBeLiveUsd` rejects A1. `norm_ma` maps A1 to A01. The shop test locks the rejection.
- Shop `normalizeMa` does not collapse K003 to K03. Shop debox stays null off V, Q, and D.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. Intake follows a named USD currency. That shop path was not changed, because it would change the admin recommended sell.

Hard recheck: PASS against origin/main after npm ci in both apps, on 55d01e3. pytest 2125 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 220 pass, 217 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites.

## 2026-11-02 pass 3

The checker now records Boss note `shop-prefers-yen`. For kind Q, with both cost fields set, intake's named USD landed is 17.50 and shop `calcPricing` landed is 22.37. The shop figure matches the named CNY landed. `calcPricing` was not changed. No price was stored. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 16.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shoe windows disagree: autolist 33–46, shop parse 34–42, intake and Excel 35–41.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. Intake named USD uses the dollar cost.

Hard recheck: PASS against origin/main after npm ci in both apps, on 01a227e. pytest 2126 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 220 pass, 217 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites.

## 2026-11-02 pass 4

Shop intake import kept only Asia letters, so a G row sized `40.0 35,36` lost every size. Kind G now keeps the same EU tokens `parseAsiaSizes` keeps, including a single trailing `.0`. `33.0`, `43`, `34.5`, and `40.00` stay dropped. Clothing rows stay on letters. Kind O still drops `36`. No catalog price was edited. `data/held.json` was not edited. Customer catalog JSON was not edited.

Checker: code fails 0, Boss notes 17. New Boss note `import-kind-o`: autolist keeps 36 on O; the importer keeps the letter M and drops 36.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. For kind Q the named USD landed is 17.50 and the shop landed is 22.37. That formula was not changed.

Hard recheck: PASS against origin/main after npm ci in both apps, on 85d6849. pytest 2127 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 222 pass, 219 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites.

## 2026-11-02 pass 5

Intake `keepSizesForKind` treated `40.0` as a different chip from `40` and dropped it. A single trailing `.0` now stays the two-digit size when that size is already on the kind's list. Intake shoes stay 35–41, so `34.0` and `42.0` still drop. `40.00` still drops. Clothing still drops `40.0`. Kind O still drops `36.0`. No catalog price was edited. `data/held.json` was not edited. The intake form reload path was not changed.

Checker: code fails 0, Boss notes 17.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. For kind Q the named USD landed is 17.50 and the shop landed is 22.37. That formula was not changed.

Hard recheck: PASS against origin/main after npm ci in both apps, on acd5968. pytest 2128 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 222 pass, 219 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites.

## 2026-11-02 pass 6

The intake gap report flagged a shoe size written as `40.0` even when `40` is on that kind's list. A single trailing `.0` now counts as those two digits. The stored row is not rewritten. `34.0`, `42.0`, and `40.00` stay flagged on the intake shoe list 35–41. A clothing row still flags `40.0`. No catalog price was edited. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 17.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. For kind Q the named USD landed is 17.50 and the shop landed is 22.37. That formula was not changed.

Hard recheck: PASS against origin/main after npm ci in both apps, on ae06396. pytest 2130 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 222 pass, 219 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites.

## 2026-11-02 pass 7

The intake gap report split sizes only on comma and whitespace. A shoe size written `35;36` was one illegal token, while listing kept 35 and 36. Semicolon, slash, and pipe now split the same way. A value that is only separators, such as `;;;`, is no size. A single trailing `.0` still counts as the two digits when that size is on the kind's list. `35;44` still flags 44. The stored row is not rewritten. No catalog price was edited. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 17. Fail code `gap-size-split` is absent on this repo.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. For kind Q the named USD landed is 17.50 and the shop landed is 22.37. That formula was not changed.

Hard recheck: PASS against origin/main after npm ci in both apps, on 4409a7e. pytest 2132 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 222 pass, 219 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites. Log `out/recheck/20261102-230328-57290`.

## 2026-11-02 pass 8

The intake gap report flagged `XXS`, `XXL`, and `3XL` even when `2XS` or `2XL` was already on that kind's list. Listing already keeps those spellings as `2XS` and `2XL`. The report now uses the same alias table. A list that does not include `2XS` or `2XL` still flags the alias, and the stored spelling stays in the report. `4XL` stays flagged. Shoe sizes stay on the shoe list, so `XXS` on a shoe row stays flagged. The stored row is not rewritten. Shop intake import still drops `XXS`. Intake chips were not changed. No catalog price was edited. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 17. Fail code `gap-size-alias` is absent on this repo.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. For kind Q the named USD landed is 17.50 and the shop landed is 22.37. That formula was not changed.

Hard recheck: PASS against origin/main after npm ci in both apps, on 2102fcb. pytest 2134 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 222 pass, 219 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites. Log `out/recheck/20261102-232552-63320`.

## 2026-11-02 pass 9

Shop `parseAsiaSizes` keeps EU 40 from `40.`, `4.0`, `40码`, and `(40)`. Listing drops those tokens. A spaced range string in the Taobao seed, `36 -37(适合平时35-36码)`, is dropped by shop. Listing keeps 36 from that string. The checker records Boss note `shop-loose-shoe`. Neither parser was changed. `products.json` sizes are plain letters, so page sizes stay as they are. No catalog price was edited. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 18.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. For kind Q the named USD landed is 17.50 and the shop landed is 22.37. That formula was not changed.
- Shop keeps 40 from `40.`, `4.0`, `40码`, and `(40)`. Listing drops those tokens. Shop drops the spaced range string. Listing keeps 36.

Hard recheck: PASS against origin/main after npm ci in both apps, on e81f3cb. pytest 2135 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 222 pass, 219 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites. Log `out/recheck/20261102-234659-69776`.

## 2026-11-02 pass 10

`wouldBeLiveUsd` accepts one letter and exactly two digits, aside from the S06 rewrite. `A100` is already the canonical mã and is still rejected. `K003` canonicalizes to `K03` and is rejected instead of rewritten. The checker records Boss note `quote-ma-width`. The quote function was not changed. No quote was stored. No catalog price was edited. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 19.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. For kind Q the named USD landed is 17.50 and the shop landed is 22.37. That formula was not changed.
- `wouldBeLiveUsd` still rejects `A100` and `K003`. `A1` still maps to `A01` in `norm_ma` and is still rejected by the quote.

Hard recheck: PASS against origin/main after npm ci in both apps, on 895b45a. pytest 2136 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 222 pass, 219 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites. Log `out/recheck/20261103-000452-75765`.

## 2026-11-03 pass 11

Shop `parseAsiaSizes` and the size-gap letter scan keep one clothing letter when a seller note is glued on with no space. Listing drops that token. The intake gap report still flags the whole string. The four seed shapes are `M【建议80-100斤】` to M, `XXL【建议140-160斤】` to 2XL, `M女【推荐80-100斤】` to M, and `M（56-58cm）` to M. The checker records Boss note `glued-size-letter`. No size parser was changed. No catalog price was edited. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 20.

Boss, files left as they are:

- `sassy-closet-shop/data/intake-extras.json` has S06 at $26. The live snapshot has S06 at $25.
- Extras versus live snapshot: A16 34 vs 31, S05 25 vs 26, S06 26 vs 25, S07 44 vs 38, S08 35 vs 37, S09 42 vs 36, V01 25 vs 39, V02 31 vs 40.
- `products.json` versus the live snapshot: 28 mãs differ (A03 is 25 in the seed and 22 live). 22 live mãs are absent from the seed, including S06.
- Shop `calcPricing` still prefers the yen figure when both cost fields are set. For kind Q the named USD landed is 17.50 and the shop landed is 22.37. That formula was not changed.
- Shop still keeps a letter glued to a seller note. Listing still drops that token.

Hard recheck: PASS against origin/main after npm ci in both apps, on 19d2dab. pytest 2137 passed, 7 skipped. Privacy CLEAN. Intake tests 278 pass, 275 fail 0, skipped 3. Shop tests 222 pass, 219 fail 0, skipped 3. tsc passed in both apps. held.json unchanged. No recheck step was SKIP. The 7 and 3 skips are the existing empty never-list cases inside the suites. Log `out/recheck/20261103-002612-81780`.
