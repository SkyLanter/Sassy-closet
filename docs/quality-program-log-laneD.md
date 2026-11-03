# Lane D quality log

Test depth only. Draft PRs. No deploys, live writes, price changes, Meta changes, or visual changes. `data/held.json` stays untouched.

Pass 1 is draft PR #257. Pass 2 is draft PR #264. Pass 3 is draft PR #271. This branch starts from `origin/main` and does not repeat those probes.

## Pass 4 — 2026-11-03

Branch `cursor/empty-catalog-sold-gate-d652`. Test commits `2ca86fedadf68c494890e97f1c4a4d80cce09e9b`, `c728951fd6120f18d8c8ae9664165bbd1bbd4832`, and `c3a32ae96ffa56d00454eb9aaf107b4314ded1ad`. This log is the commit after those. No production bug. Production files were restored after every probe.

Tests added:

- `sassy-closet-shop/tests/empty-catalog-no-legacy.test.ts`
- `sassy-closet-shop/tests/sold-hold-public-gate.test.ts`

### Mutations where the older tests stayed green

1. `parseCatalog` accepts a products array with nothing in it. The empty current catalog is returned instead of a corrupt read. `blob-catalog-corrupt.test.ts` still passes.
2. `readCatalogFromBlobPort` goes on to the next file when the parse error says the catalog cannot be empty. The older catalog's A01 is returned. The older corrupt-read tests still pass.
3. That skip happens only for a file that is not the requested key. An empty current file still throws, so the first new test stays green. A missing current file plus an empty `catalog.json` then returns null, and the shop can walk on to seed. The second new test fails.
4. `isShopVisibleStatus` treats sold as public. A01 shows up beside the hold row. `held-incomplete.test.ts`, `open-link-health-guards.test.ts`, and `padded-ma-paths.test.ts` still pass, because their rows are available.
5. The same function hides hold. The public list keeps S06 and drops A02. Those older tests still pass.
6. A row is public when its status is public or its price is null. Sold A03 has no price, so it joins the list. The priced sold row stays hidden, and the older held tests still pass.
7. `shopVisibleLooks` maps every catalog row and skips the public filter. Sold A01 and unpriced A03 reach the product list. The older tests call `shopVisibleProducts` only.
8. The sitemap assigns `document.products` and keeps the `shopVisibleProducts` import. Sold rows are published. The older sitemap test still sees the function name.
9. The sitemap filters first, then pushes every sold row from `document.products`. The older sitemap test still passes. The new test requires `document.products` to appear once.
10. `getProducts` drops looks whose price is null. Hold A02 would leave the product page. The new test locks the return line.
11. `getProduct` reads the admin catalog. Sold A01 would render. The new test locks the call to `getProducts`, and the product page still calls `getProduct` twice.

### Review

The first review asked for the empty older file, the unpriced sold row, and the sitemap, look list, and product-page wiring. Those are in `c728951`. The second review asked that `document.products` appear only as the filter input, so a later push of sold rows fails. That assertion is in `c3a32ae`.

Left alone on purpose: catalog seed fallback when Blob is down, formula-prefixed CSV cells, held image cross-mã, short product-image spellings, on-hand variant keys, yen preference, whole-dollar S06 edges, quote-gate parity, and seed-versus-live spellings. Those are already open drafts.

### Hard recheck of the test commits

`npm ci` in `sassy-closet` and `sassy-closet-shop`, then `HARD_RECHECK_PYTHON=python3 scripts/hard_recheck.sh --base origin/main`. Log `out/recheck/20261103-004544-80366`. Exit 0. No SKIP steps. `tip-status` is INFO. Pytest's own 7 skipped tests are inside the pytest run, not skipped recheck steps.

```
hard recheck  cursor/empty-catalog-sold-gate-d652 @ c3a32ae  base origin/main
git                                            PASS  rc=0      0s  conflict markers 0
pytest                                         PASS  rc=0    174s  2114 passed, 7 skipped in 173.78s
guard:test_safety_gate_coverage.py             PASS
guard:test_no_digit_literal_stdout_asserts.py  PASS
guard:test_held_never_list_parity.py           PASS
guard:test_ma_normalization_parity.py          PASS
privacy                                        PASS          privacy_scan: CLEAN
intake-npm-test                                PASS  rc=0      9s  tests 277 pass 274 fail 0 skipped 3
intake-tsc                                     PASS  rc=0      2s  ok
shop-npm-test                                  PASS  rc=0      7s  tests 221 pass 218 fail 0 skipped 3
shop-tsc                                       PASS  rc=0      1s  ok
diff-stat                                      PASS          2 files changed, 188 insertions(+)
working-tree                                   PASS          clean
held-json                                      PASS          unchanged
tip-status                                     INFO          Recommended tip: none found with PASS proof
total 193s
HARD RECHECK: PASS
```

The draft PR quotes the recheck of the commit that adds this log.
