# Lane C quality program log

PR #232 (`cursor/hard-recheck-ci-9477`), PR #239 (`cursor/readonly-browser-smoke-9477`), PR #246 (`cursor/merge-readiness-9477`), PR #251 (`cursor/workflow-token-read-9477`), and PR #254 (`cursor/pin-action-shas-9477`) each have their own copy of this log. Keep those sections when the drafts are combined.

## 2026-11-02 — Workflow install lock

Branch `cursor/workflow-install-lock-9477`.

A test fails if one of the four GitHub Actions workflows runs `npm install` (or an install alias) instead of `npm ci`, references the GitHub secrets context, or uses `pull_request_target`. The workflow files were not edited. No deploy. `held.json` was not edited.

`scripts/tests/test_workflow_install_lock.py`: 3 passed.

Draft PR #263.

Hard recheck of `ba45d8e`, base `origin/main`, 190s, PASS. Required steps PASS, none skipped. pytest 2117 passed, 7 skipped. privacy CLEAN. intake npm tests 277 pass, 274 fail 0, skipped 3. intake tsc ok. shop npm tests 218 pass, 215 fail 0, skipped 3. shop tsc ok. held.json unchanged.
