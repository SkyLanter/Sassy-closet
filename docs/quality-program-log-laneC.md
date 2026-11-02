# Lane C quality program log

## 2026-11-02 — Hard recheck on pull requests

Branch `cursor/hard-recheck-ci-9477`.

Added `.github/workflows/hard-recheck.yml`. On pull request and on demand it installs both apps, then runs `scripts/run_hard_recheck_ci.sh`. That runs `scripts/hard_recheck.sh --json --base origin/main` and fails if the result is not PASS or any required step is missing or not PASS. `hard_recheck.sh` still counts a required SKIP as PASS; the new assert closes that hole. No schedule, no deploy, no secret, contents read only. `data/held.json` was not edited.

Local recheck of code commit `62974f9` (this log was not in that commit), base `origin/main`, 216s, HARD RECHECK: PASS. Required SKIP count: 0. The same gates are run again on the commit that adds this file; that result is in the draft PR.

- pytest: 2131 passed, 7 skipped (pre-existing), step PASS
- privacy: CLEAN
- intake npm: tests 277, pass 274, fail 0, skipped 3, step PASS
- intake tsc: ok
- shop npm: tests 218, pass 215, fail 0, skipped 3, step PASS
- shop tsc: ok
- held.json unchanged: yes
- working tree: clean
- CI wrapper: HARD RECHECK COMPLETE: PASS (no required SKIP)
