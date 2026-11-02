#!/usr/bin/env bash
# CI entry for the hard recheck. Both apps must already have node_modules
# (npm ci). Runs scripts/hard_recheck.sh --json --base origin/main, then
# fails if the summary is not PASS or any required step is missing or not PASS.
# No install, no deploy, no writes to data/held.json.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null)" || {
  echo "FAIL not in a git checkout"
  exit 2
}
cd "$ROOT" || exit 2

fail() { echo "FAIL $*"; exit 1; }

git rev-parse --verify --quiet 'origin/main^{commit}' >/dev/null \
  || fail "origin/main is missing; fetch it before this script (git fetch origin main)"
command -v npm >/dev/null 2>&1 \
  || fail "npm is not installed; required app steps would SKIP"
for app in sassy-closet sassy-closet-shop; do
  [ -d "$app/node_modules" ] \
    || fail "$app/node_modules is missing; run npm ci in $app first"
done

PY="${HARD_RECHECK_PYTHON:-python3}"
bash "$HERE/hard_recheck.sh" --json --base origin/main
rc=$?
"$PY" "$HERE/assert_hard_recheck_complete.py" --latest "$ROOT/out/recheck"
arc=$?
if [ "$rc" -ne 0 ] || [ "$arc" -ne 0 ]; then
  echo "HARD RECHECK CI: FAIL (recheck=$rc assert=$arc)"
  exit 1
fi
echo "HARD RECHECK CI: PASS"
exit 0
