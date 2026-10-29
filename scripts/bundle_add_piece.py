#!/usr/bin/env python3
"""Piece 102: atomic bundle write. One process holds fcntl.flock on the lock file
for the whole run: backup -> copy piece folder -> INVENTORY row -> repack ->
inventory check + sync check --inventory + privacy scan -> rollback on failure.

Usage:
  bundle_add_piece.py --folder NN-name --src DIR --commit SHA --branch B --base BASE
                      [--tgz PATH] [--lock PATH] [--dry-run] [--no-wait]
DIR must contain patches/ and/or proof/. Exit 0 ok, 1 check failed (rolled back),
2 usage error, 3 lock busy (--no-wait).
"""
import argparse, fcntl, hashlib, os, shutil, subprocess, sys, tarfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TGZ = "/workspace/sassy-closet/out/pending-draft-prs.tgz"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def default_checks(tgz, d):
    py = sys.executable
    return [
        ("inventory", [py, os.path.join(HERE, "bundle_inventory_check.py"), d]),
        ("sync", [py, os.path.join(HERE, "bundle_sync_check.py"), "--tgz", tgz, "--dir", d, "--inventory"]),
        ("privacy", [py, os.path.join(HERE, "privacy_scan.py"), tgz]),
    ]


def upsert_row(inv, row):
    lines = open(inv).read().splitlines() if os.path.exists(inv) else []
    out, replaced = [], False
    for ln in lines:
        if ln.split("\t", 1)[0] == row[0]:
            if not replaced:
                out.append("\t".join(row)); replaced = True
        elif ln.strip():
            out.append(ln)
    if not replaced:
        out.append("\t".join(row))
    with open(inv, "w") as f:
        f.write("\n".join(out) + "\n")
    return replaced


def repack(tgz, d):
    tmp = tgz + ".tmp-%d" % os.getpid()
    with tarfile.open(tmp, "w:gz") as t:
        t.add(d, arcname=os.path.basename(d))
    os.replace(tmp, tgz)


def run(a, checks=None, log=print):
    tgz = os.path.abspath(a.tgz)
    d = tgz[:-4] if tgz.endswith(".tgz") else tgz + ".d"
    src = os.path.abspath(a.src)
    if not os.path.isdir(src) or not any(os.path.isdir(os.path.join(src, s)) for s in ("patches", "proof")):
        log("ERROR: --src must contain patches/ or proof/"); return 2
    if "/" in a.folder or not a.folder[:1].isdigit():
        log("ERROR: bad --folder"); return 2
    row = [a.folder, a.commit, a.branch, a.base, "1"]
    lockf = open(a.lock, "a")
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | (fcntl.LOCK_NB if a.no_wait else 0))
    except BlockingIOError:
        log("LOCK BUSY: %s" % a.lock); return 3
    try:
        log("lock held: %s (pid %d)" % (a.lock, os.getpid()))
        exists = os.path.isdir(os.path.join(d, a.folder))
        log("piece %s: %s folder; row %s" % (a.folder, "replace" if exists else "add", "/".join(row)))
        if a.dry_run:
            log("DRY RUN: no changes; current sha256 %s" % (sha256(tgz) if os.path.exists(tgz) else "-"))
            return 0
        ts = time.strftime("%Y%m%d-%H%M%S")
        btgz, bdir = "%s.bak-%s-%s" % (tgz, a.folder.split("-")[0], ts), "%s.bak-%s-%s" % (d, a.folder.split("-")[0], ts)
        if os.path.exists(tgz): shutil.copy2(tgz, btgz)
        if os.path.isdir(d): shutil.copytree(d, bdir, symlinks=True)
        log("backup: %s , %s" % (btgz, bdir))
        os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, a.folder)
        if exists: shutil.rmtree(dst)
        shutil.copytree(src, dst)
        upsert_row(os.path.join(d, "INVENTORY.tsv"), row)
        repack(tgz, d)
        failed = None
        for name, cmd in (checks if checks is not None else default_checks(tgz, d)):
            p = subprocess.run(cmd, capture_output=True, text=True)
            last = (p.stdout.strip().splitlines() or [""])[-1]
            log("check %s: rc=%d %s" % (name, p.returncode, last))
            if p.returncode != 0:
                failed = name; break
        if failed:
            shutil.rmtree(d, ignore_errors=True)
            if os.path.isdir(bdir): shutil.copytree(bdir, d, symlinks=True)
            if os.path.exists(btgz): shutil.copy2(btgz, tgz)
            elif os.path.exists(tgz): os.remove(tgz)
            log("ROLLED BACK (%s failed); sha256 %s" % (failed, sha256(tgz) if os.path.exists(tgz) else "-"))
            return 1
        log("OK sha256 %s" % sha256(tgz))
        return 0
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN); lockf.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("folder", "src", "commit", "branch", "base"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--tgz", default=DEFAULT_TGZ)
    ap.add_argument("--lock", default="/tmp/bundle.lock")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-wait", action="store_true")
    return run(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
