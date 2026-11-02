# Lane C quality program log

PR #232 (`cursor/hard-recheck-ci-9477`), PR #239 (`cursor/readonly-browser-smoke-9477`), and PR #246 (`cursor/merge-readiness-9477`) each have their own copy of this log. Keep those sections when the drafts are combined.

## 2026-11-02 — Workflow token read lock

Branch `cursor/workflow-token-read-9477`.

The four GitHub Actions workflows on main now set `permissions: contents: read` and `persist-credentials: false` on checkout. Build, test, and path filters are unchanged. A test rejects `pull_request_target`, a write permission, and a checkout that keeps credentials. No deploy. `held.json` was not edited.

`scripts/tests/test_workflow_token_read.py`: 4 passed.

Draft PR #251.

Hard recheck of `bbf643d`, base `origin/main`, 190s, PASS. Required steps PASS, none skipped. pytest 2118 passed, 7 skipped. privacy CLEAN. intake npm tests 277 pass, 274 fail 0, skipped 3. intake tsc ok. shop npm tests 218 pass, 215 fail 0, skipped 3. shop tsc ok. held.json unchanged.
