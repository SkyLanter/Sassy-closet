# Lane C quality program log

The hard-recheck pull-request gate is draft PR #232 on `cursor/hard-recheck-ci-9477`. This branch records the browser smoke. Keep both sections if the drafts land separately.

## 2026-11-02 — Read-only browser smoke

Branch `cursor/readonly-browser-smoke-9477`. Draft PR #239.

Added an on-demand Playwright smoke for both sell hosts and intake. It GETs the document only, with JavaScript off, and aborts anything under `/api/`. Checks: held PDP 404 (held list plus Q02), S06 PDP text `$25` and that product's USD offer at 25, and `noindex`. No deploy. `data/held.json` was not edited.

Live run: BROWSER SMOKE: PASS. 49 checks. Both shops, 22 held 404s each, S06 $25 on both, intake noindex. Local stub: SELF-TEST: PASS. `scripts/tests/test_readonly_browser_smoke.py`: 6 passed.
