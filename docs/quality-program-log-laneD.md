# Lane D quality log

Test depth only. Draft PRs. No deploys, live writes, price changes, Meta changes, or visual changes. `data/held.json` stays untouched.

Pass 1 is draft PR #257 on `cursor/test-depth-catalog-s06-held-d652`. This branch starts from `origin/main` and does not repeat those probes.

## Pass 2 — 2026-11-02

Branch `cursor/tier-under-ten-debox-d652`. Test commit `27812ee4a78ffeed96b2694cb0b1ce3e7f7fbb26`. This log is the commit after that. No production bug. Production files were restored after every probe.

Tests added:

- `sassy-closet/tests/tiered-under-ten-bump.test.ts`
- `sassy-closet-shop/tests/debox-letter-lock.test.ts`

### Mutations where the older tests stayed green

1. The intake tier quote drops the extra two dollars whenever the ceil is under ten. A small landed amount then quotes 6 instead of 8. `sassy-closet/tests/pricing.test.ts` still passes, because its tier points are all above that band and the flat quote has its own bump.
2. The same bump also fires when the ceil is exactly ten, by comparing with `<=`. Landed 6.5 then quotes 12 instead of 10. The older pricing tests still pass.
3. The bump fires for every landed amount under 6.5, which still covers a ceil of ten. Landed 6 then quotes 12. The older pricing tests still pass.
4. The shop debox lookup does not trim or upper-case the letter. A lower-case dress letter returns unknown. `sassy-closet-shop/tests/pricing.test.ts` still passes, because it never calls the lookup.
5. The shop lookup returns the locked debox for every letter, including a top. The flat quote then invents a sell of 24. The older shop pricing tests still pass.
6. The locked table gains K at the dress amount. The first version of the new test still passed. The letter loop now expects unknown for every allowed letter except V, Q, and D, and that probe fails.

### Review

First adversarial review asked for the whole ceil-of-ten band, every non-dress letter, and cost digits kept off the cost-key lines. Those are in `27812ee`. Second review: PASS.

Left alone on purpose: catalog seed fallback when Blob is down, formula-prefixed CSV cells, held image cross-mã, yen preference, and whole-dollar S06 edges. Those are already open drafts.

### Hard recheck of the test commit

`npm ci` in `sassy-closet` and `sassy-closet-shop`, then `HARD_RECHECK_PYTHON=python3 scripts/hard_recheck.sh --base origin/main`. Log `out/recheck/20261102-233241-37991`. Exit 0. No SKIP steps. `tip-status` is INFO.

```
hard recheck  cursor/tier-under-ten-debox-d652 @ 27812ee  base origin/main
git                                            PASS  rc=0      0s  conflict markers 0
pytest                                         PASS  rc=0    177s  2114 passed, 7 skipped in 176.43s
guard:test_safety_gate_coverage.py             PASS
guard:test_no_digit_literal_stdout_asserts.py  PASS
guard:test_held_never_list_parity.py           PASS
guard:test_ma_normalization_parity.py          PASS
privacy                                        PASS          privacy_scan: CLEAN
intake-npm-test                                PASS  rc=0     10s  tests 279 pass 276 fail 0 skipped 3
intake-tsc                                     PASS  rc=0      2s  ok
shop-npm-test                                  PASS  rc=0      7s  tests 220 pass 217 fail 0 skipped 3
shop-tsc                                       PASS  rc=0      1s  ok
diff-stat                                      PASS          2 files changed, 117 insertions(+)
working-tree                                   PASS          clean
held-json                                      PASS          unchanged
tip-status                                     INFO          Recommended tip: none found with PASS proof
total 197s
HARD RECHECK: PASS
```

The draft PR quotes the recheck of the commit that adds this log.
