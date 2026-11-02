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

PR: https://github.com/SkyLanter/Sassy-closet/pull/231 (draft). The commit that records this table is docs-only.

## 2026-11-02 — Intake CSV formula cells

`exportCsv` quoted commas, quotes, and newlines, and still wrote a color or note that starts with `=`, `+`, `-`, `@`, a tab, or a carriage return as a bare cell. A saved color `=1+1` or a note `+note` would open as a formula. Open drafts #217–#231 do not change this. Mid-field carriage returns stay with the other unmerged CSV quoting work.

The export now leads those cells with an apostrophe and quotes them. Plain cells stay plain. Stored JSON is unchanged. No price change. `data/held.json` unchanged.

Code: `sassy-closet/lib/store.ts`. Tests: `sassy-closet/tests/export-csv-formula.test.ts`.

Hard recheck on `63b7441` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 278 pass 275 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 218 pass 215 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 2 files changed, 168 insertions, 2 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 193s, logs `out/recheck/20261102-210149-16395` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. Shop counts are this branch; they do not include the image-route tests on draft #231.

PR: https://github.com/SkyLanter/Sassy-closet/pull/235 (draft). The commit that records this table is docs-only.

## 2026-11-02 — On-hand rows under a variant mã key

`GET /api/ma/{code}` found the staged row for `a01`, `A001`, or `S006`, then looked up Square on-hand only under the canonical key. A bucket stored as `a01` or `S006` came back empty, so the card said staged-only. Open drafts #217–#235 do not change this lookup.

The read now accepts one alias of that mã. The canonical key still wins, including when it is an empty list. Two alias buckets are not added together. A case-only spelling wins over a padded one. No price change. `data/held.json` unchanged.

Code: `sassy-closet/lib/store.ts`. Tests: `sassy-closet/tests/on-hand-ma-key.test.ts`.

Hard recheck on `e505727` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 279 pass 276 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 218 pass 215 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 2 files changed, 159 insertions, 2 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 191s, logs `out/recheck/20261102-212513-22420` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. Shop counts are this branch; they do not include the image-route tests on draft #231.

PR: https://github.com/SkyLanter/Sassy-closet/pull/238 (draft). The commit that records this table is docs-only.

## 2026-11-02 — Intake save returns 503 when the store cannot be read

`GET` routes already answer a corrupt or unreadable store with 503 and a fixed Vietnamese message. `POST /api/submissions` and `PATCH /api/submissions/{mã}` caught that same failure and returned the raw error text, usually as 400. `POST /api/fx` let `setFx` throw. Open drafts #217–#238 do not change these write handlers. A bad kind, a missing mã, and a bad rate stay their own 400 or 404.

A store failure on those writes now uses the same 503 body as the reads. The raw URL or parse text is not sent back. No price change. `data/held.json` unchanged.

Code: `sassy-closet/lib/store-unavailable.ts`, `sassy-closet/app/api/submissions/route.ts`, `sassy-closet/app/api/submissions/[ma]/route.ts`, `sassy-closet/app/api/fx/route.ts`. Tests: `sassy-closet/tests/intake-write-store-down.test.ts`.

Hard recheck on `efb98cb` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 279 pass 276 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 218 pass 215 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 5 files changed, 162 insertions, 20 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 191s, logs `out/recheck/20261102-214240-28071` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. These intake counts are this branch (main plus these two tests). Shop counts do not include the image-route tests on draft #231.

PR: https://github.com/SkyLanter/Sassy-closet/pull/242 (draft). The commit that records this table is docs-only.

## 2026-11-02 — Share card does not paint the home JPEG when the catalog cannot be read

`GET /share/m/{mã}` and `GET /share/c/{slug}` already 404 when the mã or category is missing. If the catalog read threw, the same URL returned 200 and the homepage share JPEG, which is cached `public, max-age=86400`. `/api/health` returns 503 for that corrupt read. Open drafts #217–#242 do not change these share routes. The homepage `/opengraph-image` still paints a text home card, because that URL is the home card.

A thrown catalog read on a product or category share URL is now 503 plain text, `no-store`. A missing mã or category stays 404, also `no-store`. A listed mã still gets its own JPEG. No price change. `data/held.json` unchanged.

Code: `sassy-closet-shop/lib/share-card-http.ts`, `sassy-closet-shop/app/share/m/[ma]/route.ts`, `sassy-closet-shop/app/share/c/[slug]/route.ts`, `sassy-closet-shop/scripts/alias.cjs`. Tests: `sassy-closet-shop/tests/share-card-unavailable.test.ts`.

Hard recheck on `873fce5` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 277 pass 274 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 221 pass 218 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 5 files changed, 163 insertions, 12 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 192s, logs `out/recheck/20261102-220514-33637` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. Shop counts are this branch (main plus these three tests). They do not include the image-route tests on draft #231.

PR: (draft, URL recorded in the follow-up docs commit). The commit that records this table is docs-only.


