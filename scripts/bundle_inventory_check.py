#!/usr/bin/env python3
"""Piece 50: READ-ONLY, WARN-only draft bundle inventory check.

Compares the numbered draft folders in an unpacked pending-draft-prs bundle
with the rows of its INVENTORY.tsv. Reports:
  missing_row    folder has no INVENTORY row (and is not a known non-PR folder)
  missing_folder INVENTORY row has no folder
  no_patches     PR folder has no patches/*.patch
  no_proof       PR folder has no proof/ files
  dup_row        folder listed more than once
Known non-PR folders (01-15-combined, 08-stack-check) are reported as INFO.
Output: folder names and issue codes only. No network, no writes.

Piece 87 (strict gaps): every folder without a row and every row without a
folder is listed BY NAME (GAP lines), allowlisted or not. Exit 1 when any
folder has no row and is not on the NON_PR allowlist.
"""
import argparse
import os
import re
import sys

FOLDER_RE = re.compile(r"^\d{2,}(-\d{2,})?-[a-z0-9-]+$")


def piece_key(name):
    """Piece 101: numeric sort so 100 comes after 99."""
    m = re.match(r"^(\d+)", name)
    return (int(m.group(1)) if m else -1, name)
NON_PR = {"01-15-combined": "pre-inventory combined pack",
          "08-stack-check": "push dry-run helper (no patches)"}


def check(bundle_dir):
    folders = sorted((d for d in os.listdir(bundle_dir)
                     if os.path.isdir(os.path.join(bundle_dir, d)) and FOLDER_RE.match(d)), key=piece_key)
    rows = []
    inv = os.path.join(bundle_dir, "INVENTORY.tsv")
    if os.path.exists(inv):
        with open(inv, encoding="utf-8") as fh:
            rows = [ln.split("\t")[0].strip() for ln in fh if ln.strip()]
    issues, info = [], []
    seen = set()
    for r in rows:
        if r in seen:
            issues.append((r, "dup_row"))
        seen.add(r)
    for f in folders:
        if f in NON_PR and f not in seen:
            info.append((f, "non_pr_folder"))
            continue
        if f not in seen:
            issues.append((f, "missing_row"))
        p = os.path.join(bundle_dir, f)
        pd = os.path.join(p, "patches")
        if not (os.path.isdir(pd) and any(x.endswith(".patch") for x in os.listdir(pd))):
            issues.append((f, "no_patches"))
        pr = os.path.join(p, "proof")
        if not (os.path.isdir(pr) and os.listdir(pr)):
            issues.append((f, "no_proof"))
    for r in sorted(seen, key=piece_key):
        if r not in folders:
            issues.append((r, "missing_folder"))
    folders_without_row = [f for f in folders if f not in seen]
    rows_without_folder = [r for r in sorted(seen, key=piece_key) if r not in folders]
    unallowed = [f for f in folders_without_row if f not in NON_PR]
    return {"folders": len(folders), "rows": len(rows), "issues": issues, "info": info,
            "folders_without_row": folders_without_row,
            "rows_without_folder": rows_without_folder,
            "unallowed_missing_rows": unallowed}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle_dir")
    a = ap.parse_args(argv)
    res = check(a.bundle_dir)
    print(f"folders {res['folders']} inventory_rows {res['rows']} "
          f"non_pr {len(res['info'])}")
    for f, c in res["info"]:
        print(f"INFO {c} {f}")
    print(f"gap folders_without_row {len(res['folders_without_row'])} "
          f"rows_without_folder {len(res['rows_without_folder'])}")
    for f in res["folders_without_row"]:
        tag = "allowlisted" if f in NON_PR else "NOT_ALLOWLISTED"
        print(f"GAP folder_without_row {f} {tag}")
    for r in res["rows_without_folder"]:
        print(f"GAP row_without_folder {r}")
    for f, c in res["issues"]:
        print(f"WARN {c} {f}")
    if res["unallowed_missing_rows"]:
        print("FAIL folders without inventory row: " + " ".join(res["unallowed_missing_rows"]))
        return 1
    if not res["issues"]:
        print("OK bundle matches inventory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
