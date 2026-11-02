# Sassy Closet quality program

Draft-only fixes until 2026-11-07 00:00 America/Los_Angeles. No merges, deploys, Blob writes, price changes, or Meta edits. S06 stays $25. Held mãs stay held. Incomplete Taobao stays unpublished. Intake stays open by link with noindex.

Other agents already own intake, the sell shop, script/workflow sweeps, the #208–#216 bundle, and a workflow status tool. This log skips those.

## 2026-11-02 — Midnight QC home prices

Live sell-home HTML embeds the catalog in a Next.js RSC flight string. Quotes are escaped (`\"ma\":\"A05\"` … `\"priceUsd\":25`). `parse_home_prices` only matched plain JSON, so a read-only fetch of the primary shop on 2026-11-02 (62 `priceUsd` tokens, all escaped) parsed as an empty home catalog. Midnight QC then failed the sell-site check and reported `sellCount` 0. Accepting one optional backslash before each quote parsed those 62 mãs, matched the live Blob available set, showed no price mismatches, kept S06 at $25, and did not include held mãs.

Code: `scripts/midnight_qc.py`. Tests: `scripts/tests/test_midnight_qc.py`.

Hard recheck on `6a59a43` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2120 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm/tsc | SKIP | node_modules missing |
| shop npm/tsc | SKIP | node_modules missing |
| diff-stat | PASS | 3 files changed, 81 insertions, 2 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 173s, logs `out/recheck/20261102-172334-12770` |

PR: https://github.com/SkyLanter/Sassy-closet/pull/220 (draft). The commit that records this table is docs-only and does not change the checker.
