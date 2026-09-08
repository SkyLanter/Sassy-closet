#!/usr/bin/env bash
# Kit helper. Cute / pink / emoji / phone Excel is retired.
# pull | plain | track  → build Sassy_Closet_Track.xlsx from the live site export
#                         and copy it to OneDrive only if the shop folder already exists.
# Does not delete Boss OneDrive files. No Square Save. No passwords.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: kit.sh pull|plain|track [out-dir]

Build the teammate floor tracker (Sassy_Closet_Track.xlsx) from
https://sassy-closet.vercel.app/api/export and leave it under out/.

  pull    same as track (replaces cute Wishlist and the 20-column dump)
  plain   same as track
  track   build + verify + optional OneDrive copy (no deletes)

Does not rebuild blush / emoji / phone workbooks.
Does not delete Sassy_Closet_Data.xlsx or other OneDrive files.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CMD="${1:-}"
OUT_DIR="${2:-${SASSY_OUT:-$REPO_ROOT/out}}"
XLSX_NAME="Sassy_Closet_Track.xlsx"
PYTHON="${PYTHON:-python3}"

if [[ -z "$CMD" || "$CMD" == "-h" || "$CMD" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$CMD" == "wishlist" || "$CMD" == "cute" || "$CMD" == "boutique" ]]; then
  echo "kit.sh: cute / Wishlist / boutique pull is retired. Use: kit.sh pull" >&2
  exit 2
fi

if [[ "$CMD" != "pull" && "$CMD" != "plain" && "$CMD" != "track" ]]; then
  echo "kit.sh: unknown command '$CMD' (want pull, plain, or track)." >&2
  echo "Cute Wishlist rebuilds are retired." >&2
  usage >&2
  exit 2
fi

mkdir -p "$OUT_DIR"
"$PYTHON" "$SCRIPT_DIR/build_floor_track.py" --out-dir "$OUT_DIR"
SRC="$OUT_DIR/$XLSX_NAME"
if [[ ! -f "$SRC" ]]; then
  echo "kit.sh: builder did not write $SRC" >&2
  exit 1
fi

KIT_OUT="$SCRIPT_DIR/out"
mkdir -p "$KIT_OUT"
if [[ "$(cd "$OUT_DIR" && pwd)" != "$(cd "$KIT_OUT" && pwd)" ]]; then
  cp "$SRC" "$KIT_OUT/$XLSX_NAME"
fi

echo "kit: floor tracker $SRC"

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
    dest="$dest_dir/$XLSX_NAME"
    cp "$SRC" "$dest"
    echo "kit: copied $XLSX_NAME → $dest (left other OneDrive files alone)"
    copied=1
    break
  fi
done

if [[ "$copied" -eq 0 ]]; then
  echo "kit: OneDrive shop folder not mounted; left artifact at $SRC"
  echo "kit: did not delete or touch Documents/Sassy Closet/ files"
fi
