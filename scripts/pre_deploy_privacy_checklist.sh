#!/usr/bin/env bash
# Read-only pre-deploy checklist for the intake login gate.
# Prints what must be true before deploy and what to run after.
# Never deploys; never writes Blob/Meta/prices; no network (dry-runs only).
# Usage: scripts/pre_deploy_privacy_checklist.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
echo "=== Sassy Closet — intake login gate PRE-DEPLOY CHECKLIST (read-only) ==="
echo
echo "[1] Merge tip recommendation (local drafts; Boss merges)"
echo "    - PRIMARY: piece-286-overnight-merge-ready (d9f53c7): 282 + 284 checklist tip fix (merge this alone)"
echo "    - history: 275 (633d24e), 282 (166da87) superseded by 286; do not merge them separately"
echo "    - Merge ONE line only; do not also merge 266/270/271/272/274/275/280/281 separately, linear 240-281, or overlapping cloud #188/#189"
for b in piece-286-overnight-merge-ready; do
  t=$(git -C "$HERE/.." rev-parse --short "$b" 2>/dev/null || echo "missing")
  echo "      local $b -> $t"
done
# Secondary, read-only: live answer from overnight_tip_status.sh (avoids hand-edited tip churn).
if [ -x "$HERE/overnight_tip_status.sh" ]; then
  live=$("$HERE/overnight_tip_status.sh" --repo "$HERE/.." --proof-root "${PROOF_ROOT:-/workspace}" 2>/dev/null | grep -m1 '^Recommended tip' || true)
  echo "    - SECONDARY (live, overnight_tip_status.sh): ${live:-unavailable}"
  echo "      (if PRIMARY and SECONDARY differ, trust SECONDARY: it reads proof SUMMARY PASS + merge-stack ancestry)"
else
  echo "    - SECONDARY (live): overnight_tip_status.sh not found"
fi
echo
echo "[2] Boss decisions still open (nothing applied by this script)"
cat <<'L'
    1. Deploy privacy gate (yes/no)
    2. Nhung needs admin login to submit after gate
    3. 401 body: JSON (default) vs empty (SHOP_ADMIN_401_EMPTY=1)
    4. Held nine (#192)   5. G01/H02 mint   6. Q02 listable
    7. Price drifts (which column wins)   8. Meta Giá/dual fixes
    9. Fill S06 intake ($25 lock stays)   10. Refresh seed
    11. daily-shop-check.yml   12. OneDrive D05/V03 refresh
L
echo
echo "[3] Dry-runs (no network)"
for s in live_shop_smoke.sh post_deploy_privacy_check.sh; do
  if [ -x "$HERE/$s" ]; then echo "--- $s --dry-run ---"; WRITE_PROBES=0 "$HERE/$s" --dry-run || echo "WARN $s dry-run exit $?"
  else echo "SKIP $s not present"; fi
done
echo
echo "[4] Post-deploy steps (ONLY after explicit Boss yes)"
cat <<'L'
    a. Boss deploys intake app (this script never deploys)
    b. scripts/post_deploy_privacy_check.sh            -> direct-link GETs 200, X-Robots-Tag noindex, nofollow, nosnippet; bodies not printed
    c. scripts/post_deploy_privacy_check.sh does not POST or PATCH; intake writes are open by link
    d. scripts/live_shop_smoke.sh --with-privacy        -> 62 mas, S06 $25, held 404
    e. Any FAIL -> report to Boss; do not fix live silently
L
echo "=== END (read-only; zero writes) ==="
