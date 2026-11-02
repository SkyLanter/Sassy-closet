# Lane A quality program

Sell shop (`sassy-closet-shop/`) and intake (`sassy-closet/`). Draft-only until 2026-11-07 00:00 America/Los_Angeles. No merges, deploys, Blob/KV writes, price changes, or Meta edits. S06 stays $25. Held mãs stay held. Intake stays open by link with noindex. Python workflow scripts are another lane.

## 2026-11-02 — Held folder bytes on a live mã image URL

`GET /products/{live}/cover.jpg` already 404s when `{live}` is held. It still resolved that live row's catalog src and could return a held folder's bytes: a Blob URL such as `https://…/products/S14/cover.jpg`, a path that normalizes through `..` onto a held file, a URL that ends at `/products/S14` with no slash, or a redirect into that folder. Product cards request `/products/{mã}/cover.jpg`, so the gallery filter does not cover this route. Open drafts #217–#229 do not change it.

The route now refuses a src whose path is a held or never-list folder, keeps the read inside `public/`, and checks each redirect hop before fetching. A non-held extra folder and this mã's own cover still serve. 404s stay no-store. No price change. `data/held.json` unchanged.

Code: `sassy-closet-shop/lib/catalog-image-src.ts`, `sassy-closet-shop/app/products/[ma]/[file]/route.ts`. Tests: `sassy-closet-shop/tests/product-image-held-cross-ma.test.ts`.

Hard recheck on `b294acc` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 277 pass 274 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 220 pass 217 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 3 files changed, 399 insertions, 11 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 192s, logs `out/recheck/20261102-203153-7931` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps.

PR: draft for `cursor/held-image-cross-ma-b01b`. The commit that records this table is docs-only.
