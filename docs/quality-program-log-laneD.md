# Lane D quality log

Test depth only. Draft PRs. No deploys, live writes, price changes, Meta changes, or visual changes. `data/held.json` stays untouched.

Pass 1 is draft PR #257. Pass 2 is draft PR #264. This branch starts from `origin/main` and does not repeat those probes.

## Pass 3 — 2026-11-02

Branch `cursor/padded-new-ma-flat-ten-d652`. Test commit `e43e08de61e37f8bddc06600a3b22f7fb8bcad24`. This log is the commit after that. No production bug. Production files were restored after every probe.

Tests added:

- `sassy-closet/tests/padded-new-ma.test.ts`
- `sassy-closet-shop/tests/flat-ceil-ten.test.ts`

### Mutations where the older tests stayed green

1. The last return of a new mã keeps the typed spelling. `a001` is stored as `A001`. `publish-guard.test.ts` still passes, because its new mãs are already canonical.
2. The formatted spelling is the upper-cased raw text before the duplicate and held checks. The same `A001` store happens, and the older save tests still pass.
3. Numbers of 100 or more keep the raw spelling. `a0100` is stored as `A0100`, and `b00999` is stored as `B00999`. The older tests never save a number that large.
4. The stored letter comes from the form kind instead of the typed mã. Kind A with `b010` is stored as `A10`. The older tests use the same letter in both places.
5. A one-digit mã is padded before it is parsed. `a1` becomes a real row and `s6` takes the lock path. The test requires the format error and an empty list.
6. The shop flat quote adds two dollars when the ceil is exactly ten, and when the landed amount is under 7.5. A ceil of ten then sells at 12. The older shop pricing test still passes.
7. The flat quote skips that two-dollar bump for a ceil of 7 or 8. Those sells stay 7 and 8. The older shop sample ceils to 6, so it still passes.

### Review

The review asked for the whole number range through 999, the parsed letter, a one-digit rejection, and every ceil from 1 through 9. Those are in `e43e08d`. Final review: PASS.

Left alone on purpose: catalog seed fallback when Blob is down, formula-prefixed CSV cells, held image cross-mã, short product-image spellings, on-hand variant keys, yen preference, and whole-dollar S06 edges. Those are already open drafts.

### Hard recheck of the test commit

`npm ci` in `sassy-closet` and `sassy-closet-shop`, then `HARD_RECHECK_PYTHON=python3 scripts/hard_recheck.sh --base origin/main`. Log `out/recheck/20261103-000749-58515`. Exit 0. No SKIP steps. `tip-status` is INFO.

```
hard recheck  cursor/padded-new-ma-flat-ten-d652 @ e43e08d  base origin/main
git                                            PASS  rc=0      0s  conflict markers 0
pytest                                         PASS  rc=0    175s  2114 passed, 7 skipped in 174.02s
guard:test_safety_gate_coverage.py             PASS
guard:test_no_digit_literal_stdout_asserts.py  PASS
guard:test_held_never_list_parity.py           PASS
guard:test_ma_normalization_parity.py          PASS
privacy                                        PASS          privacy_scan: CLEAN
intake-npm-test                                PASS  rc=0     10s  tests 279 pass 276 fail 0 skipped 3
intake-tsc                                     PASS  rc=0      1s  ok
shop-npm-test                                  PASS  rc=0      6s  tests 220 pass 217 fail 0 skipped 3
shop-tsc                                       PASS  rc=0      2s  ok
diff-stat                                      PASS          2 files changed, 186 insertions(+)
working-tree                                   PASS          clean
held-json                                      PASS          unchanged
tip-status                                     INFO          Recommended tip: none found with PASS proof
total 194s
HARD RECHECK: PASS
```

The draft PR quotes the recheck of the commit that adds this log.
