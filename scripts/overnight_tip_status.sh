#!/usr/bin/env bash
# Run AFTER the newest piece writes proof-NNN/SUMMARY.md, else it falls back (see docs/overnight-tip-status-lag.md).
# Read-only: for each local piece-* branch (newest piece number first), print tip SHA
# and whether PROOF_ROOT/proof-NNN/SUMMARY.md reports PASS. Recommends the highest-
# numbered branch whose proof SUMMARY says PASS (and no FAIL) and whose SHA it mentions.
# Usage: scripts/overnight_tip_status.sh [--repo DIR] [--proof-root DIR] [--limit N]
# Never writes refs, files, or remotes.
set -euo pipefail
REPO="."; PROOF_ROOT="/workspace"; LIMIT=10
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --repo) REPO="$2"; shift ;;
    --proof-root) PROOF_ROOT="$2"; shift ;;
    --limit) LIMIT="$2"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac; shift
done
echo "# Overnight tip status"
echo
echo "| Piece | Branch | Tip | Proof |"
echo "|---|---|---|---|"
rec=""; newest=""; n=0; pass_refs=(); pass_sha=()
while IFS=$'\t' read -r num ref sha; do
  [ -n "$ref" ] || continue
  [ "$n" -lt "$LIMIT" ] || break
  s="$PROOF_ROOT/proof-$num/SUMMARY.md"; st="no-summary"
  if [ -f "$s" ]; then
    # Prefer the hard_recheck verdict line(s) so unrelated words (e.g. "live privacy FAIL
    # until deploy") don't mark a passing piece FAIL. Falls back to whole-file scan.
    # Use the LAST verdict line (reruns supersede) and the first PASS/FAIL token after
    # "recheck" on it (case-insensitive: **pass**/Fail count), so "PASS (earlier FAIL fixed)" reads as PASS.
    v=$(grep -iE 'hard[_ ]?recheck' "$s" | grep -wiE 'PASS|FAIL' | tail -n1 \
        | sed -E 's/.*[Rr][Ee][Cc][Hh][Ee][Cc][Kk]//' | grep -oiE '\b(PASS|FAIL)\b' | head -n1 \
        | tr '[:lower:]' '[:upper:]' || true)
    if [ -n "$v" ]; then
      if [ "$v" = FAIL ]; then st="FAIL"
      elif grep -q "$sha" "$s"; then st="PASS"; else st="PASS (tip not in summary)"; fi
    elif grep -qw FAIL "$s"; then st="FAIL"
    elif grep -qw PASS "$s"; then
      if grep -q "$sha" "$s"; then st="PASS"; else st="PASS (tip not in summary)"; fi
    else st="unknown"; fi
  fi
  echo "| $num | \`$ref\` | \`$sha\` | $st |"
  [ "$st" = "PASS" ] && { [ -z "$newest" ] && newest="$ref @ $sha"; pass_refs+=("$ref"); pass_sha+=("$sha"); }
  n=$((n+1))
done < <(git -C "$REPO" for-each-ref --format=$'%(refname:short)\t%(objectname:short=7)' 'refs/heads/piece-*' \
  | sed -E 's/^piece-0*([0-9]+)(-[^\t]*)?\t/\1\tpiece-\1\2\t/' | awk -F'\t' '$1 ~ /^[0-9]+$/' | sort -t$'\t' -k1,1nr)
# Stack head: PASS branch containing the most other PASS tips (ties -> higher piece).
best=-1
for i in "${!pass_refs[@]}"; do
  c=0
  for j in "${!pass_refs[@]}"; do
    [ "$i" = "$j" ] && continue
    git -C "$REPO" merge-base --is-ancestor "${pass_sha[$j]}" "${pass_sha[$i]}" 2>/dev/null && c=$((c+1))
  done
  if [ "$c" -gt "$best" ]; then best=$c; rec="${pass_refs[$i]} @ ${pass_sha[$i]}"; fi
done
echo
[ -n "$newest" ] && [ "$newest" != "$rec" ] && echo "Newest PASS (side branch, not stack head): $newest"
if [ -n "$rec" ]; then echo "Recommended tip (merge-stack head with PASS proof): $rec"
else echo "Recommended tip: none found with PASS proof"; fi
echo "Note: newest PASS != merge tip if a piece is a side branch; confirm against BOSS-PR-NOTES."
