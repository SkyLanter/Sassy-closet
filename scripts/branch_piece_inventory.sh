#!/usr/bin/env bash
# Read-only: list local piece-* branches with tip SHA, date, and subject (markdown).
# Usage: scripts/branch_piece_inventory.sh [--pattern GLOB] [--repo DIR]
#   --pattern GLOB  ref glob under refs/heads (default piece-*)
#   --repo DIR      git repo to read (default: current)
# Never writes refs, never touches remotes.
set -euo pipefail
PATTERN="piece-*"; REPO="."
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --pattern) PATTERN="$2"; shift ;;
    --repo) REPO="$2"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac; shift
done
cur=$(git -C "$REPO" branch --show-current 2>/dev/null || true)
echo "# Local piece branch inventory"
echo
echo "| Branch | Tip | Date | Subject |"
echo "|---|---|---|---|"
n=0
while IFS=$'\t' read -r ref sha date subj; do
  [ -n "$ref" ] || continue
  mark=""; [ "$ref" = "$cur" ] && mark=" (current)"
  subj=${subj//|/\\|}
  echo "| \`$ref\`$mark | \`$sha\` | $date | $subj |"
  n=$((n+1))
done < <(git -C "$REPO" for-each-ref --sort=refname \
  --format=$'%(refname:short)\t%(objectname:short=7)\t%(committerdate:short)\t%(contents:subject)' \
  "refs/heads/$PATTERN")
echo
echo "Total: $n"
