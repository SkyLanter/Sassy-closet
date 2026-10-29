#!/usr/bin/env bash
# Read-only runner for scripts/daily_shop_check.py.
# Writes <out-dir>/daily-<date>.md and .json. No network, no writes outside out-dir.
# Exit: 0 = PASS or WARN, 1 = FAIL, 3 = runner/usage error (no report produced).
# Usage: run_daily_shop_check.sh [--out-dir DIR] [--date YYYY-MM-DD] [--python BIN] -- <daily_shop_check args>
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out_dir="reports/daily"; day="$(date -u +%F)"; py="${PYTHON:-python3}"
while [ $# -gt 0 ]; do
  case "$1" in
    --out-dir) out_dir="$2"; shift 2 ;;
    --date) day="$2"; shift 2 ;;
    --python) py="$2"; shift 2 ;;
    --) shift; break ;;
    *) echo "run_daily_shop_check: unknown option $1 (put check args after --)" >&2; exit 3 ;;
  esac
done
case "$day" in [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;; *) echo "bad --date $day" >&2; exit 3 ;; esac
for a in "$@"; do
  case "$a" in --out-md|--out-json|--out-md=*|--out-json=*) echo "runner sets --out-md/--out-json itself" >&2; exit 3 ;; esac
done
mkdir -p "$out_dir" || exit 3
md="$out_dir/daily-$day.md"; js="$out_dir/daily-$day.json"
rm -f "$md" "$js"
"$py" "$here/daily_shop_check.py" "$@" --out-md "$md" --out-json "$js"
rc=$?
if [ ! -s "$js" ]; then echo "run_daily_shop_check: no report (check rc=$rc)" >&2; exit 3; fi
overall="$("$py" -c 'import json,sys;print(json.load(open(sys.argv[1])).get("overall",""))' "$js")"
echo "daily shop check $day: $overall (check rc=$rc) -> $md, $js"
case "$overall" in
  PASS|WARN) exit 0 ;;
  FAIL) exit 1 ;;
  *) echo "unexpected overall '$overall'" >&2; exit 3 ;;
esac
