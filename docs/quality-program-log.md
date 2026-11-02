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

## 2026-11-02 — Caption mãs with extra or missing zeros

The caption linter only accepted a mã with exactly two digits. `Mã S006` and `Mã S6` were reported as a missing mã, so a $30 caption never failed the S06 $25 lock, and a padded held mã never met its approved Giá. One to four digits now go through the same mã key as the shop. `K3` and `K003` become `K03`. A token that is not a one-letter two-digit key is skipped, so `Mã A100 Mã A09` still sees A09. A five-digit run is still not a mã. `Mã S06` on its own line stays a clean pass.

Code: `scripts/caption_lint.py`. Tests: `scripts/tests/test_caption_lint.py`.

Hard recheck on `01ce4fc` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2118 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +45 / −7 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-193746-73344` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/228 (draft).

## 2026-11-02 — Caption price check uses padded mãs

`caption_price_mismatch.py` only took a two-digit mã, and the catalog side already used `norm_ma`. `Mã S006` and `Mã S6` never met catalog S06, so a wrong Giá stayed quiet. One to four digits now collapse through `norm_ma`. A token that is not a one-letter two-digit key is skipped, including a later label on the same line (`Mã A100 Mã S06`). A trailing letter (`Mã S06B`) is not S06. A five-digit run is not a mã. No price is rewritten.

Code: `scripts/caption_price_mismatch.py`. Tests: `scripts/tests/test_caption_price_mismatch.py`.

Hard recheck on `d226007` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2115 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +39 / −9 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 196s, logs `out/recheck/20261102-195712-87087` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/229 (draft).

## 2026-11-02 — Cost-basis report keeps the other live mãs

`cost_basis_reconcile.py` read a live catalog only as a products list, and only when every price was a finite number. A prices map (`prices`) crashed the run. So did one row that was not an object, a blank, a boolean, or junk text such as `oops`. `float(True)` would have been $1. NaN and Infinity were already left out. One bad row now stays out, and the other mãs are still reconciled. A finite number is unchanged, including 0. No price is rewritten.

Code: `scripts/cost_basis_reconcile.py`. Tests: `scripts/tests/test_price_loaders_nonfinite.py`, `scripts/tests/test_cost_basis_ma_normalize.py`, `scripts/tests/test_cost_basis_reconcile.py`.

Hard recheck on `50da51b` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2118 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 4 files, +119 / −3 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-202117-100990` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/230 (draft).

## 2026-11-02 — QC notes use the shop mã key

A QC note that named a post or Reel with a padded mã was read as the first two digits. `Mã S006` became S00, `Mã A100` became A10, and `Mã S06B` became S06. A one-digit mã such as `Mã S6`, and `IG S006 caption`, were dropped, so the missing Giá never showed up. One to four digits now collapse through the same mã key as the shop. A token that is not a one-letter two-digit key is skipped, so `Mã A100 Mã A09` still sees A09. A trailing letter is not that mã. A five-digit run is not a mã. A numeric post id still wins when the note has one. No price is rewritten.

Code: `scripts/meta_caption_gap_report.py`. Tests: `scripts/tests/test_meta_caption_gap_report.py`.

Hard recheck on `7d64750` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2115 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +77 / −9 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-204714-114722` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/234 (draft).

## 2026-11-02 — Caption gap watch reads the shop price key

`caption_gap_watch.py` only kept a price key that was already a clean mã, and only a value that was already a number. A lowercase key, a short key, a padded key, and a products list all dropped out. The check then still forced S06 to $25, so every other wrong Giá stayed quiet. Keys now go through the same mã key as the shop. A products list, a prices map, and an approved Giá map all count. A boolean, a blank, or junk text stays out. S06 stays $25. No price is rewritten.

Code: `scripts/caption_gap_watch.py`. Tests: `scripts/tests/test_caption_gap_watch.py`.

Hard recheck on `4ec60c5` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2115 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +83 / −9 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 196s, logs `out/recheck/20261102-211117-128651` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/237 (draft).

## 2026-11-02 — Intake gaps ignore sold and hold prices

`intake_gaps.py` treated a catalog row as the live shop price unless the status was hidden, draft, or deleted. A sold row and a hold row were grouped as live, and a different intake sell price was reported against that row. A row that was not an object stopped the whole report. Live statuses now match the daily snapshot: available, live, active, in stock. A blank status still counts as live. sold and hold do not. One bad row is skipped. No intake value is rewritten.

Code: `scripts/intake_gaps.py`. Tests: `scripts/tests/test_intake_gaps.py`.

Hard recheck on `7bb8108` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2116 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +88 / −10 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 196s, logs `out/recheck/20261102-213506-142560` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/241 (draft).

## 2026-11-02 — Daily snapshot checks every live S06 row

The reduced daily shop check stopped at the first live S06. The snapshot already has that row at $25, so a later live row spelled S006, S6, or with spaces could carry another price and the check still passed. Every live row whose mã is S06 is now checked. A price of 25.0 still matches the lock. A row that is not live does not. No price is rewritten.

Code: `scripts/daily_shop_check.py`. Tests: `scripts/tests/test_export_daily_inputs.py`.

Hard recheck on `dad517f` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2118 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +55 / −3 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-215428-156487` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/244 (draft).

## 2026-11-02 — Daily snapshot keeps a blank catalog status

The daily export dropped a catalog row whose status was null, spaces, or a newline. A missing status already counted as live, so those rows never reached the reduced check. A boolean price became $1, because `true` is a number in Python. Blank status now stays live. sold and hold stay out. A boolean price is omitted. One non-object row is skipped, and a catalog with no object rows still fails. A bad mã on a live row still fails the export. No price is rewritten.

Code: `scripts/export_daily_inputs.py`. Tests: `scripts/tests/test_export_live_row.py`.

Hard recheck on `fcc7150` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2120 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 2 files, +98 / −1 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-221746-170467` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/248 (draft).

## 2026-11-02 — Approved Giá skips a bad value

The caption Giá check and the Meta inventory report turned a boolean `true` into an approved price of $1. A held caption then failed against that dollar. A junk value such as text, a blank, or a huge integer aborted the whole map, so a real price beside it never loaded. Bad values are now skipped. NaN and Infinity stay out. A numeric string still counts. A later junk spelling of the same mã does not erase the earlier price. A file whose approved Giá is not an object still fails. No price is rewritten.

Code: `scripts/caption_gia_check.py`, `scripts/meta_inventory.py`. Tests: `scripts/tests/test_approved_gia_values.py`.

Hard recheck on `556b241` (`scripts/hard_recheck.sh --base origin/main`) after `npm ci`: **PASS**. No step was SKIP.

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2120 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake npm test | PASS | 277 tests, 274 pass, 0 fail, 3 skipped |
| intake tsc | PASS | ok |
| shop npm test | PASS | 218 tests, 215 pass, 0 fail, 3 skipped |
| shop tsc | PASS | ok |
| diff-stat | PASS | 3 files, +121 / −3 |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 197s, logs `out/recheck/20261102-223838-184346` |

The commit that records this table is docs-only.

PR: https://github.com/SkyLanter/Sassy-closet/pull/252 (draft).
