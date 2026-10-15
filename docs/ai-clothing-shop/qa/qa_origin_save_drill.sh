#!/usr/bin/env bash
# Preview Save drill — proves Save is not silent and public HTML cannot drift.
# Requires Origin §18 endpoints. Refuses the Production sell-test host unless
# Boss set CONFIRM_PROD_DRILL=YES and you restore in the same sitting.
#
# Never invent mã. Default target is A01 titleEn nudge + restore only.
set -euo pipefail

SHOP="${SHOP:-}"
MA="${MA:-A01}"
ADMIN_COOKIE="${ADMIN_COOKIE:-}"
ADMIN_TOKEN="${ADMIN_TOKEN:-}"
CONFIRM_PROD_DRILL="${CONFIRM_PROD_DRILL:-}"
PROD="https://sassy-closet-shop.vercel.app"
UA="SassyCloset-LearnQA/1.0"
HERE="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "$SHOP" ]]; then
  echo "Set SHOP to a Preview URL (not Production)." >&2
  exit 2
fi
SHOP="${SHOP%/}"

if [[ "$SHOP" == "$PROD" && "$CONFIRM_PROD_DRILL" != "YES" ]]; then
  echo "Refusing Production sell-test. Use a Preview host, or Boss CONFIRM_PROD_DRILL=YES + restore." >&2
  exit 2
fi

case "$MA" in
  A01|S01|P01|P03|P04|K01|H01|A02) ;;
  P02|P05)
    echo "Refusing Hold mã $MA for a title drill. Use A01." >&2
    exit 2
    ;;
  *)
    echo "Refusing non-allowlist mã $MA." >&2
    exit 2
    ;;
esac

auth_args=()
if [[ -n "$ADMIN_COOKIE" ]]; then
  auth_args=(-H "Cookie: $ADMIN_COOKIE")
elif [[ -n "$ADMIN_TOKEN" ]]; then
  auth_args=(-H "Authorization: Bearer $ADMIN_TOKEN")
else
  echo "Set ADMIN_COOKIE or ADMIN_TOKEN for the Preview admin session." >&2
  exit 2
fi

json_get() {
  curl -sS -A "$UA" "${auth_args[@]}" --max-time 25 "$1"
}

echo "== 0 look lock on this host =="
SHOP="$SHOP" python3 "$HERE/qa_selltest_origin_gate.py" --look

echo "== 1 catalog snapshot =="
CATALOG_JSON="$(json_get "$SHOP/api/admin/catalog")"
python3 - "$CATALOG_JSON" "$MA" <<'PY'
import json, sys
payload = json.loads(sys.argv[1])
ma = sys.argv[2]
products = payload["products"]
row = next(p for p in products if p["ma"] == ma)
print("catalogSha", payload.get("catalogSha") or payload.get("sha256"))
print("updatedAt", payload.get("updatedAt") or payload.get("exportedAt"))
print("titleEn", row.get("titleEn") or row.get("title_en"))
if row.get("status") == "hold":
    raise SystemExit("refusing to drill a Hold row")
PY

OLD_SHA="$(python3 -c 'import json,sys; p=json.loads(sys.argv[1]); print(p.get("catalogSha") or p.get("sha256"))' "$CATALOG_JSON")"
OLD_TITLE="$(python3 -c 'import json,sys; p=json.loads(sys.argv[1]); ma=sys.argv[2]; r=next(x for x in p["products"] if x["ma"]==ma); print(r.get("titleEn") or r.get("title_en") or "")' "$CATALOG_JSON" "$MA")"
NONCE="qa-cache-$(date -u +%Y%m%dT%H%M%SZ)"
NEW_TITLE="${OLD_TITLE} ${NONCE}"

echo "== 2 Save $MA title nudge =="
SAVE_BODY="$(printf '%s' "$NEW_TITLE" | python3 -c 'import json,sys; print(json.dumps({"ma":sys.argv[1],"titleEn":sys.stdin.read()}))' "$MA")"
SAVE_RESP="$(curl -sS -A "$UA" "${auth_args[@]}" --max-time 25 \
  -H "Content-Type: application/json" \
  -X POST "$SHOP/api/admin/save" \
  --data "$SAVE_BODY")"
echo "$SAVE_RESP" | python3 -c '
import json, sys
r = json.load(sys.stdin)
need = ("ok", "blobWritten", "catalogSha", "revalidated")
missing = [k for k in need if k not in r]
if missing:
    raise SystemExit("Save receipt missing " + ",".join(missing))
if r.get("ok") is not True or r.get("blobWritten") is not True:
    raise SystemExit("Save did not confirm Blob write")
paths = r.get("revalidated") or []
for p in ("/", f"/m/{r.get(\"ma\")}"):
    if p not in paths and not any(str(x).startswith("/m/") for x in paths):
        raise SystemExit("revalidated[] missing public paths")
print("receipt ok", r.get("catalogSha"), "paths", paths)
'

echo "== 3 catalog sha must change =="
sleep 1
CATALOG2="$(json_get "$SHOP/api/admin/catalog")"
NEW_SHA="$(python3 -c 'import json,sys; p=json.loads(sys.argv[1]); print(p.get("catalogSha") or p.get("sha256"))' "$CATALOG2")"
if [[ "$NEW_SHA" == "$OLD_SHA" ]]; then
  echo "FAIL catalogSha unchanged after Save — silent Save" >&2
  exit 1
fi
echo "catalogSha $OLD_SHA -> $NEW_SHA"

echo "== 4 public HTML must pick up nonce (two warms) =="
saw=0
for i in 1 2; do
  body="$(curl -sS -A "$UA" --max-time 25 "$SHOP/m/$MA")"
  if grep -Fq "$NONCE" <<<"$body"; then
    echo "GET $i /m/$MA has nonce"
    saw=1
    break
  fi
  echo "GET $i /m/$MA missing nonce (ISR STALE is allowed once)"
  sleep 2
done
if [[ "$saw" -ne 1 ]]; then
  echo "FAIL /m/$MA still missing nonce after two warms — cache drift" >&2
  exit 1
fi

echo "== 5 restore title =="
RESTORE="$(printf '%s' "$OLD_TITLE" | python3 -c 'import json,sys; print(json.dumps({"ma":sys.argv[1],"titleEn":sys.stdin.read()}))' "$MA")"
curl -sS -A "$UA" "${auth_args[@]}" --max-time 25 \
  -H "Content-Type: application/json" \
  -X POST "$SHOP/api/admin/save" \
  --data "$RESTORE" >/dev/null
sleep 2
curl -sS -A "$UA" --max-time 25 "$SHOP/m/$MA" >/dev/null
curl -sS -A "$UA" --max-time 25 "$SHOP/m/$MA" >/dev/null

echo "== 6 look lock after restore =="
SHOP="$SHOP" python3 "$HERE/qa_selltest_origin_gate.py" --look
echo "Save drill passed."
