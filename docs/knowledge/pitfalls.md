# Pitfalls

Each item is something the code or a pull request body already describes. Live behavior that was not re-fetched for this file is marked as a report, not as a new measurement.

## Squash-merge base, and `eb8a143`

`scripts/hard_recheck.sh` picks a default diff base only when you omit `--base`:

1. Commit `eb8a143` if `git rev-parse` can see it.
2. Otherwise the root commit (`git rev-list --max-parents=0 HEAD`).

Open PR #215 says squash-merges dropped `eb8a143`, so a fresh clone fails the rev-parse and the script diffs the whole history. Privacy and `data/held.json` then fail even when the branch itself is clean. This checkout confirms the object is gone: `git rev-parse eb8a143` fails on `04bfc35`. The proposed merge-base default is **not merged**. Pass `--base origin/main` when you want the diff against current main. An explicit `--base` is used as given (`scripts/hard_recheck.sh`).

PR #207 says the privacy scan against `eb8a143` was also dirty because `shared/live-price-snapshot.json` still held supplier costs. Those four cost fields are now null. Other hits the PR mentions (Taobao and 1688 fixtures) were left in place.

## Blob down, and seed fallback

`sassy-closet-shop/lib/catalog-store.ts` `readLiveCatalogRecordFresh`:

- Reads Blob, then KV, then a local file, then the seed document.
- A **corrupt** catalog throws `CatalogCorruptError` and does not fall back to seed (`lib/blob-catalog.ts`: "will not fall back to seed").
- A Blob, KV, or local read that throws a non-corrupt error logs and tries the next source. An empty result also moves on. Either way the read can end on seed.

`docs/seed-vs-live-mismatch.md` (piece 262, report only) says the live shop was reading Blob (62 mãs) and `sassy-closet-shop/data/products.json` is only the fallback (40 mãs). That doc counts 28 price differences and 22 live-only mãs, including S06. If Blob is down and the read is not a corrupt-document error, the shop can show the seed: wrong dollars, and missing mãs. Refreshing the seed is a Boss decision. The doc says it was not done.

`docs/post-blob-unblock-checklist.md` says shop `/api/health` should report `"reading":"blob"`. `"seed"` after an unblock is a failure of that checklist. The checklist is a GET list. It says not to write Blob, change prices, touch Meta, or deploy.

Intake has no seed catalog. Its health report is `blob`, `local`, or `ephemeral` (`sassy-closet` health, described in merged PR #205). A redeploy without Blob wipes `/tmp` (`sassy-closet/README.md`).

## Escaped quotes in sell HTML

Open PR #220 is titled "Fix midnight QC home prices on RSC flight HTML". Its body says the live home page embeds the catalog in a "Next.js RSC flight string", with quotes escaped, and that the midnight QC parser matched plain JSON only. The Python sources do not contain `flight` or `__next_f`. #220 is open. It is not merged.

On main the two quote matchers read different pages:

- `sassy-closet-shop/docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py` `look_pdp` matches both backslash-escaped `"ma"` / `"priceUsd"` and plain JSON. Those regexes run only when the mã is in `HOLD` (`P02` and `P05`), on `/m/P02` and `/m/P05`. `look_home` has no `"ma"` / `"priceUsd"` regex.
- `scripts/midnight_qc.py` `_HOME_PRICE_RE` matches plain `"ma"` / `"priceUsd"` in sell-home HTML.

The #220 body says a read-only fetch of the primary shop then parsed zero home prices, so the nightly sell check failed even when the dollars matched Blob. That fetch was not repeated for this knowledge file. The regex on main is the part you can see in git. Midnight QC home prices stay on the plain-quote regex until #220 is merged or the regex changes.

`scripts/freshness_check.py` `parse_pdp_price` reads JSON-LD (`application/ld+json`). A PDP JSON-LD check and the home-page quote check are different parsers.

## Escaped ampersands on an item URL

`scripts/freshness_check.py` `_price_from_item_url` reads `price=` from an item URL embedded in an e.tb.cn bridge page. Before the match, it replaces the sequences `\u0026` and `&amp;` with `&`. `parse_taobao_cny` uses that function when the JSON price keys are absent. `scripts/tests/test_taobao_fixtures.py` covers both replacements. A reader that skips the replace misses the list price. This parser is separate from the sell-home quote regex above.

## Seed photos replace live images for the hub ten

`overlaySeedHubGalleries` in `sassy-closet-shop/lib/catalog-store.ts` runs inside `hydrateLiveCatalog`. `readBlobCatalog`, `readKvCatalog`, and `readLocalCatalog` each pass a document they successfully read through `hydrateLiveCatalog`. For a mã in `KNOWN_SEED_MAS` whose seed product has at least one image, the returned product's `images` are `seed.images`. The function comment says the hub ten always show the intake files under `public/products/{MA}/`. A readable Blob catalog still goes through that replacement.

## Q02 stays off the sell PDP in the smoke checks

Q02 is absent from `data/held.json`. `publishBlock` allows create, mint, and save of Q02 (`sassy-closet/tests/publish-guard.test.ts`).

`scripts/midnight_qc.py` appends finding `q02-live` ("Q02 is on Blob, hub, or a sell PDP") when Q02 is in the Blob price index, in the hub price index, or on a checked sell origin whose PDP status is present and not 404. When Q02 is in intake and that live check is false, it warns: "Q02 is in intake and is not on sell. It stays held until Boss approves." In the held table, Q02 with Blob absent, hub absent or skipped, and PDP 404 is "Observed 404. Not a never-list requirement." Other mãs in that same shape are "PASS unpublished." Q02 with Blob absent and PDP 404 uses that same observed-404 line when the hub cell is present too.

`scripts/live_shop_smoke.sh` builds the default 404 list from `heldIncomplete`, `neverList`, and `Q02`, and the dry-run line labels each of those GET checks `(held)`. `scripts/post_deploy_privacy_check.sh` defaults `HELD_MAS` to `K03 K04 K05 V04 Q02 G01 H02 A27 S16` and expects `GET /m/Q02` to be 404. `scripts/pre_deploy_privacy_checklist.sh` lists "Q02 listable" among Boss decisions still open.

## UTC dates versus Pacific time

- `scripts/freshness_check.py` `today_pt` uses `America/Los_Angeles`. Its comment says the UTC date is already the next day after 5 PM PDT or 4 PM PST.
- `scripts/luxubu_status_record.py` and `scripts/daily_summary_draft.py` label times as Pacific.
- `scripts/run_daily_shop_check.sh` defaults `--date` to `date -u` (UTC).

A run after 5 PM PDT (4 PM PST) can file Tuesday's shop check under Wednesday's UTC date, while `freshness_check.py` and `scripts/run_daily_summary.sh` (default `--date` is today in PT) still use Tuesday. `luxubu_status_record.py` takes `--date` as a required flag. Pass `--date` explicitly when the shop day matters.

`scripts/hung_run_watch.py` uses a window of 08:09–22:54 `America/Los_Angeles`.

## `overnight_tip_status.sh` lags a piece

`docs/overnight-tip-status-lag.md` says the script counts a branch as PASS only when `PROOF_ROOT/proof-NNN/SUMMARY.md` exists, contains a hard-recheck PASS, and mentions the branch tip SHA. Inside piece N the summary is not written yet, so the tip falls back. Those `proof-*` folders are box-only. They are not in this repo. See [proof-and-hub-snapshot.md](proof-and-hub-snapshot.md).

## Held list and S06 copy drift

Merged PR #204 says several script checks passed on their own branches and failed once main's held list, S06 copy, or hub parser moved. The checks were pointed at `held_policy` and the current S06 wording. A new test that hard-codes an old held list, or expects S06 copy from an older page, will fail the same way.

`scripts/hard_recheck.sh` also fails if the branch changes `data/held.json`.

## False FAIL on a local `tieredSellUsd`

Merged PR #206: `sassy-closet/tests/tiered-price-diff.test.ts` used to treat any `tieredSellUsd` under `lib/` as an import of `shared/tiered-pricing.ts`. Intake defines that function locally in `sassy-closet/lib/pricing.ts`. The test now allows that one definition. Importing `shared/tiered-pricing.ts` from sell-site code is still the thing the test is guarding.

## OneDrive mirror and hub dollars

`docs/onedrive-mirror-drift.md` lists two rows from a committed fixture, not from a live re-read: D05 mirror 28 vs live 26, V03 mirror 24 vs live 21. S06 has no mirror row in that fixture. The doc says a mirror write needs Boss's OK.

`docs/price-drift-boss-decision.md` lists 13 mãs where hub and intake agree and the live shop differs (largest: P03 live 11 vs hub 18, S01 live 39 vs hub 28). No column was applied. Do not "fix" one side because the other is newer.

`scripts/freshness_check.py` reads an Official sheet's USD from `list_price` when that header exists, and from `sell_usd` when it does not. A sheet that has neither fails the parse.

## Intake login drafts

#188 and #189 would 401 the cost reads. Tests on main assert those reads are not 401 (`sassy-closet/tests/privacy-gate-regression.test.ts`, `open-link-health-guards.test.ts`). Porting the draft on top of main without Boss will fight those tests.

## Seed `allowlist` versus the live catalog

`KNOWN_SEED_MAS` is ten mãs: A01, S01, P01, P02, P03, P04, P05, K01, H01, A02 (`sassy-closet-shop/lib/catalog-contract.ts`). The live snapshot in `docs/seed-vs-live-mismatch.md` has 62 mãs. A tool that treats the allowlist as the whole shop will drop the rest.

## Shop `hold` versus `held.json`

Visible `status: "hold"` still has a product page and asks the customer to inbox for the price. A `heldIncomplete` mã has no public product page. Mixing the words holds the wrong set. See [shop.md](shop.md).
