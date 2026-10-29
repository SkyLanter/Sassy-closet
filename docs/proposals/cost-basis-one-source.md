# Proposal (draft, not applied): one cost source for every price check

Status: DRAFT. Nothing here is applied. No price changes without Boss's yes.

## Why
Midnight QC and the daily too-cheap run disagreed on O02 and V03 (and P01, D05):
- Midnight QC (`out/midnight-qc/<date>/pass2.py`) reads Nhung's intake export
  (`/api/export`, column `cost_cny`).
- The too-cheap run (`verify/too-cheap-<date>/run_check.py`) reads
  `verify/cost-recheck/cost-recheck-<date>.csv` column `baseline_cny` (the older
  "used" cost the live price was set on), falling back to the reprice report `yen`.
- `scripts/too_cheap_check.py` `load_costs()` takes `intake_cny`, else `baseline_cny`,
  so a recheck CSV fed in as `--costs` silently uses the baseline.

Same formula, same kg, different cost field, so the verdicts flip.

## Proposed change (Boss's rule: Nhung's intake is the source)
1. `too_cheap_check.py --costs` reads the intake export's `cost_cny` only.
   Drop the `baseline_cny` fallback; a mã with no intake cost is SKIP (missing
   intake), never priced on baseline.
2. The cost-recheck CSV stays a reference: `baseline_cny` and the public list
   (`recheck_cny`) are reported, never used for a verdict.
3. The daily too-cheap runner loads the same intake export Midnight QC loads.
4. `cost_basis_reconcile.py` runs in both checks; any FLIP or DISAGREE mã goes
   to Boss as a flag (bad intake price rule), never fixed silently.
5. Mãs whose intake row may belong to another item (code reuse, e.g. V03)
   are flagged for Boss before any raise.

## Not in this proposal
No live price, Blob, Square, Meta or intake writes. Any raise found under the
single source goes through the price approval queue for Boss's yes.
