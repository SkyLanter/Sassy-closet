#!/usr/bin/env bash
# Read-only health check to run AFTER Boss unblocks the Vercel Blob store.
# GET requests only. No tokens, no writes, no deploy. Prints PASS/FAIL per check.
# Usage: scripts/post_blob_unblock_check.sh
# Env (for tests): INTAKE_BASE, SHOP_BASE, CHECK_TIMEOUT (seconds, default 20)
set -u
INTAKE="${INTAKE_BASE:-https://sassy-closet.vercel.app}"
SHOP="${SHOP_BASE:-https://sassy-closet-shop.vercel.app}"
T="${CHECK_TIMEOUT:-20}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
FAILS=0
get() { curl -s -D "$TMP/hdr" -m "$T" -o "$TMP/body" -w '%{http_code}' "$1" 2>/dev/null || echo 000; }
res() { if [ "$1" = ok ]; then echo "PASS  $2"; else echo "FAIL  $2  ($3)"; FAILS=$((FAILS+1)); fi; }
down() { grep -q '"storeUnavailable":true' "$TMP/body"; }
noindex() { tr -d '\r' < "$TMP/hdr" | grep -qiE '^x-robots-tag:[[:space:]]*noindex,[[:space:]]*nofollow'; }

c=$(get "$INTAKE/"); { [ "$c" = 200 ] && ! grep -q "kho đang không đọc được" "$TMP/body"; } && res ok "intake home 200, real FX" || res no "intake home" "http $c or default-FX fallback shown"
c=$(get "$INTAKE/api/fx"); { [ "$c" = 200 ] && grep -q usd_cny "$TMP/body" && ! down; } && res ok "intake /api/fx 200 (store readable)" || res no "intake /api/fx" "http $c"
# Direct links, no session. Bodies are not printed. S06 sell lock is checked on the shop page.
for path in /api/submissions /api/ma/S06 /api/export; do
  c=$(get "$INTAKE$path")
  { [ "$c" = 200 ] && noindex && ! down; } && res ok "intake $path 200 noindex without login" || res no "intake $path" "http $c, expected 200 with X-Robots-Tag noindex, nofollow"
done
c=$(get "$INTAKE/api/submissions/S06")
{ { [ "$c" = 200 ] || [ "$c" = 404 ]; } && noindex && ! down; } && res ok "intake /api/submissions/S06 $c noindex without login" || res no "intake /api/submissions/S06" "http $c, expected 200 or 404 with X-Robots-Tag noindex, nofollow"

c=$(get "$SHOP/api/health")
r=$(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d.get("reading"),(d.get("blob") or {}).get("readable"))' "$TMP/body" 2>/dev/null || echo "? ?")
{ [ "$c" = 200 ] && [ "$r" = "blob True" ]; } && res ok "shop health reading=blob, blob readable" || res no "shop health" "http $c, reading/readable=$r"
c=$(get "$SHOP/m/S06"); { [ "$c" = 200 ] && grep -q '\$25' "$TMP/body"; } && res ok "shop /m/S06 200 shows \$25" || res no "shop /m/S06 \$25" "http $c"
c=$(get "$SHOP/m/K03"); [ "$c" = 404 ] && res ok "shop /m/K03 404 (held)" || res no "shop /m/K03 held" "http $c - HELD MÃ VISIBLE, tell Boss"
for m in A01 A02 S01 P01; do c=$(get "$SHOP/m/$m"); [ "$c" = 200 ] && res ok "shop /m/$m 200" || res no "shop /m/$m" "http $c"; done

echo; if [ "$FAILS" = 0 ]; then echo "POST-UNBLOCK CHECK: PASS"; exit 0; else echo "POST-UNBLOCK CHECK: FAIL ($FAILS)"; exit 1; fi
