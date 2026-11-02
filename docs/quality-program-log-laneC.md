# Lane C quality program log

PR #232 (`cursor/hard-recheck-ci-9477`), PR #239 (`cursor/readonly-browser-smoke-9477`), PR #246 (`cursor/merge-readiness-9477`), and PR #251 (`cursor/workflow-token-read-9477`) each have their own copy of this log. Keep those sections when the drafts are combined.

## 2026-11-02 — Pin third-party actions

Branch `cursor/pin-action-shas-9477`.

The four GitHub Actions workflows on main now pin checkout, setup-node, and setup-python to the commits their major tags resolved to: checkout v4.4.0 `11d5960a326750d5838078e36cf38b85af677262`, setup-node v4.4.0 `49933ea5288caeca8642d1e84afbd3f7d6820020`, setup-python v5.6.0 `a26af69be951a213d495a4c3e4e4022e16d87065`. Build, test, and path filters are unchanged. No deploy. `held.json` was not edited.

`scripts/tests/test_action_pins.py`: 3 passed.

Draft PR #254.

Hard recheck of `f201e9d`, base `origin/main`, 191s, PASS. Required steps PASS, none skipped. pytest 2117 passed, 7 skipped. privacy CLEAN. intake npm tests 277 pass, 274 fail 0, skipped 3. intake tsc ok. shop npm tests 218 pass, 215 fail 0, skipped 3. shop tsc ok. held.json unchanged.
