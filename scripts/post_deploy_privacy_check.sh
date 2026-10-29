#!/usr/bin/env bash
# Read-only check after intake data links are open without a session.
# GET /api/submissions, /api/export, and /api/ma/S06 must be 200 with no cookie
# and X-Robots-Tag: noindex, nofollow. GET /api/submissions/S06 may be 200 or 404.
# POST/PATCH stay 401. No tokens, no cookies, no deploy, no Blob/Meta/price writes.
# Never prints response bodies (so cost values never reach logs).
#
# Usage: scripts/post_deploy_privacy_check.sh [--dry-run]
#   --dry-run   list every check and its expected result; no network.
# Env: INTAKE_BASE, SHOP_BASE, CHECK_TIMEOUT (default 20),
#      SHOP_ADMIN_401_EMPTY=1  expect EMPTY 401 bodies on write probes
#                              (default expects JSON {"ok":false,...}),
#      WRITE_PROBES=1          also send unauthenticated POST /api/submissions and
#                              PATCH /api/submissions/ZZ99 (bogus mã, empty body) -> expect 401.
#                              Off by default. Only runs after every direct-link GET PASSes.
#      HELD_MAS (space list, default "K03 K04 K05 V04 Q02 G01 H02 A27 S16")
# Exit 0 only when every check PASSes.
set -u
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
INTAKE="${INTAKE_BASE:-https://sassy-closet.vercel.app}"
SHOP="${SHOP_BASE:-https://sassy-closet-shop.vercel.app}"
T="${CHECK_TIMEOUT:-20}"
HELD="${HELD_MAS:-K03 K04 K05 V04 Q02 G01 H02 A27 S16}"
case "$(echo "${SHOP_ADMIN_401_EMPTY:-}" | tr -d ' ' | tr A-Z a-z)" in 1|true|yes) MODE=empty ;; *) MODE=json ;; esac
OPEN="/api/export /api/submissions /api/ma/S06"
LEAK_RE='cost_cny|cost_usd|costCny|costUsd|source_link|sourceLink|taobao'

if [ "$DRY" = 1 ]; then
  echo "DRY RUN (no network). intake=$INTAKE shop=$SHOP write-401-body=$MODE"
  for p in $OPEN; do echo "CHECK GET  $INTAKE$p -> 200 without auth, X-Robots-Tag: noindex, nofollow"; done
  echo "CHECK GET  $INTAKE/api/submissions/S06 -> 200 or 404, X-Robots-Tag: noindex, nofollow"
  if [ "${WRITE_PROBES:-0}" = 1 ]; then
    echo "CHECK POST  $INTAKE/api/submissions (empty JSON) -> 401  [only if all direct-link GETs PASS]"
    echo "CHECK PATCH $INTAKE/api/submissions/ZZ99 (empty JSON) -> 401  [only if all direct-link GETs PASS]"
  else echo "SKIP  POST/PATCH write probes (set WRITE_PROBES=1 after deploy)"; fi
  echo "CHECK GET  $SHOP/api/health -> 200 reading=blob, blob readable"
  echo "CHECK GET  $SHOP/m/S06 -> 200 shows \$25"
  for m in $HELD; do echo "CHECK GET  $SHOP/m/$m -> 404 (held)"; done
  exit 0
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
FAILS=0; LEAKS=0
req() { curl -s -D "$TMP/hdr" -m "$T" -X "$1" -o "$TMP/body" -w '%{http_code}' "${@:3}" "$2" 2>/dev/null || echo 000; }
res() { if [ "$1" = ok ]; then echo "PASS  $2"; else echo "FAIL  $2  ($3)"; FAILS=$((FAILS+1)); fi; }
leaked() { grep -oiE "$LEAK_RE" "$TMP/body" | sort -u | tr '\n' ' '; }
has_noindex() { tr -d '\r' < "$TMP/hdr" | grep -qiE '^x-robots-tag:[[:space:]]*noindex,[[:space:]]*nofollow'; }
body_ok() {  # 401 body shape matches mode
  if [ "$MODE" = empty ]; then [ ! -s "$TMP/body" ]
  else grep -q '"ok":false' "$TMP/body"; fi
}
check401() {  # $1 label, $2 code — write probes only; never used on direct-link GETs
  local f; f="$(leaked)"
  if [ -n "$f" ]; then LEAKS=$((LEAKS+1)); res no "$1" "http $2 LEAK fields: ${f}- write answer included cost/source names, tell Boss"
  elif [ "$2" != 401 ]; then res no "$1" "http $2, expected 401"
  elif ! body_ok; then res no "$1" "401 but body not $MODE shape"
  else res ok "$1 (401, $MODE body)"; fi
}
check_open() {  # $1 label, $2 code, $3 1 to allow 404
  if [ "$3" = 1 ]; then
    if [ "$2" != 200 ] && [ "$2" != 404 ]; then res no "$1" "http $2, expected 200 or 404 without auth"; return; fi
  elif [ "$2" != 200 ]; then res no "$1" "http $2, expected 200 without auth"; return; fi
  if ! has_noindex; then res no "$1" "http $2 missing X-Robots-Tag: noindex, nofollow"; return; fi
  res ok "$1 ($2, noindex, nofollow)"
}

GETFAIL=0
for p in $OPEN; do
  before=$FAILS; c=$(req GET "$INTAKE$p"); check_open "intake GET $p" "$c" 0
  [ "$FAILS" != "$before" ] && GETFAIL=1
done
before=$FAILS; c=$(req GET "$INTAKE/api/submissions/S06"); check_open "intake GET /api/submissions/S06" "$c" 1
[ "$FAILS" != "$before" ] && GETFAIL=1

if [ "${WRITE_PROBES:-0}" = 1 ]; then
  if [ "$GETFAIL" = 0 ]; then
    c=$(req POST "$INTAKE/api/submissions" -H 'content-type: application/json' --data '{}'); check401 "intake POST /api/submissions locked" "$c"
    c=$(req PATCH "$INTAKE/api/submissions/ZZ99" -H 'content-type: application/json' --data '{}'); check401 "intake PATCH /api/submissions/[ma] locked" "$c"
  else res no "intake POST/PATCH probes" "skipped: direct-link GET not live, a write probe could create data"; fi
else echo "SKIP  intake POST/PATCH probes (WRITE_PROBES=1 to enable after deploy)"; fi

c=$(req GET "$SHOP/api/health")
r=$(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d.get("reading"),(d.get("blob") or {}).get("readable"))' "$TMP/body" 2>/dev/null || echo "? ?")
{ [ "$c" = 200 ] && [ "$r" = "blob True" ]; } && res ok "shop health reading=blob, blob readable" || res no "shop health" "http $c, reading/readable=$r"
c=$(req GET "$SHOP/m/S06"); { [ "$c" = 200 ] && grep -q '\$25' "$TMP/body"; } && res ok "shop /m/S06 200 shows \$25" || res no "shop /m/S06 \$25" "http $c"
for m in $HELD; do c=$(req GET "$SHOP/m/$m"); [ "$c" = 404 ] && res ok "shop /m/$m 404 (held)" || res no "shop /m/$m held" "http $c - HELD MÃ VISIBLE, tell Boss"; done

echo; if [ "$FAILS" = 0 ]; then echo "POST-DEPLOY PRIVACY CHECK: PASS"; exit 0
else echo "POST-DEPLOY PRIVACY CHECK: FAIL ($FAILS fails, $LEAKS leaks)"; exit 1; fi
