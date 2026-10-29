# Seed products.json vs live Blob — sell USD mismatch (read-only)

Piece 262. **Report only. No dollars changed anywhere.** The live shop reads Blob (`/api/health`: `reading=blob`, 62 mãs); the seed file `sassy-closet-shop/data/products.json` (40 mãs) is used only as a fallback if Blob is unreadable.

- Live side: `data/fixtures/seed-vs-live/live-sell-2026-10-22.json` (mã + sell `priceUsd` only, from the Oct 22 live catalog snapshot; midnight QC 2026-10-29 confirmed live = that snapshot 62/62).
- Regenerate: `python3 scripts/seed_vs_live_report.py` (prints; writes nothing; `--all` includes matches).

## Summary
- **28 price-diff** (both have the mã, dollars differ) — mostly seed higher than live.
- **22 live-only** (seed fallback lacks the mã, incl. S06 — live S06 = $25).
- **0 seed-only**, 12 match.

Risk: if Blob ever fails, the fallback would show 28 wrong prices and hide 22 mãs. Fixing the seed (e.g. regenerate from Blob) is a **Boss decision**; not done here.

## Table
| mã | seed $ | live $ | kind |
|---|---|---|---|
| A03 | $25 | $22 | price-diff |
| A04 | $23 | $21 | price-diff |
| A05 | $28 | $25 | price-diff |
| A06 | $26 | $23 | price-diff |
| A07 | $28 | $26 | price-diff |
| A08 | $32 | $29 | price-diff |
| A09 | $28 | $26 | price-diff |
| A10 | $31 | $29 | price-diff |
| A11 | $29 | $27 | price-diff |
| A12 | $32 | $29 | price-diff |
| A13 | $27 | $25 | price-diff |
| A14 | $26 | $24 | price-diff |
| A15 | $27 | $25 | price-diff |
| A16 | — | $31 | live-only |
| A17 | — | $27 | live-only |
| A18 | — | $27 | live-only |
| A19 | — | $27 | live-only |
| A20 | — | $23 | live-only |
| A21 | — | $21 | live-only |
| A22 | — | $33 | live-only |
| A23 | — | $27 | live-only |
| B01 | $45 | $46 | price-diff |
| B02 | $25 | $31 | price-diff |
| D01 | $46 | $40 | price-diff |
| D02 | $46 | $40 | price-diff |
| D03 | $34 | $31 | price-diff |
| D04 | — | $35 | live-only |
| D05 | — | $26 | live-only |
| J01 | $32 | $29 | price-diff |
| J02 | $46 | $40 | price-diff |
| O01 | $21 | $22 | price-diff |
| O02 | $21 | $24 | price-diff |
| O03 | $6 | $7 | price-diff |
| O05 | $14 | $15 | price-diff |
| Q01 | $30 | $28 | price-diff |
| S02 | $28 | $25 | price-diff |
| S03 | $29 | $26 | price-diff |
| S04 | $48 | $41 | price-diff |
| S05 | — | $26 | live-only |
| S06 | — | $25 | live-only |
| S07 | — | $38 | live-only |
| S08 | — | $37 | live-only |
| S09 | — | $36 | live-only |
| S10 | — | $37 | live-only |
| S11 | — | $51 | live-only |
| S12 | — | $33 | live-only |
| S13 | — | $26 | live-only |
| V01 | — | $39 | live-only |
| V02 | — | $40 | live-only |
| V03 | — | $21 | live-only |

live-only=22, match=12, price-diff=28
