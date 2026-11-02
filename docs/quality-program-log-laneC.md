# Lane C quality program log

PR #232 (`cursor/hard-recheck-ci-9477`) and PR #239 (`cursor/readonly-browser-smoke-9477`) each have their own copy of this log. Keep those sections when the drafts are combined.

## 2026-11-02 — Merge readiness report

Branch `cursor/merge-readiness-9477`.

Read-only list of open draft pull requests. Each line says whether the draft conflicts with the base branch and whether the hard-recheck check passed on that commit. A check named only `recheck`, with no workflow name `hard-recheck`, does not count. The script does not merge, comment, or push. `held.json` was not edited.

`scripts/tests/test_merge_readiness.py`: 13 passed.

Live read of open drafts: 111 drafts, 14 conflicts, 1 hard-recheck PASS. Draft #232 was conflicts=no, recheck=PASS, UNSTABLE, `8b608ca`. Draft #239 was conflicts=no, recheck=NONE, CLEAN, `7770cab`.

Draft PR #246.

Hard recheck of `0794ec0`, base `origin/main`, 191s, PASS. Required steps PASS, none skipped. pytest 2127 passed, 7 skipped. privacy CLEAN. intake npm tests 277 pass, 274 fail 0, skipped 3. intake tsc ok. shop npm tests 218 pass, 215 fail 0, skipped 3. shop tsc ok. held.json unchanged.
