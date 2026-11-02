# Lane B quality log

## 2026-11-02 pass 1

Read-only checker: `scripts/parity_check.py` (probes `scripts/parity_probe_intake.ts` and `scripts/parity_probe_shop.ts`). No catalog price was edited. `data/held.json` was not edited.

Checker: code fails 0, Boss notes 14.

A named `costCurrency` on `wouldBeLiveUsd` now follows intake (USD uses `costUsd`, then yen). Omitting the field still prefers yen. On A04 with ¥100 and $10, the omitted quote is 23 and the blank-currency intake quote is 16. Nothing was stored.

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

Hard recheck: recorded after the run.
