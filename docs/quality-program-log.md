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

## 2026-11-02 — Digest and cost-recheck streak

Open Boss lines were dropped or stretched.

- `not decided` / `not yet approved` matched the closed-word list. Negation keeps the line open. `Boss price approved` still closes.
- A mã on a bullet continuation was invisible. Lines are still read alone, and the bullet is read together when that is what makes the decision. A closed line does not hide an open line in the same bullet.
- `streak_start` treated a missing cost-recheck day as still unreachable. A gap breaks the run. If today's summary omits the mã, there is no streak.
- Default `--order` / `--held` pointed under `--root` (`/workspace/sassy-closet`), where those files are not. They now use the repo copies. The Muse pack lists held mãs that are still in popular order.

Code: `scripts/boss_decisions_digest.py`, `scripts/boss_decisions.py`, `scripts/muse_pack_sections.py`.

Hard recheck on `b04dabf` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2124 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm/tsc | SKIP | node_modules missing |
| shop npm/tsc | SKIP | node_modules missing |
| diff-stat | PASS | 6 files changed, 279 insertions, 44 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 173s, logs `out/recheck/20261102-180654-17551` |

PR: https://github.com/SkyLanter/Sassy-closet/pull/224 (draft).

Skipped as not real enough to ship: `run_shop_drafts.py` writes proposals under the report dir while `daily_summary_draft.py` reads `$SASSY_OUT/proposals` unless `--proposal` is passed. The shop-draft tests lock that step list. Not changed.
