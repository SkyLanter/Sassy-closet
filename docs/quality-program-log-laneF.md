# Lane F quality log

## 2026-11-02 pass 1

Draft PR #255 on `cursor/cost-recheck-stale-flags-4d7b`. The cost-recheck streak report names missing, unusable, and stale flag files. This branch does not add to that PR.

## 2026-11-02 pass 2

Read-only Meta snapshot saver: `scripts/meta_snapshot_save.py`. No price was edited. `data/held.json` was not edited. Nothing was posted or sent. Caption text is not stored or printed.

An empty sheet says `MISSING no meta snapshot rows`, not a saved snapshot. A missing file says `MISSING meta snapshot input` and does not print the path. A bad `--as-of` exits 2 before the file is read. A saved sheet says whether the latest America/Los_Angeles check date is before (`STALE`), on (`OK`), or after (`NOTE`) `--as-of`. `--as-of` defaults to today in America/Los_Angeles. A timestamp with no zone is read as America/Los_Angeles and the report says so. Duplicate posts keep the later instant, not the later timestamp text, so an older check is not labeled the latest. A stale sheet still saves and exits 0. The snapshot posts keep the same fields. `save()` without the new fields does not add them.

Golden files: `scripts/tests/fixtures/golden/meta_snapshot_stale.txt`, `meta_snapshot_empty.txt`, `meta_snapshot_fresh.txt`, `meta_snapshot_unusable.txt`, `meta_snapshot_future.txt`, `meta_snapshot_mixed.txt`, `meta_snapshot_naive.txt`.

Hard recheck of `890b08b` against `origin/main` (`04bfc35`), after `npm ci` in `sassy-closet` and `sassy-closet-shop`: PASS. No recheck step was SKIP. pytest 2144 passed, 7 skipped. Privacy CLEAN. Intake npm tests 277, pass 274, fail 0, skipped 3; tsc ok. Shop npm tests 218, pass 215, fail 0, skipped 3; tsc ok. held.json unchanged. Working tree clean. Total 191s. Logs: `out/recheck/20261103-000311-18065`. Diff: 9 files changed, 613 insertions, 45 deletions.
