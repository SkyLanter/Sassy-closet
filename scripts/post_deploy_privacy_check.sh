#!/usr/bin/env bash
# Read-only check after intake data links are open without a session.
# GET /api/submissions, /api/export, /api/ma/S06, and /admin/shop must be 200
# with no cookie and X-Robots-Tag: noindex, nofollow, nosnippet.
# GET /api/submissions/S06 may be 200 or 404. This script never POSTs or PATCHes.
# No tokens, no cookies, no deploy, no Blob/Meta/price writes.
# Never prints response bodies (so cost values never reach logs).
#
# Usage: scripts/post_deploy_privacy_check.sh [--dry-run]
#   --dry-run   list every check and its expected result; no network.
# Env: INTAKE_BASE, SHOP_BASE, CHECK_TIMEOUT (default 20),
#      HELD_MAS (space list, default "K03 K04 K05 V04 Q02 G01 H02 A27 S16")
# Exit 0 only when every check PASSes.
set -u
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
INTAKE="${INTAKE_BASE:-https://sassy-closet.vercel.app}"
SHOP="${SHOP_BASE:-https://sassy-closet-shop.vercel.app}"
T="${CHECK_TIMEOUT:-20}"
HELD="${HELD_MAS:-K03 K04 K05 V04 Q02 G01 H02 A27 S16}"
OPEN="/api/export /api/submissions /api/ma/S06 /admin/shop"
LEAK_RE='cost_cny|cost_usd|costCny|costUsd|source_link|sourceLink|taobao'

if [ "$DRY" = 1 ]; then
  echo "DRY RUN (no network). intake=$INTAKE shop=$SHOP"
  for p in $OPEN; do echo "CHECK GET  $INTAKE$p -> 200 without auth, X-Robots-Tag: noindex, nofollow, nosnippet"; done
  echo "CHECK GET  $INTAKE/api/submissions/S06 -> 200 or 404, X-Robots-Tag: noindex, nofollow, nosnippet"
  echo "SKIP  POST/PATCH (intake writes are open; this script does not send them)"
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
has_noindex() { tr -d '\r' < "$TMP/hdr" | grep -qiE '^x-robots-tag:[[:space:]]*noindex,[[:space:]]*nofollow,[[:space:]]*nosnippet'; }
check_open() {  # $1 label, $2 code, $3 1 to allow 404
  if [ "$3" = 1 ]; then
    if [ "$2" != 200 ] && [ "$2" != 404 ]; then res no "$1" "http $2, expected 200 or 404 without auth"; return; fi
  elif [ "$2" != 200 ]; then res no "$1" "http $2, expected 200 without auth"; return; fi
  if ! has_noindex; then res no "$1" "http $2 missing X-Robots-Tag: noindex, nofollow, nosnippet"; return; fi
  res ok "$1 ($2, noindex, nofollow, nosnippet)"
}

GETFAIL=0
for p in $OPEN; do
  before=$FAILS; c=$(req GET "$INTAKE$p"); check_open "intake GET $p" "$c" 0
  [ "$FAILS" != "$before" ] && GETFAIL=1
done
before=$FAILS; c=$(req GET "$INTAKE/api/submissions/S06"); check_open "intake GET /api/submissions/S06" "$c" 1
[ "$FAILS" != "$before" ] && GETFAIL=1
echo "SKIP  POST/PATCH (intake writes are open; this script does not send them)"

c=$(req GET "$SHOP/api/health")
r=$(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d.get("reading"),(d.get("blob") or {}).get("readable"))' "$TMP/body" 2>/dev/null || echo "? ?")
{ [ "$c" = 200 ] && [ "$r" = "blob True" ]; } && res ok "shop health reading=blob, blob readable" || res no "shop health" "http $c, reading/readable=$r"
c=$(req GET "$SHOP/m/S06"); { [ "$c" = 200 ] && grep -q '\$25' "$TMP/body"; } && res ok "shop /m/S06 200 shows \$25" || res no "shop /m/S06 \$25" "http $c"
for m in $HELD; do c=$(req GET "$SHOP/m/$m"); [ "$c" = 404 ] && res ok "shop /m/$m 404 (held)" || res no "shop /m/$m held" "http $c - HELD MÃ VISIBLE, tell Boss"; done

echo; if [ "$FAILS" = 0 ]; then echo "POST-DEPLOY PRIVACY CHECK: PASS"; exit 0
else echo "POST-DEPLOY PRIVACY CHECK: FAIL ($FAILS fails, $LEAKS leaks)"; exit 1; fi
