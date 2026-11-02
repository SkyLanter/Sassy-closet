# Lane D quality log

Test depth only. Draft PRs. No deploys, live writes, price changes, Meta changes, or visual changes. `data/held.json` stays untouched.

## Pass 1 — 2026-11-02

Branch `cursor/test-depth-catalog-s06-held-d652`. Test commit `12b5ab67da73e781e114effb333c091fd6ede518`. This log is the commit after that. No production bug. Production files were restored after every probe.

Tests added:

- `sassy-closet-shop/tests/blob-catalog-legacy-fallback.test.ts`
- `sassy-closet-shop/tests/held-padded-photo-404.test.ts`
- `sassy-closet/tests/s06-cost-still-locks.test.ts`
- `sassy-closet/tests/intake-legacy-ma-export.test.ts`

### Mutations where the older tests stayed green

1. Catalog read keeps only the versioned path and drops the legacy candidates. The new fallback tests fail. `blob-catalog-corrupt.test.ts` still passes.
2. A corrupt versioned catalog, or a corrupt official `catalog.json`, falls through to a good later file. The new tests fail because they require the error and no later read. The older corrupt test can stay green when the throw still happens on the versioned path.
3. The photo route treats only the exact held spelling `S14` as off-live, or only held codes that start with S. A padded spelling and an A-letter held file on disk return 200. `product-image-held.test.ts` still passes. The new held-photo test fails.
4. Save compares the normalized stored mã with the raw `existingMa`. An update through `a1` or `a0001` throws. `webhook-ma-normalize.test.ts` still passes.
5. CSV quoting drops the comma, the quote, or the newline from its trigger. The export test fails on `Kem, Xanh`, `say "hi"`, or a size split across two lines. `store.test.ts` still passes. The comma, the quote, and the newline are in different cells.
6. The live S06 quote locks only when the tiered quote is at least the lock, so a one-unit dollar cost returns 4. Intake and shop copies of `tiered-price-diff.test.ts`, `open-link-health-guards.test.ts`, and `pricing.test.ts` still pass. The new S06 test fails (expected 25, actual 4).
7. The intake price view shows a typed sell when the tiered quote is under the lock. The new test fails (expected 25, actual 80). The older intake tests above still pass. A lock that applies only when both cost fields are blank fails the same typed-sell test, and `open-link-health-guards.test.ts` still passes.

### Review

First adversarial review asked for separate quote and newline cells, and for a cost whose tiered quote is under the lock. Both are in `12b5ab6`. Second review: PASS. Privacy scan of the tests is CLEAN. Cost digits are built off the cost-key lines.

Left alone on purpose: padded live photo URLs are not required to 404. Open draft work on formula-prefixed CSV cells, held image cross-mã, the every-row S06 snapshot, blob-down, and yen preference is not repeated here.

### Hard recheck of the test commit

`npm ci` in `sassy-closet` and `sassy-closet-shop`, then `HARD_RECHECK_PYTHON=python3 scripts/hard_recheck.sh --base origin/main`. Log `out/recheck/20261102-225632-21781`. Exit 0. No SKIP steps. `tip-status` is INFO.

```
hard recheck  cursor/test-depth-catalog-s06-held-d652 @ 12b5ab6  base origin/main
git                                            PASS  rc=0      0s  conflict markers 0
pytest                                         PASS  rc=0    181s  2114 passed, 7 skipped in 180.35s
guard:test_safety_gate_coverage.py             PASS
guard:test_no_digit_literal_stdout_asserts.py  PASS
guard:test_held_never_list_parity.py           PASS
guard:test_ma_normalization_parity.py          PASS
privacy                                        PASS          privacy_scan: CLEAN
intake-npm-test                                PASS  rc=0     13s  tests 283 pass 280 fail 0 skipped 3
intake-tsc                                     PASS  rc=0      2s  ok
shop-npm-test                                  PASS  rc=0     10s  tests 229 pass 226 fail 0 skipped 3
shop-tsc                                       PASS  rc=0      2s  ok
diff-stat                                      PASS          4 files changed, 588 insertions(+)
working-tree                                   PASS          clean
held-json                                      PASS          unchanged
tip-status                                     INFO          Recommended tip: none found with PASS proof
total 208s
HARD RECHECK: PASS
```

An earlier run on `cb8d32e` failed privacy because cost keys sat on the same line as digits. That was rewritten before `36b2466`, which passed. `89689ea` also passed after the CSV cells were split. The table above is the recheck of the tests. The draft PR quotes the recheck of the commit that adds this log.
