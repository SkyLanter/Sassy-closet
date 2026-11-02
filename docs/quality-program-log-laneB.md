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
