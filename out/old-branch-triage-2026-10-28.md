# Old branch triage — 2026-10-28 (piece 228, READ-ONLY)

Base: combined `c8cf3c3`. 35 unmerged piece branches (from the piece-227 inventory). Nothing was merged.
Method: `scripts/branch_triage.py` (patch-id equivalence, red-flag scan, trial apply in throwaway
worktrees under /workspace/trial-228, since deleted) plus a proof-only driver that ran each branch's touched
tests on base and with its code, then the full pytest and the full suite of each touched app.
Logs: /workspace/proof-228/trials/<branch>.log.

## Counts
| class | n | branches |
|---|---|---|
| A new safety/check logic | 21 | 125,130,131,133,140,141, 142,143,144,147,148,149,150,151,152,153,154,155,156,158,159 |
| A* new logic, needs adapting to current guards | 11 | 124,126,127,128,129,132,135,136,137,138,139 |
| B tests only | 0 | — |
| C already redone / covered | 3 | 145 (redone by 186/190), 146 (patch-equivalent), 157-combined (umbrella of 142–156) |
| D obsolete/conflicting (red flags) | 0 | — |
| E unclear | 0 (after manual review) | — |

A* = the script's raw class was E: own touched tests PASS with the code applied, but the full pytest fails only
on the newer guard `test_ma_normalization_parity::test_no_raw_strip_upper_outside_norm_ma` (old code does
`.strip().upper()` instead of `norm_ma`); 124 also trips `test_no_digit_literal_stdout_asserts`. Fix = swap to
`norm_ma` / structural asserts while porting. Not a reason to drop them.

## Summary table
| branch | class | applies cleanly | tests on combined | evidence |
|---|---|---|---|---|
| piece-124-ma-collision | A* (safety) | yes | own pass; full fails norm_ma + bare-digit guards | carries stack 112–124 (14 commits, 31 files: daily summary, price baseline, seed fallback/restore_plan, preflight, ma_collision_check). None of these files exist in combined |
| piece-125-caption-typo-check | A | yes | pass | caption_typo_check.py new |
| piece-126-next-free-ma | A* (safety) | yes | own pass; norm_ma guard | next_free_ma.py not in combined; never offers gaps (no reuse) |
| piece-127-catalog-lint | A* (safety) | yes | own pass; norm_ma guard | held/never-list listed, S06!=$25, dup mã |
| piece-128-fb-ig-gia-diff | A* | yes | own pass; norm_ma guard | FB vs IG Giá check |
| piece-129-caption-fix-draft | A* | yes | own pass; norm_ma guard | draft-only, refuses S06!=$25 / held |
| piece-130-local-pieces-index | A | yes | pass | local branch index |
| piece-131-caption-size-check | A | yes | pass | caption size line |
| piece-132-caption-intake-size-diff | A* | yes | own pass; norm_ma guard | caption vs intake size |
| piece-133-caption-kind-check | A | yes | pass | caption vs kind |
| piece-135-intake-size-options | A* | yes | own pass; norm_ma guard | intake size menu |
| piece-136-intake-color-pieces | A* | yes | own pass; norm_ma guard | intake colour |
| piece-137-intake-snapshot-diff | A* | yes | own pass; norm_ma guard | silent edit detect |
| piece-138-intake-color-vocab | A* | yes | own pass; norm_ma guard | colour chips |
| piece-139-intake-timestamp-check | A* | yes | own pass; norm_ma guard | timestamps / mint order |
| piece-140-intake-export-shape | A | yes | pass | CSV shape, dup mã |
| piece-141-piece-merge-preview | A | yes | pass | merge preview tool |
| piece-142-mint-999-overflow | A (safety) | yes | fail on base, pass with code | combined nextMa still mints A1000 past 999 (unparseable → re-mint = mã reuse). Real gap |
| piece-143-caption-price-guard | A | yes | fail→pass | no $0/negative Giá |
| piece-144-fx-plain-decimal | A | yes | fail→pass | plain decimals only |
| piece-145-guard-normalize-ma | C | no (conflicts) | its tests already pass on base | publishBlock canonical mã redone by 186 (+190) |
| piece-146-held-padded-ma | C | — | — | patch-id equivalent to base |
| piece-147-webhook-normalize-ma | A (safety) | yes | fail→pass | webhooks keyed on normalizeMa — NOT covered by 186/190 |
| piece-148-listing-status-normalize-ma | A (safety) | yes | fail→pass | listing-status normalizeMa |
| piece-149-on-hand-qty-strict | A | yes | fail→pass | strict qty |
| piece-150-admin-cookie-malformed | A | yes | fail→pass | malformed cookie no throw |
| piece-151-store-next-id-floor | A (safety) | yes | fail→pass | nextId never below existing ids |
| piece-152-local-photo-dir-read | A | yes | fail→pass | |
| piece-153-form-keep-photos-shape | A | yes | fail→pass | |
| piece-154-form-pieces-shape | A | yes | fail→pass | |
| piece-155-sync-malformed-pieces | A | yes | fail→pass | |
| piece-156-export-csv-malformed-pieces | A | yes | fail→pass | |
| piece-157-combined-check | C | no | — | umbrella of 142–156 commits; merge members instead |
| piece-158-ask-fallback-held | A (safety) | yes | fail→pass | held fallback |
| piece-159-product-image-held | A (safety) | yes | fail→pass | held product image |

## Special questions
- 186/190 vs old publish-guard/mint tests: 186/190 subsume **145** only (its tests pass on base). They do NOT
  cover 142 (999 overflow), 147 (webhooks), 148 (listing-status), 151 (nextId floor).
- mã collision check (124): genuinely new — no `ma_collision_check`, `next_free_ma`, or "collision" logic anywhere in combined (192–226 included).

## Recommended merge plan (each as its own combined piece, Boss approves)
1. Safety A, clean, fail→pass: 142, 151, 147, 148, 158, 159.
2. Other A app fixes: 143, 144, 149, 150, 152–156 (one at a time; pairwise conflicts not checked).
3. A tools: 125, 130, 131, 133, 140, 141.
4. A* port with norm_ma adaptation: 126, 127 first (mã reuse / held), then 128, 129, 132, 135–139.
5. 124: split the 112–124 stack; port ma_collision_check first, rest needs Boss call (large daily-summary change).
No B. Skip C.

## Skip list
- piece-145: redone by 186/190; conflicts.
- piece-146: already in base (patch-equivalent).
- piece-157-combined-check: umbrella; conflicts; merge 142–156 individually.

## Boss decisions
- 124 stack scope (14 commits, daily summary/price-baseline/restore_plan) — port all, some, or only collision check?
- 142 policy: past 999 throw "No free mã left" (never reuse) — confirm.
