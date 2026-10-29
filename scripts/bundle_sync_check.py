#!/usr/bin/env python3
"""Piece 83: READ-ONLY bundle sync check.

Compares every file in pending-draft-prs.tgz with the unpacked
pending-draft-prs/ folder by sha256. Reports:
  missing    in tarball, not in folder
  extra      in folder, not in tarball
  different  in both, sha256 differs
Exit 1 on any drift. --inventory also runs bundle_inventory_check.
Output: relative paths and codes only. No network, no writes.
"""
import argparse
import hashlib
import os
import sys
import tarfile

DEFAULT_TGZ = "/workspace/sassy-closet/out/pending-draft-prs.tgz"


def _sha(fh):
    h = hashlib.sha256()
    for chunk in iter(lambda: fh.read(65536), b""):
        h.update(chunk)
    return h.hexdigest()


def tar_hashes(tgz):
    out = {}
    with tarfile.open(tgz, "r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            name = m.name.lstrip("./")
            parts = name.split("/", 1)
            if len(parts) != 2:
                continue
            out[parts[1]] = _sha(tf.extractfile(m))
    return out


def dir_hashes(d):
    out = {}
    for root, _, files in os.walk(d):
        for f in files:
            p = os.path.join(root, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, d).replace(os.sep, "/")] = _sha(fh)
    return out


def compare(tgz, folder):
    t, d = tar_hashes(tgz), dir_hashes(folder)
    issues = [(p, "missing") for p in sorted(set(t) - set(d))]
    issues += [(p, "extra") for p in sorted(set(d) - set(t))]
    issues += [(p, "different") for p in sorted(set(t) & set(d)) if t[p] != d[p]]
    return {"tar_files": len(t), "dir_files": len(d), "issues": issues}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tgz", default=DEFAULT_TGZ)
    ap.add_argument("--dir", default=None, help="default: tgz path minus .tgz")
    ap.add_argument("--inventory", action="store_true")
    a = ap.parse_args(argv)
    folder = a.dir or a.tgz[:-4]
    res = compare(a.tgz, folder)
    print(f"tar_files {res['tar_files']} dir_files {res['dir_files']}")
    for p, c in res["issues"]:
        print(f"DRIFT {c} {p}")
    rc = 1 if res["issues"] else 0
    if not res["issues"]:
        print("OK bundle in sync")
    if a.inventory:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import bundle_inventory_check as bic
        inv = bic.check(folder)
        for f in inv["folders_without_row"]:
            tag = "allowlisted" if f in bic.NON_PR else "NOT_ALLOWLISTED"
            print(f"INVENTORY GAP folder_without_row {f} {tag}")
        for r in inv["rows_without_folder"]:
            print(f"INVENTORY GAP row_without_folder {r}")
        for f, c in inv["issues"]:
            print(f"INVENTORY WARN {c} {f}")
        if inv["issues"] or inv["unallowed_missing_rows"]:
            rc = 1
        else:
            print(f"OK inventory folders {inv['folders']} rows {inv['rows']}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
