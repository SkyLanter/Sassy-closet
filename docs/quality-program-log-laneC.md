# Lane C quality program log

PR #232 (`cursor/hard-recheck-ci-9477`), PR #239 (`cursor/readonly-browser-smoke-9477`), PR #246 (`cursor/merge-readiness-9477`), PR #251 (`cursor/workflow-token-read-9477`), PR #254 (`cursor/pin-action-shas-9477`), and PR #263 (`cursor/workflow-install-lock-9477`) each have their own copy of this log. Keep those sections when the drafts are combined.

## 2026-11-02 — npm lifecycle lock

Branch `cursor/npm-lifecycle-lock-9477`.

A test fails if `sassy-closet/package.json` or `sassy-closet-shop/package.json` defines an install lifecycle script (`preinstall`, `install`, `postinstall`, `prepublish`, `preprepare`, `prepare`, `postprepare`, `prepublishOnly`, `prepack`), including a nested `scripts` object. It also fails if a script body would run npm install, curl, wget, or a deploy. Neither file was edited. No deploy. `held.json` was not edited.

`scripts/tests/test_npm_lifecycle_lock.py`: 2 passed.

Draft PR #277.

Hard recheck of `ca67707`, base `origin/main`, 197s, PASS. Required steps PASS, none skipped. pytest 2116 passed, 7 skipped. privacy CLEAN. intake npm tests 277 pass, 274 fail 0, skipped 3. intake tsc ok. shop npm tests 218 pass, 215 fail 0, skipped 3. shop tsc ok. held.json unchanged.
