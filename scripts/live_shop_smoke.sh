#!/usr/bin/env bash
# Read-only live HTTP smoke for Sassy Closet. GET only: no tokens, no cookies,
# no deploy, no Blob/Meta/price writes. Never prints response bodies; any
# cost/source leak is reported by field NAME only.
#
# Usage: scripts/live_shop_smoke.sh [--dry-run] [--with-privacy]
#   --dry-run       list every check; no network.
#   --with-privacy  also run scripts/post_deploy_privacy_check.sh (GET-only by default).
# Env: SHOP_HOSTS (space list, default both shop hosts), INTAKE_BASE,
#      HELD_MAS (space list; default = data/held.json heldIncomplete + neverList + Q02),
#      MIN_CATALOG (default 1), CHECK_TIMEOUT (default 20).
# Exit 0 only when every check PASSes.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
DRY=0; PRIV=0
for a in "$@"; do case "$a" in --dry-run) DRY=1;; --with-privacy) PRIV=1;; *) echo "unknown arg $a" >&2; exit 2;; esac; done
SHOPS="${SHOP_HOSTS:-https://sassy-closet-shop.vercel.app https://sassycloset.vercel.app}"
INTAKE="${INTAKE_BASE:-https://sassy-closet.vercel.app}"
T="${CHECK_TIMEOUT:-20}"; MIN="${MIN_CATALOG:-1}"
# Intake home is the Nhung form (has a "Taobao link" label), so only cost field names count there.
LEAK_RE='cost_cny|cost_usd|costCny|costUsd'
# Held list, canonicalised with held_policy.norm_ma (trim, upper, strip leading zeros).
HELD="$(HELD_MAS="${HELD_MAS:-}" python3 - "$HERE" <<'PY'
import json, os, sys
sys.path.insert(0, sys.argv[1])
from held_policy import norm_ma
raw = os.environ.get("HELD_MAS", "").split()
if not raw:
    p = os.path.join(sys.argv[1], "..", "data", "held.json")
    d = json.load(open(p))
    raw = list(d.get("heldIncomplete", [])) + list(d.get("neverList", [])) + ["Q02"]
out = []
for m in raw:
    n = norm_ma(m)
    if n and n not in out: out.append(n)
print(" ".join(out))
PY
)" || { echo "FAIL  could not build held list"; exit 1; }

if [ "$DRY" = 1 ]; then
  echo "DRY RUN (no network). shops=[$SHOPS] intake=$INTAKE"
  for s in $SHOPS; do
    echo "CHECK GET  $s/api/health -> 200 reading=blob, productCount>=$MIN"
    echo "CHECK GET  $s/m/S06 -> 200 shows \$25"
    for m in $HELD; do echo "CHECK GET  $s/m/$m -> 404 (held)"; done
  done
  echo "CHECK GET  $INTAKE/ -> 200, no cost/source field names"
  [ "$PRIV" = 1 ] && { echo "--- post_deploy_privacy_check.sh --dry-run ---"; WRITE_PROBES=0 "$HERE/post_deploy_privacy_check.sh" --dry-run; } \
    || echo "NOTE  privacy gates: run scripts/post_deploy_privacy_check.sh (or --with-privacy)"
  exit 0
fi

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
FAILS=0
get() { curl -s -m "$T" -o "$TMP/body" -w '%{http_code}' "$1" 2>/dev/null || echo 000; }
res() { if [ "$1" = ok ]; then echo "PASS  $2"; else echo "FAIL  $2  ($3)"; FAILS=$((FAILS+1)); fi; }
for s in $SHOPS; do
  c=$(get "$s/api/health")
  r=$(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print(d.get("reading"),int(d.get("productCount") or 0))' "$TMP/body" 2>/dev/null || echo "? 0")
  rd=${r% *}; n=${r#* }
  { [ "$c" = 200 ] && [ "$rd" = blob ] && [ "$n" -ge "$MIN" ]; } && res ok "$s health reading=blob, catalog=$n" || res no "$s health" "http $c reading=$rd catalog=$n"
  c=$(get "$s/m/S06"); { [ "$c" = 200 ] && grep -q '\$25' "$TMP/body"; } && res ok "$s /m/S06 shows \$25" || res no "$s /m/S06 \$25" "http $c - S06 MUST BE \$25, tell Boss"
  for m in $HELD; do c=$(get "$s/m/$m"); [ "$c" = 404 ] && res ok "$s /m/$m 404 (held)" || res no "$s /m/$m held" "http $c - HELD MÃ VISIBLE, tell Boss"; done
done
c=$(get "$INTAKE/"); f=$(grep -oiE "$LEAK_RE" "$TMP/body" | sort -u | tr '\n' ' ')
if [ "$c" != 200 ]; then res no "intake home" "http $c"
elif [ -n "$f" ]; then res no "intake home" "200 but LEAK fields: $f"
else res ok "intake home 200"; fi

PF=0
if [ "$PRIV" = 1 ]; then
  echo "--- post_deploy_privacy_check.sh (GET-only) ---"
  WRITE_PROBES=0 INTAKE_BASE="$INTAKE" HELD_MAS="$HELD" SHOP_BASE="${SHOPS%% *}" CHECK_TIMEOUT="$T" "$HERE/post_deploy_privacy_check.sh" || PF=1
fi
echo
if [ "$FAILS" = 0 ]; then echo "LIVE SHOP SMOKE: PASS"; else echo "LIVE SHOP SMOKE: FAIL ($FAILS fails)"; fi
[ "$PRIV" = 1 ] && { [ "$PF" = 0 ] && echo "PRIVACY CHECK: PASS" || echo "PRIVACY CHECK: FAIL"; }
[ "$FAILS" = 0 ] && [ "$PF" = 0 ]
