#!/usr/bin/env bash
# Kit helper for Square.xlsx + Finance.xlsx.
# square | finance | books  → rebuild both empty books and copy to OneDrive
#                             only if Documents/Sassy Closet/ already exists.
# Does not delete Boss OneDrive files. No Square Save. No passwords. No cute.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: kit.sh square|finance|books [out-dir]

Build the bought / on-hand tracker and the tax-ready book:

  out/Square.xlsx
  out/Finance.xlsx

  square    build both + optional OneDrive copy (no deletes)
  finance   same as square
  books     same as square

On_Hand starts empty (staged site mãs are not bought).
Finance starts empty (no invented sales or $).
Does not rebuild blush / emoji / phone workbooks.
Does not invent mã. Does not Square Save. Does not Facebook Post.

OneDrive land path:
  Documents/Sassy Closet/Square.xlsx
  Documents/Sassy Closet/Finance.xlsx
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
  echo "kit.sh: cute / Wishlist / boutique pull is retired. Use: kit.sh square" >&2
  exit 2
fi

if [[ "$CMD" != "square" && "$CMD" != "finance" && "$CMD" != "books" ]]; then
  echo "kit.sh: unknown command '$CMD' (want square, finance, or books)." >&2
  echo "Cute Wishlist rebuilds are retired." >&2
  usage >&2
  exit 2
fi

mkdir -p "$OUT_DIR"
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

shop_dirs=()
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

copied=0
for dest_dir in "${shop_dirs[@]}"; do
  if [[ -d "$dest_dir" ]]; then
    cp "$OUT_DIR/Square.xlsx" "$dest_dir/Square.xlsx"
    cp "$OUT_DIR/Finance.xlsx" "$dest_dir/Finance.xlsx"
    echo "kit: copied Square.xlsx + Finance.xlsx → $dest_dir (left other OneDrive files alone)"
    copied=1
    break
  fi
done

if [[ "$copied" -eq 0 ]]; then
  echo "kit: OneDrive Documents/Sassy Closet/ not mounted; left artifacts at $OUT_DIR"
  echo "kit: did not delete or touch OneDrive files"
fi
