#!/usr/bin/env bash
# Kit helper for Square.xlsx + Finance.xlsx.
# books | square | finance → rebuild empty tax-ready books.
# Does not delete Boss OneDrive files. No Square Save. No passwords. No cute.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: kit.sh books|square|finance [out-dir]

Bought / tax books (empty templates — no invented mã or $):

  out/Square.xlsx
  out/Finance.xlsx

  books     rebuild both books + optional OneDrive copy (no deletes)
  square    same as books
  finance   same as books

OneDrive land path (copy only if the shop folder already exists):

  Documents/Sassy Closet/Square.xlsx
  Documents/Sassy Closet/Finance.xlsx

On_Hand starts empty (staged site mãs are not bought).
Finance starts empty (no invented sales or $).
San Jose, CA sales tax is 10.000% (CDTFA, effective Apr 1, 2026).
Does not invent mã. Does not Square Save. Does not Facebook Post.
Does not delete other OneDrive files.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CMD="${1:-}"
OUT_DIR="${2:-${SASSY_OUT:-$REPO_ROOT/out}}"
PYTHON="${PYTHON:-python3}"

if [[ -z "$CMD" || "$CMD" == "-h" || "$CMD" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$CMD" == "wishlist" || "$CMD" == "cute" || "$CMD" == "boutique" ]]; then
  echo "kit.sh: cute / Wishlist / boutique pull is retired. Use: kit.sh books" >&2
  exit 2
fi

if [[ "$CMD" == "save" || "$CMD" == "run" ]]; then
  echo "kit.sh: hub save/run is not part of this books rebuild. Use: kit.sh square" >&2
  exit 2
fi

shop_dirs=()
if [[ -n "${SASSY_HUB_DIR:-}" ]]; then
  shop_dirs+=("${SASSY_HUB_DIR}")
fi
if [[ -n "${SASSY_SHOP_DIR:-}" ]]; then
  shop_dirs+=("${SASSY_SHOP_DIR}")
fi
if [[ -n "${SASSY_SOT_DIR:-}" ]]; then
  shop_dirs+=("${SASSY_SOT_DIR}")
fi
shop_dirs+=(
  "${HOME}/OneDrive/Documents/Sassy Closet"
  "${HOME}/OneDrive - Personal/Documents/Sassy Closet"
  "${HOME}/Library/CloudStorage/OneDrive-Personal/Documents/Sassy Closet"
)

copy_if_shop_mounted() {
  local copied=0
  local dest_dir
  for dest_dir in "${shop_dirs[@]}"; do
    if [[ -d "$dest_dir" ]]; then
      "$@" "$dest_dir"
      echo "kit: copied → $dest_dir (left other OneDrive files alone)"
      copied=1
      break
    fi
  done
  if [[ "$copied" -eq 0 ]]; then
    echo "kit: OneDrive Documents/Sassy Closet/ not mounted; left artifacts at $OUT_DIR"
    echo "kit: did not delete or touch OneDrive files"
  fi
}

copy_books() {
  local dest_dir="$1"
  cp "$OUT_DIR/Square.xlsx" "$dest_dir/Square.xlsx"
  cp "$OUT_DIR/Finance.xlsx" "$dest_dir/Finance.xlsx"
}

mkdir -p "$OUT_DIR"

if [[ "$CMD" == "square" || "$CMD" == "finance" || "$CMD" == "books" ]]; then
  "$PYTHON" "$SCRIPT_DIR/build_square_finance.py" --out-dir "$OUT_DIR"
  for name in Square.xlsx Finance.xlsx; do
    if [[ ! -f "$OUT_DIR/$name" ]]; then
      echo "kit.sh: builder did not write $OUT_DIR/$name" >&2
      exit 1
    fi
  done
  echo "kit: Square.xlsx + Finance.xlsx in $OUT_DIR"
  echo "kit: OneDrive land path: Documents/Sassy Closet/Square.xlsx"
  echo "kit: OneDrive land path: Documents/Sassy Closet/Finance.xlsx"
  copy_if_shop_mounted copy_books
  exit 0
fi

echo "kit.sh: unknown command '$CMD' (want books, square, or finance)." >&2
echo "Cute Wishlist rebuilds are retired." >&2
usage >&2
exit 2
