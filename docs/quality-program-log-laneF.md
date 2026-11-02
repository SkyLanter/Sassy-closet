# Lane F quality log

## 2026-11-02 pass 1

Read-only cost-recheck streak report: `scripts/taobao_unreachable_streak.py`. No price was edited. `data/held.json` was not edited. Nothing was posted or sent.

An empty flags file, a file with no `ma`/`flag` columns, a NUL byte, a shifted column, or an unclosed quote is `UNUSABLE`. It does not count as a clean day and does not clear an unreachable streak. A header-only `ma,flag` file is still a real clean day. A missing folder or no usable file says `MISSING`, not `OK`. Impossible dates such as `2026-99-99` are `UNUSABLE` and are not the latest run. `--as-of` defaults to today in America/Los_Angeles. When the newest usable file is older than that date, the report says `STALE`. Missing days between files are named. A long gap that is one block says the count and the dates. A long gap with a file in the middle says the missing days are separate, and does not call the filed day missing. Day counts stay consecutive files. The report prints mã codes, dates, filenames, and those words only.

Golden files: `scripts/tests/fixtures/golden/cost_recheck_streak_stale.txt`, `cost_recheck_streak_unusable_only.txt`, `cost_recheck_streak_fresh_quiet.txt`.

Hard recheck of `19a9e6a` against `origin/main` (`04bfc35`), after `npm ci` in `sassy-closet` and `sassy-closet-shop`: PASS. No recheck step was SKIP. pytest 2127 passed, 7 skipped. Privacy CLEAN. Intake npm tests 277, pass 274, fail 0, skipped 3; tsc ok. Shop npm tests 218, pass 215, fail 0, skipped 3; tsc ok. held.json unchanged. Working tree clean. Total 206s. Logs: `out/recheck/20261102-225633-4814`.
