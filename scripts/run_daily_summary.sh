#!/usr/bin/env bash
# Local runner for scripts/daily_summary_draft.py with repo-resolved defaults.
# Resolves --order/--held from this script's repo and --date to today (PT).
# Extra args pass through (e.g. --date 2026-10-22, --stdout). No network, no live writes.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
py="${PYTHON:-python3}"
# Piece 110: one shop out folder for every worktree (override with SASSY_OUT or --out-dir).
export SASSY_OUT="${SASSY_OUT:-/workspace/sassy-closet/out}"
echo "run_daily_summary: SASSY_OUT=$SASSY_OUT" >&2
# Piece 92: archive the day's decision inputs first (box only, never overwrites;
# set NO_ARCHIVE=1 to skip).
if [ -z "${NO_ARCHIVE:-}" ]; then
  "$py" "$here/archive_daily_inputs.py" >&2
fi
# Piece 93: write the day's BOSS-DECISIONS.md with the same defaults first
# (refuses to overwrite a file made with different inputs; BOSS_FORCE=1 forces).
bd_args=()
prev=""
for x in "$@"; do
  case "$x" in --date=*) bd_args+=("$x");; esac
  [ "$prev" = "--date" ] && bd_args+=(--date "$x")
  prev="$x"
done
"$py" "$here/boss_decisions.py" ${bd_args[@]+"${bd_args[@]}"} ${BOSS_FORCE:+--force} >&2
"$py" "$here/daily_summary_draft.py" --defaults "$@"
