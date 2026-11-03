#!/usr/bin/env bash
# One-command hard recheck for Sassy Closet pieces. Local only: no network, no writes
# outside out/recheck/<stamp>/ (gitignored).
#
# Usage: scripts/hard_recheck.sh [--json] [--base SHA] [extra pytest args]
#   --json       also write summary.json in the log dir
#   --base SHA   diff/privacy/held.json base (default eb8a143, else root commit)
#   other args   passed through to scripts/run_tests.sh (e.g. --basetemp=/tmp/x-300)
# Env: HARD_RECHECK_PYTHON (default /tmp/venv08/bin/python, else python3),
#      HARD_RECHECK_TIMEOUT seconds per step (default 1200),
#      HARD_RECHECK_KILL_AFTER seconds before SIGKILL after timeout (default 15).
# Exit 0 only when every required step is PASS or SKIP; prints "HARD RECHECK: PASS|FAIL".
set +e
usage() { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; }

JSON=0; BASE=""; PYARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --json) JSON=1 ;;
    --base) BASE="$2"; shift ;;
    --base=*) BASE="${1#--base=}" ;;
    *) PYARGS+=("$1") ;;
  esac
  shift
done

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null || (cd "$HERE/.." && pwd))"
cd "$ROOT" || exit 2
if [ -z "$BASE" ]; then
  if git rev-parse -q --verify eb8a143^{commit} >/dev/null; then BASE=eb8a143
  else BASE="$(git rev-list --max-parents=0 HEAD | tail -1)"; fi
fi
PY="${HARD_RECHECK_PYTHON:-}"
[ -z "$PY" ] && { [ -x /tmp/venv08/bin/python ] && PY=/tmp/venv08/bin/python || PY=python3; }
TMO="${HARD_RECHECK_TIMEOUT:-1200}"
KILL_AFTER="${HARD_RECHECK_KILL_AFTER:-15}"
LOG="out/recheck/$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$LOG"
STEPS="$LOG/steps.tsv"; : > "$STEPS"
T0=$(date +%s)

# record <step> <required 1|0> <status> <rc> <secs> <detail> <note>
record() { printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$@" >> "$STEPS"; }

# timed <logfile> <cmd...>: runs with timeout, sets RC and SECS
timed() {
  local log="$1"; shift; local s=$(date +%s)
  # stdin from /dev/null so npm/node never waits on a prompt; -k SIGKILLs the step's
  # process group (timeout runs it in its own group) if lingering npm/node ignore TERM.
  timeout -k "$KILL_AFTER" "$TMO" "$@" < /dev/null > "$log" 2>&1; RC=$?
  SECS=$(( $(date +%s) - s ))
  [ "$RC" = 137 ] && RC=124
  [ "$RC" = 124 ] && echo "TIMEOUT after ${TMO}s" >> "$log" && echo "step timed out after ${TMO}s: $*" >&2
}

echo "hard recheck in $ROOT (base $BASE) -> $LOG"

# a. branch / head / conflict markers
BR="$(git branch --show-current)"; HEADSHA="$(git rev-parse --short HEAD)"
NM=$(git grep -nE '^(<<<<<<<|>>>>>>>|=======)( .*)?$' -- . > "$LOG/conflicts.log" 2>/dev/null; wc -l < "$LOG/conflicts.log" | tr -d ' ')
record git 1 "$([ "$NM" = 0 ] && echo PASS || echo FAIL)" 0 0 "branch $BR @ $HEADSHA; conflict markers $NM" ""

# b + f. pytest (guards run inside it)
timed "$LOG/pytest.log" env PYTHON="$PY" bash scripts/run_tests.sh "${PYARGS[@]}"
LINE="$(grep -E '[0-9]+ (passed|failed)' "$LOG/pytest.log" | tail -1 | sed 's/=//g; s/^ *//; s/ *$//')"
record pytest 1 "$([ "$RC" = 0 ] && echo PASS || echo FAIL)" "$RC" "$SECS" "${LINE:-no summary}" ""
GUARDS="test_safety_gate_coverage.py test_no_digit_literal_stdout_asserts.py test_held_never_list_parity.py test_ma_normalization_parity.py"
for g in $GUARDS; do
  [ -f "scripts/tests/$g" ] || { record "guard:$g" 0 SKIP 0 0 "not present" ""; continue; }
  if grep -qE "$g::.* (FAILED|ERROR)|FAILED scripts/tests/$g" "$LOG/pytest.log"; then st=FAIL; else st=$([ "$RC" = 124 ] && echo SKIP || echo PASS); fi
  record "guard:$g" 0 "$st" 0 0 "in pytest run" ""
done

# c. privacy scan
timed "$LOG/privacy.log" "$PY" scripts/privacy_scan.py --git-diff "$BASE..HEAD"
PL="$(tail -1 "$LOG/privacy.log")"
if [ "$RC" = 0 ] && grep -q CLEAN "$LOG/privacy.log"; then st=PASS; else st=FAIL; fi
record privacy 1 "$st" "$RC" "$SECS" "$PL" ""

# d/e. apps
for pair in "intake:sassy-closet" "shop:sassy-closet-shop"; do
  tag="${pair%%:*}"; app="${pair#*:}"
  if [ ! -f "$app/package.json" ]; then
    record "$tag-npm-test" 1 SKIP 0 0 "" "$app missing"; record "$tag-tsc" 1 SKIP 0 0 "" "$app missing"; continue
  fi
  if [ ! -d "$app/node_modules" ] || ! command -v npm >/dev/null; then
    why="node_modules missing"; command -v npm >/dev/null || why="npm not installed"
    record "$tag-npm-test" 1 SKIP 0 0 "" "$why"; record "$tag-tsc" 1 SKIP 0 0 "" "$why"; continue
  fi
  timed "$LOG/$tag-npm-test.log" bash -c "cd '$app' && npm test"
  n() { grep -E "^# $1 " "$LOG/$tag-npm-test.log" | tail -1 | awk '{print $3}'; }
  record "$tag-npm-test" 1 "$([ "$RC" = 0 ] && echo PASS || echo FAIL)" "$RC" "$SECS" "tests $(n tests) pass $(n pass) fail $(n fail) skipped $(n skipped)" ""
  timed "$LOG/$tag-tsc.log" bash -c "cd '$app' && npx tsc --noEmit"
  record "$tag-tsc" 1 "$([ "$RC" = 0 ] && echo PASS || echo FAIL)" "$RC" "$SECS" "$([ "$RC" = 0 ] && echo ok || echo "err $(grep -c 'error TS' "$LOG/$tag-tsc.log")")" ""
done

# g. diff stat + working tree
DS="$(git diff --stat "$BASE..HEAD" | tail -1 | sed 's/^ *//')"
record diff-stat 0 PASS 0 0 "${DS:-no changes}" ""
git status --porcelain > "$LOG/status.log"
LINKS="$(grep -E 'node_modules/?$' "$LOG/status.log" | sed 's/^?? //' | tr '\n' ' ')"
OTHER="$(grep -vcE 'node_modules/?$' "$LOG/status.log")"
note=""; [ -n "$LINKS" ] && note="node_modules link (ignored): $LINKS"
if [ "$OTHER" = 0 ]; then record working-tree 0 PASS 0 0 "clean: yes" "$note"
else record working-tree 0 WARN 0 0 "clean: no ($OTHER changes)" "$note"; fi

# h. held.json
if git diff --quiet "$BASE..HEAD" -- data/held.json; then record held-json 1 PASS 0 0 "held.json unchanged: yes" ""
else record held-json 1 FAIL 1 0 "held.json unchanged: no" ""; fi

# i. read-only tip-status footer (informational, never required; never fails the run)
TIPLINE=""; TIPNOTE="read-only"
TIPSCRIPT="$(dirname "$0")/overnight_tip_status.sh"
if [ ! -f "$TIPSCRIPT" ]; then TIPNOTE="read-only; overnight_tip_status.sh not found, skipped"
elif ! command -v timeout >/dev/null 2>&1; then TIPNOTE="read-only; timeout unavailable, skipped"
else
  TIPOUT=$(PROOF_ROOT="${PROOF_ROOT:-/workspace}" timeout "${TIP_TIMEOUT:-30}" bash "$TIPSCRIPT" < /dev/null 2>/dev/null); TIPRC=$?
  [ "$TIPRC" = 124 ] && TIPNOTE="read-only; tip-status timed out after ${TIP_TIMEOUT:-30}s"
  TIPLINE=$(printf '%s\n' "$TIPOUT" | grep -m1 '^Recommended tip' | tr '\t\r' '  ')
fi
[ -n "$TIPLINE" ] || TIPLINE="Recommended tip: none found"
record tip-status 0 INFO 0 0 "$TIPLINE" "$TIPNOTE"

TOTAL=$(( $(date +%s) - T0 ))
"$PY" - "$STEPS" "$LOG" "$JSON" "$TOTAL" "$BR" "$HEADSHA" "$BASE" <<'PY'
import json, sys
steps_path, log, want_json, total, br, head, base = sys.argv[1:]
steps = []
for line in open(steps_path, encoding="utf-8"):
    name, req, st, rc, secs, detail, note = (line.rstrip("\n").split("\t") + [""] * 7)[:7]
    steps.append(dict(step=name, required=req == "1", status=st, exit=int(rc or 0), seconds=int(secs or 0), detail=detail, note=note))
fail = any(s["required"] and s["status"] == "FAIL" for s in steps)
result = "FAIL" if fail else "PASS"
w = max(len(s["step"]) for s in steps)
rows = [f"+{'-' * 78}", f"| hard recheck  {br} @ {head}  base {base}"]
for s in steps:
    extra = f"  [{s['note']}]" if s["note"] else ""
    rows.append(f"| {s['step']:<{w}}  {s['status']:<4}  rc={s['exit']:<3} {s['seconds']:>4}s  {s['detail']}{extra}")
rows += [f"| total {total}s   logs: {log}", f"+{'-' * 78}", f"HARD RECHECK: {result}"]
text = "\n".join(rows) + "\n"
print(text, end="")
open(f"{log}/summary.txt", "w", encoding="utf-8").write(text)
if want_json == "1":
    json.dump(dict(branch=br, head=head, base=base, total_seconds=int(total), result=result, steps=steps),
              open(f"{log}/summary.json", "w", encoding="utf-8"), indent=1)
sys.exit(1 if fail else 0)
PY
exit $?
