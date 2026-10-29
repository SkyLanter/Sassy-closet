#!/usr/bin/env bash
# Read-only privacy check to run AFTER Boss deploys the intake login gate (piece 240/245/253).
# No tokens, no cookies, no deploy, no Blob/Meta/price writes. Prints PASS/FAIL per check.
# Never prints response bodies (so no cost values reach logs) - only field NAMES that leaked.
#
# Usage: scripts/post_deploy_privacy_check.sh [--dry-run]
#   --dry-run   list every check and its expected result; no network.
# Env: INTAKE_BASE, SHOP_BASE, CHECK_TIMEOUT (default 20),
#      SHOP_ADMIN_401_EMPTY=1  expect EMPTY 401 bodies (default expects JSON {"ok":false,...}),
#      WRITE_PROBES=1          also send unauthenticated POST /api/submissions and
#                              PATCH /api/submissions/ZZ99 (bogus mã, empty body) -> expect 401.
#                              Off by default: on a host WITHOUT the gate these could write.
#                              Only enabled after every GET gate check PASSes in this run.
#      HELD_MAS (space list, default "K03 K04 K05 V04 Q02 G01 H02 A27 S16")
# Exit 0 only when every check PASSes; exit 1 on any FAIL (incl. any cost/source leak).
set -u
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
INTAKE="${INTAKE_BASE:-https://sassy-closet.vercel.app}"
SHOP="${SHOP_BASE:-https://sassy-closet-shop.vercel.app}"
T="${CHECK_TIMEOUT:-20}"
HELD="${HELD_MAS:-K03 K04 K05 V04 Q02 G01 H02 A27 S16}"
case "$(echo "${SHOP_ADMIN_401_EMPTY:-}" | tr -d ' ' | tr A-Z a-z)" in 1|true|yes) MODE=empty ;; *) MODE=json ;; esac
GATED="/api/export /api/submissions /api/submissions/S06 /api/ma/S06"
# Public mã list. 200 is expected. Cost and supplier field names are still a leak.
INDEX="/api/ma-index"
LEAK_RE='cost_cny|cost_usd|costCny|costUsd|source_link|sourceLink|taobao'

if [ "$DRY" = 1 ]; then
  echo "DRY RUN (no network). intake=$INTAKE shop=$SHOP 401-body=$MODE"
  for p in $GATED; do echo "CHECK GET  $INTAKE$p -> 401, body $MODE, no cost/source fields"; done
  echo "CHECK GET  $INTAKE$INDEX -> 200, no cost/source fields"
  if [ "${WRITE_PROBES:-0}" = 1 ]; then
    echo "CHECK POST  $INTAKE/api/submissions (empty JSON) -> 401  [only if all GET gates PASS]"
    echo "CHECK PATCH $INTAKE/api/submissions/ZZ99 (empty JSON) -> 401  [only if all GET gates PASS]"
  else echo "SKIP  POST/PATCH write probes (set WRITE_PROBES=1 after deploy)"; fi
  echo "CHECK GET  $SHOP/api/health -> 200 reading=blob, blob readable"
  echo "CHECK GET  $SHOP/m/S06 -> 200 shows \$25"
  for m in $HELD; do echo "CHECK GET  $SHOP/m/$m -> 404 (held)"; done
  exit 0
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
FAILS=0; LEAKS=0
req() { curl -s -m "$T" -X "$1" -o "$TMP/body" -w '%{http_code}' "${@:3}" "$2" 2>/dev/null || echo 000; }
res() { if [ "$1" = ok ]; then echo "PASS  $2"; else echo "FAIL  $2  ($3)"; FAILS=$((FAILS+1)); fi; }
leaked() { grep -oiE "$LEAK_RE" "$TMP/body" | sort -u | tr '\n' ' '; }
body_ok() {  # 401 body shape matches mode
  if [ "$MODE" = empty ]; then [ ! -s "$TMP/body" ]
  else grep -q '"ok":false' "$TMP/body"; fi
}
check401() {  # $1 label, $2 code
  local f; f="$(leaked)"
  if [ -n "$f" ]; then LEAKS=$((LEAKS+1)); res no "$1" "http $2 LEAK fields: ${f}- costs/sources public, tell Boss"
  elif [ "$2" != 401 ]; then res no "$1" "http $2, expected 401"
  elif ! body_ok; then res no "$1" "401 but body not $MODE shape"
  else res ok "$1 (401, $MODE body)"; fi
}

GETFAIL=0
for p in $GATED; do
  before=$FAILS; c=$(req GET "$INTAKE$p"); check401 "intake GET $p locked" "$c"
  [ "$FAILS" != "$before" ] && GETFAIL=1
done

c=$(req GET "$INTAKE$INDEX"); f="$(leaked)"
if [ -n "$f" ]; then LEAKS=$((LEAKS+1)); res no "intake GET $INDEX public list" "http $c LEAK fields: ${f}- costs/sources public, tell Boss"
elif [ "$c" != 200 ]; then res no "intake GET $INDEX public list" "http $c, expected 200"
else res ok "intake GET $INDEX public list (200, no cost/source fields)"; fi

if [ "${WRITE_PROBES:-0}" = 1 ]; then
  if [ "$GETFAIL" = 0 ]; then
    c=$(req POST "$INTAKE/api/submissions" -H 'content-type: application/json' --data '{}'); check401 "intake POST /api/submissions locked" "$c"
    c=$(req PATCH "$INTAKE/api/submissions/ZZ99" -H 'content-type: application/json' --data '{}'); check401 "intake PATCH /api/submissions/[ma] locked" "$c"
  else res no "intake POST/PATCH probes" "skipped: GET gate not live, a write probe could create data"; fi
else echo "SKIP  intake POST/PATCH probes (WRITE_PROBES=1 to enable after deploy)"; fi

c=$(req GET "$SHOP/api/health")
r=$(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d.get("reading"),(d.get("blob") or {}).get("readable"))' "$TMP/body" 2>/dev/null || echo "? ?")
{ [ "$c" = 200 ] && [ "$r" = "blob True" ]; } && res ok "shop health reading=blob, blob readable" || res no "shop health" "http $c, reading/readable=$r"
c=$(req GET "$SHOP/m/S06"); { [ "$c" = 200 ] && grep -q '\$25' "$TMP/body"; } && res ok "shop /m/S06 200 shows \$25" || res no "shop /m/S06 \$25" "http $c"
for m in $HELD; do c=$(req GET "$SHOP/m/$m"); [ "$c" = 404 ] && res ok "shop /m/$m 404 (held)" || res no "shop /m/$m held" "http $c - HELD MÃ VISIBLE, tell Boss"; done

echo; if [ "$FAILS" = 0 ]; then echo "POST-DEPLOY PRIVACY CHECK: PASS"; exit 0
else echo "POST-DEPLOY PRIVACY CHECK: FAIL ($FAILS fails, $LEAKS leaks)"; exit 1; fi
