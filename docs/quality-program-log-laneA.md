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

PR: https://github.com/SkyLanter/Sassy-closet/pull/245 (draft). The commit that records this table is docs-only.

## 2026-11-02 — A removed intake photo still matched find-mã

Saving a row set `photo_paths` to the photos staff kept, and still copied the whole previous `photo_hashes` list whenever at least one photo stayed. Find-by-photo then returned the mã for an image that had been removed. Keeping only the later photo could also leave the earlier photo's hash in its place. Open drafts #217–#245 do not change this pairing.

The save now stores one hash per kept path, in that order, using the hash that sat beside that path. A dropped path's hash is not kept. A kept path with no stored hash, including a stray path on a new mã, is an empty slot so a photo uploaded in the same save stays lined up with its own hash. An empty search hash matches nothing, and a row whose hash list is not an array does not fail the search for other mãs. No price change. `data/held.json` unchanged.

Code: `sassy-closet/lib/store.ts`. Tests: `sassy-closet/tests/find-ma-dropped-photo.test.ts`.

Hard recheck on `a7b57ce` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 288 pass 285 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 218 pass 215 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 2 files changed, 360 insertions, 5 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 191s, logs `out/recheck/20261102-223024-40254` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. These intake counts are this branch (main plus these eleven tests). Shop counts do not include the image-route tests on draft #231 or the share-card tests on draft #245.

PR: https://github.com/SkyLanter/Sassy-closet/pull/250 (draft). The commit that records this table is docs-only.

## 2026-11-02 — A new photo replaced a file that was kept

Saving a row named the next photo from how many paths were kept. Keeping `001` and `003` made the upload `003`, and keeping only `002.png` made the next `.png` that same name. The write replaces the file, so the kept photo's bytes were gone. Open drafts #217–#250 do not change this naming. Find-by-photo hashes stay with the dropped-hash draft.

The next file now uses the lowest free `{mã}/NNN` slot. A kept path that is the same file with a leading slash, `./`, or `..` occupies that slot too. A full `001`/`002` prefix still continues at `003`. A new mã still starts at `001`. No price change. `data/held.json` unchanged.

Code: `sassy-closet/lib/store.ts`. Tests: `sassy-closet/tests/photo-keep-gap.test.ts`.

Hard recheck on `183231e` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 282 pass 279 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 218 pass 215 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 2 files changed, 197 insertions, 6 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 191s, logs `out/recheck/20261102-230131-46285` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. These intake counts are this branch (main plus these five tests). Shop counts do not include the image-route tests on draft #231 or the share-card tests on draft #245.

PR: https://github.com/SkyLanter/Sassy-closet/pull/256 (draft). The commit that records this table is docs-only.

## 2026-11-02 — Short product image URLs 404 while the PDP resolves

`/m/a1` and `/m/A001` already redirect to `/m/A01`. `/products/A1/cover.jpg` and `/products/a01/cover.jpg` did not. The image route uppercased the mã and looked for that exact folder and catalog row, so the public file in `public/products/A01/` was missed. Open drafts #217–#256 do not change this. Shop search still treats `a1` as a prefix.

The proxy now redirects `/products/a1/cover.jpg` to `/products/A01/cover.jpg`. The image route uses that same spelling for the file read and the catalog match. A held spelling such as `s14` or `S014` does not redirect onto `public/products/S14`, and the route still 404s it before reading a file. A sold mã still serves. No price change. `data/held.json` unchanged.

Code: `sassy-closet-shop/lib/ma-url.ts`, `sassy-closet-shop/app/products/[ma]/[file]/route.ts`. Tests: `sassy-closet-shop/tests/product-image-ma-spelling.test.ts`, `sassy-closet-shop/tests/ma-url-canonical-spelling.test.ts`, `sassy-closet-shop/tests/ma-url-malformed.test.ts`.

Hard recheck on `b2cdcbd` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 277 pass 274 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 219 pass 216 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 5 files changed, 129 insertions, 14 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 191s, logs `out/recheck/20261102-232652-52112` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. Shop counts are this branch (main plus this test). They do not include the held-folder image tests on draft #231 or the share-card tests on draft #245.

PR: https://github.com/SkyLanter/Sassy-closet/pull/262 (draft). The commit that records this table is docs-only.

## 2026-11-02 — Rename left kept photos in the old mã folder

Changing a row's mã updated the code and the photo folder label, and left the files under the old code. Thumbs still opened the old paths. The CSV `photo_link` and the find-card folder pointed at the new mã, where those files were not. Open drafts #217–#262 do not move these files. Photo hashes stay in their previous list. A new photo still takes the next length-based name.

The save now copies each kept file whose folder is the old mã onto the new mã and stores that path. The old file stays. A path another row still names, a keep path that stays, a file that already holds different bytes, or the name a new photo is about to write, stays on the old path so those bytes remain readable. A missing file keeps its old path. No price change. `data/held.json` unchanged.

Code: `sassy-closet/lib/store.ts`. Tests: `sassy-closet/tests/rename-photo-folder.test.ts`.

Hard recheck on `895bf0e` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 291 pass 288 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 218 pass 215 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 2 files changed, 500 insertions, 8 deletions |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 191s, logs `out/recheck/20261103-001124-58365` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. These intake counts are this branch (main plus these fourteen tests). Shop counts match main. They do not include the held-folder image tests on draft #231 or the share-card tests on draft #245.

PR: https://github.com/SkyLanter/Sassy-closet/pull/270 (draft). The commit that records this table is docs-only.

## 2026-11-03 — Rename let a held mã, or S06 at another dollar, leave its code

Saving a held mã in place already returned 409. Saving S06 at a dollar other than the locked one did too. Changing the mã checked only the new code, so the same row could be stored under a free mã. On the shop, change-mã refused a held target and an S06 target at another dollar, and still allowed the source row to leave. Open drafts #217–#270 do not close this. Photo copy on rename stays with draft #270.

The intake save now applies the same block to the code being left. A held or never-list source stays on that code. An S06 source posted at another dollar stays S06. A posted S06 sell of the locked dollar can still move, and a blank S06 sell can still move, matching the existing save rule. The shop change-mã refuses a held source, and refuses to leave S06 unless the price is the locked dollar. The catalog array is left unchanged when the call returns an error. No price change. `data/held.json` unchanged.

Code: `sassy-closet/lib/store.ts`, `sassy-closet-shop/lib/admin-ops.ts`. Tests: `sassy-closet/tests/held-rename-away.test.ts`, `sassy-closet-shop/tests/rename-held-source.test.ts`.

Hard recheck on `e1a7975` (`scripts/hard_recheck.sh --base origin/main`): **PASS**

| step | status | detail |
| --- | --- | --- |
| git | PASS | conflict markers 0 |
| pytest | PASS | 2114 passed, 7 skipped |
| privacy | PASS | CLEAN |
| intake-npm-test | PASS | tests 281 pass 278 fail 0 skipped 3 |
| intake-tsc | PASS | ok |
| shop-npm-test | PASS | tests 221 pass 218 fail 0 skipped 3 |
| shop-tsc | PASS | ok |
| diff-stat | PASS | 4 files changed, 192 insertions, 1 deletion |
| working-tree | PASS | clean |
| held-json | PASS | unchanged |
| total | PASS | 192s, logs `out/recheck/20261103-004435-65541` |

No hard-recheck step was SKIP. The pytest and npm skipped counts are tests inside those suites, not skipped recheck steps. Intake counts are this branch (main plus these four tests). Shop counts are this branch (main plus these three tests). They do not include the held-folder image tests on draft #231, the share-card tests on draft #245, or the photo-rename tests on draft #270.

PR: (draft, URL recorded in the follow-up docs commit). The commit that records this table is docs-only.
