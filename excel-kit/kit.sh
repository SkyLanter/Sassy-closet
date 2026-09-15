#!/usr/bin/env bash
# Kit helper.
# books | square | finance → rebuild empty Square.xlsx + Finance.xlsx
# save | run               → fetch live export, rebuild sassycloset.xlsx
# Does not delete Boss OneDrive files. No Square Save. No passwords. No cute.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: kit.sh books|square|finance|save|run [out-dir]

Bought / tax books (empty templates — no invented mã or $):

  out/Square.xlsx
  out/Finance.xlsx

  books     rebuild both books + optional OneDrive copy (no deletes)
  square    same as books
  finance   same as books

ONE hub named sassycloset (offline backup if the website dies):

  save    fetch export → rebuild xlsx → sync Photos (the one command)
  run     same as save

OneDrive land path:
  Documents/Sassy Closet/Square.xlsx
  Documents/Sassy Closet/Finance.xlsx
  Documents/Sassy Closet/sassycloset.xlsx
  Documents/Sassy Closet/Photos/{MA}/001.jpg
  Documents/Sassy Closet/README.txt

On_Hand starts empty (staged site mãs are not bought).
Finance starts empty (no invented sales or $).
Does not rebuild blush / emoji / phone workbooks.
Does not invent mã. Does not Square Save. Does not Facebook Post.
Does not delete other OneDrive files.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CMD="${1:-}"
OUT_DIR="${2:-${SASSY_OUT:-$REPO_ROOT/out}}"
PYTHON="${PYTHON:-python3}"
XLSX_NAME="sassycloset.xlsx"

if [[ -z "$CMD" || "$CMD" == "-h" || "$CMD" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$CMD" == "wishlist" || "$CMD" == "cute" || "$CMD" == "boutique" ]]; then
  echo "kit.sh: cute / Wishlist / boutique pull is retired. Use: kit.sh books or kit.sh save" >&2
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

copy_hub() {
  local dest_dir="$1"
  cp "$OUT_DIR/$XLSX_NAME" "$dest_dir/$XLSX_NAME"
  if [[ -f "$OUT_DIR/README.txt" ]]; then
    cp "$OUT_DIR/README.txt" "$dest_dir/README.txt"
  fi
  if [[ -d "$OUT_DIR/Photos" ]]; then
    mkdir -p "$dest_dir/Photos"
    local ma_dir ma
    for ma_dir in "$OUT_DIR/Photos"/*; do
      [[ -d "$ma_dir" ]] || continue
      ma="$(basename "$ma_dir")"
      if [[ "$ma" == "A02" ]]; then
        echo "kit: refusing to copy retired mã A02 (renamed to P02, not P05)" >&2
        continue
      fi
      mkdir -p "$dest_dir/Photos/$ma"
      cp -R "$ma_dir/." "$dest_dir/Photos/$ma/"
    done
  fi
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

if [[ "$CMD" == "save" || "$CMD" == "run" ]]; then
  "$PYTHON" "$SCRIPT_DIR/build_sassycloset_hub.py" --out-dir "$OUT_DIR"
  SRC="$OUT_DIR/$XLSX_NAME"
  if [[ ! -f "$SRC" ]]; then
    echo "kit.sh: builder did not write $SRC" >&2
    exit 1
  fi
  echo "kit: sassycloset hub $SRC"
  echo "kit: OneDrive land path: Documents/Sassy Closet/sassycloset.xlsx"
  echo "kit:   Photos/{MA}/ = Documents/Sassy Closet/Photos/{MA}/"
  echo "kit:   README.txt notes that path"
  copy_if_shop_mounted copy_hub
  exit 0
fi

echo "kit.sh: unknown command '$CMD' (want books, square, finance, save, or run)." >&2
echo "Cute Wishlist rebuilds are retired." >&2
usage >&2
exit 2
