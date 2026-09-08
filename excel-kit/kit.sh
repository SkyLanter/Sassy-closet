#!/usr/bin/env bash
# Kit helper. Cute / pink / emoji / phone Excel is retired.
# save | run  → fetch live export, rebuild out/sassycloset.xlsx (all sheets),
#               sync Photos to out/Photos/{ma}/.
# Does not delete Boss OneDrive files. No Square Save. No passwords.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: kit.sh save|run [out-dir]

ONE hub named sassycloset. Fetch live
https://sassy-closet.vercel.app/api/export, rebuild out/sassycloset.xlsx
(All + category sheets + Orders + Readme), and sync Photos to
out/Photos/{ma}/.

  save    fetch export → rebuild xlsx → sync Photos (the one command)
  run     same as save

OneDrive land path:
  Documents/Sassy Closet/sassycloset.xlsx
  Documents/Sassy Closet/Photos/{MA}/001.jpg
  Documents/Sassy Closet/README.txt

Does not rebuild blush / emoji / phone workbooks.
Does not invent mã. Does not Square Save. Does not Facebook Post.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CMD="${1:-}"
OUT_DIR="${2:-${SASSY_OUT:-$REPO_ROOT/out}}"
XLSX_NAME="sassycloset.xlsx"
PYTHON="${PYTHON:-python3}"

if [[ -z "$CMD" || "$CMD" == "-h" || "$CMD" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$CMD" == "wishlist" || "$CMD" == "cute" || "$CMD" == "boutique" ]]; then
  echo "kit.sh: cute / Wishlist / boutique pull is retired. Use: kit.sh save" >&2
  exit 2
fi

if [[ "$CMD" != "save" && "$CMD" != "run" ]]; then
  echo "kit.sh: unknown command '$CMD' (want save or run)." >&2
  echo "Cute Wishlist rebuilds are retired." >&2
  usage >&2
  exit 2
fi

mkdir -p "$OUT_DIR"
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

copied=0
for dest_dir in "${shop_dirs[@]}"; do
  if [[ -d "$dest_dir" ]]; then
    dest="$dest_dir/$XLSX_NAME"
    cp "$SRC" "$dest"
    if [[ -f "$OUT_DIR/README.txt" ]]; then
      cp "$OUT_DIR/README.txt" "$dest_dir/README.txt"
    fi
    if [[ -d "$OUT_DIR/Photos" ]]; then
      mkdir -p "$dest_dir/Photos"
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
    echo "kit: copied hub → $dest_dir (left other OneDrive files alone)"
    copied=1
    break
  fi
done

if [[ "$copied" -eq 0 ]]; then
  echo "kit: OneDrive Documents/Sassy Closet/ not mounted; left artifact at $OUT_DIR"
  echo "kit: did not delete or touch OneDrive files"
fi
