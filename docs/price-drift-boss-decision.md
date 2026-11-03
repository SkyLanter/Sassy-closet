# Price drift — Boss decision sheet (piece 259)

**No dollars applied.** Nothing changes live prices, Blob, `products.json` sell dollars or intake `sell_usd`. **Boss picks which column wins** for each mã.

Sources: live shop PDP snapshot 2026-10-28 ~11:18 PM PT (62 mãs, same as Oct 22 catalog), hub `sassycloset.xlsx` All, intake store `/api/submissions` (prices only), seed `sassy-closet-shop/data/products.json` (40 mãs). Overnight audit proof-241 / draft PR #193. Costs, links and customer data are not included.

## 1. The 13 intake vs live gaps (#193) — hub and intake agree, live is different
| mã | live | hub = intake | diff (live − hub) |
|---|---|---|---|
| A01 | 27 | 25 | +2 |
| A02 | 23 | 22 | +1 |
| A03 | 22 | 19 | +3 |
| A04 | 21 | 20 | +1 |
| B01 | 46 | 41 | +5 |
| B02 | 31 | 30 | +1 |
| J01 | 29 | 30 | −1 |
| J02 | 40 | 35 | +5 |
| K01 | 36 | 37 | −1 |
| P03 | 11 | 18 | **−7** |
| P04 | 10 | 13 | −3 |
| P05 | 25 | 23 | +2 |
| S01 | 39 | 28 | **+11** |

## 2. Hub-ten drifts
Hub ten = A01, A02, S01, P01–P05, K01, H01. Seven of them drift: A01, A02, S01, P03, P04, P05, K01. P01, P02 and H01 match.

## 3. S06
Live $25, hub $25, Oct 22 catalog $25, **intake `sell_usd` blank**, not in the seed file, no OneDrive mirror row. The S06 $25 lock stays as it is. The only open question is whether to fill the blank intake field with 25 later. That needs Boss's OK.

## 4. OneDrive mirror only (stale)
D05: OneDrive 28 vs live 26. V03: OneDrive 24 vs live 21.

## 5. Full table incl. seed `products.json` (output of `python3 scripts/price_drift_report.py`)
"—" in hub/intake means the mã is not in the drift fixture (hub matched live in proof-241) or the field is blank (S06 intake). Many seed values are older pre-reprice dollars: 23 mãs differ from live in the seed only. The seed is a local fallback; live reads Blob.

| mã | live | hub | intake | seed products.json |
|---|---|---|---|---|
| A01 | 27 | 25 | 25 | 27 |
| A02 | 23 | 22 | 22 | 23 |
| A03 | 22 | 19 | 19 | 25 |
| A04 | 21 | 20 | 20 | 23 |
| A05 | 25 | — | — | 28 |
| A06 | 23 | — | — | 26 |
| A07 | 26 | — | — | 28 |
| A08 | 29 | — | — | 32 |
| A09 | 26 | — | — | 28 |
| A10 | 29 | — | — | 31 |
| A11 | 27 | — | — | 29 |
| A12 | 29 | — | — | 32 |
| A13 | 25 | — | — | 27 |
| A14 | 24 | — | — | 26 |
| A15 | 25 | — | — | 27 |
| B01 | 46 | 41 | 41 | 45 |
| B02 | 31 | 30 | 30 | 25 |
| D01 | 40 | — | — | 46 |
| D02 | 40 | — | — | 46 |
| D03 | 31 | — | — | 34 |
| J01 | 29 | 30 | 30 | 32 |
| J02 | 40 | 35 | 35 | 46 |
| K01 | 36 | 37 | 37 | 36 |
| O01 | 22 | — | — | 21 |
| O02 | 24 | — | — | 21 |
| O03 | 7 | — | — | 6 |
| O05 | 15 | — | — | 14 |
| P03 | 11 | 18 | 18 | 11 |
| P04 | 10 | 13 | 13 | 10 |
| P05 | 25 | 23 | 23 | 25 |
| Q01 | 28 | — | — | 30 |
| S01 | 39 | 28 | 28 | 39 |
| S02 | 25 | — | — | 28 |
| S03 | 26 | — | — | 29 |
| S04 | 41 | — | — | 48 |
| S06 | 25 | 25 | — | — |

No dollars applied. Boss picks which column wins.

## Boss picks (none applied)
1. For the 13 gaps: live wins (update hub + intake later), hub/intake wins (reprice live), or pick per mã. P03 and S01 are the largest.
2. Seed `products.json`: refresh it from live, or leave it as a fallback.
3. S06 intake blank: fill 25, or leave it.
4. OneDrive mirror D05/V03: refresh, or ignore as stale.

## S06 blank intake sell_usd (piece-261)
- Live shop: S06 = **$25**. Hub: $25. Oct 22 good catalog: $25.
- Intake `sell_usd` for S06: **blank**. Seed `sassy-closet-shop/data/products.json`: **no S06 row**.
- `scripts/price_drift_report.py` now prints `S06 intake check: WARN` while the intake field is blank, and FAIL if intake or live S06 is ever anything but $25. `--strict` exits 1 on WARN/FAIL.
- The check is read-only. It never fills intake, Blob, or products.json. Filling the intake field with 25 needs **Boss's OK**. The S06 $25 lock does not change.
