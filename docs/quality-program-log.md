# Sassy Closet quality program

Draft-only fixes until 2026-11-07 00:00 America/Los_Angeles. No merges, deploys, Blob writes, price changes, or Meta edits. S06 stays $25. Held mãs stay held. Incomplete Taobao stays unpublished. Intake stays open by link with noindex.

Other agents already own intake, the sell shop, script/workflow sweeps, the #208–#216 bundle, and a workflow status tool. This log skips those.

From 2026-11-02 18:12 UTC, hard recheck runs after `npm ci` in `sassy-closet` and `sassy-closet-shop`. A SKIP step is a failure for this program.

## 2026-11-02 — Midnight QC home prices

Live sell-home HTML embeds the catalog in a Next.js RSC flight string. Quotes are escaped (`\"ma\":\"A05\"` … `\"priceUsd\":25`). `parse_home_prices` only matched plain JSON, so a read-only fetch of the primary shop on 2026-11-02 (62 `priceUsd` tokens, all escaped) parsed as an empty home catalog. Midnight QC then failed the sell-site check and reported `sellCount` 0. Accepting one optional backslash before each quote parsed those 62 mãs, matched the live Blob available set, showed no price mismatches, kept S06 at $25, and did not include held mãs.

Code: `scripts/midnight_qc.py`. Tests: `scripts/tests/test_midnight_qc.py`.

Hard recheck on `ad25c91` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2120 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 3 files, +110 / −2 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 208s, logs `out/recheck/20261102-181254-21474` |

PR: https://github.com/SkyLanter/Sassy-closet/pull/220 (draft).

## 2026-11-02 — Digest and cost-recheck streak

Open Boss lines were dropped or stretched.

- `not decided` / `not yet approved` matched the closed-word list. Negation keeps the line open. `Boss price approved` still closes.
- A mã on a bullet continuation was invisible. Lines are still read alone, and the bullet is read together when that is what makes the decision. A closed line does not hide an open line in the same bullet.
- `streak_start` treated a missing cost-recheck day as still unreachable. A gap breaks the run. If today's summary omits the mã, there is no streak.
- Default `--order` / `--held` pointed under `--root` (`/workspace/sassy-closet`), where those files are not. They now use the repo copies. The Muse pack lists held mãs that are still in popular order.

Code: `scripts/boss_decisions_digest.py`, `scripts/boss_decisions.py`, `scripts/muse_pack_sections.py`.

Hard recheck on `b04dabf` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2124 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 6 files, +279 / −44 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-181634-26859` |

PR: https://github.com/SkyLanter/Sassy-closet/pull/224 (draft).

## 2026-11-02 — Daily summary reads the flat midnight QC file

`daily_summary_draft.py` still expected `counts`, `fails`, `warns`, `pass2.agrees`, and `s06.blob`. `midnight_qc.py` writes a flat summary (`dataOk`, `sellSite`, `freshnessGuards`, `blobCount`, `heldCount`, `intakeCount`, `s06Usd`). A real file therefore printed "second pass did not confirm" and left out the live counts and S06. The draft now keeps the old wording for the old keys, and for the flat file prints only allowlisted status words, integer counts, and a finite S06. Notes, titles, and mismatch text stay out.

Code: `scripts/daily_summary_draft.py`. Tests: `scripts/tests/test_daily_summary_draft.py`.

Hard recheck on `a110c64` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP. The first run failed the mã parity guard because a status word used `strip().upper()`; that is a status token, not a mã, and the follow-up commit is the one rechecked here.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2119 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +94 / −9 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-184034-36480` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/226 (draft).

## 2026-11-02 — Shop drafts show the proposal they just wrote

`run_shop_drafts.py` wrote `held-price-proposal-<date>.json` under the report dir, then ran the daily draft without `--proposal`. The draft looks in `$SASSY_OUT/proposals` unless that flag is set, so the suggested prices were missing from the summary of the same run. The summary step now points at the file the proposal step writes. A missing file still means no suggestion lines.

Code: `scripts/run_shop_drafts.py`. Tests: `scripts/tests/test_run_shop_drafts.py`.

Hard recheck on `ed43b27` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +6 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-190001-50417` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/227 (draft).
